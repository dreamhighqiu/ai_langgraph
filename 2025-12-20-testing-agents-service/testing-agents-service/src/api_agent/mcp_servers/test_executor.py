"""
测试执行器MCP服务器

本MCP服务器提供pytest测试执行和结果收集功能：
- 执行pytest测试脚本（支持并行执行）
- 收集测试结果和Allure报告
- 生成Allure HTML报告
- 分析测试失败原因
- 生成执行摘要

主要工具：
1. execute_pytest: 执行pytest测试（支持pytest-xdist并行）
2. generate_allure_report: 生成Allure HTML报告
3. collect_test_results: 收集测试结果
4. analyze_failures: 分析测试失败
5. generate_report_summary: 生成报告摘要
6. check_parallel_support: 检查并行执行支持
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


import os
import json
import subprocess
import xml.etree.ElementTree as ET
import shutil
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Optional, List
from pathlib import Path
from enum import Enum

from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# 数据模型
# ============================================================================
# noqa  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WldwUFVBPT06OTgxOTczMGY=

class DistributionMode(str, Enum):
    """pytest-xdist分发模式"""
    LOAD = "load"
    LOADSCOPE = "loadscope"
    LOADFILE = "loadfile"
    EACH = "each"
    NO = "no"


class ExecutionResult(BaseModel):
    """执行结果"""
    success: bool = Field(description="是否成功")
    exit_code: int = Field(description="退出码")
    stdout: str = Field(default="", description="标准输出")
    stderr: str = Field(default="", description="标准错误")
    duration_seconds: float = Field(default=0, description="执行耗时(秒)")
    total_tests: int = Field(default=0, description="总测试数")
    passed: int = Field(default=0, description="通过数")
    failed: int = Field(default=0, description="失败数")
    skipped: int = Field(default=0, description="跳过数")
    errors: int = Field(default=0, description="错误数")
    allure_results_dir: Optional[str] = Field(default=None, description="Allure JSON结果目录")
    allure_report_dir: Optional[str] = Field(default=None, description="Allure HTML报告目录")
    junit_xml: Optional[str] = Field(default=None, description="JUnit XML路径")
    parallel_enabled: bool = Field(default=False, description="是否启用了并行执行")
    workers_used: int = Field(default=1, description="使用的worker数量")
    command: str = Field(default="", description="执行的命令")


class FailureInfo(BaseModel):
    """失败信息"""
    test_name: str = Field(description="测试名称")
    test_file: str = Field(description="测试文件")
    error_type: str = Field(default="", description="错误类型")
    error_message: str = Field(description="错误消息")
    stack_trace: str = Field(default="", description="堆栈追踪")
    suggestion: str = Field(default="", description="修复建议")


class ParallelSupportInfo(BaseModel):
    """并行支持信息"""
    xdist_installed: bool = Field(description="pytest-xdist是否已安装")
    xdist_version: Optional[str] = Field(default=None, description="pytest-xdist版本")
    cpu_count: int = Field(description="CPU核心数")
    recommended_workers: int = Field(description="推荐的worker数量")
    rerunfailures_installed: bool = Field(default=False, description="pytest-rerunfailures是否已安装")
    allure_installed: bool = Field(default=False, description="allure命令行是否可用")


class AllureReportResult(BaseModel):
    """Allure报告生成结果"""
    success: bool = Field(description="是否成功")
    message: str = Field(description="结果消息")
    report_dir: Optional[str] = Field(default=None, description="报告目录")
    report_url: Optional[str] = Field(default=None, description="报告URL（如果启动了服务器）")


class TestExecutorContext:
    """测试执行器上下文"""
    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir
        self.last_result: Optional[ExecutionResult] = None
        self._parallel_support: Optional[ParallelSupportInfo] = None

    def check_parallel_support(self) -> ParallelSupportInfo:
        """检查并行执行支持"""
        if self._parallel_support is not None:
            return self._parallel_support
# noqa  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WldwUFVBPT06OTgxOTczMGY=

        # 检查pytest-xdist
        xdist_installed = False
        xdist_version = None
        try:
            result = subprocess.run(
                ["pip", "show", "pytest-xdist"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                xdist_installed = True
                for line in result.stdout.split("\n"):
                    if line.startswith("Version:"):
                        xdist_version = line.split(":")[1].strip()
                        break
        except Exception:
            pass

        # 检查pytest-rerunfailures
        rerun_installed = False
        try:
            result = subprocess.run(
                ["pip", "show", "pytest-rerunfailures"],
                capture_output=True,
                text=True
            )
            rerun_installed = result.returncode == 0
        except Exception:
            pass

        # 检查allure命令行
        allure_installed = False
        try:
            result = subprocess.run(
                ["allure", "--version"],
                capture_output=True,
                text=True
            )
            allure_installed = result.returncode == 0
        except Exception:
            pass

        # 获取CPU核心数
        cpu_count = os.cpu_count() or 4
        recommended_workers = min(cpu_count, 8)

        self._parallel_support = ParallelSupportInfo(
            xdist_installed=xdist_installed,
            xdist_version=xdist_version,
            cpu_count=cpu_count,
            recommended_workers=recommended_workers,
            rerunfailures_installed=rerun_installed,
            allure_installed=allure_installed
        )

        return self._parallel_support


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[TestExecutorContext]:
    """管理服务器生命周期"""
    config = server.config or {}
    working_dir = config.get("working_dir", ".")
    context = TestExecutorContext(working_dir=working_dir)

    parallel_info = context.check_parallel_support()
    logger.info(f"并行执行支持: xdist={parallel_info.xdist_installed}, "
                f"CPU核心数={parallel_info.cpu_count}, "
                f"Allure CLI={parallel_info.allure_installed}")

    yield context


# 创建MCP服务器实例
mcp = FastMCP(name="TestExecutor", lifespan=server_lifespan)


# ============================================================================
# 辅助函数
# ============================================================================

def _parse_junit_xml(xml_path: str) -> dict[str, Any]:
    """解析JUnit XML结果"""
    if not os.path.exists(xml_path):
        return {"error": f"JUnit XML文件不存在: {xml_path}"}
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        results = {
            "testsuite": root.get("name", "unknown"),
            "tests": int(root.get("tests", 0)),
            "failures": int(root.get("failures", 0)),
            "errors": int(root.get("errors", 0)),
            "skipped": int(root.get("skipped", 0)),
            "time": float(root.get("time", 0)),
            "test_cases": []
        }
        
        for testcase in root.findall(".//testcase"):
            case = {
                "name": testcase.get("name"),
                "classname": testcase.get("classname"),
                "time": float(testcase.get("time", 0)),
                "status": "passed"
            }
            
            failure = testcase.find("failure")
            if failure is not None:
                case["status"] = "failed"
                case["failure"] = {
                    "type": failure.get("type", "AssertionError"),
                    "message": failure.get("message", ""),
                    "text": failure.text or ""
                }
# pragma: no cover  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WldwUFVBPT06OTgxOTczMGY=
            
            error = testcase.find("error")
            if error is not None:
                case["status"] = "error"
                case["error"] = {
                    "type": error.get("type", "Exception"),
                    "message": error.get("message", ""),
                    "text": error.text or ""
                }
            
            skipped = testcase.find("skipped")
            if skipped is not None:
                case["status"] = "skipped"
                case["skip_reason"] = skipped.get("message", "")
            
            results["test_cases"].append(case)
        
        return results
    except Exception as e:
        return {"error": f"解析JUnit XML失败: {str(e)}"}


def _analyze_failure(failure_info: dict) -> FailureInfo:
    """分析单个失败并生成建议"""
    error_type = failure_info.get("type", "Unknown")
    error_message = failure_info.get("message", "")
    stack_trace = failure_info.get("text", "")
    
    suggestion = ""
    
    if "AssertionError" in error_type:
        if "status" in error_message.lower():
            suggestion = "检查API端点是否正确，确认服务器状态是否正常运行"
        elif "expected" in error_message.lower():
            suggestion = "验证期望值是否与实际API响应匹配，可能需要更新测试数据"
        else:
            suggestion = "检查断言条件是否正确，确认测试数据是否有效"
    elif "ConnectionError" in error_type or "connection" in error_message.lower():
        suggestion = "确认API服务器正在运行，检查网络连接和BASE_URL配置"
    elif "Timeout" in error_type:
        suggestion = "增加请求超时时间，或检查API服务器性能问题"
    elif "JSONDecodeError" in error_type:
        suggestion = "API返回的不是有效的JSON，检查Content-Type和响应体格式"
    elif "KeyError" in error_type:
        suggestion = "响应JSON中缺少预期的字段，检查API文档确认字段名称"
    elif "401" in error_message or "Unauthorized" in error_message:
        suggestion = "认证失败，检查API密钥或Token配置"
    elif "403" in error_message or "Forbidden" in error_message:
        suggestion = "权限不足，确认用户角色和API访问权限"
    elif "404" in error_message or "Not Found" in error_message:
        suggestion = "API端点不存在，检查URL路径是否正确"
    elif "500" in error_message:
        suggestion = "服务器内部错误，检查请求参数是否有效，查看服务器日志"
    else:
        suggestion = "检查测试代码和API实现，确认测试环境配置正确"
    
    return FailureInfo(
        test_name=failure_info.get("test_name", "unknown"),
        test_file=failure_info.get("test_file", "unknown"),
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        suggestion=suggestion
    )


# ============================================================================
# MCP工具
# ============================================================================

@mcp.tool()
async def check_parallel_support(ctx: Context = None) -> str:
    """
    检查并行执行支持状态

    返回pytest-xdist安装状态、CPU核心数、推荐的worker数量和Allure CLI状态

    返回：
        并行支持信息的JSON字符串
    """
    context = ctx.request_context.lifespan_context
    parallel_info = context.check_parallel_support()

    result = {
        "xdist_installed": parallel_info.xdist_installed,
        "xdist_version": parallel_info.xdist_version,
        "cpu_count": parallel_info.cpu_count,
        "recommended_workers": parallel_info.recommended_workers,
        "rerunfailures_installed": parallel_info.rerunfailures_installed,
        "allure_cli_installed": parallel_info.allure_installed,
        "message": ""
    }

    messages = []
    if parallel_info.xdist_installed:
        messages.append(f"✅ 并行执行已就绪，推荐使用 {parallel_info.recommended_workers} 个worker")
    else:
        messages.append("⚠️ pytest-xdist未安装，请运行: pip install pytest-xdist")

    if parallel_info.allure_installed:
        messages.append("✅ Allure CLI已安装，可生成HTML报告")
    else:
        messages.append("⚠️ Allure CLI未安装，无法生成HTML报告。请参考: https://allurereport.org/docs/install/")
# pragma: no cover  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WldwUFVBPT06OTgxOTczMGY=

    result["message"] = "\n".join(messages)

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def execute_pytest(
    test_path: str,
    markers: Optional[List[str]] = None,
    parallel: bool = False,
    workers: int = 0,
    dist_mode: str = "load",
    timeout: int = 300,
    verbose: bool = True,
    allure_results_dir: str = "./allure-results",
    fail_fast: bool = False,
    reruns: int = 0,
    reruns_delay: float = 1.0,
    extra_args: Optional[List[str]] = None,
    ctx: Context = None
) -> str:
    """
    执行pytest测试（支持并行执行）

    参数：
        test_path: 测试文件或目录路径
        markers: pytest markers列表（例如：["smoke", "critical"]）
        parallel: 是否并行执行（需要安装pytest-xdist）
        workers: 并行工作进程数（0=自动检测，-1=使用所有CPU）
        dist_mode: 分发模式 - load(负载均衡)/loadscope(按模块)/loadfile(按文件)/each/no
        timeout: 超时时间（秒）
        verbose: 是否详细输出
        allure_results_dir: Allure JSON结果目录
        fail_fast: 遇到失败立即停止（-x参数）
        reruns: 失败重试次数（需要pytest-rerunfailures）
        reruns_delay: 重试延迟（秒）
        extra_args: 额外的pytest参数

    返回：
        执行结果的JSON字符串，包含测试统计、并行执行信息等
    """
    context = ctx.request_context.lifespan_context
    parallel_info = context.check_parallel_support()

    cmd = ["pytest", test_path]

    if verbose:
        cmd.append("-v")

    if markers:
        marker_expr = " or ".join(markers)
        cmd.extend(["-m", marker_expr])

    actual_workers = 1
    parallel_enabled = False

    if parallel:
        if parallel_info.xdist_installed:
            parallel_enabled = True
            if workers == 0:
                actual_workers = parallel_info.recommended_workers
            elif workers == -1:
                actual_workers = parallel_info.cpu_count
            else:
                actual_workers = min(workers, parallel_info.cpu_count)

            cmd.extend(["-n", str(actual_workers)])

            if dist_mode in ["load", "loadscope", "loadfile", "each", "no"]:
                cmd.extend(["--dist", dist_mode])

            logger.info(f"启用并行执行: {actual_workers} workers, 分发模式: {dist_mode}")
        else:
            logger.warning("请求并行执行但pytest-xdist未安装，将使用串行执行")

    if fail_fast:
        cmd.append("-x")

    if reruns > 0 and parallel_info.rerunfailures_installed:
        cmd.extend(["--reruns", str(reruns)])
        if reruns_delay > 0:
            cmd.extend(["--reruns-delay", str(reruns_delay)])

    # JUnit XML用于结果解析
    junit_xml = os.path.join(context.working_dir, "junit-results.xml")
    cmd.extend(["--junitxml", junit_xml])

    # Allure JSON结果目录
    allure_path = os.path.join(context.working_dir, allure_results_dir)
    os.makedirs(allure_path, exist_ok=True)
    cmd.extend(["--alluredir", allure_path])

    if extra_args:
        cmd.extend(extra_args)

    cmd_str = " ".join(cmd)
    logger.info(f"执行命令: {cmd_str}")

    start_time = datetime.now()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=context.working_dir
        )
        exit_code = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        exit_code = -1
        stdout = ""
        stderr = f"测试执行超时（{timeout}秒）"
        logger.error(f"测试执行超时: {timeout}秒")
    except Exception as e:
        exit_code = -1
        stdout = ""
        stderr = str(e)
        logger.error(f"测试执行异常: {e}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    junit_results = _parse_junit_xml(junit_xml)

    total_tests = junit_results.get("tests", 0)
    failures = junit_results.get("failures", 0)
    errors = junit_results.get("errors", 0)
    skipped = junit_results.get("skipped", 0)
    passed = total_tests - failures - errors - skipped

    execution_result = ExecutionResult(
        success=exit_code == 0,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        duration_seconds=duration,
        total_tests=total_tests,
        passed=passed,
        failed=failures,
        skipped=skipped,
        errors=errors,
        allure_results_dir=allure_path,
        junit_xml=junit_xml,
        parallel_enabled=parallel_enabled,
        workers_used=actual_workers,
        command=cmd_str
    )

    context.last_result = execution_result

    logger.info(f"测试执行完成: 总计={total_tests}, 通过={passed}, 失败={failures}, "
                f"错误={errors}, 跳过={skipped}, 耗时={duration:.2f}s")

    return execution_result.model_dump_json(indent=2)


@mcp.tool()
async def generate_allure_report(
    allure_results_dir: str = "./allure-results",
    output_dir: str = "./allure-report",
    clean: bool = True,
    ctx: Context = None
) -> str:
    """
    从Allure JSON结果生成HTML报告

    参数：
        allure_results_dir: Allure JSON结果目录
        output_dir: HTML报告输出目录
        clean: 是否清理旧报告

    返回：
        生成结果的JSON字符串
    """
    context = ctx.request_context.lifespan_context
    parallel_info = context.check_parallel_support()

    if not parallel_info.allure_installed:
        return AllureReportResult(
            success=False,
            message="Allure CLI未安装。请参考安装指南: https://allurereport.org/docs/install/"
        ).model_dump_json(indent=2)

    results_path = os.path.join(context.working_dir, allure_results_dir)
    report_path = os.path.join(context.working_dir, output_dir)

    if not os.path.exists(results_path):
        return AllureReportResult(
            success=False,
            message=f"Allure结果目录不存在: {results_path}"
        ).model_dump_json(indent=2)

    # 构建allure generate命令
    cmd = ["allure", "generate", results_path, "-o", report_path]
    if clean:
        cmd.append("--clean")

    logger.info(f"生成Allure报告: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=context.working_dir
        )

        if result.returncode == 0:
            return AllureReportResult(
                success=True,
                message=f"Allure HTML报告已生成: {report_path}",
                report_dir=report_path
            ).model_dump_json(indent=2)
        else:
            return AllureReportResult(
                success=False,
                message=f"生成报告失败: {result.stderr}"
            ).model_dump_json(indent=2)

    except subprocess.TimeoutExpired:
        return AllureReportResult(
            success=False,
            message="生成报告超时"
        ).model_dump_json(indent=2)
    except Exception as e:
        return AllureReportResult(
            success=False,
            message=f"生成报告异常: {str(e)}"
        ).model_dump_json(indent=2)


@mcp.tool()
async def collect_test_results(
    junit_xml_path: Optional[str] = None,
    allure_results_dir: Optional[str] = None,
    ctx: Context = None
) -> str:
    """
    收集和解析测试结果

    参数：
        junit_xml_path: JUnit XML结果文件路径（可选，默认使用上次执行的结果）
        allure_results_dir: Allure结果目录（可选）

    返回：
        测试结果详情的JSON字符串
    """
    context = ctx.request_context.lifespan_context

    xml_path = junit_xml_path
    if not xml_path and context.last_result:
        xml_path = context.last_result.junit_xml

    if not xml_path:
        return json.dumps({
            "success": False,
            "error": "未找到JUnit XML结果文件，请先执行测试或提供文件路径"
        }, ensure_ascii=False, indent=2)

    results = _parse_junit_xml(xml_path)

    if "error" in results:
        return json.dumps({
            "success": False,
            "error": results["error"]
        }, ensure_ascii=False, indent=2)

    output = {
        "success": True,
        "summary": {
            "testsuite": results["testsuite"],
            "total": results["tests"],
            "passed": results["tests"] - results["failures"] - results["errors"] - results["skipped"],
            "failed": results["failures"],
            "errors": results["errors"],
            "skipped": results["skipped"],
            "duration_seconds": results["time"]
        },
        "test_cases": results["test_cases"]
    }

    return json.dumps(output, ensure_ascii=False, indent=2)


@mcp.tool()
async def analyze_failures(
    junit_xml_path: Optional[str] = None,
    ctx: Context = None
) -> str:
    """
    分析测试失败原因并生成修复建议

    参数：
        junit_xml_path: JUnit XML结果文件路径（可选）

    返回：
        失败分析和建议的JSON字符串
    """
    context = ctx.request_context.lifespan_context

    xml_path = junit_xml_path
    if not xml_path and context.last_result:
        xml_path = context.last_result.junit_xml

    if not xml_path:
        return json.dumps({
            "success": False,
            "error": "未找到测试结果，请先执行测试"
        }, ensure_ascii=False, indent=2)

    results = _parse_junit_xml(xml_path)

    if "error" in results:
        return json.dumps({
            "success": False,
            "error": results["error"]
        }, ensure_ascii=False, indent=2)

    failures = []
    for case in results.get("test_cases", []):
        if case["status"] in ["failed", "error"]:
            failure_data = case.get("failure") or case.get("error", {})
            failure_data["test_name"] = case["name"]
            failure_data["test_file"] = case.get("classname", "")

            failure_info = _analyze_failure(failure_data)
            failures.append(failure_info.model_dump())

    output = {
        "success": True,
        "total_failures": len(failures),
        "failures": failures,
        "general_recommendations": []
    }

    if len(failures) > 0:
        error_types = set(f["error_type"] for f in failures)

        if any("Connection" in t for t in error_types):
            output["general_recommendations"].append(
                "检查API服务器状态和网络连接"
            )

        if any("401" in f["error_message"] or "Unauthorized" in f["error_message"]
               for f in failures):
            output["general_recommendations"].append(
                "检查认证配置，确保Token或API Key正确"
            )

        if len(failures) > results["tests"] * 0.5:
            output["general_recommendations"].append(
                "大量测试失败，建议检查测试环境和基础配置"
            )

    return json.dumps(output, ensure_ascii=False, indent=2)


@mcp.tool()
async def generate_report_summary(
    junit_xml_path: Optional[str] = None,
    include_details: bool = True,
    ctx: Context = None
) -> str:
    """
    生成测试执行报告摘要

    参数：
        junit_xml_path: JUnit XML结果文件路径（可选）
        include_details: 是否包含详细信息

    返回：
        格式化的报告摘要字符串
    """
    context = ctx.request_context.lifespan_context

    xml_path = junit_xml_path
    if not xml_path and context.last_result:
        xml_path = context.last_result.junit_xml

    if not xml_path:
        return "❌ 未找到测试结果，请先执行测试"

    results = _parse_junit_xml(xml_path)

    if "error" in results:
        return f"❌ 无法读取测试结果: {results['error']}"

    total = results["tests"]
    passed = total - results["failures"] - results["errors"] - results["skipped"]
    pass_rate = (passed / total * 100) if total > 0 else 0

    report = []
    report.append("=" * 60)
    report.append("📊 API自动化测试执行报告")
    report.append("=" * 60)
    report.append(f"⏱️  执行时间: {results['time']:.2f}秒")
    report.append(f"📋 测试套件: {results['testsuite']}")
    report.append("")
    report.append("📈 执行统计:")
    report.append(f"   ├─ 总用例数: {total}")
    report.append(f"   ├─ ✅ 通过: {passed}")
    report.append(f"   ├─ ❌ 失败: {results['failures']}")
    report.append(f"   ├─ ⚠️  错误: {results['errors']}")
    report.append(f"   ├─ ⏭️  跳过: {results['skipped']}")
    report.append(f"   └─ 📊 通过率: {pass_rate:.1f}%")

    if include_details and results.get("test_cases"):
        report.append("")
        report.append("-" * 60)
        report.append("📝 用例详情:")

        for case in results["test_cases"]:
            status_icon = {
                "passed": "✅",
                "failed": "❌",
                "error": "⚠️",
                "skipped": "⏭️"
            }.get(case["status"], "❓")

            report.append(f"   {status_icon} {case['name']} ({case['time']:.3f}s)")

            if case["status"] == "failed" and "failure" in case:
                msg = case['failure']['message'][:80]
                report.append(f"      └─ {msg}...")
            elif case["status"] == "error" and "error" in case:
                msg = case['error']['message'][:80]
                report.append(f"      └─ {msg}...")

    report.append("")
    report.append("=" * 60)

    if pass_rate == 100:
        report.append("🎉 所有测试通过！")
    elif pass_rate >= 80:
        report.append("⚡ 大部分测试通过，请关注失败用例")
    elif pass_rate >= 50:
        report.append("⚠️  测试通过率较低，需要检查失败原因")
    else:
        report.append("🚨 大量测试失败，请检查测试环境和配置")

    return "\n".join(report)


@mcp.tool()
async def run_specific_tests(
    test_names: list[str],
    test_path: str = ".",
    ctx: Context = None
) -> str:
    """
    运行指定的测试用例

    参数：
        test_names: 测试用例名称列表
        test_path: 测试目录路径

    返回：
        执行结果的JSON字符串
    """
    if not test_names:
        return json.dumps({
            "success": False,
            "error": "请提供要运行的测试用例名称"
        }, ensure_ascii=False, indent=2)

    test_expr = " or ".join(test_names)

    return await execute_pytest(
        test_path=test_path,
        extra_args=["-k", test_expr],
        ctx=ctx
    )


# ============================================================================
# 主入口点
# ============================================================================

def main():
    """主入口点"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Executor MCP Server")
    parser.add_argument(
        "--working-dir", type=str, default=".",
        help="工作目录"
    )
    parser.add_argument(
        "--port", type=int, default=8004,
        help="SSE服务器端口号"
    )
    parser.add_argument(
        "--sse", action="store_true", default=True,
        help="启用SSE模式"
    )
    args = parser.parse_args()

    mcp.config = {
        "working_dir": args.working_dir
    }

    if args.sse:
        mcp.run(transport="sse", port=args.port, host="0.0.0.0")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
