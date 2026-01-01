"""
知识库集成测试脚本
测试完整的知识库管理和 RAG 查询流程
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置
BASE_URL = "http://localhost:8000"
LIGHTRAG_URL = "http://localhost:9621"

# 测试用户 token（需要先登录获取）
TOKEN = None


async def test_lightrag_health():
    """测试 LightRAG 健康状态"""
    logger.info("=" * 50)
    logger.info("测试 LightRAG 健康状态")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{LIGHTRAG_URL}/health", timeout=10.0)
            response.raise_for_status()
            result = response.json()
            logger.info(f"✅ LightRAG 健康检查成功: {result}")
            return True
        except Exception as e:
            logger.error(f"❌ LightRAG 健康检查失败: {e}")
            return False


async def login():
    """登录获取 token"""
    logger.info("=" * 50)
    logger.info("登录获取 token")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/login",
                json={
                    "user_name": "admin",
                    "password": "admin123"
                }
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 200:
                token = result['data']['access_token']
                logger.info(f"✅ 登录成功, token: {token[:50]}...")
                return token
            else:
                logger.error(f"❌ 登录失败: {result.get('msg')}")
                return None
        except Exception as e:
            logger.error(f"❌ 登录异常: {e}")
            return None


async def create_knowledge(token: str, project_id: int = 1):
    """创建知识库"""
    logger.info("=" * 50)
    logger.info("创建知识库")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/testing/knowledge/create",
                headers=headers,
                json={
                    "project_id": project_id,
                    "knowledge_name": f"测试知识库_{asyncio.get_event_loop().time():.0f}",
                    "description": "这是一个测试知识库",
                    "remark": "集成测试"
                }
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 200:
                knowledge_id = result['data']['knowledge_id']
                logger.info(f"✅ 知识库创建成功, knowledge_id: {knowledge_id}")
                return knowledge_id
            else:
                logger.error(f"❌ 知识库创建失败: {result.get('msg')}")
                return None
        except Exception as e:
            logger.error(f"❌ 创建知识库异常: {e}")
            return None


async def get_knowledge_detail(token: str, knowledge_id: int):
    """获取知识库详情"""
    logger.info("=" * 50)
    logger.info(f"获取知识库详情 (ID: {knowledge_id})")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/testing/knowledge/{knowledge_id}",
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 200:
                data = result['data']
                logger.info(f"✅ 知识库详情: {data}")
                return data
            else:
                logger.error(f"❌ 获取失败: {result.get('msg')}")
                return None
        except Exception as e:
            logger.error(f"❌ 获取详情异常: {e}")
            return None


async def upload_file(token: str, knowledge_id: int, file_content: str, filename: str):
    """上传文件"""
    logger.info("=" * 50)
    logger.info(f"上传文件: {filename}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            files = {
                'file': (filename, file_content, 'text/plain')
            }
            data = {
                'remark': '测试文件'
            }
            
            response = await client.post(
                f"{BASE_URL}/testing/knowledge/{knowledge_id}/files/upload",
                headers=headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 200:
                file_id = result['data']['file_id']
                logger.info(f"✅ 文件上传成功, file_id: {file_id}")
                return file_id
            else:
                logger.error(f"❌ 文件上传失败: {result.get('msg')}")
                return None
        except Exception as e:
            logger.error(f"❌ 上传文件异常: {e}")
            return None


async def get_file_list(token: str, knowledge_id: int):
    """获取文件列表"""
    logger.info("=" * 50)
    logger.info(f"获取文件列表 (knowledge_id: {knowledge_id})")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/testing/knowledge/{knowledge_id}/files",
                headers=headers,
                params={'page_num': 1, 'page_size': 10}
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 200:
                files = result['data']['rows']
                logger.info(f"✅ 获取文件列表成功, 共 {len(files)} 个文件")
                for file in files:
                    logger.info(f"  - {file['file_name']}: {file['process_status']} ({file['process_progress']}%)")
                return files
            else:
                logger.error(f"❌ 获取失败: {result.get('msg')}")
                return []
        except Exception as e:
            logger.error(f"❌ 获取文件列表异常: {e}")
            return []


async def query_knowledge(token: str, knowledge_id: int, query: str, mode: str = 'hybrid'):
    """查询知识库"""
    logger.info("=" * 50)
    logger.info(f"查询知识库: {query}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/testing/knowledge/{knowledge_id}/query",
                headers=headers,
                json={
                    'query': query,
                    'mode': mode
                }
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 200:
                data = result['data']
                logger.info(f"✅ 查询成功")
                logger.info(f"  回答: {data.get('answer', '')[:200]}...")
                return data
            else:
                logger.error(f"❌ 查询失败: {result.get('msg')}")
                return None
        except Exception as e:
            logger.error(f"❌ 查询异常: {e}")
            return None


async def get_knowledge_stats(token: str, knowledge_id: int):
    """获取知识库统计"""
    logger.info("=" * 50)
    logger.info(f"获取知识库统计 (ID: {knowledge_id})")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/testing/knowledge/{knowledge_id}/stats",
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 200:
                stats = result['data']
                logger.info(f"✅ 统计信息: {stats}")
                return stats
            else:
                logger.error(f"❌ 获取失败: {result.get('msg')}")
                return None
        except Exception as e:
            logger.error(f"❌ 获取统计异常: {e}")
            return None


async def main():
    """主测试流程"""
    logger.info("🚀 开始知识库集成测试")
    
    # 1. 检查 LightRAG 服务
    if not await test_lightrag_health():
        logger.error("⚠️  LightRAG 服务未启动，请先启动 anything-chat-rag 服务")
        return
    
    # 2. 登录
    token = await login()
    if not token:
        logger.error("⚠️  登录失败，请检查用户名密码")
        return
    
    # 3. 创建知识库
    knowledge_id = await create_knowledge(token, project_id=1)
    if not knowledge_id:
        logger.error("⚠️  创建知识库失败")
        return
    
    # 4. 获取知识库详情
    detail = await get_knowledge_detail(token, knowledge_id)
    if detail:
        logger.info(f"📊 Collection 名称: {detail.get('collection_name')}")
    
    # 5. 上传测试文件
    test_content = """
