"""API Query and Data Generation Tools for K6 Performance Testing.

这个模块提供从知识库查询API信息和生成测试数据的工具：
1. 从 anything-chat-rag 查询任意 API 接口的原始数据
2. 生成各类测试数据（用户、商品、购物车、订单等）
3. 支持 Faker 风格的数据构造

这些工具通用于测试任何存储在知识库中的 API 接口。
"""

import os
import json
import random
import string
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Literal
from langchain_core.tools import tool
from pydantic import BaseModel, Field


# 从环境变量获取知识库 API 地址
KNOWLEDGE_API_URL = os.getenv("KNOWLEDGE_API_URL", "http://localhost:9621")


# ============================================================================
# API 查询工具 - 从知识库获取接口信息
# ============================================================================

class QueryAPIInput(BaseModel):
    """Input schema for API query tool."""
    query: str = Field(
        description="查询文本，描述要查找的API接口，如'购物车添加商品接口'、'用户登录接口'等"
    )
    mode: str = Field(
        default="naive",
        description="查询模式：naive(向量搜索,推荐)、local(实体)、global(关系)、hybrid(混合)、mix(综合)"
    )
    top_k: int = Field(
        default=5,
        description="返回结果数量，建议1-5条"
    )


@tool(args_schema=QueryAPIInput)
async def query_api_from_knowledge_base(
    query: str,
    mode: str = "naive",
    top_k: int = 5,
) -> str:
    """从知识库查询API接口的原始数据。

    使用 POST /query/data 接口从 anything-chat-rag 知识库中检索 API 信息。
    返回结构化的原始数据，包括：
    - 文档块（chunks）：包含完整的 API 定义、参数、请求/响应示例
    - 实体信息：API 名称、类型、描述
    - 关系信息：接口之间的关联

    这是一个通用工具，可以查询知识库中存储的任何 API 接口信息，
    如购物车接口、用户登录接口、订单接口等。

    查询结果可直接用于：
    1. 分析 API 结构，提取接口 URL、方法、参数
    2. 生成 K6 性能测试脚本
    3. 了解接口之间的依赖关系

    Args:
        query: 查询文本，如"购物车相关接口"、"用户登录API"
        mode: 查询模式
            - naive: 向量相似度搜索（推荐，最精确）
            - local: 聚焦实体检索
            - global: 关系模式检索
            - hybrid: local + global 混合
            - mix: 知识图谱 + 向量综合
        top_k: 返回结果数量（1-10）

    Returns:
        JSON 格式的 API 信息，包含原始文档内容
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "query": query,
            "mode": mode,
            "top_k": min(max(top_k, 1), 10),  # 限制 1-10
        }
        
        try:
            response = await client.post(
                f"{KNOWLEDGE_API_URL}/query/data",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") == "failure" or "error" in result:
                return f"❌ 查询失败: {result.get('error', result.get('message', '未知错误'))}"
            
            data = result.get("data", {})
            output_parts = []
            
            # 查询摘要
            output_parts.append(f"# 📡 API 查询结果\n")
            output_parts.append(f"**查询**: {query}")
            output_parts.append(f"**模式**: {mode} | **数量**: {top_k}\n")
            
            # 提取文本块（包含原始 API 信息）- 最重要的部分
            chunks = data.get("chunks", [])
            if chunks:
                output_parts.append("## 📄 API 原始文档\n")
                for i, chunk in enumerate(chunks[:top_k], 1):
                    content = chunk.get("content", "")
                    file_path = chunk.get("file_path", "未知来源")
                    output_parts.append(f"### 文档 {i} (来源: {file_path})")
                    output_parts.append(f"```\n{content}\n```\n")
            
            # 提取实体信息
            entities = data.get("entities", [])
            if entities:
                output_parts.append("## 🏷️ 相关实体\n")
                for entity in entities[:5]:
                    name = entity.get("entity_name", "")
                    entity_type = entity.get("entity_type", "")
                    description = entity.get("description", "")[:300]
                    output_parts.append(f"- **{name}** ({entity_type})")
                    if description:
                        output_parts.append(f"  {description}")
            
            # 提取关系信息
            relationships = data.get("relationships", [])
            if relationships:
                output_parts.append("\n## 🔗 接口关系\n")
                for rel in relationships[:5]:
                    src = rel.get("src_id", "")
                    tgt = rel.get("tgt_id", "")
                    desc = rel.get("description", "")[:100]
                    output_parts.append(f"- {src} → {tgt}: {desc}")
            
            if not chunks and not entities:
                return f"⚠️ 未找到与 '{query}' 相关的 API 信息。\n\n建议：\n1. 尝试更具体的关键词\n2. 检查知识库是否已导入相关文档"
            
            return "\n".join(output_parts)
            
        except httpx.HTTPError as e:
            return f"❌ 知识库请求失败: {str(e)}\n\n请检查：\n1. 知识库服务是否运行\n2. KNOWLEDGE_API_URL 配置是否正确 ({KNOWLEDGE_API_URL})"


# ============================================================================
# 测试数据生成工具 - Faker 风格
# ============================================================================

class GenerateTestDataInput(BaseModel):
    """Input schema for test data generation tool."""
    data_type: str = Field(
        description="数据类型：user/product/cart/order/address/payment/custom"
    )
    count: int = Field(
        default=100,
        description="生成数量，建议 10-1000"
    )
    output_format: str = Field(
        default="k6_array",
        description="输出格式：k6_array(K6脚本用)、json、csv"
    )
    custom_fields: Optional[str] = Field(
        default=None,
        description="自定义字段定义(JSON)，用于 custom 类型"
    )


@tool(args_schema=GenerateTestDataInput)
def generate_test_data(
    data_type: str,
    count: int = 100,
    output_format: str = "k6_array",
    custom_fields: Optional[str] = None,
) -> str:
    """生成性能测试所需的测试数据。

    支持多种预定义数据类型和自定义数据，使用 Faker 风格生成逼真的测试数据。

    预定义数据类型：
    - user: 用户数据（用户名、邮箱、手机、密码等）
    - product: 商品数据（SKU、名称、价格、库存等）
    - cart: 购物车数据（用户ID、商品ID、数量等）
    - order: 订单数据（订单号、金额、状态等）
    - address: 地址数据（省市区、详细地址等）
    - payment: 支付数据（支付方式、金额、状态等）
    - custom: 自定义数据（需提供 custom_fields）

    输出格式：
    - k6_array: K6 脚本可直接使用的 JavaScript 数组
    - json: 标准 JSON 格式
    - csv: CSV 格式（适合大量数据）

    Args:
        data_type: 数据类型
        count: 生成数量（10-1000）
        output_format: 输出格式
        custom_fields: 自定义字段定义（JSON），如 '{"name":"string","age":"int:18-60"}'

    Returns:
        生成的测试数据
    """
    count = min(max(count, 10), 1000)  # 限制 10-1000
    
    # 辅助函数
    def random_string(length=8):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def random_phone():
        return f"1{random.choice(['3','5','7','8','9'])}{random.randint(100000000, 999999999)}"
    
    def random_email(username):
        domains = ['qq.com', '163.com', 'gmail.com', 'hotmail.com', 'test.com']
        return f"{username}@{random.choice(domains)}"
    
    def random_date(days_back=30):
        return (datetime.now() - timedelta(days=random.randint(0, days_back))).strftime('%Y-%m-%d %H:%M:%S')
    
    def random_cn_name():
        surnames = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴']
        names = ['伟', '芳', '娜', '秀英', '敏', '静', '强', '磊', '洋', '艳']
        return random.choice(surnames) + random.choice(names) + random.choice(names)
    
    data = []
    
    if data_type == "user":
        for i in range(count):
            username = f"user_{random_string(6)}"
            data.append({
                "id": i + 1,
                "username": username,
                "email": random_email(username),
                "phone": random_phone(),
                "nickname": f"测试用户{i+1}",
                "password": random_string(12),
                "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}",
                "status": random.choice(["active", "inactive"]),
                "created_at": random_date(365),
            })
    
    elif data_type == "product":
        categories = ["电子产品", "服装鞋帽", "食品饮料", "家居用品", "图书音像", "美妆护肤", "运动户外"]
        for i in range(count):
            data.append({
                "id": i + 1001,
                "sku": f"SKU{str(i+1).zfill(8)}",
                "name": f"测试商品{i+1}",
                "category": random.choice(categories),
                "price": round(random.uniform(9.9, 9999.99), 2),
                "original_price": round(random.uniform(19.9, 12999.99), 2),
                "stock": random.randint(0, 10000),
                "sales": random.randint(0, 50000),
                "rating": round(random.uniform(3.0, 5.0), 1),
                "status": random.choice(["active", "inactive", "sold_out"]),
            })
    
    elif data_type == "cart":
        for i in range(count):
            data.append({
                "id": i + 1,
                "user_id": random.randint(1, 1000),
                "product_id": random.randint(1001, 2000),
                "sku": f"SKU{str(random.randint(1,1000)).zfill(8)}",
                "quantity": random.randint(1, 10),
                "price": round(random.uniform(9.9, 999.99), 2),
                "selected": random.choice([True, False]),
                "added_at": random_date(7),
            })
    
    elif data_type == "order":
        statuses = ["pending", "paid", "processing", "shipped", "delivered", "cancelled", "refunded"]
        for i in range(count):
            data.append({
                "id": i + 1,
                "order_no": f"ORD{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(6)}",
                "user_id": random.randint(1, 1000),
                "total_amount": round(random.uniform(10, 10000), 2),
                "discount_amount": round(random.uniform(0, 100), 2),
                "shipping_fee": round(random.choice([0, 5, 10, 15]), 2),
                "status": random.choice(statuses),
                "items_count": random.randint(1, 10),
                "payment_method": random.choice(["alipay", "wechat", "credit_card"]),
                "created_at": random_date(30),
            })
    
    elif data_type == "address":
        provinces = ["北京市", "上海市", "广东省", "浙江省", "江苏省", "四川省", "湖北省"]
        cities = {
            "北京市": ["北京市"],
            "上海市": ["上海市"],
            "广东省": ["广州市", "深圳市", "东莞市", "佛山市"],
            "浙江省": ["杭州市", "宁波市", "温州市", "绍兴市"],
            "江苏省": ["南京市", "苏州市", "无锡市", "常州市"],
            "四川省": ["成都市", "绵阳市", "德阳市"],
            "湖北省": ["武汉市", "宜昌市", "襄阳市"],
        }
        for i in range(count):
            province = random.choice(provinces)
            city = random.choice(cities.get(province, ["未知市"]))
            data.append({
                "id": i + 1,
                "user_id": random.randint(1, 1000),
                "name": random_cn_name(),
                "phone": random_phone(),
                "province": province,
                "city": city,
                "district": f"测试区{random.randint(1,10)}",
                "street": f"测试街道{random.randint(1,100)}号",
                "detail": f"{random.randint(1,30)}栋{random.randint(1,50)}层{random.randint(1,10)}室",
                "zip_code": f"{random.randint(100000, 999999)}",
                "is_default": i == 0,
            })
    
    elif data_type == "payment":
        methods = ["alipay", "wechat", "credit_card", "debit_card", "balance"]
        for i in range(count):
            data.append({
                "id": i + 1,
                "order_id": i + 1,
                "user_id": random.randint(1, 1000),
                "method": random.choice(methods),
                "amount": round(random.uniform(10, 10000), 2),
                "status": random.choice(["pending", "success", "failed", "refunded"]),
                "transaction_id": f"TXN{random_string(16).upper()}",
                "paid_at": random_date(30) if random.random() > 0.2 else None,
            })
    
    elif data_type == "custom" and custom_fields:
        try:
            fields_def = json.loads(custom_fields)
            for i in range(count):
                item = {"id": i + 1}
                for field_name, field_type in fields_def.items():
                    if field_type == "string":
                        item[field_name] = random_string(10)
                    elif field_type == "int":
                        item[field_name] = random.randint(1, 1000)
                    elif field_type.startswith("int:"):
                        range_str = field_type[4:]
                        min_val, max_val = map(int, range_str.split("-"))
                        item[field_name] = random.randint(min_val, max_val)
                    elif field_type == "float":
                        item[field_name] = round(random.uniform(0, 1000), 2)
                    elif field_type == "bool":
                        item[field_name] = random.choice([True, False])
                    elif field_type == "email":
                        item[field_name] = random_email(f"user{i}")
                    elif field_type == "phone":
                        item[field_name] = random_phone()
                    elif field_type == "date":
                        item[field_name] = random_date(365)
                    elif field_type == "uuid":
                        import uuid
                        item[field_name] = str(uuid.uuid4())
                data.append(item)
        except json.JSONDecodeError:
            return "❌ custom_fields JSON 格式错误"
    else:
        return f"❌ 不支持的数据类型: {data_type}\n\n支持的类型: user, product, cart, order, address, payment, custom"
    
    # 格式化输出
    if output_format == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    elif output_format == "csv":
        if not data:
            return "No data generated"
        headers = list(data[0].keys())
        lines = [",".join(headers)]
        for item in data:
            values = []
            for h in headers:
                v = item.get(h, "")
                if isinstance(v, str) and ("," in v or '"' in v):
                    v = f'"{v}"'
                values.append(str(v) if v is not None else "")
            lines.append(",".join(values))
        return "\n".join(lines)
    
    else:  # k6_array (default)
        var_name = f"{data_type}Data"
        return f"""// 测试数据 - {data_type} (共 {count} 条)
