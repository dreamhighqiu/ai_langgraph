"""
Pytest MCP Server - 统一的 Pytest 测试生成和执行服务

合并了原来的 pytest_generator (Port 8005) 和 test_executor (Port 8004)

本 MCP 服务器提供:
- 测试代码生成 (pytest + requests + allure)
- 测试执行 (支持并行执行)
- Allure 报告生成
- 测试结果分析

主要工具:
生成类:
  - generate_pytest_tests: 从测试套件生成 pytest 测试文件
  - generate_conftest: 生成 conftest.py 配置文件
  - generate_pytest_ini: 生成 pytest.ini 配置
  - generate_requirements: 生成测试依赖

执行类:
  - execute_pytest: 执行 pytest 测试（支持并行）
  - generate_allure_report: 生成 Allure HTML 报告
  - collect_test_results: 收集测试结果
  - analyze_failures: 分析测试失败
  - generate_report_summary: 生成报告摘要
  - check_parallel_support: 检查并行执行支持
"""

import os
import json
import subprocess
import xml.etree.ElementTree as ET
import shutil
import logging
import argparse
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Optional, List
from pathlib import Path
from enum import Enum

from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

# 尝试导入 schemas，如果失败则定义简化版本
try:
    from api_agent.models.schemas import (
        TestCase, TestSuite, TestPlan, TestStep, 
        HttpMethod, TestPriority, GeneratedTestFile, GenerationResult
    )
except ImportError:
    # 简化的数据模型（当无法导入时使用）
    class TestPriority(str, Enum):
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    class GeneratedTestFile(BaseModel):
        file_path: str
        file_name: str
        content: str
        language: str = "python"
        framework: str = "pytest"

    class GenerationResult(BaseModel):
        success: bool
        message: str
        files: List[Any] = []
        errors: List[str] = []

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# 数据模型
# ============================================================================

class DistributionMode(str, Enum):
    """pytest-xdist 分发模式"""
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
    report_url: Optional[str] = Field(default=None, description="报告URL")


