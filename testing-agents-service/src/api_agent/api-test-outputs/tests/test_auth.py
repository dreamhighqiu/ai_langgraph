"""
用户认证模块测试
测试playturbo.com的用户注册、登录、登出和用户信息获取功能
"""
import pytest
import allure
import json
from typing import Dict, Any
from datetime import datetime


@allure.feature("用户认证模块")
class TestAuthentication:
    """用户认证相关测试类"""
    
    @allure.story("用户注册")
    @allure.title("测试用户注册成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "auth")
    def test_user_registration_success(self, api_client, test_user_data):
        """
        测试用户注册成功
        
        验证点：
        1. 注册接口返回201状态码
        2. 响应中包含用户ID
        3. 响应中包含注册时间
        """
        with allure.step("准备注册数据"):
            registration_data = {
                "username": test_user_data["username"],
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "nickname": test_user_data["nickname"]
            }
            allure.attach(
                json.dumps(registration_data, indent=2, ensure_ascii=False),
                "注册请求数据",
                allure.attachment_type.JSON
            )
        
        with allure.step("发送注册请求"):
            response = api_client.post("/api/v1/auth/register", json=registration_data)
        
        with allure.step("验证注册响应"):
            assert response.status_code == 201, f"注册失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "user_id" in response_data, "响应中缺少user_id字段"
            assert "created_at" in response_data, "响应中缺少created_at字段"
            assert response_data["username"] == test_user_data["username"], "用户名不匹配"
            assert response_data["email"] == test_user_data["email"], "邮箱不匹配"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "注册响应数据",
                allure.attachment_type.JSON
            )
    
    @allure.story("用户注册")
    @allure.title("测试用户注册失败 - 重复用户名")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "auth")
    def test_user_registration_duplicate_username(self, api_client, test_user_data):
        """
        测试使用重复用户名注册失败
        
        验证点：
        1. 注册接口返回409状态码
        2. 响应中包含错误信息
        """
        # 先注册一个用户
        registration_data = {
            "username": test_user_data["username"],
            "email": f"different_{test_user_data['email']}",
            "password": test_user_data["password"],
            "nickname": test_user_data["nickname"]
        }
        
        with allure.step("第一次注册用户"):
            api_client.post("/api/v1/auth/register", json=registration_data)
        
        with allure.step("使用相同用户名再次注册"):
            duplicate_data = {
                "username": test_user_data["username"],
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "nickname": f"{test_user_data['nickname']}_2"
            }
            response = api_client.post("/api/v1/auth/register", json=duplicate_data)
        
        with allure.step("验证重复注册失败"):
            assert response.status_code == 409, f"预期409冲突状态码，实际: {response.status_code}"
            response_data = response.json()
            assert "error" in response_data, "响应中缺少error字段"
            assert "username" in response_data.get("error", "").lower(), "错误信息应包含用户名相关提示"
    
    @allure.story("用户注册")
    @allure.title("测试用户注册失败 - 无效邮箱格式")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "auth")
    @pytest.mark.parametrize("invalid_email", [
        "invalid-email",
        "user@",
        "@domain.com",
        "user@domain",
        "user@.com"
    ])
    def test_user_registration_invalid_email(self, api_client, test_user_data, invalid_email):
        """
        测试使用无效邮箱格式注册失败
        
        验证点：
        1. 注册接口返回400状态码
        2. 响应中包含邮箱验证错误信息
        """
        with allure.step(f"使用无效邮箱格式: {invalid_email}"):
            registration_data = {
                "username": f"{test_user_data['username']}_{datetime.now().timestamp()}",
                "email": invalid_email,
                "password": test_user_data["password"],
                "nickname": test_user_data["nickname"]
            }
            
            response = api_client.post("/api/v1/auth/register", json=registration_data)
        
        with allure.step("验证无效邮箱注册失败"):
            assert response.status_code == 400, f"预期400状态码，实际: {response.status_code}"
            response_data = response.json()
            assert "error" in response_data, "响应中缺少error字段"
            assert "email" in response_data.get("error", "").lower(), "错误信息应包含邮箱相关提示"
    
    @allure.story("用户登录")
    @allure.title("测试用户登录成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "auth")
    def test_user_login_success(self, api_client, test_user_data):
        """
        测试用户登录成功
        
        验证点：
        1. 登录接口返回200状态码
        2. 响应中包含access_token
        3. 响应中包含token_type
        4. 响应中包含用户基本信息
        """
        # 先注册用户
        with allure.step("注册测试用户"):
            registration_data = {
                "username": test_user_data["username"],
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "nickname": test_user_data["nickname"]
            }
            api_client.post("/api/v1/auth/register", json=registration_data)
        
        with allure.step("准备登录数据"):
            login_data = {
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
            allure.attach(
                json.dumps(login_data, indent=2),
                "登录请求数据",
                allure.attachment_type.JSON
            )
        
        with allure.step("发送登录请求"):
            response = api_client.post("/api/v1/auth/login", json=login_data)
        
        with allure.step("验证登录响应"):
            assert response.status_code == 200, f"登录失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "access_token" in response_data, "响应中缺少access_token字段"
            assert "token_type" in response_data, "响应中缺少token_type字段"
            assert response_data["token_type"] == "bearer", "token_type应为bearer"
            assert "user" in response_data, "响应中缺少user字段"
            assert response_data["user"]["username"] == test_user_data["username"], "用户名不匹配"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "登录响应数据",
                allure.attachment_type.JSON
            )
    
    @allure.story("用户登录")
    @allure.title("测试用户登录失败 - 错误密码")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "auth")
    def test_user_login_wrong_password(self, api_client, test_user_data):
        """
        测试使用错误密码登录失败
        
        验证点：
        1. 登录接口返回401状态码
        2. 响应中包含认证失败错误信息
        """
        # 先注册用户
        with allure.step("注册测试用户"):
            registration_data = {
                "username": test_user_data["username"],
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "nickname": test_user_data["nickname"]
            }
            api_client.post("/api/v1/auth/register", json=registration_data)
        
        with allure.step("使用错误密码登录"):
            wrong_login_data = {
                "username": test_user_data["username"],
                "password": "WrongPassword123!"
            }
            response = api_client.post("/api/v1/auth/login", json=wrong_login_data)
        
        with allure.step("验证错误密码登录失败"):
            assert response.status_code == 401, f"预期401状态码，实际: {response.status_code}"
            response_data = response.json()
            assert "error" in response_data, "响应中缺少error字段"
            assert "invalid" in response_data.get("error", "").lower() or \
                   "password" in response_data.get("error", "").lower(), "错误信息应包含密码相关提示"
    
    @allure.story("用户登录")
    @allure.title("测试用户登录失败 - 不存在的用户")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "auth")
    def test_user_login_nonexistent_user(self, api_client):
        """
        测试使用不存在的用户登录失败
        
        验证点：
        1. 登录接口返回401状态码
        2. 响应中包含用户不存在错误信息
        """
        with allure.step("使用不存在的用户登录"):
            login_data = {
                "username": "nonexistent_user_123456",
                "password": "SomePassword123!"
            }
            response = api_client.post("/api/v1/auth/login", json=login_data)
        
        with allure.step("验证不存在的用户登录失败"):
            assert response.status_code == 401, f"预期401状态码，实际: {response.status_code}"
            response_data = response.json()
            assert "error" in response_data, "响应中缺少error字段"
            assert "user" in response_data.get("error", "").lower() or \
                   "exist" in response_data.get("error", "").lower(), "错误信息应包含用户不存在提示"
    
    @allure.story("用户登出")
    @allure.title("测试用户登出成功")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "auth")
    def test_user_logout_success(self, api_client, test_user_data):
        """
        测试用户登出成功
        
        验证点：
        1. 登出接口返回200状态码
        2. 登出后token失效
        """
        # 先注册并登录用户
        with allure.step("注册并登录测试用户"):
            registration_data = {
                "username": test_user_data["username"],
                "email": test_user_data["email"],
                "password": test_user_data["password"],
                "nickname": test_user_data["nickname"]
            }
            api_client.post("/api/v1/auth/register", json=registration_data)
            
            login_data = {
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
            login_response = api_client.post("/api/v1/auth/login", json=login_data)
            token = login_response.json()["access_token"]
            api_client.set_token(token)
        
        with allure.step("发送登出请求"):
            response = api_client.post("/api/v1/auth/logout")
        
        with allure.step("验证登出响应"):
            assert response.status_code == 200, f"登出失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "message" in response_data, "响应中缺少message字段"
            assert "success" in response_data.get("message", "").lower(), "登出成功消息不正确"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "登出响应数据",
                allure.attachment_type.JSON
            )
        
        with allure.step("验证token已失效"):
            # 尝试使用已登出的token访问受保护接口
            profile_response = api_client.get("/api/v1/auth/profile")
            assert profile_response.status_code in [401, 403], f"token应已失效，但状态码为: {profile_response.status_code}"
    
    @allure.story("用户信息获取")
    @allure.title("测试获取用户个人信息成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "auth")
    def test_get_user_profile_success(self, authenticated_client, test_user_data):
        """
        测试获取已登录用户的个人信息
        
        验证点：
        1. 用户信息接口返回200状态码
        2. 响应中包含完整的用户信息
        3. 用户信息与注册信息一致
        """
        with allure.step("发送获取用户信息请求"):
            response = authenticated_client.get("/api/v1/auth/profile")
        
        with allure.step("验证用户信息响应"):
            assert response.status_code == 200, f"获取用户信息失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "user_id" in response_data, "响应中缺少user_id字段"
            assert "username" in response_data, "响应中缺少username字段"
            assert "email" in response_data, "响应中缺少email字段"
            assert "nickname" in response_data, "响应中缺少nickname字段"
            assert "created_at" in response_data, "响应中缺少created_at字段"
            assert "last_login" in response_data, "响应中缺少last_login字段"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "用户信息响应数据",
                allure.attachment_type.JSON
            )
    
    @allure.story("用户信息获取")
    @allure.title("测试未认证用户获取个人信息失败")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "auth")
    def test_get_user_profile_unauthorized(self, api_client):
        """
        测试未认证用户获取个人信息失败
        
        验证点：
        1. 用户信息接口返回401状态码
        2. 响应中包含认证错误信息
        """
        with allure.step("未认证状态下发送获取用户信息请求"):
            response = api_client.get("/api/v1/auth/profile")
        
        with allure.step("验证未认证访问失败"):
            assert response.status_code == 401, f"预期401状态码，实际: {response.status_code}"
            response_data = response.json()
            assert "error" in response_data, "响应中缺少error字段"
            assert "unauthorized" in response_data.get("error", "").lower() or \
                   "authenticate" in response_data.get("error", "").lower(), "错误信息应包含认证相关提示"
    
    @allure.story("用户信息更新")
    @allure.title("测试更新用户个人信息成功")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "auth")
    def test_update_user_profile_success(self, authenticated_client, test_user_data):
        """
        测试更新用户个人信息成功
        
        验证点：
        1. 更新接口返回200状态码
        2. 响应中包含更新后的用户信息
        3. 更新后的信息与请求一致
        """
        with allure.step("准备更新数据"):
            update_data = {
                "nickname": f"{test_user_data['nickname']}_updated",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "这是一个测试用户的个人简介"
            }
            allure.attach(
                json.dumps(update_data, indent=2, ensure_ascii=False),
                "更新请求数据",
                allure.attachment_type.JSON
            )
        
        with allure.step("发送更新用户信息请求"):
            response = authenticated_client.put("/api/v1/auth/profile", json=update_data)
        
        with allure.step("验证更新响应"):
            assert response.status_code == 200, f"更新用户信息失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert response_data["nickname"] == update_data["nickname"], "昵称更新失败"
            assert response_data.get("avatar_url") == update_data["avatar_url"], "头像URL更新失败"
            assert response_data.get("bio") == update_data["bio"], "个人简介更新失败"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "更新后的用户信息",
                allure.attachment_type.JSON
            )
    
    @allure.story("密码管理")
    @allure.title("测试修改密码成功")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "auth")
    def test_change_password_success(self, authenticated_client, test_user_data):
        """
        测试修改密码成功
        
        验证点：
        1. 修改密码接口返回200状态码
        2. 使用新密码可以登录
        3. 使用旧密码无法登录
        """
        with allure.step("准备修改密码数据"):
            password_change_data = {
                "current_password": test_user_data["password"],
                "new_password": "NewPassword456!"
            }
        
        with allure.step("发送修改密码请求"):
            response = authenticated_client.post("/api/v1/auth/change-password", json=password_change_data)
        
        with allure.step("验证修改密码响应"):
            assert response.status_code == 200, f"修改密码失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "message" in response_data, "响应中缺少message字段"
            assert "success" in response_data.get("message", "").lower(), "修改密码成功消息不正确"
        
        with allure.step("验证新密码可以登录"):
            # 清除当前token
            authenticated_client.clear_token()
            
            login_data = {
                "username": test_user_data["username"],
                "password": "NewPassword456!"
            }
            login_response = authenticated_client.post("/api/v1/auth/login", json=login_data)
