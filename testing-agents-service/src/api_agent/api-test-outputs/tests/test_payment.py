"""
支付模块测试
测试playturbo.com的商品列表、购买接口和订单查询功能
"""
import pytest
import allure
import json
import time
from typing import Dict, Any, List
from datetime import datetime


@allure.feature("支付模块")
class TestPayment:
    """支付相关测试类"""
    
    @allure.story("商品列表")
    @allure.title("测试获取商品列表成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "payment")
    def test_get_product_list_success(self, api_client):
        """
        测试获取商品列表成功
        
        验证点：
        1. 商品列表接口返回200状态码
        2. 响应中包含商品列表数据
        3. 每个商品包含必要字段
        4. 支持按类型和分类过滤
        """
        with allure.step("发送获取商品列表请求"):
            params = {
                "page": 1,
                "page_size": 20,
                "category": "all",  # all, game, currency, subscription, etc.
                "currency": "USD"
            }
            response = api_client.get("/api/v1/payment/products", params=params)
        
        with allure.step("验证商品列表响应"):
            assert response.status_code == 200, f"获取商品列表失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "products" in response_data, "响应中缺少products字段"
            assert "total" in response_data, "响应中缺少total字段"
            assert "currency" in response_data, "响应中缺少currency字段"
            
            products = response_data["products"]
            if products:  # 如果有商品数据
                product = products[0]
                required_fields = ["product_id", "name", "description", "price", "currency", "category"]
                for field in required_fields:
                    assert field in product, f"商品数据缺少{field}字段"
                
                # 验证价格格式
                assert isinstance(product["price"], (int, float)), "价格应为数字类型"
                assert product["price"] >= 0, "价格应为非负数"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "商品列表响应数据",
                allure.attachment_type.JSON
            )
    
    @allure.story("商品列表")
    @allure.title("测试按分类过滤商品列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "payment")
    @pytest.mark.parametrize("category", ["game", "currency", "subscription", "bundle"])
    def test_product_list_by_category(self, api_client, category):
        """
        测试按分类过滤商品列表
        
        验证点：
        1. 按分类过滤返回正确商品
        2. 返回的商品都属于指定分类
        """
        with allure.step(f"按分类'{category}'过滤商品列表"):
            params = {
                "category": category,
                "page": 1,
                "page_size": 10
            }
            response = api_client.get("/api/v1/payment/products", params=params)
        
        with allure.step("验证分类过滤结果"):
            assert response.status_code == 200, f"分类过滤请求失败，状态码: {response.status_code}"
            
            response_data = response.json()
            products = response_data.get("products", [])
            
            for product in products:
                assert product.get("category") == category, f"商品分类不匹配: {product.get('category')}"
    
    @allure.story("商品详情")
    @allure.title("测试获取商品详情成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "payment")
    def test_get_product_detail_success(self, api_client, test_payment_data):
        """
        测试获取商品详情成功
        
        验证点：
        1. 商品详情接口返回200状态码
        2. 响应中包含完整的商品信息
        3. 商品信息字段完整
        """
        product_id = test_payment_data["product_id"]
        
        with allure.step(f"获取商品'{product_id}'的详情"):
            response = api_client.get(f"/api/v1/payment/products/{product_id}")
        
        with allure.step("验证商品详情响应"):
            assert response.status_code == 200, f"获取商品详情失败，状态码: {response.status_code}"
            
            response_data = response.json()
            required_fields = [
                "product_id", "name", "description", "price", "currency",
                "category", "features", "created_at", "updated_at"
            ]
            
            for field in required_fields:
                assert field in response_data, f"商品详情缺少{field}字段"
            
            assert response_data["product_id"] == product_id, "商品ID不匹配"
            assert response_data["price"] == test_payment_data["price"], "商品价格不匹配"
            assert response_data["currency"] == test_payment_data["currency"], "货币类型不匹配"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "商品详情响应数据",
                allure.attachment_type.JSON
            )
    
    @allure.story("商品详情")
    @allure.title("测试获取不存在的商品详情失败")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "payment")
    def test_get_nonexistent_product_detail(self, api_client):
        """
        测试获取不存在的商品详情失败
        
        验证点：
        1. 接口返回404状态码
        2. 响应中包含商品不存在错误信息
        """
        nonexistent_product_id = "nonexistent_product_123456"
        
        with allure.step(f"获取不存在的商品'{nonexistent_product_id}'的详情"):
            response = api_client.get(f"/api/v1/payment/products/{nonexistent_product_id}")
        
        with allure.step("验证商品不存在响应"):
            assert response.status_code == 404, f"预期404状态码，实际: {response.status_code}"
            
            response_data = response.json()
            assert "error" in response_data, "响应中缺少error字段"
            assert "not found" in response_data.get("error", "").lower() or \
                   "exist" in response_data.get("error", "").lower(), "错误信息应包含商品不存在提示"
    
    @allure.story("购买接口")
    @allure.title("测试创建购买订单成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "payment")
    def test_create_purchase_order_success(self, authenticated_client, test_payment_data):
        """
        测试创建购买订单成功
        
        验证点：
        1. 创建订单接口返回201状态码
        2. 响应中包含订单ID和状态
        3. 订单信息与请求一致
        """
        product_id = test_payment_data["product_id"]
        
        with allure.step("准备购买订单数据"):
            order_data = {
                "product_id": product_id,
                "quantity": 1,
                "payment_method": "credit_card",  # credit_card, paypal, apple_pay, etc.
                "billing_address": {
                    "name": "Test User",
                    "email": "test@example.com",
                    "address": "123 Test Street",
                    "city": "Test City",
                    "country": "US",
                    "postal_code": "12345"
                }
            }
            allure.attach(
                json.dumps(order_data, indent=2, ensure_ascii=False),
                "购买订单数据",
                allure.attachment_type.JSON
            )
        
        with allure.step("创建购买订单"):
            response = authenticated_client.post("/api/v1/payment/orders", json=order_data)
        
        with allure.step("验证创建订单响应"):
            assert response.status_code == 201, f"创建订单失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "order_id" in response_data, "响应中缺少order_id字段"
            assert "status" in response_data, "响应中缺少status字段"
            assert response_data["status"] == "pending", f"订单状态应为pending，实际: {response_data['status']}"
            assert "total_amount" in response_data, "响应中缺少total_amount字段"
            assert "currency" in response_data, "响应中缺少currency字段"
            assert "created_at" in response_data, "响应中缺少created_at字段"
            
            order_id = response_data["order_id"]
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "创建订单响应",
                allure.attachment_type.JSON
            )
        
        return order_id  # 返回订单ID供后续测试使用
    
    @allure.story("购买接口")
    @allure.title("测试购买不存在的商品失败")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "payment")
    def test_purchase_nonexistent_product(self, authenticated_client):
        """
        测试购买不存在的商品失败
        
        验证点：
        1. 创建订单接口返回404状态码
        2. 响应中包含商品不存在错误信息
        """
        with allure.step("尝试购买不存在的商品"):
            order_data = {
                "product_id": "nonexistent_product_789012",
                "quantity": 1,
                "payment_method": "credit_card"
            }
            response = authenticated_client.post("/api/v1/payment/orders", json=order_data)
        
        with allure.step("验证购买失败响应"):
            assert response.status_code == 404, f"预期404状态码，实际: {response.status_code}"
            
            response_data = response.json()
            assert "error" in response_data, "响应中缺少error字段"
            assert "product" in response_data.get("error", "").lower() or \
                   "exist" in response_data.get("error", "").lower(), "错误信息应包含商品不存在提示"
    
    @allure.story("购买接口")
    @allure.title("测试购买数量为0失败")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "payment")
    def test_purchase_zero_quantity(self, authenticated_client, test_payment_data):
        """
        测试购买数量为0失败
        
        验证点：
        1. 创建订单接口返回400状态码
        2. 响应中包含数量错误信息
        """
        product_id = test_payment_data["product_id"]
        
        with allure.step("尝试购买数量为0的商品"):
            order_data = {
                "product_id": product_id,
                "quantity": 0,
                "payment_method": "credit_card"
            }
            response = authenticated_client.post("/api/v1/payment/orders", json=order_data)
        
        with allure.step("验证购买失败响应"):
            assert response.status_code == 400, f"预期400状态码，实际: {response.status_code}"
            
            response_data = response.json()
            assert "error" in response_data, "响应中缺少error字段"
            assert "quantity" in response_data.get("error", "").lower() or \
                   "zero" in response_data.get("error", "").lower(), "错误信息应包含数量相关提示"
    
    @allure.story("购买接口")
    @allure.title("测试批量购买商品")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "payment")
    def test_batch_purchase_products(self, authenticated_client):
        """
        测试批量购买多个商品
        
        验证点：
        1. 批量购买接口返回201状态码
        2. 响应中包含多个订单信息
        3. 每个订单状态正确
        """
        with allure.step("准备批量购买数据"):
            batch_order_data = {
                "items": [
                    {
                        "product_id": "game_currency_100",
                        "quantity": 1
                    },
                    {
                        "product_id": "premium_subscription",
                        "quantity": 1
                    }
                ],
                "payment_method": "paypal",
                "billing_address": {
                    "name": "Test User",
                    "email": "test@example.com"
                }
            }
        
        with allure.step("发送批量购买请求"):
            response = authenticated_client.post("/api/v1/payment/orders/batch", json=batch_order_data)
        
        with allure.step("验证批量购买响应"):
            assert response.status_code == 201, f"批量购买失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "orders" in response_data, "响应中缺少orders字段"
            assert "total_amount" in response_data, "响应中缺少total_amount字段"
            
            orders = response_data["orders"]
            assert len(orders) == len(batch_order_data["items"]), f"订单数量不匹配，预期{len(batch_order_data['items'])}，实际{len(orders)}"
            
            for order in orders:
                assert "order_id" in order, "订单缺少order_id字段"
                assert "status" in order, "订单缺少status字段"
                assert order["status"] == "pending", f"订单状态应为pending，实际: {order['status']}"
    
    @allure.story("订单查询")
    @allure.title("测试获取订单详情成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "payment")
    def test_get_order_detail_success(self, authenticated_client, test_payment_data):
        """
        测试获取订单详情成功
        
        验证点：
        1. 订单详情接口返回200状态码
        2. 响应中包含完整的订单信息
        3. 订单信息字段完整
        """
        # 先创建一个订单
        order_id = self.test_create_purchase_order_success(authenticated_client, test_payment_data)
        
        with allure.step(f"获取订单'{order_id}'的详情"):
            response = authenticated_client.get(f"/api/v1/payment/orders/{order_id}")
        
        with allure.step("验证订单详情响应"):
            assert response.status_code == 200, f"获取订单详情失败，状态码: {response.status_code}"
            
            response_data = response.json()
            required_fields = [
                "order_id", "user_id", "product_id", "quantity", "total_amount",
                "currency", "status", "payment_method", "created_at", "updated_at"
            ]
            
            for field in required_fields:
                assert field in response_data, f"订单详情缺少{field}字段"
            
            assert response_data["order_id"] == order_id, "订单ID不匹配"
            assert response_data["product_id"] == test_payment_data["product_id"], "商品ID不匹配"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "订单详情响应数据",
                allure.attachment_type.JSON
            )
    
    @allure.story("订单查询")
    @allure.title("测试获取用户订单列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "payment")
    def test_get_user_orders(self, authenticated_client, test_payment_data):
        """
        测试获取用户的订单列表
        
        验证点：
        1. 订单列表接口返回200状态码
        2. 响应中包含订单列表
        3. 支持按状态和时间过滤
        """
        # 先创建几个订单
        for i in range(2):
            self.test_create_purchase_order_success(authenticated_client, test_payment_data)
        
        with allure.step("获取用户订单列表"):
            params = {
                "page": 1,
                "page_size": 10,
                "status": "all",  # all, pending, completed, cancelled, failed
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": datetime.now().isoformat()
            }
            response = authenticated_client.get("/api/v1/payment/orders", params=params)
        
        with allure.step("验证订单列表响应"):
            assert response.status_code == 200, f"获取订单列表失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "orders" in response_data, "响应中缺少orders字段"
            assert "total" in response_data, "响应中缺少total字段"
            assert "total_amount" in response_data, "响应中缺少total_amount字段"
            
            orders = response_data["orders"]
            assert len(orders) >= 2, f"订单数量不足，预期至少2个，实际: {len(orders)}"
            
            for order in orders:
                required_fields = ["order_id", "product_id", "total_amount", "status", "created_at"]
                for field in required_fields:
                    assert field in order, f"订单数据缺少{field}字段"
    
    @allure.story("订单管理")
    @allure.title("测试取消订单成功")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "payment")
    def test_cancel_order_success(self, authenticated_client, test_payment_data):
        """
        测试取消订单成功
        
        验证点：
        1. 取消订单接口返回200状态码
        2. 订单状态变为cancelled
        3. 响应中包含取消原因和时间
        """
        # 先创建一个订单
        order_id = self.test_create_purchase_order_success(authenticated_client, test_payment_data)
        
        with allure.step(f"取消订单'{order_id}'"):
            cancel_data = {
                "reason": "Changed my mind",
                "refund_requested": False
            }
            response = authenticated_client.post(f"/api/v1/payment/orders/{order_id}/cancel", json=cancel_data)
        
        with allure.step("验证取消订单响应"):
            assert response.status_code == 200, f"取消订单失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "order_id" in response_data, "响应中缺少order_id字段"
            assert "status" in response_data, "响应中缺少status字段"
            assert response_data["status"] == "cancelled", f"订单状态应为cancelled，实际: {response_data['status']}"
            assert "cancelled_at" in response_data, "响应中缺少cancelled_at字段"
            assert "cancellation_reason" in response_data, "响应中缺少cancellation_reason字段"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "取消订单响应",
                allure.attachment_type.JSON
            )
        
        with allure.step("验证订单详情已更新"):
            detail_response = authenticated_client.get(f"/api/v1/payment/orders/{order_id}")
            detail_data = detail_response.json()
            assert detail_data["status"] == "cancelled", "订单详情状态未更新为cancelled"
    
    @allure.story("支付处理")
    @allure.title("测试模拟支付成功")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "payment")
    def test_simulate_payment_success(self, authenticated_client, test_payment_data):
        """
        测试模拟支付成功
        
        验证点：
        1. 支付接口返回200状态码
        2. 订单状态变为completed
        3. 响应中包含支付确认信息
        """
        # 先创建一个订单
        order_id = self.test_create_purchase_order_success(authenticated_client, test_payment_data)
        
        with allure.step(f"模拟支付订单'{order_id}'"):
            payment_data = {
                "payment_method": "credit_card",
                "card_token": "test_card_token_123",
                "save_card": False
            }
            response = authenticated_client.post(f"/api/v1/payment/orders/{order_id}/pay", json=payment_data)
        
        with allure.step("验证支付响应"):
            assert response.status_code == 200, f"支付失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "order_id" in response_data, "响应中缺少order_id字段"
            assert "status" in response_data, "响应中缺少status字段"
            assert response_data["status"] == "completed", f"订单状态应为completed，实际: {response_data['status']}"
            assert "paid_at" in response_data, "响应中缺少paid_at字段"
            assert "transaction_id" in response_data, "响应中缺少transaction_id字段"
            assert "payment_method" in response_data, "响应中缺少payment_method字段"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "支付响应",
                allure.attachment_type.JSON
            )
    
    @allure.story("支付处理")
    @allure.title("测试模拟支付失败")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "payment")
    def test_simulate_payment_failure(self, authenticated_client, test_payment_data):
        """
        测试模拟支付失败
        
        验证点：
        1. 支付接口返回400状态码
        2. 订单状态变为failed
        3. 响应中包含支付失败原因
        """
        # 先创建一个订单
        order_id = self.test_create_purchase_order_success(authenticated_client, test_payment_data)
        
        with allure.step(f"模拟支付失败订单'{order_id}'"):
            payment_data = {
                "payment_method": "credit_card",
                "card_token": "invalid_card_token",
                "save_card": False
            }
            response = authenticated_client.post(f"/api/v1/payment/orders/{order_id}/pay", json=payment_data)
        
        with allure.step("验证支付失败响应"):
            assert response.status_code == 400, f"预期400状态码，实际: {response.status_code}"
            
            response_data = response.json()
            assert "error" in response_data, "响应中缺少error字段"
            assert "payment" in response_data.get("error", "").lower() or \
                   "failed" in response_data.get("error", "").lower(), "错误信息应包含支付失败提示"
        
        with allure.step("验证订单状态已更新"):
            detail_response = authenticated_client.get(f"/api/v1/payment/orders/{order_id}")
            detail_data = detail_response.json()
            assert detail_data["status"] == "failed", "订单状态应更新为failed"
    
    @allure.story("退款处理")
    @allure.title("测试申请退款成功")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "payment")
    def test_request_refund_success(self, authenticated_client, test_payment_data):
        """
        测试申请退款成功
        
        验证点：
        1. 退款接口返回200状态码
        2. 退款状态为pending
        3. 响应中包含退款信息
        """
        # 先创建一个已支付的订单
        order_id = self.test_create_purchase_order_success(authenticated_client, test_payment_data)
        
        # 模拟支付成功
        payment_data = {
            "payment_method": "credit_card",
            "card_token": "test_card_token_123",
            "save_card": False
        }
        authenticated_client.post(f"/api/v1/payment/orders/{order_id}/pay", json=payment_data)
        
        with allure.step(f"申请订单'{order_id}'退款"):
            refund_data = {
                "reason": "Product not as described",
                "amount": test_payment_data["price"],  # 全额退款
                "description": "The product features were not as advertised."
            }
            response = authenticated_client.post(f"/api/v1/payment/orders/{order_id}/refund", json=refund_data)
        
        with allure.step("验证退款申请响应"):
            assert response.status_code == 200, f"申请退款失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "refund_id" in response_data, "响应中缺少refund_id字段"
            assert "order_id" in response_data, "响应中缺少order_id字段"
            assert "status" in response_data, "响应中缺少status字段"
            assert response_data["status"] == "pending", f"退款状态应为pending，实际: {response_data['status']}"
            assert "amount" in response_data, "响应中缺少amount字段"
            assert "reason" in response_data, "响应中缺少reason字段"
            assert "requested_at" in response_data, "响应中缺少requested_at字段"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "退款申请响应",
                allure.attachment_type.JSON
            )
    
    @allure.story("货币转换")
    @allure.title("测试货币转换功能")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression", "payment")
    @pytest.mark.parametrize("from_currency,to_currency", [
        ("USD", "EUR"),
        ("EUR", "USD"),
        ("USD", "GBP"),
        ("GBP", "USD")
    ])
    def test_currency_conversion(self, api_client, from_currency, to_currency):
        """
        测试货币转换功能
        
        验证点：
        1. 货币转换接口返回200状态码
        2. 响应中包含转换后的金额
        3. 转换率合理
        """
        with allure.step(f"测试货币转换: {from_currency} -> {to_currency}"):
            params = {
                "amount": 100.0,
                "from_currency": from_currency,
                "to_currency": to_currency
            }
            response = api_client.get("/api/v1/payment/currency/convert", params=params)
        
        with allure.step("验证货币转换响应"):
            assert response.status_code == 200, f"货币转换失败，状态码: {response.status_code}"
            
            response_data = response.json()
            assert "amount" in response_data, "响应中缺少amount字段"
            assert "from_currency" in response_data, "响应中缺少from_currency字段"
            assert "to_currency" in response_data, "响应中缺少to_currency字段"
            assert "converted_amount" in response_data, "响应中缺少converted_amount字段"
            assert "exchange_rate" in response_data, "响应中缺少exchange_rate字段"
            assert "timestamp" in response_data, "响应中缺少timestamp字段"
            
            # 验证转换金额合理
            converted_amount = response_data["converted_amount"]
            exchange_rate = response_data["exchange_rate"]
            
            assert isinstance(converted_amount, (int, float)), "转换金额应为数字类型"
            assert isinstance(exchange_rate, (int, float)), "汇率应为数字类型"
            assert exchange_rate > 0, "汇率应为正数"
            
            # 验证转换计算（允许微小误差）
            expected_amount = params["amount"] * exchange_rate
            tolerance = 0.01  # 1% 容差
            assert abs(converted_amount - expected_amount) / expected_amount < tolerance, \
                f"转换金额计算错误: {converted_amount} != {params['amount']} * {exchange_rate}"
            
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False),
                "货币转换响应",
                allure.attachment_type.JSON
            )