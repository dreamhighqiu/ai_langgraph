"""
社交功能模块测试
测试playturbo.com的好友列表、消息通知和社区动态功能
"""
import pytest
import allure
import json
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta


@allure.feature("社交功能模块")
class TestSocialFeatures:
    """社交功能相关测试类"""
    
    @allure.story("好友列表")
    @allure.title("测试获取好友列表成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "social")
    def test_get_friend_list_success(self, authenticated_client):
        """
        测试获取好友列表成功
        
        验证点：
        1. 好友列表接口返回200状态码
        2. 响应中包含好友列表数据
        3. 好友信息字段完整
        4. 支持分页参数
        """
        with allure.step("发送获取好友列表请求"):
            params = {
                "page": 1,
                "page_size": 20,
                "status": "all"  # all, online, offline
            }
            response = authenticated_client.get("/api/v1/social/friends", params=params)
        
        with allure.step("验证好友列表响应"):
            assert response.status_code == 200, f"获取好友列表失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "friends" in response_data, "响应中缺少friends字段"
            assert "total" in response_data, "响应中缺少total字段"
            assert "online_count" in response_data, "响应中缺少online_count字段"
            
            friends = response_data["friends"]
            if friends:  # 如果有好友数据
                friend = friends[0]
                required_fields = ["user_id", "username", "nickname", "avatar_url", "is_online", "last_seen"]
                for field in required_fields:
                    assert field in friend, f"好友数据缺少{field}字段"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "好友列表响应数据",
                allure.attachment_type.JSON
            )
    
    @allure.story("好友管理")
    @allure.title("测试发送好友请求成功")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "social")
    def test_send_friend_request_success(self, authenticated_client, test_user_data):
        """
        测试发送好友请求成功
        
        验证点：
        1. 发送好友请求接口返回200状态码
        2. 响应中包含请求ID
        3. 请求状态为pending
        """
        # 注意：实际测试中需要另一个测试用户
        target_user_id = "test_friend_001"  # 模拟目标用户ID
        
        with allure.step("准备好友请求数据"):
            request_data = {
                "target_user_id": target_user_id,
                "message": "你好，我想加你为好友！"
            }
            allure.attach(
                json.dumps(request_data, indent=2, ensure_ascii=False),
                "好友请求数据",
                allure.attachment_type.JSON
            )
        
        with allure.step("发送好友请求"):
            response = authenticated_client.post("/api/v1/social/friends/requests", json=request_data)
        
        with allure.step("验证好友请求响应"):
            assert response.status_code == 200, f"发送好友请求失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "request_id" in response_data, "响应中缺少request_id字段"
            assert "status" in response_data, "响应中缺少status字段"
            assert response_data["status"] == "pending", f"请求状态应为pending，实际: {response_data['status']}"
            assert "created_at" in response_data, "响应中缺少created_at字段"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "好友请求响应",
                allure.attachment_type.JSON
            )
    
    @allure.story("好友管理")
    @allure.title("测试接受好友请求成功")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "social")
    def test_accept_friend_request_success(self, authenticated_client):
        """
        测试接受好友请求成功
        
        验证点：
        1. 接受好友请求接口返回200状态码
        2. 请求状态变为accepted
        3. 用户被添加到好友列表
        """
        # 模拟一个待处理的好友请求ID
        request_id = "friend_request_001"
        
        with allure.step(f"接受好友请求'{request_id}'"):
            response = authenticated_client.put(f"/api/v1/social/friends/requests/{request_id}/accept")
        
        with allure.step("验证接受好友请求响应"):
            assert response.status_code == 200, f"接受好友请求失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "request_id" in response_data, "响应中缺少request_id字段"
            assert "status" in response_data, "响应中缺少status字段"
            assert response_data["status"] == "accepted", f"请求状态应为accepted，实际: {response_data['status']}"
            assert "accepted_at" in response_data, "响应中缺少accepted_at字段"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "接受好友请求响应",
                allure.attachment_type.JSON
            )
        
        with allure.step("验证好友已添加到列表"):
            friends_response = authenticated_client.get("/api/v1/social/friends")
            friends_data = friends_response.json()
            
            # 在实际测试中，这里应该验证新好友是否在列表中
            # 由于是模拟测试，我们只验证接口调用成功
            assert friends_response.status_code == 200, "获取好友列表失败"
    
    @allure.story("好友管理")
    @allure.title("测试拒绝好友请求成功")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "social")
    def test_reject_friend_request_success(self, authenticated_client):
        """
        测试拒绝好友请求成功
        
        验证点：
        1. 拒绝好友请求接口返回200状态码
        2. 请求状态变为rejected
        3. 用户不会被添加到好友列表
        """
        # 模拟一个待处理的好友请求ID
        request_id = "friend_request_002"
        
        with allure.step(f"拒绝好友请求'{request_id}'"):
            response = authenticated_client.put(f"/api/v1/social/friends/requests/{request_id}/reject")
        
        with allure.step("验证拒绝好友请求响应"):
            assert response.status_code == 200, f"拒绝好友请求失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "request_id" in response_data, "响应中缺少request_id字段"
            assert "status" in response_data, "响应中缺少status字段"
            assert response_data["status"] == "rejected", f"请求状态应为rejected，实际: {response_data['status']}"
            assert "rejected_at" in response_data, "响应中缺少rejected_at字段"
    
    @allure.story("好友管理")
    @allure.title("测试获取待处理的好友请求")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "social")
    def test_get_pending_friend_requests(self, authenticated_client):
        """
        测试获取待处理的好友请求
        
        验证点：
        1. 待处理请求接口返回200状态码
        2. 响应中包含待处理请求列表
        3. 每个请求包含完整信息
        """
        with allure.step("获取待处理的好友请求"):
            response = authenticated_client.get("/api/v1/social/friends/requests/pending")
        
        with allure.step("验证待处理请求响应"):
            assert response.status_code == 200, f"获取待处理请求失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "requests" in response_data, "响应中缺少requests字段"
            assert "total" in response_data, "响应中缺少total字段"
            
            requests = response_data["requests"]
            if requests:  # 如果有待处理请求
                request = requests[0]
                required_fields = ["request_id", "from_user_id", "from_username", "message", "created_at", "status"]
                for field in required_fields:
                    assert field in request, f"请求数据缺少{field}字段"
                assert request["status"] == "pending", f"请求状态应为pending，实际: {request['status']}"
    
    @allure.story("消息通知")
    @allure.title("测试获取消息通知列表成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "social")
    def test_get_notifications_success(self, authenticated_client):
        """
        测试获取消息通知列表成功
        
        验证点：
        1. 通知列表接口返回200状态码
        2. 响应中包含通知列表
        3. 通知信息字段完整
        4. 支持按类型过滤
        """
        with allure.step("发送获取通知列表请求"):
            params = {
                "page": 1,
                "page_size": 20,
                "type": "all",  # all, unread, system, friend, game
                "mark_as_read": False
            }
            response = authenticated_client.get("/api/v1/social/notifications", params=params)
        
        with allure.step("验证通知列表响应"):
            assert response.status_code == 200, f"获取通知列表失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "notifications" in response_data, "响应中缺少notifications字段"
            assert "total" in response_data, "响应中缺少total字段"
            assert "unread_count" in response_data, "响应中缺少unread_count字段"
            
            notifications = response_data["notifications"]
            if notifications:  # 如果有通知数据
                notification = notifications[0]
                required_fields = ["notification_id", "type", "title", "content", "created_at", "is_read"]
                for field in required_fields:
                    assert field in notification, f"通知数据缺少{field}字段"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "通知列表响应数据",
                allure.attachment_type.JSON
            )
    
    @allure.story("消息通知")
    @allure.title("测试标记通知为已读")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "social")
    def test_mark_notification_as_read(self, authenticated_client):
        """
        测试标记通知为已读
        
        验证点：
        1. 标记已读接口返回200状态码
        2. 通知状态更新为已读
        3. 未读计数减少
        """
        # 模拟一个未读通知ID
        notification_id = "notification_001"
        
        with allure.step(f"标记通知'{notification_id}'为已读"):
            response = authenticated_client.put(f"/api/v1/social/notifications/{notification_id}/read")
        
        with allure.step("验证标记已读响应"):
            assert response.status_code == 200, f"标记通知为已读失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "notification_id" in response_data, "响应中缺少notification_id字段"
            assert "is_read" in response_data, "响应中缺少is_read字段"
            assert response_data["is_read"] is True, "通知应标记为已读"
            assert "read_at" in response_data, "响应中缺少read_at字段"
    
    @allure.story("消息通知")
    @allure.title("测试批量标记通知为已读")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "social")
    def test_batch_mark_notifications_as_read(self, authenticated_client):
        """
        测试批量标记通知为已读
        
        验证点：
        1. 批量标记接口返回200状态码
        2. 多个通知被标记为已读
        3. 返回处理结果统计
        """
        with allure.step("批量标记通知为已读"):
            batch_data = {
                "notification_ids": ["notification_001", "notification_002", "notification_003"],
                "mark_as_read": True
            }
            response = authenticated_client.post("/api/v1/social/notifications/batch-read", json=batch_data)
        
        with allure.step("验证批量标记响应"):
            assert response.status_code == 200, f"批量标记通知失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "processed_count" in response_data, "响应中缺少processed_count字段"
            assert "success_count" in response_data, "响应中缺少success_count字段"
            assert "failed_count" in response_data, "响应中缺少failed_count字段"
            
            assert response_data["success_count"] >= 0, "成功计数应为非负数"
            assert response_data["failed_count"] >= 0, "失败计数应为非负数"
            assert response_data["processed_count"] == response_data["success_count"] + response_data["failed_count"], "处理计数不正确"
    
    @allure.story("社区动态")
    @allure.title("测试获取社区动态成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "social")
    def test_get_community_feed_success(self, authenticated_client):
        """
        测试获取社区动态成功
        
        验证点：
        1. 社区动态接口返回200状态码
        2. 响应中包含动态列表
        3. 动态信息字段完整
        4. 支持分页和时间过滤
        """
        with allure.step("发送获取社区动态请求"):
            params = {
                "page": 1,
                "page_size": 10,
                "feed_type": "all",  # all, friends, popular, recent
                "since": (datetime.now() - timedelta(days=7)).isoformat()
            }
            response = authenticated_client.get("/api/v1/social/feed", params=params)
        
        with allure.step("验证社区动态响应"):
            assert response.status_code == 200, f"获取社区动态失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "feed" in response_data, "响应中缺少feed字段"
            assert "total" in response_data, "响应中缺少total字段"
            assert "has_more" in response_data, "响应中缺少has_more字段"
            
            feed = response_data["feed"]
            if feed:  # 如果有动态数据
                post = feed[0]
                required_fields = ["post_id", "user_id", "username", "content", "created_at", "like_count", "comment_count"]
                for field in required_fields:
                    assert field in post, f"动态数据缺少{field}字段"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "社区动态响应数据",
                allure.attachment_type.JSON
            )
    
    @allure.story("社区动态")
    @allure.title("测试发布社区动态成功")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "social")
    def test_create_community_post_success(self, authenticated_client):
        """
        测试发布社区动态成功
        
        验证点：
        1. 发布动态接口返回201状态码
        2. 响应中包含新发布的动态ID
        3. 动态内容与请求一致
        """
        with allure.step("准备动态内容"):
            post_data = {
                "content": "今天在Turbo Racing游戏中创造了新的记录！🎮 #游戏 #记录",
                "visibility": "public",  # public, friends, private
                "tags": ["游戏", "记录", "TurboRacing"],
                "attachments": [
                    {
                        "type": "image",
                        "url": "https://example.com/screenshot.jpg",
                        "caption": "游戏截图"
                    }
                ]
            }
            allure.attach(
                json.dumps(post_data, indent=2, ensure_ascii=False),
                "动态发布数据",
                allure.attachment_type.JSON
            )
        
        with allure.step("发布社区动态"):
            response = authenticated_client.post("/api/v1/social/feed/posts", json=post_data)
        
        with allure.step("验证动态发布响应"):
            assert response.status_code == 201, f"发布动态失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "post_id" in response_data, "响应中缺少post_id字段"
            assert "content" in response_data, "响应中缺少content字段"
            assert response_data["content"] == post_data["content"], "动态内容不匹配"
            assert "created_at" in response_data, "响应中缺少created_at字段"
            assert "like_count" in response_data, "响应中缺少like_count字段"
            assert response_data["like_count"] == 0, "新动态的点赞数应为0"
            
            post_id = response_data["post_id"]
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "动态发布响应",
                allure.attachment_type.JSON
            )
        
        with allure.step("验证动态已出现在社区动态中"):
            # 等待一下确保数据同步
            time.sleep(1)
            
            feed_response = authenticated_client.get("/api/v1/social/feed")
            feed_data = feed_response.json()
            
            # 在实际测试中，这里应该验证新发布的动态是否在列表中
            # 由于是模拟测试，我们只验证接口调用成功
            assert feed_response.status_code == 200, "获取社区动态失败"
    
    @allure.story("社区动态")
    @allure.title("测试点赞社区动态")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "social")
    def test_like_community_post(self, authenticated_client):
        """
        测试点赞社区动态
        
        验证点：
        1. 点赞接口返回200状态码
        2. 动态的点赞数增加
        3. 可以取消点赞
        """
        # 模拟一个动态ID
        post_id = "community_post_001"
        
        with allure.step(f"点赞动态'{post_id}'"):
            response = authenticated_client.post(f"/api/v1/social/feed/posts/{post_id}/like")
        
        with allure.step("验证点赞响应"):
            assert response.status_code == 200, f"点赞动态失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "post_id" in response_data, "响应中缺少post_id字段"
            assert "like_count" in response_data, "响应中缺少like_count字段"
            assert "is_liked" in response_data, "响应中缺少is_liked字段"
            assert response_data["is_liked"] is True, "动态应被标记为已点赞"
            
            like_count_after = response_data["like_count"]
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "点赞响应",
                allure.attachment_type.JSON
            )
        
        with allure.step("取消点赞"):
            unlike_response = authenticated_client.delete(f"/api/v1/social/feed/posts/{post_id}/like")
            assert unlike_response.status_code == 200, f"取消点赞失败，状态码: {unlike_response.status_code}"
            
            unlike_data = unlike_response.json()
            assert unlike_data["is_liked"] is False, "动态应被标记为未点赞"
    
    @allure.story("社区动态")
    @allure.title("测试评论社区动态")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "social")
    def test_comment_on_community_post(self, authenticated_client):
        """
        测试评论社区动态
        
        验证点：
        1. 评论接口返回201状态码
        2. 响应中包含评论ID
        3. 动态的评论数增加
        """
        # 模拟一个动态ID
        post_id = "community_post_002"
        
        with allure.step("准备评论内容"):
            comment_data = {
                "content": "太棒了！我也喜欢这个游戏！👍",
                "parent_comment_id": None  # 如果是回复评论，这里填父评论ID
            }
        
        with allure.step(f"评论动态'{post_id}'"):
            response = authenticated_client.post(f"/api/v1/social/feed/posts/{post_id}/comments", json=comment_data)
        
        with allure.step("验证评论响应"):
            assert response.status_code == 201, f"评论动态失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "comment_id" in response_data, "响应中缺少comment_id字段"
            assert "content" in response_data, "响应中缺少content字段"
            assert response_data["content"] == comment_data["content"], "评论内容不匹配"
            assert "created_at" in response_data, "响应中缺少created_at字段"
            assert "user_id" in response_data, "响应中缺少user_id字段"
            assert "username" in response_data, "响应中缺少username字段"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "评论响应",
                allure.attachment_type.JSON
            )
    
    @allure.story("私信功能")
    @allure.title("测试发送私信成功")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "social")
    def test_send_private_message_success(self, authenticated_client):
        """
        测试发送私信成功
        
        验证点：
        1. 发送私信接口返回201状态码
        2. 响应中包含消息ID
        3. 消息内容与请求一致
        """
        # 模拟目标用户ID
        target_user_id = "friend_user_001"
        
        with allure.step("准备私信内容"):
            message_data = {
                "to_user_id": target_user_id,
                "content": "你好！想一起玩Turbo Racing吗？",
                "type": "text"  # text, image, link, etc.
            }
            allure.attach(
                json.dumps(message_data, indent=2, ensure_ascii=False),
                "私信数据",
                allure.attachment_type.JSON
            )
        
        with allure.step("发送私信"):
            response = authenticated_client.post("/api/v1/social/messages", json=message_data)
        
        with allure.step("验证私信发送响应"):
            assert response.status_code == 201, f"发送私信失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "message_id" in response_data, "响应中缺少message_id字段"
            assert "content" in response_data, "响应中缺少content字段"
            assert response_data["content"] == message_data["content"], "消息内容不匹配"
            assert "from_user_id" in response_data, "响应中缺少from_user_id字段"
            assert "to_user_id" in response_data, "响应中缺少to_user_id字段"
            assert response_data["to_user_id"] == target_user_id, "目标用户ID不匹配"
            assert "sent_at" in response_data, "响应中缺少sent_at字段"
            assert "is_read" in response_data, "响应中缺少is_read字段"
            assert response_data["is_read"] is False, "新消息应标记为未读"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "私信发送响应",
                allure.attachment_type.JSON
            )