class PytestMCPContext:
    """Pytest MCP 上下文"""
    def __init__(self, output_dir: str = "./generated_tests", working_dir: str = "."):
        self.output_dir = output_dir
        self.working_dir = working_dir
        self.generated_files: list = []
        self.last_result: Optional[ExecutionResult] = None
        self._parallel_support: Optional[ParallelSupportInfo] = None

    def check_parallel_support(self) -> ParallelSupportInfo:
        """检查并行执行支持"""
        if self._parallel_support is not None:
            return self._parallel_support

        xdist_installed = False
        xdist_version = None
        try:
            result = subprocess.run(
                ["pip", "show", "pytest-xdist"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                xdist_installed = True
                for line in result.stdout.split("\n"):
                    if line.startswith("Version:"):
                        xdist_version = line.split(":")[1].strip()
                        break
        except Exception:
            pass

        rerun_installed = False
        try:
            result = subprocess.run(
                ["pip", "show", "pytest-rerunfailures"],
                capture_output=True, text=True
            )
            rerun_installed = result.returncode == 0
        except Exception:
            pass

        allure_installed = False
        try:
            result = subprocess.run(
                ["allure", "--version"],
                capture_output=True, text=True
            )
            allure_installed = result.returncode == 0
        except Exception:
            pass

        cpu_count = os.cpu_count() or 1
        recommended = max(1, cpu_count - 1)

        self._parallel_support = ParallelSupportInfo(
            xdist_installed=xdist_installed,
            xdist_version=xdist_version,
            cpu_count=cpu_count,
            recommended_workers=recommended,
            rerunfailures_installed=rerun_installed,
            allure_installed=allure_installed
        )
        return self._parallel_support


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[PytestMCPContext]:
    """管理服务器生命周期"""
    config = server.config or {}
    output_dir = config.get("output_dir", "./generated_tests")
    working_dir = config.get("working_dir", ".")
    
    os.makedirs(output_dir, exist_ok=True)
    
    context = PytestMCPContext(output_dir=output_dir, working_dir=working_dir)
    yield context


# 创建 MCP 服务器实例
mcp = FastMCP(name="PytestMCP", lifespan=server_lifespan)


# ============================================================================
# 代码生成辅助函数
# ============================================================================

def _sanitize_name(name: str) -> str:
    """将名称转换为有效的 Python 标识符"""
    sanitized = name.lower()
    for char in [' ', '-', '.', '/', '\\', ':', '(', ')', '[', ']', '{', '}']:
        sanitized = sanitized.replace(char, '_')
    while '__' in sanitized:
        sanitized = sanitized.replace('__', '_')
    sanitized = sanitized.strip('_')
    if sanitized and sanitized[0].isdigit():
        sanitized = f"test_{sanitized}"
    return sanitized or "test_unnamed"


CONFTEST_TEMPLATE = '''"""
Pytest配置文件 - 共享fixtures和配置

Generated by Pytest MCP Server
"""

import json
import pytest
import requests
import allure
from typing import Generator, Optional

# API基础配置
BASE_URL = "{base_url}"
DEFAULT_TIMEOUT = 30


@pytest.fixture(scope="session")
def base_url() -> str:
    """返回API基础URL"""
    return BASE_URL


@pytest.fixture(scope="session")
def session() -> Generator[requests.Session, None, None]:
    """创建共享的requests session"""
    with requests.Session() as session:
        session.headers.update({{
            "Content-Type": "application/json",
            "Accept": "application/json"
        }})
        yield session


@pytest.fixture(scope="session")
def auth_token(session: requests.Session, base_url: str) -> Optional[str]:
    """获取认证token (根据实际API修改)"""
    return None


@pytest.fixture
def api_client(session: requests.Session, base_url: str, auth_token: Optional[str]):
    """创建API客户端fixture"""
    class APIClient:
        def __init__(self):
            self.session = session
            self.base_url = base_url
            if auth_token:
                self.session.headers["Authorization"] = f"Bearer {{auth_token}}"
        
        def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
            url = f"{{self.base_url}}{{endpoint}}"
            kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
            response = self.session.request(method, url, **kwargs)
            self._attach_to_allure(method, endpoint, kwargs, response)
            return response
        
        def _attach_to_allure(self, method: str, endpoint: str, kwargs: dict, response: requests.Response):
            request_info = {{
                "method": method,
                "url": f"{{self.base_url}}{{endpoint}}",
                "headers": dict(self.session.headers),
                "params": kwargs.get("params"),
                "json": kwargs.get("json"),
            }}
            allure.attach(
                json.dumps(request_info, indent=2, ensure_ascii=False),
                "请求信息", allure.attachment_type.JSON
            )
            
            try:
                response_body = response.json()
            except:
                response_body = response.text
            
            response_info = {{
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response_body,
                "elapsed_ms": response.elapsed.total_seconds() * 1000
            }}
            allure.attach(
                json.dumps(response_info, indent=2, ensure_ascii=False),
                "响应信息", allure.attachment_type.JSON
            )
        
        def get(self, endpoint: str, **kwargs): return self.request("GET", endpoint, **kwargs)
        def post(self, endpoint: str, **kwargs): return self.request("POST", endpoint, **kwargs)
        def put(self, endpoint: str, **kwargs): return self.request("PUT", endpoint, **kwargs)
        def delete(self, endpoint: str, **kwargs): return self.request("DELETE", endpoint, **kwargs)
        def patch(self, endpoint: str, **kwargs): return self.request("PATCH", endpoint, **kwargs)
    
    return APIClient()
'''


# ============================================================================
# 测试生成工具
# ============================================================================

@mcp.tool()
async def generate_conftest(
    base_url: str,
    output_dir: Optional[str] = None,
    ctx: Context = None
) -> str:
    """
    生成 pytest 的 conftest.py 配置文件

    参数：
        base_url: API 基础 URL
        output_dir: 输出目录（可选）

    返回：
        生成结果的 JSON 字符串
    """
    try:
        context = ctx.request_context.lifespan_context
        out_dir = output_dir or context.output_dir
        os.makedirs(out_dir, exist_ok=True)

        file_path = os.path.join(out_dir, "conftest.py")
        content = CONFTEST_TEMPLATE.format(base_url=base_url)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return json.dumps({
            "success": True,
            "message": "成功生成 conftest.py",
            "file_path": file_path
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"生成失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


@mcp.tool()
async def generate_pytest_ini(
    output_dir: Optional[str] = None,
    markers: Optional[List[str]] = None,
    ctx: Context = None
) -> str:
    """
    生成 pytest.ini 配置文件

    参数：
        output_dir: 输出目录（可选）
        markers: 自定义 markers 列表（可选）

    返回：
        生成结果的 JSON 字符串
    """
    try:
        context = ctx.request_context.lifespan_context
        out_dir = output_dir or context.output_dir
        os.makedirs(out_dir, exist_ok=True)

        default_markers = [
            "critical: 关键测试",
            "high: 高优先级测试",
            "medium: 中优先级测试",
            "low: 低优先级测试",
            "smoke: 冒烟测试",
            "regression: 回归测试"
        ]

        all_markers = default_markers + (markers or [])
        markers_str = "\n    ".join(all_markers)

        content = f'''[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --alluredir=./allure-results
markers =
    {markers_str}
'''

        file_path = os.path.join(out_dir, "pytest.ini")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return json.dumps({
            "success": True,
            "message": "成功生成 pytest.ini",
            "file_path": file_path
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"生成失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


@mcp.tool()
async def generate_requirements(
    output_dir: Optional[str] = None,
    extra_packages: Optional[List[str]] = None,
    ctx: Context = None
) -> str:
    """
    生成测试依赖的 requirements.txt

    参数：
        output_dir: 输出目录（可选）
        extra_packages: 额外的依赖包（可选）

    返回：
        生成结果的 JSON 字符串
    """
    try:
        context = ctx.request_context.lifespan_context
        out_dir = output_dir or context.output_dir
        os.makedirs(out_dir, exist_ok=True)

        packages = [
            "pytest>=7.0.0",
            "pytest-xdist>=3.0.0",
            "pytest-rerunfailures>=12.0",
            "pytest-timeout>=2.2.0",
            "allure-pytest>=2.13.0",
            "requests>=2.28.0",
            "jsonpath-ng>=1.5.0",
            "python-dotenv>=1.0.0",
            "pydantic>=2.0.0"
        ]

        if extra_packages:
            packages.extend(extra_packages)

        content = "\n".join(packages)
        file_path = os.path.join(out_dir, "requirements.txt")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return json.dumps({
            "success": True,
            "message": "成功生成 requirements.txt",
            "file_path": file_path
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"生成失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


# ============================================================================
# 测试执行工具
# ============================================================================

@mcp.tool()
async def execute_pytest(
    test_path: str = ".",
    markers: Optional[str] = None,
    keywords: Optional[str] = None,
    parallel: bool = False,
    workers: int = 0,
    reruns: int = 0,
    timeout: int = 300,
    verbose: bool = True,
    allure_results_dir: str = "./allure-results",
    junit_xml: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    ctx: Context = None
) -> str:
    """
    执行 pytest 测试

    参数：
        test_path: 测试路径或文件
        markers: pytest marker 表达式 (如 "smoke and not slow")
        keywords: 关键字表达式 (如 "test_login or test_logout")
        parallel: 是否启用并行执行
        workers: worker 数量 (0=自动检测)
        reruns: 失败重试次数
        timeout: 超时时间（秒）
        verbose: 详细输出
        allure_results_dir: Allure 结果目录
        junit_xml: JUnit XML 报告路径
        extra_args: 额外的 pytest 参数

    返回：
        执行结果的 JSON 字符串
    """
    try:
        context = ctx.request_context.lifespan_context
        start_time = datetime.now()

        # 构建命令
        cmd = ["pytest", test_path]
        
        if verbose:
            cmd.append("-v")
        
        if markers:
            cmd.extend(["-m", markers])
        
        if keywords:
            cmd.extend(["-k", keywords])
        
        # 并行执行
        parallel_enabled = False
        workers_used = 1
        if parallel:
            support = context.check_parallel_support()
            if support.xdist_installed:
                actual_workers = workers if workers > 0 else support.recommended_workers
                cmd.extend(["-n", str(actual_workers)])
                parallel_enabled = True
                workers_used = actual_workers
        
        # 失败重试
        if reruns > 0:
            support = context.check_parallel_support()
            if support.rerunfailures_installed:
                cmd.extend(["--reruns", str(reruns)])
        
        # Allure 结果
        os.makedirs(allure_results_dir, exist_ok=True)
        cmd.extend(["--alluredir", allure_results_dir])
        
        # JUnit XML
        actual_junit = junit_xml or "./junit-results.xml"
        cmd.extend(["--junitxml", actual_junit])
        
        # 超时
        cmd.extend(["--timeout", str(timeout)])
        
        # 额外参数
        if extra_args:
            cmd.extend(extra_args)

        logger.info(f"Executing: {' '.join(cmd)}")
        
        # 执行测试
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=context.working_dir,
            timeout=timeout + 60
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 解析结果
        total = passed = failed = skipped = errors = 0
        
        # 从 JUnit XML 解析结果
        if os.path.exists(actual_junit):
            try:
                tree = ET.parse(actual_junit)
                root = tree.getroot()
                for testsuite in root.findall(".//testsuite"):
                    total += int(testsuite.get("tests", 0))
                    failed += int(testsuite.get("failures", 0))
                    errors += int(testsuite.get("errors", 0))
                    skipped += int(testsuite.get("skipped", 0))
                passed = total - failed - errors - skipped
            except Exception as e:
                logger.warning(f"Failed to parse JUnit XML: {e}")
        
        exec_result = ExecutionResult(
            success=result.returncode == 0,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_seconds=duration,
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            allure_results_dir=allure_results_dir,
            junit_xml=actual_junit,
            parallel_enabled=parallel_enabled,
            workers_used=workers_used,
            command=" ".join(cmd)
        )
        
        context.last_result = exec_result
        return exec_result.model_dump_json(indent=2)

    except subprocess.TimeoutExpired:
        return json.dumps({
            "success": False,
            "message": f"测试执行超时 ({timeout}秒)",
            "exit_code": -1
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Execution error: {e}")
        return json.dumps({
            "success": False,
            "message": f"执行失败: {str(e)}",
            "exit_code": -1
        }, ensure_ascii=False, indent=2)


@mcp.tool()
async def generate_allure_report(
    results_dir: str = "./allure-results",
    report_dir: str = "./allure-report",
    clean: bool = True,
    ctx: Context = None
) -> str:
    """
    生成 Allure HTML 报告

    参数：
        results_dir: Allure 结果目录
        report_dir: 报告输出目录
        clean: 是否清理已有报告

    返回：
        生成结果的 JSON 字符串
    """
    try:
        context = ctx.request_context.lifespan_context
        support = context.check_parallel_support()
        
        if not support.allure_installed:
            return json.dumps({
                "success": False,
                "message": "Allure 命令行工具未安装，请先安装: npm install -g allure-commandline"
            }, ensure_ascii=False, indent=2)
        
        if clean and os.path.exists(report_dir):
            shutil.rmtree(report_dir)
        
        cmd = ["allure", "generate", results_dir, "-o", report_dir, "--clean"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=context.working_dir
        )
        
        if result.returncode == 0:
            return json.dumps({
                "success": True,
                "message": "Allure 报告生成成功",
                "report_dir": os.path.abspath(report_dir)
            }, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "success": False,
                "message": f"报告生成失败: {result.stderr}"
            }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"生成失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


@mcp.tool()
async def check_parallel_support(ctx: Context = None) -> str:
    """
    检查并行执行支持情况

    返回：
        并行支持信息的 JSON 字符串
    """
    try:
        context = ctx.request_context.lifespan_context
        support = context.check_parallel_support()
        return support.model_dump_json(indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e)
        }, ensure_ascii=False, indent=2)


@mcp.tool()
async def analyze_failures(
    junit_xml: str = "./junit-results.xml",
    ctx: Context = None
) -> str:
    """
    分析测试失败原因

    参数：
        junit_xml: JUnit XML 报告路径

    返回：
        失败分析结果的 JSON 字符串
    """
    try:
        if not os.path.exists(junit_xml):
            return json.dumps({
                "success": False,
                "message": f"JUnit XML 文件不存在: {junit_xml}"
            }, ensure_ascii=False, indent=2)
        
        failures = []
        tree = ET.parse(junit_xml)
        root = tree.getroot()
        
        for testcase in root.findall(".//testcase"):
            failure = testcase.find("failure")
            error = testcase.find("error")
            
            if failure is not None or error is not None:
                elem = failure if failure is not None else error
                failures.append(FailureInfo(
                    test_name=testcase.get("name", "unknown"),
                    test_file=testcase.get("classname", "unknown"),
                    error_type=elem.get("type", ""),
                    error_message=elem.get("message", ""),
                    stack_trace=elem.text or "",
                    suggestion="请检查测试代码和被测系统"
                ).model_dump())
        
        return json.dumps({
            "success": True,
            "total_failures": len(failures),
            "failures": failures
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"分析失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


# ============================================================================
# 主入口点
# ============================================================================

def main():
    """主入口点"""
    parser = argparse.ArgumentParser(description="Pytest MCP Server")
    parser.add_argument(
        "--output-dir", type=str, default="./generated_tests",
        help="默认输出目录"
    )
    parser.add_argument(
        "--working-dir", type=str, default=".",
        help="工作目录"
    )
    parser.add_argument(
        "--port", type=int, default=8004,
        help="SSE 服务器端口号"
    )
    parser.add_argument(
        "--sse", action="store_true", default=True,
        help="启用 SSE 模式"
    )
    args = parser.parse_args()

    mcp.config = {
        "output_dir": args.output_dir,
        "working_dir": args.working_dir
    }

    if args.sse:
        mcp.run(transport="sse", port=args.port, host="0.0.0.0")
    else:
        mcp.run()


if __name__ == "__main__":
    main()

