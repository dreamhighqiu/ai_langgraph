"""
MCP 服务健康检查模块

用于检查各个 MCP 服务的连接状态，方便排查问题。
"""

import asyncio
import logging
import os
from typing import Dict, List, Tuple
from pathlib import Path

from config.mcp_settings import mcp_settings

logger = logging.getLogger(__name__)


async def check_stdio_mcp_server(
    name: str, command: str, args: List[str], timeout: float = 5.0
) -> Tuple[bool, str]:
    """
    检查 stdio 类型的 MCP 服务器
    
    Args:
        name: 服务器名称
        command: 命令
        args: 命令参数
        timeout: 超时时间（秒）
    
    Returns:
        (是否正常, 错误信息)
    """
    try:
        import subprocess
        import sys
        
        # 检查命令是否存在
        if command == "npx":
            # 对于 npx，我们只检查是否能执行
            process = subprocess.Popen(
                [command, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate(timeout=timeout)
            if process.returncode != 0:
                return False, f"命令 '{command}' 不可用: {stderr}"
        elif command == "node":
            # 检查 node 是否可用
            process = subprocess.Popen(
                [command, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate(timeout=timeout)
            if process.returncode != 0:
                return False, f"命令 '{command}' 不可用: {stderr}"
        else:
            # 对于其他命令，检查文件是否存在
            if not Path(command).exists() and not any(
                Path(p) / command for p in os.environ.get("PATH", "").split(os.pathsep)
            ):
                return False, f"命令 '{command}' 不存在"
        
        return True, "命令可用"
    except subprocess.TimeoutExpired:
        return False, f"检查超时（{timeout}秒）"
    except FileNotFoundError:
        return False, f"命令 '{command}' 未找到"
    except Exception as e:
        return False, f"检查失败: {str(e)}"


async def check_sse_mcp_server(name: str, url: str, timeout: float = 5.0) -> Tuple[bool, str]:
    """
    检查 SSE 类型的 MCP 服务器
    
    Args:
        name: 服务器名称
        url: 服务器 URL
        timeout: 超时时间（秒）
    
    Returns:
        (是否正常, 错误信息)
    """
    try:
        import aiohttp
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            # 首先尝试健康检查端点
            health_urls = [
                url.replace("/sse", "/health"),
                url.replace("/sse", "/ok"),
                url.rsplit("/", 1)[0] + "/health" if "/" in url else url + "/health",
            ]
            
            for health_url in health_urls:
                try:
                    async with session.get(health_url) as response:
                        if response.status == 200:
                            return True, f"服务正常 (HTTP {response.status})"
                except aiohttp.ClientError:
                    continue
            
            # 如果健康检查都失败，尝试连接 SSE 端点本身
            try:
                async with session.get(url) as response:
                    # 200 表示正常
                    # 404/405 可能表示端点存在但方法不对，说明服务器在运行
                    # 其他状态码可能表示服务器有问题
                    if response.status in (200, 404, 405):
                        status_msg = "服务器运行中" if response.status != 200 else "服务正常"
                        return True, f"{status_msg} (HTTP {response.status})"
                    else:
                        return False, f"服务返回错误状态码: {response.status}"
            except aiohttp.ClientConnectorError as e:
                return False, f"无法连接到服务器 ({url}): {str(e)}"
            except Exception as e:
                return False, f"连接失败: {str(e)}"
    except ImportError:
        # 如果没有 aiohttp，使用 requests 作为备选
        try:
            import requests
            health_urls = [
                url.replace("/sse", "/health"),
                url.replace("/sse", "/ok"),
                url.rsplit("/", 1)[0] + "/health" if "/" in url else url + "/health",
            ]
            
            for health_url in health_urls:
                try:
                    response = requests.get(health_url, timeout=timeout)
                    if response.status_code == 200:
                        return True, f"服务正常 (HTTP {response.status_code})"
                except requests.exceptions.RequestException:
                    continue
            
            # 尝试连接 SSE 端点
            try:
                response = requests.get(url, timeout=timeout)
                if response.status_code in (200, 404, 405):
                    status_msg = "服务器运行中" if response.status_code != 200 else "服务正常"
                    return True, f"{status_msg} (HTTP {response.status_code})"
                else:
                    return False, f"服务返回错误状态码: {response.status_code}"
            except requests.exceptions.ConnectionError as e:
                return False, f"无法连接到服务器 ({url}): {str(e)}"
            except requests.exceptions.RequestException as e:
                return False, f"连接失败: {str(e)}"
        except ImportError:
            return False, "需要安装 aiohttp 或 requests 库来检查 SSE 服务"
    except Exception as e:
        return False, f"检查失败: {str(e)}"


async def check_automation_quality_mcp() -> Tuple[bool, str]:
    """检查 automation_quality MCP 服务"""
    if not mcp_settings.automation_quality_enabled:
        return False, "服务已禁用"
    
    config = mcp_settings.get_automation_quality_config()
    server_path = mcp_settings.automation_quality_server_path
    
    # 检查服务器文件是否存在
    if not Path(server_path).exists():
        return False, f"服务器文件不存在: {server_path}"
    
    # 检查命令
    return await check_stdio_mcp_server(
        "automation_quality",
        config["command"],
        config["args"],
    )


async def check_playwright_mcp() -> Tuple[bool, str]:
    """检查 Playwright MCP 服务"""
    if not mcp_settings.playwright_mcp_enabled:
        return False, "服务已禁用"
    
    config = mcp_settings.get_playwright_mcp_config()
    return await check_stdio_mcp_server(
        "playwright",
        config["command"],
        config["args"],
    )


async def check_midscene_mcp() -> Tuple[bool, str]:
    """检查 Midscene MCP 服务"""
    if not mcp_settings.midscene_mcp_enabled:
        return False, "服务已禁用"
    
    config = mcp_settings.get_midscene_mcp_config()
    return await check_stdio_mcp_server(
        "midscene",
        config["command"],
        config["args"],
    )


async def check_rag_query_mcp() -> Tuple[bool, str]:
    """检查 RAG Query MCP 服务"""
    if not mcp_settings.rag_query_enabled:
        return False, "服务已禁用"
    
    config = mcp_settings.get_rag_query_config()
    return await check_sse_mcp_server("rag_query", config["url"])


async def check_rag_anything_mcp() -> Tuple[bool, str]:
    """检查 RAG Anything MCP 服务"""
    if not mcp_settings.rag_anything_enabled:
        return False, "服务已禁用"
    
    config = mcp_settings.get_rag_anything_config()
    return await check_sse_mcp_server("rag_anything", config["url"])


async def check_pytest_mcp() -> Tuple[bool, str]:
    """检查 Pytest MCP 服务"""
    if not mcp_settings.pytest_mcp_enabled:
        return False, "服务已禁用"
    
    config = mcp_settings.get_pytest_mcp_config()
    return await check_sse_mcp_server("pytest_mcp", config["url"])


async def check_chrome_mcp() -> Tuple[bool, str]:
    """检查 Chrome MCP 服务"""
    if not mcp_settings.chrome_mcp_enabled:
        return False, "服务已禁用"
    
    config = mcp_settings.get_chrome_mcp_config()
    return await check_sse_mcp_server("chrome_mcp", config["url"])


async def check_llm_api_key() -> Tuple[bool, str]:
    """
    检查 LLM API Key 配置
    
    Returns:
        (是否正常, 详细信息)
    """
    try:
        from config.settings import settings
        from config.llm_config import get_llm_info
        
        info = get_llm_info()
        provider = info.get("provider", "unknown")
        model = info.get("model", "unknown")
        base_url = info.get("base_url", "")
        
        if provider == "openai":
            api_key = settings.openai_api_key
            if not api_key:
                return False, "未配置 OPENAI_API_KEY"
            
            # 尝试简单的 API key 格式验证
            if not api_key.startswith("sk-"):
                return False, "API Key 格式可能不正确（应以 'sk-' 开头）"
            
            # 检查长度（OpenAI API key 通常较长）
            if len(api_key) < 20:
                return False, f"API Key 长度异常（{len(api_key)} 字符），可能无效"
            
            # 显示配置信息（不显示完整 key）
            key_preview = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 11 else "***"
            message = f"已配置（格式正确，模型: {model}"
            if base_url:
                message += f", Base URL: {base_url}"
            message += f", Key: {key_preview}）"
            
            # 注意：这里只做格式检查，不做实际 API 调用验证
            # 如果 API key 无效，会在实际使用时返回 401 错误
            return True, message
        
        elif provider == "deepseek":
            api_key = settings.deepseek_api_key
            if not api_key:
                return False, "未配置 DEEPSEEK_API_KEY"
            if not api_key.startswith("sk-"):
                return False, "API Key 格式可能不正确（应以 'sk-' 开头）"
            if len(api_key) < 20:
                return False, f"API Key 长度异常（{len(api_key)} 字符），可能无效"
            key_preview = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 11 else "***"
            return True, f"已配置（格式正确，模型: {model}, Key: {key_preview}）"
        
        elif provider == "anthropic":
            api_key = settings.anthropic_api_key
            if not api_key:
                return False, "未配置 ANTHROPIC_API_KEY"
            if not api_key.startswith("sk-ant-"):
                return False, "API Key 格式可能不正确（应以 'sk-ant-' 开头）"
            if len(api_key) < 20:
                return False, f"API Key 长度异常（{len(api_key)} 字符），可能无效"
            key_preview = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
            return True, f"已配置（格式正确，模型: {model}, Key: {key_preview}）"
        
        else:
            return False, f"未知的 LLM 提供商: {provider}"
    
    except ImportError as e:
        return False, f"无法导入配置模块: {str(e)}"
    except Exception as e:
        return False, f"检查失败: {str(e)}"


async def check_all_mcp_services() -> Dict[str, Tuple[bool, str]]:
    """
    检查所有 MCP 服务的状态
    
    Returns:
        字典，键为服务名称，值为 (是否正常, 详细信息) 元组
    """
    checks = {
        "automation_quality": check_automation_quality_mcp,
        "playwright": check_playwright_mcp,
        "midscene": check_midscene_mcp,
        "rag_query": check_rag_query_mcp,
        "rag_anything": check_rag_anything_mcp,
        "pytest_mcp": check_pytest_mcp,
        "chrome_mcp": check_chrome_mcp,
    }
    
    results = {}
    for name, check_func in checks.items():
        try:
            status, message = await check_func()
            results[name] = (status, message)
        except Exception as e:
            results[name] = (False, f"检查异常: {str(e)}")
    
    # 添加 LLM API Key 检查
    try:
        llm_status, llm_message = await check_llm_api_key()
        results["llm_api_key"] = (llm_status, llm_message)
    except Exception as e:
        results["llm_api_key"] = (False, f"检查异常: {str(e)}")
    
    return results


def print_mcp_health_report(results: Dict[str, Tuple[bool, str]]) -> None:
    """
    打印 MCP 服务健康检查报告
    
    Args:
        results: check_all_mcp_services() 的返回结果
    """
    print("\n" + "=" * 70)
    print("MCP 服务健康检查报告")
    print("=" * 70)
    
    # 分离 LLM 配置和其他服务
    llm_result = results.pop("llm_api_key", None)
    mcp_results = results
    
    healthy_count = 0
    unhealthy_count = 0
    
    # 先打印 LLM 配置（最重要）
    if llm_result:
        status, message = llm_result
        status_icon = "✓" if status else "✗"
        status_text = "正常" if status else "异常"
        status_color = "\033[92m" if status else "\033[91m"  # 绿色/红色
        reset_color = "\033[0m"
        
        print(f"{status_color}{status_icon} LLM API Key        {status_text:6s}{reset_color} - {message}")
        if status:
            healthy_count += 1
        else:
            unhealthy_count += 1
        print("-" * 70)
    
    # 打印 MCP 服务
    for name, (status, message) in sorted(mcp_results.items()):
        status_icon = "✓" if status else "✗"
        status_text = "正常" if status else "异常"
        status_color = "\033[92m" if status else "\033[91m"  # 绿色/红色
        reset_color = "\033[0m"
        
        print(f"{status_color}{status_icon} {name:20s} {status_text:6s}{reset_color} - {message}")
        
        if status:
            healthy_count += 1
        else:
            unhealthy_count += 1
    
    print("=" * 70)
    print(f"总计: {healthy_count} 个服务正常, {unhealthy_count} 个服务异常")
    
    # 如果有异常，给出提示
    if unhealthy_count > 0:
        print("\n⚠️  提示:")
        if llm_result and not llm_result[0]:
            print("  - ❌ LLM API Key 配置错误会导致 Agent 无法正常工作")
            print("  - 请检查 .env 文件中的 OPENAI_API_KEY、DEEPSEEK_API_KEY 或 ANTHROPIC_API_KEY")
            print("  - 如果 API Key 格式正确但仍报 401 错误，可能是 Key 已过期或无效")
            print("  - 请访问对应提供商的网站重新生成 API Key")
        elif llm_result and llm_result[0]:
            print("  - ⚠️  LLM API Key 格式检查通过，但实际使用时如出现 401 错误，请验证 Key 是否有效")
        print("  - 某些 MCP 服务异常可能不影响所有 Agent 的功能")
        print("  - 请根据实际使用的 Agent 检查对应的 MCP 服务状态")
    
    print("=" * 70 + "\n")


async def main():
    """主函数，用于命令行测试"""
    results = await check_all_mcp_services()
    print_mcp_health_report(results)


if __name__ == "__main__":
    import os
    import sys
    
    # 添加项目路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "src"))
    
    asyncio.run(main())