# AI 智能测试平台

## 简介
AI 智能测试平台是一个基于 FastAPI 和 LightRAG 的智能测试管理系统。

## 主要功能
1. 项目管理
2. 知识库管理
3. RAG 问答
4. 文件上传与处理

## 技术栈
- FastAPI: Web 框架
- LightRAG: RAG 引擎
- Milvus: 向量数据库
- MinIO: 对象存储
    """
    
    file_id = await upload_file(token, knowledge_id, test_content, "test_document.txt")
    if not file_id:
        logger.error("⚠️  上传文件失败")
        return
    
    # 6. 等待文件处理
    logger.info("⏳ 等待文件处理（30秒）...")
    await asyncio.sleep(30)
    
    # 7. 查看文件列表
    files = await get_file_list(token, knowledge_id)
    
    # 8. 获取统计信息
    stats = await get_knowledge_stats(token, knowledge_id)
    
    # 9. 查询知识库
    if files and any(f['process_status'] == 'completed' for f in files):
        await query_knowledge(token, knowledge_id, "AI 智能测试平台有哪些功能？", mode='hybrid')
        await query_knowledge(token, knowledge_id, "使用了哪些技术栈？", mode='local')
    else:
        logger.warning("⚠️  文件尚未处理完成，跳过查询测试")
    
    logger.info("=" * 50)
    logger.info("✅ 测试完成！")
    logger.info(f"📌 知识库 ID: {knowledge_id}")
    logger.info(f"📌 Collection: {detail.get('collection_name') if detail else 'N/A'}")


if __name__ == '__main__':
    asyncio.run(main())


