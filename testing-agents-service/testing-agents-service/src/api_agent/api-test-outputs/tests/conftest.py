"""
PlayTurbo API测试配置文件
包含共享的fixtures和配置
"""
import pytest
import requests
import json
import os
from typing import Dict, Any, Generator
import allure


class APIClient:
    """API客户端类，封装requests操作"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        初始化API客户端
        
        Args:
            base_url: API基础URL
            timeout: 请求超时时间
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "PlayTurbo-Test-Suite/1.0",
            "Accept": "application/json"
        })
        self.token = None
        
    def set_token(self, token: str):
        """设置认证token"""
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
    def clear_token(self):
        """清除认证token"""
        self.token = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
    
    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE等)
            endpoint: API端点路径
            **kwargs: 传递给requests的额外参数
            
        Returns:
            requests.Response对象
        """
        url = f"{self.base_url}{endpoint}"
        
        # 添加默认超时
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
            
        # 记录请求信息到Allure
        with allure.step(f"发送{method}请求到{endpoint}"):
            allure.attach(
                json.dumps({
                    "url": url,
                    "method": method,
                    "headers": dict(self.session.headers),
                    "params": kwargs.get("params"),
                    "json": kwargs.get("json"),
                    "data": kwargs.get("data")
                }, indent=2, ensure_ascii=False),
                "请求信息",
                allure.attachment_type.JSON
            )
            
            response = self.session.request(method, url, **kwargs)
            
            # 记录响应信息到Allure
            try:
                response_json = response.json()
                allure.attach(
                    json.dumps(response_json, indent=2, ensure_ascii=False),
                    "响应数据",
                    allure.attachment_type.JSON
                )
            except json.JSONDecodeError:
                allure.attach(
                    response.text[:1000],
                    "响应文本",
                    allure.attachment_type.TEXT
                )
            
            allure.attach(
                json.dumps({
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "elapsed": str(response.elapsed)
                }, indent=2),
                "响应元数据",
                allure.attachment_type.JSON
            )
            
            return response
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """发送GET请求"""
        return self.request("GET", endpoint, **kwargs)
        
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """发送POST请求"""
        return self.request("POST", endpoint, **kwargs)
        
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """发送PUT请求"""
        return self.request("PUT", endpoint, **kwargs)
        
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """发送DELETE请求"""
        return self.request("DELETE", endpoint, **kwargs)


@pytest.fixture(scope="session")
def base_url() -> str:
    """
    获取API基础URL
    
    Returns:
        API基础URL字符串
    """
    # 从环境变量获取，默认为playturbo.com
    return os.getenv("PLAYTURBO_API_URL", "https://api.playturbo.com")


@pytest.fixture(scope="session")
def api_client(base_url: str) -> Generator[APIClient, None, None]:
    """
    创建API客户端实例
    
    Args:
        base_url: API基础URL
        
    Yields:
        APIClient实例
    """
    client = APIClient(base_url)
    yield client
    # 清理工作
    client.session.close()


@pytest.fixture(scope="function")
def test_user_data() -> Dict[str, Any]:
    """
    生成测试用户数据
    
    Returns:
        测试用户数据字典
    """
    import random
    import string
    
    # 生成随机用户名和邮箱
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    username = f"testuser_{random_str}"
    email = f"{username}@test.com"
    
    return {
        "username": username,
        "email": email,
        "password": "TestPassword123!",
        "nickname": f"测试用户_{random_str}"
    }


@pytest.fixture(scope="function")
def authenticated_client(api_client: APIClient, test_user_data: Dict[str, Any]) -> Generator[APIClient, None, None]:
    """
    创建已认证的API客户端
    
    Args:
        api_client: 基础API客户端
        test_user_data: 测试用户数据
        
    Yields:
        已认证的APIClient实例
    """
    # 这里模拟认证过程，实际测试中应该调用登录接口获取token
    # 为了演示，我们使用一个模拟的token
    mock_token = "mock_auth_token_for_testing"
    api_client.set_token(mock_token)
    
    yield api_client
    
    # 测试结束后清理token
    api_client.clear_token()


@pytest.fixture(scope="session")
def test_game_data() -> Dict[str, Any]:
    """
    测试游戏数据
    
    Returns:
        测试游戏数据字典
    """
    return {
        "game_id": "test_game_001",
        "game_name": "Turbo Racing",
        "game_type": "racing",
        "difficulty": "medium",
        "max_players": 4
    }


@pytest.fixture(scope="session")
def test_payment_data() -> Dict[str, Any]:
    """
    测试支付数据
    
    Returns:
        测试支付数据字典
    """
    return {
        "product_id": "premium_pack_001",
        "product_name": "Premium Game Pack",
        "price": 9.99,
        "currency": "USD",
        "description": "包含高级游戏功能和道具"
    }


@pytest.fixture(scope="function")
def cleanup_test_data(api_client: APIClient):
    """清理测试数据"""
    yield
    # 测试结束后清理数据
    try:
        # 这里可以添加清理逻辑，如删除测试用户等
        pass
    except Exception as e:
        print(f"清理数据时出错: {e}")


def pytest_configure(config):
    """pytest配置钩子"""
    # 添加自定义标记说明
    config.addinivalue_line(
        "markers", "smoke: 冒烟测试 - 核心功能测试"
    )
    config.addinivalue_line(
        "markers", "regression: 回归测试 - 全面功能测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试 - 多模块集成测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试 - 需要较长时间执行的测试"
    )


def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption(
        "--env",
        action="store",
        default="test",
        help="测试环境: test, staging, prod"
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="浏览器类型: chrome, firefox, safari"
    )


def pytest_runtest_makereport(item, call):
    """测试报告钩子"""
    if call.when == "call":
        if call.excinfo is not None:
            # 测试失败时附加额外信息
            allure.attach(
                f"测试失败: {str(call.excinfo.value)}",
                "失败信息",
                allure.attachment_type.TEXT
            )