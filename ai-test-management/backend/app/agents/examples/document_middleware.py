"""
文档解析 Middleware

在 before_agent hook 中解析上传的文档(PDF/图片),并根据文件类型动态切换模型
"""



import os
import logging
from typing import Callable

import httpx
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.messages import SystemMessage
from langchain.chat_models import init_chat_model

from app.agents.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

# pylint: disable  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TkRsMmJRPT06YjA3NWY3MTQ=

class DocumentParsingMiddleware(AgentMiddleware):
    """
    文档解析中间件

    功能:
    1. 从 context 中获取 document_url
    2. 下载并解析文档内容(PDF/图片)
    3. 根据文件类型动态切换模型(图片用豆包,其他用DeepSeek)
    4. 将解析的内容添加到 system message 中
    """

    def __init__(self, enable_cache: bool = True):
        """
        初始化中间件

        Args:
            enable_cache: 是否启用 PDF 解析缓存
        """
        # 配置豆包 API (用于图片识别)
        self.doubao_api_key = os.getenv("DOUBAO_API_KEY", "")

        # 初始化 PDF 处理器
        self.pdf_processor = PDFProcessor(enable_cache=enable_cache)

        logger.info(f"DocumentParsingMiddleware 初始化完成 (缓存: {enable_cache})")

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """
        异步拦截模型调用,解析文档并动态切换模型

        Args:
            request: 模型请求对象
            handler: 原始处理函数

        Returns:
            ModelResponse: 模型响应
        """
        # 获取 context
        context = request.runtime.context
        document_url = getattr(context, "document_url", "")
        document_type = getattr(context, "document_type", "")

        # 如果没有文档URL,直接调用原始handler
        if not document_url:
            return await handler(request)
# fmt: off  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TkRsMmJRPT06YjA3NWY3MTQ=

        logger.info(f"开始解析文档: {document_url} (类型: {document_type})")

        # 判断是否为图片类型
        is_image = document_type.startswith("image/") if document_type else False

        # 根据文件类型动态切换模型和解析方法
        if is_image and self.doubao_api_key:
            # 使用豆包模型处理图片
            logger.info("检测到图片文件，切换到豆包模型")
            llm = init_chat_model("doubao:doubao-vision", api_key=self.doubao_api_key)
            parsed_content = await self._parse_image_async(document_url)
        else:
            # 使用默认的 DeepSeek 模型处理 PDF 等文档
            logger.info("使用 DeepSeek 模型处理文档")
            llm = init_chat_model("deepseek:deepseek-chat")

            # 根据文件类型选择解析方法
            if document_type == "application/pdf":
                parsed_content = await self._parse_pdf_async(document_url)
            else:
                # 其他文档类型（Word, TXT等）
                parsed_content = await self._parse_generic_document_async(document_url, document_type)

        # 将解析的内容添加到 system message 的 content_blocks 中
        existing_content = list(request.system_message.content_blocks) if request.system_message else []
        new_content = existing_content + [
            {
                "type": "text",
                "text": f"\n\n## 📄 上传的文档内容\n\n{parsed_content}\n\n请基于以上文档内容生成测试用例。"
            }
        ]

        new_system_message = SystemMessage(content=new_content)

        logger.info(f"文档解析完成，内容长度: {len(parsed_content)} 字符")

        # 使用新的模型和system message
        return await handler(request.override(
            system_message=new_system_message,
            model=llm
        ))
    
    async def _parse_pdf_async(self, url: str) -> str:
        """
        异步解析 PDF 文档（使用优化的 PDFProcessor）

        Args:
            url: PDF 文件的 URL (MinIO 预签名 URL)

        Returns:
            str: 解析后的文本内容
        """
        try:
            logger.info(f"开始下载 PDF: {url}")

            # 使用 httpx 异步下载 PDF 文件
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=60.0)
                response.raise_for_status()

            pdf_data = response.content
            logger.info(f"PDF 下载完成，大小: {len(pdf_data)} 字节")
# fmt: off  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TkRsMmJRPT06YjA3NWY3MTQ=

            # 使用 PDFProcessor 解析（支持缓存和多种解析方法）
            text_content = self.pdf_processor.extract_text(pdf_data, filename="uploaded.pdf")

            return text_content

        except httpx.HTTPError as e:
            logger.error(f"下载 PDF 失败: {e}")
            return f"PDF 文档下载失败: {str(e)}"
        except Exception as e:
            logger.error(f"PDF 文档解析失败: {e}")
            return f"PDF 文档解析失败: {str(e)}"

    async def _parse_image_async(self, url: str) -> str:
        """
        异步解析图片

        对于图片,我们返回图片URL,让支持视觉的模型(如豆包)直接处理

        Args:
            url: 图片文件的 URL (MinIO 预签名 URL)

        Returns:
            str: 图片描述信息
        """
        logger.info(f"准备解析图片: {url}")
        return f"用户上传了一张图片,图片URL: {url}\n\n请分析这张图片的内容,并根据图片中的信息生成测试用例。"

    async def _parse_generic_document_async(self, url: str, document_type: str) -> str:
        """
        异步解析通用文档（Word, TXT等）

        Args:
            url: 文档文件的 URL (MinIO 预签名 URL)
            document_type: 文档 MIME 类型

        Returns:
            str: 解析后的文本内容
        """
        try:
            logger.info(f"开始下载文档: {url} (类型: {document_type})")

            # 使用 httpx 异步下载文件
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=60.0)
                response.raise_for_status()

            content = response.content
            logger.info(f"文档下载完成，大小: {len(content)} 字节")

            # 根据文件类型解析
            if document_type == "text/plain":
                # 纯文本文件
                try:
                    text = content.decode('utf-8')
                except UnicodeDecodeError:
                    text = content.decode('gbk', errors='ignore')
                return text

            elif document_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                # Word 文档
                return "Word 文档解析功能待实现。建议将文档转换为 PDF 格式上传。"
# fmt: off  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TkRsMmJRPT06YjA3NWY3MTQ=

            else:
                return f"不支持的文档类型: {document_type}。建议将文档转换为 PDF 或 TXT 格式上传。"

        except httpx.HTTPError as e:
            logger.error(f"下载文档失败: {e}")
            return f"文档下载失败: {str(e)}"
        except Exception as e:
            logger.error(f"文档解析失败: {e}")
            return f"文档解析失败: {str(e)}"