// 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

const {var_name} = {json.dumps(data, ensure_ascii=False, indent=2)};

// 使用示例:
// import {{ randomItem }} from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';
// const item = randomItem({var_name});

export {{ {var_name} }};
"""


# ============================================================================
# API 解析工具 - 从原始文档提取接口定义
# ============================================================================

class ParseAPIInput(BaseModel):
    """Input schema for API parsing tool."""
    api_document: str = Field(
        description="API 原始文档内容（从 query_api_from_knowledge_base 获取）"
    )


@tool(args_schema=ParseAPIInput)
def parse_api_for_k6_script(
    api_document: str,
) -> str:
    """解析 API 文档，提取用于 K6 脚本生成的接口定义。

    分析从知识库查询到的 API 原始文档，提取关键信息：
    - 接口 URL
    - HTTP 方法
    - 请求参数
    - 请求体结构
    - 响应格式

    输出 JSON 格式的接口定义，可直接用于 generate_k6_script 工具。

    注意：此工具进行基础解析，复杂的 API 文档可能需要人工调整。

    Args:
        api_document: API 原始文档内容

    Returns:
        JSON 格式的接口定义数组
    """
    import re
    
    endpoints = []
    
    # 尝试提取 URL 模式
    url_patterns = [
        r'(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/\-\{\}]+)',  # GET /api/users
        r'URL[：:]\s*[`\'"]?(/[\w/\-\{\}]+)[`\'"]?',       # URL: /api/users
        r'接口[：:]\s*[`\'"]?(/[\w/\-\{\}]+)[`\'"]?',      # 接口：/api/users
        r'路径[：:]\s*[`\'"]?(/[\w/\-\{\}]+)[`\'"]?',      # 路径：/api/users
        r'"url"[：:]\s*"(/[\w/\-\{\}]+)"',                 # "url": "/api/users"
    ]
    
    # 尝试提取方法模式
    method_patterns = [
        r'方法[：:]\s*(GET|POST|PUT|DELETE|PATCH)',
        r'Method[：:]\s*(GET|POST|PUT|DELETE|PATCH)',
        r'"method"[：:]\s*"(GET|POST|PUT|DELETE|PATCH)"',
    ]
    
    found_urls = []
    found_methods = []
    
    for pattern in url_patterns:
        matches = re.findall(pattern, api_document, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                if len(match) == 2:
                    found_methods.append(match[0].upper())
                    found_urls.append(match[1])
                else:
                    found_urls.append(match[0])
            else:
                found_urls.append(match)
    
    for pattern in method_patterns:
        matches = re.findall(pattern, api_document, re.IGNORECASE)
        found_methods.extend([m.upper() for m in matches])
    
    # 去重并创建端点
    seen_urls = set()
    for i, url in enumerate(found_urls):
        if url in seen_urls:
            continue
        seen_urls.add(url)
        
        method = found_methods[i] if i < len(found_methods) else "GET"
        
        # 从 URL 推断名称
        name = url.strip("/").replace("/", "_").replace("{", "").replace("}", "")
        if not name:
            name = "api_endpoint"
        
        endpoint = {
            "name": name,
            "url": url,
            "method": method,
        }
        
        # 如果是 POST/PUT，添加默认请求体
        if method in ["POST", "PUT", "PATCH"]:
            endpoint["body"] = "{}"
        
        endpoints.append(endpoint)
    
    if not endpoints:
        return """⚠️ 未能自动解析出接口定义。

请手动提供接口信息，格式如下：
```json
[
  {
    "name": "添加购物车",
    "url": "/api/cart/add",
    "method": "POST",
    "body": "{ \\"product_id\\": 1, \\"quantity\\": 1 }"
  }
]
```

或者提供更详细的 API 文档给我分析。"""
    
    result = {
        "status": "success",
        "message": f"成功解析出 {len(endpoints)} 个接口",
        "endpoints": endpoints,
        "usage": "将 endpoints 数组传给 generate_k6_script 工具生成测试脚本"
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


# 导出所有工具
api_query_tools = [
    query_api_from_knowledge_base,
    generate_test_data,
    parse_api_for_k6_script,
]
