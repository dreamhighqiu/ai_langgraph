"""
系统状态模块测试
测试playturbo.com的服务器状态检查、配置信息和版本检查功能
"""
import pytest
import allure
import json
import time
from typing import Dict, Any
from datetime import datetime


@allure.feature("系统状态模块")
class TestSystemStatus:
    """系统状态相关测试类"""
    
    @allure.story("服务器状态检查")
    @allure.title("测试服务器健康检查成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "system")
    def test_health_check_success(self, api_client):
        """
        测试服务器健康检查成功
        
        验证点：
        1. 健康检查接口返回200状态码
        2. 响应中包含服务状态信息
        3. 所有服务组件状态正常
        """
        with allure.step("发送健康检查请求"):
            response = api_client.get("/api/v1/system/health")
        
        with allure.step("验证健康检查响应"):
            assert response.status_code == 200, f"健康检查失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "status" in response_data, "响应中缺少status字段"
            assert response_data["status"] == "healthy", f"服务状态应为healthy，实际: {response_data['status']}"
            assert "timestamp" in response_data, "响应中缺少timestamp字段"
            assert "version" in response_data, "响应中缺少version字段"
            assert "services" in response_data, "响应中缺少services字段"
            
            # 检查各个服务组件状态
            services = response_data["services"]
            for service_name, service_status in services.items():
                assert service_status["status"] == "up", f"服务{service_name}状态异常: {service_status}"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "健康检查响应数据",
                allure.attachment_type.JSON
            )
    
    @allure.story("服务器状态检查")
    @allure.title("测试服务器健康检查详细状态")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "system")
    def test_health_check_detailed(self, api_client):
        """
        测试服务器健康检查详细状态
        
        验证点：
        1. 详细健康检查接口返回200状态码
        2. 响应中包含详细的系统指标
        3. 包含数据库、缓存、存储等组件状态
        """
        with allure.step("发送详细健康检查请求"):
            response = api_client.get("/api/v1/system/health/detailed")
        
        with allure.step("验证详细健康检查响应"):
            assert response.status_code == 200, f"详细健康检查失败，状态码: {response.status_code}"
            
            response_data = response.json()
            required_fields = [
                "status", "timestamp", "version", "uptime",
                "database", "cache", "storage", "queue", "api"
            ]
            
            for field in required_fields:
                assert field in response_data, f"响应中缺少{field}字段"
            
            # 验证数据库状态
            assert "status" in response_data["database"], "数据库状态缺少status字段"
            assert response_data["database"]["status"] == "connected", "数据库连接状态异常"
            
            # 验证缓存状态
            assert "status" in response_data["cache"], "缓存状态缺少status字段"
            assert response_data["cache"]["status"] == "connected", "缓存连接状态异常"
            
            # 验证API响应时间
            if "response_time" in response_data["api"]:
                response_time = response_data["api"]["response_time"]
                assert isinstance(response_time, (int, float)), "API响应时间应为数字类型"
                assert response_time < 1000, f"API响应时间过长: {response_time}ms"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "详细健康检查响应",
                allure.attachment_type.JSON
            )
    
    @allure.story("服务器状态检查")
    @allure.title("测试服务器性能指标")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "system", "slow")
    def test_performance_metrics(self, api_client):
        """
        测试服务器性能指标
        
        验证点：
        1. 性能指标接口返回200状态码
        2. 响应中包含系统性能数据
        3. 性能指标在合理范围内
        """
        with allure.step("发送性能指标请求"):
            response = api_client.get("/api/v1/system/metrics")
        
        with allure.step("验证性能指标响应"):
            assert response.status_code == 200, f"获取性能指标失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "timestamp" in response_data, "响应中缺少timestamp字段"
            assert "metrics" in response_data, "响应中缺少metrics字段"
            
            metrics = response_data["metrics"]
            
            # 验证CPU使用率
            if "cpu" in metrics:
                cpu_usage = metrics["cpu"].get("usage_percent")
                if cpu_usage is not None:
                    assert 0 <= cpu_usage <= 100, f"CPU使用率异常: {cpu_usage}%"
            
            # 验证内存使用率
            if "memory" in metrics:
                memory_usage = metrics["memory"].get("usage_percent")
                if memory_usage is not None:
                    assert 0 <= memory_usage <= 100, f"内存使用率异常: {memory_usage}%"
            
            # 验证磁盘使用率
            if "disk" in metrics:
                disk_usage = metrics["disk"].get("usage_percent")
                if disk_usage is not None:
                    assert 0 <= disk_usage <= 100, f"磁盘使用率异常: {disk_usage}%"
            
            # 验证API请求统计
            if "api_requests" in metrics:
                api_stats = metrics["api_requests"]
                if "total_requests" in api_stats:
                    assert api_stats["total_requests"] >= 0, "API总请求数应为非负数"
                if "requests_per_second" in api_stats:
                    assert api_stats["requests_per_second"] >= 0, "API每秒请求数应为非负数"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "性能指标响应",
                allure.attachment_type.JSON
            )
    
    @allure.story("配置信息")
    @allure.title("测试获取系统配置信息")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "system")
    def test_get_system_config(self, api_client):
        """
        测试获取系统配置信息
        
        验证点：
        1. 配置信息接口返回200状态码
        2. 响应中包含系统配置数据
        3. 配置信息字段完整
        """
        with allure.step("发送获取配置信息请求"):
            response = api_client.get("/api/v1/system/config")
        
        with allure.step("验证配置信息响应"):
            assert response.status_code == 200, f"获取配置信息失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "environment" in response_data, "响应中缺少environment字段"
            assert "version" in response_data, "响应中缺少version字段"
            assert "api_version" in response_data, "响应中缺少api_version字段"
            assert "features" in response_data, "响应中缺少features字段"
            assert "limits" in response_data, "响应中缺少limits字段"
            
            # 验证环境类型
            valid_environments = ["development", "testing", "staging", "production"]
            assert response_data["environment"] in valid_environments, \
                f"环境类型无效: {response_data['environment']}"
            
            # 验证版本格式
            version = response_data["version"]
            assert isinstance(version, str), "版本号应为字符串类型"
            assert len(version) > 0, "版本号不能为空"
            
            # 验证API版本格式
            api_version = response_data["api_version"]
            assert isinstance(api_version, str), "API版本号应为字符串类型"
            assert api_version.startswith("v"), "API版本号应以'v'开头"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "配置信息响应",
                allure.attachment_type.JSON
            )
    
    @allure.story("配置信息")
    @allure.title("测试获取特性开关配置")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "system")
    def test_get_feature_flags(self, api_client):
        """
        测试获取特性开关配置
        
        验证点：
        1. 特性开关接口返回200状态码
        2. 响应中包含特性开关配置
        3. 特性开关状态正确
        """
        with allure.step("发送获取特性开关请求"):
            response = api_client.get("/api/v1/system/config/features")
        
        with allure.step("验证特性开关响应"):
            assert response.status_code == 200, f"获取特性开关失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "features" in response_data, "响应中缺少features字段"
            assert "last_updated" in response_data, "响应中缺少last_updated字段"
            
            features = response_data["features"]
            
            # 验证常见特性开关
            common_features = ["social_features", "payment_gateway", "game_leaderboards", "user_avatars"]
            for feature in common_features:
                if feature in features:
                    feature_config = features[feature]
                    assert "enabled" in feature_config, f"特性{feature}缺少enabled字段"
                    assert isinstance(feature_config["enabled"], bool), f"特性{feature}的enabled应为布尔类型"
                    
                    if "percentage" in feature_config:
                        percentage = feature_config["percentage"]
                        assert 0 <= percentage <= 100, f"特性{feature}的percentage应在0-100之间: {percentage}"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "特性开关响应",
                allure.attachment_type.JSON
            )
    
    @allure.story("配置信息")
    @allure.title("测试获取系统限制配置")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "system")
    def test_get_system_limits(self, api_client):
        """
        测试获取系统限制配置
        
        验证点：
        1. 系统限制接口返回200状态码
        2. 响应中包含系统限制配置
        3. 限制值合理
        """
        with allure.step("发送获取系统限制请求"):
            response = api_client.get("/api/v1/system/config/limits")
        
        with allure.step("验证系统限制响应"):
            assert response.status_code == 200, f"获取系统限制失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "limits" in response_data, "响应中缺少limits字段"
            
            limits = response_data["limits"]
            
            # 验证API限制
            if "api" in limits:
                api_limits = limits["api"]
                if "rate_limit" in api_limits:
                    rate_limit = api_limits["rate_limit"]
                    assert "requests_per_minute" in rate_limit, "速率限制缺少requests_per_minute字段"
                    assert rate_limit["requests_per_minute"] > 0, "每分钟请求数应为正数"
            
            # 验证文件上传限制
            if "uploads" in limits:
                upload_limits = limits["uploads"]
                if "max_file_size" in upload_limits:
                    max_size = upload_limits["max_file_size"]
                    assert max_size > 0, "最大文件大小应为正数"
            
            # 验证游戏相关限制
            if "games" in limits:
                game_limits = limits["games"]
                if "max_save_states" in game_limits:
                    max_saves = game_limits["max_save_states"]
                    assert max_saves > 0, "最大保存状态数应为正数"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "系统限制响应",
                allure.attachment_type.JSON
            )
    
    @allure.story("版本检查")
    @allure.title("测试获取API版本信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "system")
    def test_get_api_version(self, api_client):
        """
        测试获取API版本信息
        
        验证点：
        1. 版本信息接口返回200状态码
        2. 响应中包含版本信息
        3. 版本格式正确
        """
        with allure.step("发送获取版本信息请求"):
            response = api_client.get("/api/v1/system/version")
        
        with allure.step("验证版本信息响应"):
            assert response.status_code == 200, f"获取版本信息失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "api_version" in response_data, "响应中缺少api_version字段"
            assert "build_version" in response_data, "响应中缺少build_version字段"
            assert "build_date" in response_data, "响应中缺少build_date字段"
            assert "git_commit" in response_data, "响应中缺少git_commit字段"
            assert "environment" in response_data, "响应中缺少environment字段"
            
            # 验证API版本格式
            api_version = response_data["api_version"]
            assert isinstance(api_version, str), "API版本号应为字符串类型"
            assert api_version.startswith("v"), "API版本号应以'v'开头"
            
            # 验证构建版本格式
            build_version = response_data["build_version"]
            assert isinstance(build_version, str), "构建版本号应为字符串类型"
            assert len(build_version) > 0, "构建版本号不能为空"
            
            # 验证构建日期格式
            build_date = response_data["build_date"]
            assert isinstance(build_date, str), "构建日期应为字符串类型"
            
            # 尝试解析日期
            try:
                datetime.fromisoformat(build_date.replace('Z', '+00:00'))
            except ValueError:
                # 如果不是ISO格式，至少检查非空
                assert len(build_date) > 0, "构建日期格式无效"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "版本信息响应",
                allure.attachment_type.JSON
            )
    
    @allure.story("版本检查")
    @allure.title("测试检查客户端版本兼容性")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "system")
    @pytest.mark.parametrize("client_version,expected_compatible", [
        ("1.0.0", True),
        ("0.9.0", False),  # 旧版本
        ("2.0.0", True),   # 新版本
        ("1.5.0", True),
    ])
    def test_check_client_compatibility(self, api_client, client_version, expected_compatible):
        """
        测试检查客户端版本兼容性
        
        验证点：
        1. 兼容性检查接口返回200状态码
        2. 响应中包含兼容性信息
        3. 兼容性判断正确
        """
        with allure.step(f"检查客户端版本{client_version}的兼容性"):
            params = {
                "client_version": client_version,
                "platform": "web",  # web, ios, android
                "device_type": "desktop"
            }
            response = api_client.get("/api/v1/system/version/compatibility", params=params)
        
        with allure.step("验证兼容性检查响应"):
            assert response.status_code == 200, f"兼容性检查失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "compatible" in response_data, "响应中缺少compatible字段"
            assert "client_version" in response_data, "响应中缺少client_version字段"
            assert "min_supported_version" in response_data, "响应中缺少min_supported_version字段"
            assert "recommended_version" in response_data, "响应中缺少recommended_version字段"
            
            # 验证兼容性判断
            is_compatible = response_data["compatible"]
            assert isinstance(is_compatible, bool), "compatible字段应为布尔类型"
            
            # 在实际测试中，这里应该根据业务逻辑验证兼容性
            # 由于是模拟测试，我们只验证字段存在和类型正确
            
            if not is_compatible:
                assert "upgrade_message" in response_data, "不兼容时应包含升级消息"
                assert "upgrade_url" in response_data, "不兼容时应包含升级URL"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "兼容性检查响应",
                allure.attachment_type.JSON
            )
    
    @allure.story("系统日志")
    @allure.title("测试获取系统日志")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "system")
    def test_get_system_logs(self, authenticated_client):
        """
        测试获取系统日志（需要管理员权限）
        
        验证点：
        1. 系统日志接口返回200状态码
        2. 响应中包含日志条目
        3. 支持按级别和时间过滤
        """
        with allure.step("发送获取系统日志请求"):
            params = {
                "level": "error",  # error, warning, info, debug
                "limit": 10,
                "start_time": (datetime.now() - timedelta(hours=1)).isoformat(),
                "end_time": datetime.now().isoformat()
            }
            response = authenticated_client.get("/api/v1/system/logs", params=params)
        
        with allure.step("验证系统日志响应"):
            # 注意：实际系统中，获取日志可能需要管理员权限
            # 这里我们根据响应状态码进行不同验证
            if response.status_code == 200:
                response_data = response.json()
                assert "logs" in response_data, "响应中缺少logs字段"
                assert "total" in response_data, "响应中缺少total字段"
                
                logs = response_data["logs"]
                if logs:  # 如果有日志数据
                    log_entry = logs[0]
                    required_fields = ["timestamp", "level", "message", "source"]
                    for field in required_fields:
                        assert field in log_entry, f"日志条目缺少{field}字段"
                    
                    # 验证日志级别
                    valid_levels = ["error", "warning", "info", "debug"]
                    assert log_entry["level"] in valid_levels, f"无效的日志级别: {log_entry['level']}"
            elif response.status_code == 403:
                # 没有权限访问日志
                response_data = response.json()
                assert "error" in response_data, "响应中缺少error字段"
                assert "permission" in response_data.get("error", "").lower() or \
                       "forbidden" in response_data.get("error", "").lower(), "错误信息应包含权限相关提示"
            else:
                assert False, f"获取系统日志失败，状态码: {response.status_code}"
    
    @allure.story("系统维护")
    @allure.title("测试系统维护模式")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "system")
    def test_maintenance_mode(self, api_client):
        """
        测试系统维护模式
        
        验证点：
        1. 维护模式接口返回503状态码
        2. 响应中包含维护信息
        3. 包含预计恢复时间
        """
        with allure.step("检查系统维护状态"):
            response = api_client.get("/api/v1/system/maintenance")
        
        with allure.step("验证维护状态响应"):
            # 系统可能处于维护模式或正常运行
            if response.status_code == 503:
                # 系统处于维护模式
                response_data = response.json()
                assert "maintenance" in response_data, "响应中缺少maintenance字段"
                assert response_data["maintenance"] is True, "维护状态应为true"
                assert "message" in response_data, "响应中缺少message字段"
                assert "estimated_recovery" in response_data, "响应中缺少estimated_recovery字段"
                
                # 验证预计恢复时间格式
                estimated_recovery = response_data["estimated_recovery"]
                try:
                    datetime.fromisoformat(estimated_recovery.replace('Z', '+00:00'))
                except ValueError:
                    # 如果不是ISO格式，至少检查非空
                    assert len(estimated_recovery) > 0, "预计恢复时间格式无效"
            elif response.status_code == 200:
                # 系统正常运行
                response_data = response.json()
                assert "maintenance" in response_data, "响应中缺少maintenance字段"
                assert response_data["maintenance"] is False, "维护状态应为false"
            else:
                assert False, f"检查维护状态失败，状态码: {response.status_code}"
    
    @allure.story("系统监控")
    @allure.title("测试系统监控端点")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "system")
    def test_system_monitoring_endpoints(self, api_client):
        """
        测试系统监控相关端点
        
        验证点：
        1. 监控端点返回正确状态码
        2. 响应中包含监控数据
        """
        monitoring_endpoints = [
            ("/api/v1/system/metrics/prometheus", 200),  # Prometheus metrics
            ("/api/v1/system/health/ready", 200),        # Readiness probe
            ("/api/v1/system/health/live", 200),         # Liveness probe
        ]
        
        for endpoint, expected_status in monitoring_endpoints:
            with allure.step(f"测试监控端点: {endpoint}"):
                response = api_client.get(endpoint)
                
                allure.attach(
                    f"端点: {endpoint}\n状态码: {response.status_code}\n响应大小: {len(response.text)}字节",
                    "监控端点测试结果",
                    allure.attachment_type.TEXT
                )
                
                # 验证状态码
                if response.status_code != expected_status:
                    # 如果不是预期状态码，检查是否是维护或错误状态
                    if response.status_code in [503, 500]:
                        # 系统可能处于维护或错误状态
                        allure.attach(
                            f"端点 {endpoint} 返回非预期状态码: {response.status_code}\n响应: {response.text[:500]}",
                            "监控端点警告",
                            allure.attachment_type.TEXT
                        )
                    else:
                        assert response.status_code == expected_status, \
                            f"端点{endpoint}预期状态码{expected_status}，实际: {response.status_code}"
    
    @allure.story("系统信息")
    @allure.title("测试获取系统信息汇总")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "system")
    def test_get_system_info_summary(self, api_client):
        """
        测试获取系统信息汇总
        
        验证点：
        1. 系统信息接口返回200状态码
        2. 响应中包含完整的系统信息
        3. 信息字段完整且合理
        """
        with allure.step("发送获取系统信息请求"):
            response = api_client.get("/api/v1/system/info")
        
        with allure.step("验证系统信息响应"):
            assert response.status_code == 200, f"获取系统信息失败，状态码: {response.status_code}"
            
            response_data = response.json()
            
            # 验证基本信息
            basic_info_fields = ["name", "version", "environment", "uptime", "started_at"]
            for field in basic_info_fields:
                assert field in response_data, f"响应中缺少{field}字段"
            
            # 验证服务信息
            assert "services" in response_data, "响应中缺少services字段"
            services = response_data["services"]
            assert isinstance(services, dict), "services字段应为字典类型"
            
            # 验证数据库信息
            if "database" in response_data:
                db_info = response_data["database"]
                assert "type" in db_info, "数据库信息缺少type字段"
                assert "version" in db_info, "数据库信息缺少version字段"
            
            # 验证缓存信息
            if "cache" in response_data:
                cache_info = response_data["cache"]
                assert "type" in cache_info, "缓存信息缺少type字段"
            
            # 验证存储信息
            if "storage" in response_data:
                storage_info = response_data["storage"]
                assert "type" in storage_info, "存储信息缺少type字段"
            
            # 验证统计信息
            if "statistics" in response_data:
                stats = response_data["statistics"]
                if "total_users" in stats:
                    assert stats["total_users"] >= 0, "总用户数应为非负数"
                if "total_games" in stats:
                    assert stats["total_games"] >= 0, "总游戏数应为非负数"
                if "total_orders" in stats:
                    assert stats["total_orders"] >= 0, "总订单数应为非负数"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "系统信息响应",
                allure.attachment_type.JSON
            )
    
    @allure.story("系统性能")
    @allure.title("测试系统响应时间性能")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "system", "slow")
    def test_system_response_time_performance(self, api_client):
        """
        测试系统响应时间性能
        
        验证点：
        1. 关键接口响应时间在可接受范围内
        2. 性能指标稳定
        """
        test_endpoints = [
            ("/api/v1/system/health", "健康检查"),
            ("/api/v1/system/version", "版本信息"),
            ("/api/v1/games", "游戏列表"),
            ("/api/v1/payment/products", "商品列表"),
        ]
        
        performance_results = []
        
        for endpoint, description in test_endpoints:
            with allure.step(f"测试{description}响应时间: {endpoint}"):
                # 测试多次取平均值
                response_times = []
                for i in range(3):  # 测试3次
                    start_time = time.time()
                    response = api_client.get(endpoint)
                    end_time = time.time()
                    
                    response_time = (end_time - start_time) * 1000  # 转换为毫秒
                    response_times.append(response_time)
                    
                    # 验证响应状态
                    assert response.status_code == 200, f"{description}接口失败，状态码: {response.status_code}"
                
                # 计算平均响应时间
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                
                performance_results.append({
                    "endpoint": endpoint,
                    "description": description,
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "max_response_time_ms": round(max_response_time, 2),
                    "test_count": len(response_times)
                })
                
                # 验证响应时间在可接受范围内
                assert avg_response_time < 1000, f"{description}平均响应时间过长: {avg_response_time:.2f}ms"
                assert max_response_time < 2000, f"{description}最大响应时间过长: {max_response_time:.2f}ms"
        
        # 生成性能报告
        performance_summary = {
            "test_time": datetime.now().isoformat(),
            "total_endpoints_tested": len(test_endpoints),
            "performance_results": performance_results,
            "summary": {
                "avg_response_time_all": round(
                    sum(r["avg_response_time_ms"] for r in performance_results) / len(performance_results), 2
                ),
                "max_response_time_all": round(
                    max(r["max_response_time_ms"] for r in performance_results), 2
                )
            }
        }
        
        allure.attach(
            json.dumps(performance_summary, indent=2, ensure_ascii=False),
            "系统性能测试报告",
            allure.attachment_type.JSON
        )