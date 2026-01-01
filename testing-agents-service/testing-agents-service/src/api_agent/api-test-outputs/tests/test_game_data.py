"""
游戏数据模块测试
测试playturbo.com的游戏列表、详情、状态保存/加载和排行榜功能
"""
import pytest
import allure
import json
import time
from typing import Dict, Any, List
from datetime import datetime


@allure.feature("游戏数据模块")
class TestGameData:
    """游戏数据相关测试类"""
    
    @allure.story("游戏列表获取")
    @allure.title("测试获取游戏列表成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "game")
    def test_get_game_list_success(self, api_client):
        """
        测试获取游戏列表成功
        
        验证点：
        1. 游戏列表接口返回200状态码
        2. 响应中包含游戏列表数据
        3. 每个游戏包含必要字段
        4. 支持分页参数
        """
        with allure.step("发送获取游戏列表请求"):
            params = {
                "page": 1,
                "page_size": 10,
                "category": "all"
            }
            response = api_client.get("/api/v1/games", params=params)
        
        with allure.step("验证游戏列表响应"):
            assert response.status_code == 200, f"获取游戏列表失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "games" in response_data, "响应中缺少games字段"
            assert "total" in response_data, "响应中缺少total字段"
            assert "page" in response_data, "响应中缺少page字段"
            assert "page_size" in response_data, "响应中缺少page_size字段"
            
            games = response_data["games"]
            if games:  # 如果有游戏数据
                game = games[0]
                required_fields = ["game_id", "game_name", "category", "description", "thumbnail_url"]
                for field in required_fields:
                    assert field in game, f"游戏数据缺少{field}字段"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "游戏列表响应数据",
                allure.attachment_type.JSON
            )
    
    @allure.story("游戏列表获取")
    @allure.title("测试游戏列表分页功能")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "game")
    @pytest.mark.parametrize("page,page_size", [(1, 5), (2, 5), (1, 20)])
    def test_game_list_pagination(self, api_client, page, page_size):
        """
        测试游戏列表分页功能
        
        验证点：
        1. 不同分页参数返回正确数据
        2. 分页元数据正确
        """
        with allure.step(f"测试分页参数: page={page}, page_size={page_size}"):
            params = {
                "page": page,
                "page_size": page_size
            }
            response = api_client.get("/api/v1/games", params=params)
        
        with allure.step("验证分页响应"):
            assert response.status_code == 200, f"分页请求失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert response_data["page"] == page, f"返回的page不正确: {response_data['page']}"
            assert response_data["page_size"] == page_size, f"返回的page_size不正确: {response_data['page_size']}"
            
            games = response_data.get("games", [])
            assert len(games) <= page_size, f"返回的游戏数量超过page_size: {len(games)}"
    
    @allure.story("游戏列表获取")
    @allure.title("测试游戏列表分类过滤")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "game")
    @pytest.mark.parametrize("category", ["racing", "puzzle", "action", "strategy"])
    def test_game_list_category_filter(self, api_client, category):
        """
        测试游戏列表按分类过滤
        
        验证点：
        1. 按分类过滤返回正确游戏
        2. 返回的游戏都属于指定分类
        """
        with allure.step(f"按分类'{category}'过滤游戏列表"):
            params = {
                "category": category,
                "page": 1,
                "page_size": 20
            }
            response = api_client.get("/api/v1/games", params=params)
        
        with allure.step("验证分类过滤结果"):
            assert response.status_code == 200, f"分类过滤请求失败，状态码: {response.status_code}"
            
            response_data = response.json()
            games = response_data.get("games", [])
            
            for game in games:
                assert game.get("category") == category, f"游戏分类不匹配: {game.get('category')}"
    
    @allure.story("游戏详情")
    @allure.title("测试获取游戏详情成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "game")
    def test_get_game_detail_success(self, api_client, test_game_data):
        """
        测试获取游戏详情成功
        
        验证点：
        1. 游戏详情接口返回200状态码
        2. 响应中包含完整的游戏信息
        3. 游戏信息字段完整
        """
        game_id = test_game_data["game_id"]
        
        with allure.step(f"获取游戏'{game_id}'的详情"):
            response = api_client.get(f"/api/v1/games/{game_id}")
        
        with allure.step("验证游戏详情响应"):
            assert response.status_code == 200, f"获取游戏详情失败，状态码: {response.status_code}"
            
            response_data = response.json()
            required_fields = [
                "game_id", "game_name", "description", "category", 
                "difficulty", "thumbnail_url", "created_at", "updated_at"
            ]
            
            for field in required_fields:
                assert field in response_data, f"游戏详情缺少{field}字段"
            
            assert response_data["game_id"] == game_id, "游戏ID不匹配"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "游戏详情响应数据",
                allure.attachment_type.JSON
            )
    
    @allure.story("游戏详情")
    @allure.title("测试获取不存在的游戏详情失败")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "game")
    def test_get_nonexistent_game_detail(self, api_client):
        """
        测试获取不存在的游戏详情失败
        
        验证点：
        1. 接口返回404状态码
        2. 响应中包含游戏不存在错误信息
        """
        nonexistent_game_id = "nonexistent_game_123456"
        
        with allure.step(f"获取不存在的游戏'{nonexistent_game_id}'的详情"):
            response = api_client.get(f"/api/v1/games/{nonexistent_game_id}")
        
        with allure.step("验证游戏不存在响应"):
            assert response.status_code == 404, f"预期404状态码，实际: {response.status_code}"
            
            response_data = response.json()
            assert "error" in response_data, "响应中缺少error字段"
            assert "not found" in response_data.get("error", "").lower() or \
                   "exist" in response_data.get("error", "").lower(), "错误信息应包含游戏不存在提示"
    
    @allure.story("游戏状态保存")
    @allure.title("测试保存游戏状态成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "game")
    def test_save_game_state_success(self, authenticated_client, test_game_data):
        """
        测试保存游戏状态成功
        
        验证点：
        1. 保存游戏状态接口返回200状态码
        2. 响应中包含保存的游戏状态ID
        3. 可以获取保存的游戏状态
        """
        game_id = test_game_data["game_id"]
        
        with allure.step("准备游戏状态数据"):
            game_state_data = {
                "level": 5,
                "score": 12500,
                "progress": 0.75,
                "items": ["sword", "shield", "potion"],
                "checkpoint": "level_5_boss",
                "custom_data": {
                    "player_name": "TestPlayer",
                    "play_time": 3600,
                    "achievements": ["first_win", "speed_run"]
                }
            }
            allure.attach(
                json.dumps(game_state_data, indent=2, ensure_ascii=False),
                "游戏状态数据",
                allure.attachment_type.JSON
            )
        
        with allure.step(f"保存游戏'{game_id}'的状态"):
            response = authenticated_client.post(
                f"/api/v1/games/{game_id}/state",
                json=game_state_data
            )
        
        with allure.step("验证保存游戏状态响应"):
            assert response.status_code == 200, f"保存游戏状态失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "state_id" in response_data, "响应中缺少state_id字段"
            assert "saved_at" in response_data, "响应中缺少saved_at字段"
            
            state_id = response_data["state_id"]
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "保存游戏状态响应",
                allure.attachment_type.JSON
            )
        
        with allure.step("验证可以获取保存的游戏状态"):
            get_response = authenticated_client.get(f"/api/v1/games/{game_id}/state/{state_id}")
            assert get_response.status_code == 200, f"获取保存的游戏状态失败，状态码: {get_response.status_code}"
            
            retrieved_state = get_response.json()
            assert retrieved_state["state_id"] == state_id, "获取的状态ID不匹配"
            assert retrieved_state["level"] == game_state_data["level"], "游戏等级不匹配"
            assert retrieved_state["score"] == game_state_data["score"], "游戏分数不匹配"
    
    @allure.story("游戏状态保存")
    @allure.title("测试保存游戏状态 - 大状态数据")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "game", "slow")
    def test_save_large_game_state(self, authenticated_client, test_game_data):
        """
        测试保存大型游戏状态数据
        
        验证点：
        1. 可以保存较大的游戏状态数据
        2. 响应时间在可接受范围内
        """
        game_id = test_game_data["game_id"]
        
        with allure.step("准备大型游戏状态数据"):
            # 创建包含大量数据的状态
            large_state_data = {
                "level": 10,
                "score": 50000,
                "progress": 0.9,
                "inventory": {
                    "weapons": [f"weapon_{i}" for i in range(50)],
                    "armor": [f"armor_{i}" for i in range(30)],
                    "potions": [f"potion_{i}" for i in range(100)]
                },
                "map_data": {
                    "discovered_areas": [f"area_{i}" for i in range(200)],
                    "completed_quests": [f"quest_{i}" for i in range(50)]
                },
                "stats": {
                    f"stat_{i}": i * 10 for i in range(100)
                }
            }
        
        with allure.step("保存大型游戏状态"):
            start_time = time.time()
            response = authenticated_client.post(
                f"/api/v1/games/{game_id}/state",
                json=large_state_data
            )
            end_time = time.time()
            response_time = end_time - start_time
        
        with allure.step("验证大型状态保存"):
            assert response.status_code == 200, f"保存大型游戏状态失败，状态码: {response.status_code}"
            assert response_time < 5.0, f"保存大型状态响应时间过长: {response_time:.2f}秒"
            
            allure.attach(
                f"响应时间: {response_time:.2f}秒\n状态大小: 约{len(json.dumps(large_state_data))}字节",
                "性能数据",
                allure.attachment_type.TEXT
            )
    
    @allure.story("游戏状态加载")
    @allure.title("测试加载游戏状态成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "game")
    def test_load_game_state_success(self, authenticated_client, test_game_data):
        """
        测试加载游戏状态成功
        
        验证点：
        1. 加载游戏状态接口返回200状态码
        2. 加载的状态数据与保存的一致
        3. 包含状态元数据
        """
        game_id = test_game_data["game_id"]
        
        with allure.step("先保存一个游戏状态"):
            game_state_data = {
                "level": 3,
                "score": 8000,
                "progress": 0.5,
                "checkpoint": "level_3_mid"
            }
            save_response = authenticated_client.post(
                f"/api/v1/games/{game_id}/state",
                json=game_state_data
            )
            state_id = save_response.json()["state_id"]
        
        with allure.step(f"加载游戏状态'{state_id}'"):
            response = authenticated_client.get(f"/api/v1/games/{game_id}/state/{state_id}")
        
        with allure.step("验证加载游戏状态响应"):
            assert response.status_code == 200, f"加载游戏状态失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert response_data["state_id"] == state_id, "状态ID不匹配"
            assert response_data["level"] == game_state_data["level"], "游戏等级不匹配"
            assert response_data["score"] == game_state_data["score"], "游戏分数不匹配"
            assert response_data["progress"] == game_state_data["progress"], "游戏进度不匹配"
            assert "saved_at" in response_data, "响应中缺少saved_at字段"
            assert "loaded_at" in response_data, "响应中缺少loaded_at字段"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "加载的游戏状态",
                allure.attachment_type.JSON
            )
    
    @allure.story("游戏状态管理")
    @allure.title("测试获取用户游戏状态列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "game")
    def test_get_user_game_states(self, authenticated_client, test_game_data):
        """
        测试获取用户的游戏状态列表
        
        验证点：
        1. 状态列表接口返回200状态码
        2. 响应中包含状态列表
        3. 每个状态包含必要信息
        """
        game_id = test_game_data["game_id"]
        
        with allure.step("先保存几个游戏状态"):
            for i in range(3):
                state_data = {
                    "level": i + 1,
                    "score": (i + 1) * 1000,
                    "progress": (i + 1) * 0.25
                }
                authenticated_client.post(f"/api/v1/games/{game_id}/state", json=state_data)
        
        with allure.step("获取用户的游戏状态列表"):
            response = authenticated_client.get(f"/api/v1/games/{game_id}/states")
        
        with allure.step("验证状态列表响应"):
            assert response.status_code == 200, f"获取状态列表失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "states" in response_data, "响应中缺少states字段"
            
            states = response_data["states"]
            assert len(states) >= 3, f"状态数量不足，预期至少3个，实际: {len(states)}"
            
            for state in states:
                required_fields = ["state_id", "level", "score", "saved_at"]
                for field in required_fields:
                    assert field in state, f"状态数据缺少{field}字段"
    
    @allure.story("游戏排行榜")
    @allure.title("测试获取游戏排行榜成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "game")
    def test_get_game_leaderboard_success(self, api_client, test_game_data):
        """
        测试获取游戏排行榜成功
        
        验证点：
        1. 排行榜接口返回200状态码
        2. 响应中包含排行榜数据
        3. 排行榜数据格式正确
        4. 支持不同的排行榜类型
        """
        game_id = test_game_data["game_id"]
        
        with allure.step("获取游戏排行榜"):
            params = {
                "type": "global",  # global, weekly, daily
                "limit": 10
            }
            response = api_client.get(f"/api/v1/games/{game_id}/leaderboard", params=params)
        
        with allure.step("验证排行榜响应"):
            assert response.status_code == 200, f"获取排行榜失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "leaderboard" in response_data, "响应中缺少leaderboard字段"
            assert "type" in response_data, "响应中缺少type字段"
            assert "updated_at" in response_data, "响应中缺少updated_at字段"
            
            leaderboard = response_data["leaderboard"]
            if leaderboard:  # 如果排行榜有数据
                entry = leaderboard[0]
                required_fields = ["rank", "user_id", "username", "score"]
                for field in required_fields:
                    assert field in entry, f"排行榜条目缺少{field}字段"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "排行榜响应数据",
                allure.attachment_type.JSON
            )
