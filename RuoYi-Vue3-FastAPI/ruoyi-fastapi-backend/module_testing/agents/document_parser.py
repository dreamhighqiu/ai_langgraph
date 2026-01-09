"""
文档解析工具

严格参照 ai-test-management 项目实现
支持 PDF、图片、TXT 等多种格式的文档解析

关键功能：
1. PDF 文档解析（使用 PyMuPDF4LLM，支持表格和多模态图片解析）
2. 图片处理（返回提示信息，让视觉模型处理）
3. 文本文件解析
4. URL 下载和解析
"""

import os
import tempfile
import logging
import hashlib
import time
from typing import Optional, Dict, Any

import httpx
from langchain_core.tools import tool

from utils.log_util import logger

# PDF 内容缓存，避免重复解析同一个文件
_pdf_cache = {}


def _safe_delete_temp_file(file_path: str, max_retries: int = 3, delay: float = 0.1):
    """
    安全删除临时文件，处理Windows文件锁定问题

    Args:
        file_path: 要删除的文件路径
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
    """
    if not os.path.exists(file_path):
        return

    for attempt in range(max_retries):
        try:
            os.unlink(file_path)
            logger.debug(f"临时文件已删除: {file_path}")
            return
        except PermissionError as e:
            if attempt < max_retries - 1:
                logger.debug(f"删除临时文件失败（尝试 {attempt + 1}/{max_retries}），等待后重试: {e}")
                time.sleep(delay)
            else:
                logger.warning(f"无法删除临时文件（已重试{max_retries}次），文件将由系统清理: {file_path}")
        except Exception as e:
            logger.warning(f"删除临时文件时发生异常: {e}")
            break


class PDFProcessor:
    """PDF 处理器类"""
    
    def __init__(self, enable_cache: bool = True):
        self.enable_cache = enable_cache
        self.cache = _pdf_cache if enable_cache else {}
    
    def extract_text(self, pdf_data: bytes, filename: str = "unknown.pdf") -> str:
        """从PDF字节数据中提取文本"""
        return extract_pdf_text(pdf_data, filename, self.cache if self.enable_cache else None)
    
    def clear_cache(self):
        """清空缓存"""
        if self.enable_cache:
            self.cache.clear()
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计信息"""
        return {
            "cache_enabled": self.enable_cache,
            "cached_files": len(self.cache) if self.enable_cache else 0,
            "cache_keys": list(self.cache.keys()) if self.enable_cache else []
        }


def extract_pdf_text(pdf_data: bytes, filename: str = "unknown.pdf", cache: Optional[dict] = None) -> str:
    """
    从PDF字节数据中提取文本，使用缓存避免重复解析

    提取方法：
    1. PyMuPDF4LLM (推荐): 支持表格提取和多模态图片解析
       安装: pip install -qU langchain-community langchain-pymupdf4llm
    2. PyPDF2 (备用): 基础文本提取
       安装: pip install PyPDF2

    Args:
        pdf_data: PDF文件的字节数据
        filename: 文件名（用于日志和缓存）
        cache: 可选的缓存字典

    Returns:
        str: 提取的文本内容
    """
    # 生成PDF数据的哈希值作为缓存键
    pdf_hash = hashlib.md5(pdf_data).hexdigest()
    cache_key = f"{filename}_{pdf_hash}"

    # 检查缓存
    if cache is not None and cache_key in cache:
        logger.info(f"从缓存中获取PDF内容: {filename}")
        return cache[cache_key]

    # 创建临时文件（Windows需要先关闭文件句柄才能被其他程序访问）
    temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    try:
        temp_file.write(pdf_data)
        temp_file.flush()  # 确保数据写入磁盘
        os.fsync(temp_file.fileno())  # 强制同步到磁盘
        temp_file_path = temp_file.name
    finally:
        temp_file.close()  # 显式关闭文件句柄，释放文件锁

    text_content = ""

    try:
        # 优先尝试使用 PyMuPDF4LLM (功能更强大)
        logger.info(f"使用 PyMuPDF4LLM 解析PDF: {filename}")

        try:
            from langchain_pymupdf4llm import PyMuPDF4LLMLoader

            # 检查是否启用多模态图片解析
            # 从环境变量读取配置
            enable_multimodal = os.getenv("ENABLE_PDF_MULTIMODAL", "false").lower() == "true"

            if enable_multimodal:
                try:
                    from langchain_community.document_loaders.parsers import LLMImageBlobParser
                    from langchain.chat_models import init_chat_model

                    # 使用豆包模型进行图片解析
                    doubao_api_key = os.getenv("DOUBAO_API_KEY", "")
                    if doubao_api_key:
                        image_llm = init_chat_model("doubao:doubao-vision", api_key=doubao_api_key)
                        image_parser = LLMImageBlobParser(model=image_llm)

                        loader = PyMuPDF4LLMLoader(
                            temp_file_path,
                            mode="single",
                            extract_images=True,
                            images_parser=image_parser,
                            table_strategy="lines"
                        )
                        logger.info("启用多模态图片解析")
                    else:
                        logger.warning("未配置 DOUBAO_API_KEY，禁用图片解析")
                        loader = PyMuPDF4LLMLoader(
                            temp_file_path,
                            mode="single",
                            table_strategy="lines"
                        )
                except ImportError as e:
                    logger.warning(f"多模态依赖未安装，使用基础模式: {e}")
                    loader = PyMuPDF4LLMLoader(
                        temp_file_path,
                        mode="single",
                        table_strategy="lines"
                    )
            else:
                # 基础模式：只提取文本和表格
                loader = PyMuPDF4LLMLoader(
                    temp_file_path,
                    mode="single",
                    table_strategy="lines"
                )

            documents = loader.load()

            if documents:
                text_content = documents[0].page_content
                logger.info(f"PyMuPDF4LLM 解析成功，内容长度: {len(text_content)} 字符")
            else:
                text_content = "PDF文件解析后内容为空"

        except ImportError:
            logger.warning("PyMuPDF4LLM 未安装，尝试使用 PyPDF2")
            raise  # 继续到备用方法

    except Exception as e:
        # 备用方法：使用 PyPDF2
        logger.warning(f"PyMuPDF4LLM 解析失败: {e}，尝试使用 PyPDF2")

        try:
            from PyPDF2 import PdfReader
            import io

            pdf_file = io.BytesIO(pdf_data)
            reader = PdfReader(pdf_file)

            # 提取所有页面的文本
            text_parts = []
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    text_parts.append(f"### 第 {page_num} 页\n\n{text.strip()}")

            if text_parts:
                text_content = "\n\n".join(text_parts)
                logger.info(f"PyPDF2 解析成功，内容长度: {len(text_content)} 字符")
            else:
                text_content = "PDF文档解析成功，但未提取到文本内容。可能是扫描版PDF。"

        except ImportError:
            text_content = "错误: 未安装 PDF 解析库。请安装: pip install PyPDF2 或 pip install langchain-pymupdf4llm"
        except Exception as e2:
            logger.error(f"PyPDF2 解析也失败: {e2}")
            text_content = f"PDF文件处理出错: {str(e2)}"

    finally:
        # 清理临时文件（Windows上可能需要重试）
        _safe_delete_temp_file(temp_file_path)

    # 缓存结果
    if cache is not None and text_content:
        cache[cache_key] = text_content
        logger.info(f"PDF内容已缓存: {filename}")

    return text_content


# 初始化 PDF 处理器（全局单例，启用缓存）
_pdf_processor = PDFProcessor(enable_cache=True)


# ============ 工具函数 ============

@tool
async def parse_document_from_url(
    url: str,
    document_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    从 URL 下载并解析文档内容（支持 PDF、图片、TXT 等多种格式）

    这是从文档生成测试用例的核心工具，必须优先使用！

    支持的文档类型:
    - PDF: 使用 PyMuPDF4LLM (支持表格和多模态图片) 或 PyPDF2 (备用)
    - 图片: 自动使用视觉模型（如豆包 Vision）解析图片内容，提取文字和功能描述
        - 支持格式: JPG, JPEG, PNG, GIF, WEBP, BMP
        - 如果配置了 DOUBAO_API_KEY，会自动使用视觉模型解析
        - 如果未配置，会返回图片URL供视觉模型使用
    - TXT: 纯文本解析

    Args:
        url: 文档的 URL (通常是 MinIO 预签名 URL)
        document_type: 文档 MIME 类型 (可选，自动检测)

    Returns:
        dict: 包含解析结果的字典
            - success: bool, 是否成功
            - content: str, 解析的文本内容（图片会包含解析的文字描述）
            - document_type: str, 文档类型 (pdf/image/text)
            - image_url: str, 图片URL（仅图片类型）
            - parsed: bool, 是否已解析（仅图片类型，True表示已用视觉模型解析）
            - size_bytes: int, 文件大小（字节）
            - error: str, 错误信息 (如果失败)

    Examples:
        # 解析 PDF 文档
        >>> result = await parse_document_from_url("http://example.com/doc.pdf")
        >>> if result["success"]:
        >>>     print(result["content"])
        
        # 解析图片（会自动使用视觉模型）
        >>> result = await parse_document_from_url("http://example.com/image.png")
        >>> if result["success"]:
        >>>     if result.get("parsed"):
        >>>         print("图片已解析:", result["content"])
        >>>     else:
        >>>         print("图片URL:", result["image_url"])
    
    Important:
        - 当用户提供文档URL时，必须首先调用此工具解析文档
        - 图片文件会自动尝试使用视觉模型解析，提取文字和功能描述
        - 解析后的内容将用于生成测试用例
    """
    try:
        logger.info(f"开始解析文档: {url} (类型: {document_type})")

        # 下载文档
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=60.0)
            response.raise_for_status()

        content_data = response.content
        detected_type = document_type or response.headers.get("content-type", "")

        logger.info(f"文档下载完成，大小: {len(content_data)} 字节，类型: {detected_type}")

        # 根据文档类型选择解析方法
        if detected_type == "application/pdf" or url.lower().endswith(".pdf"):
            # PDF 文档解析
            text_content = _pdf_processor.extract_text(content_data, filename="document.pdf")

            return {
                "success": True,
                "content": text_content,
                "document_type": "pdf",
                "size_bytes": len(content_data),
            }

        elif detected_type.startswith("image/") or any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]):
            # 图片文件 - 尝试使用视觉模型解析
            logger.info(f"检测到图片文件，尝试使用视觉模型解析: {url}")
            
            # 检查是否配置了视觉模型（豆包）
            doubao_api_key = os.getenv("DOUBAO_API_KEY", "")
            if doubao_api_key:
                try:
                    from langchain_community.document_loaders.parsers import LLMImageBlobParser
                    from langchain.chat_models import init_chat_model
                    from langchain_core.document_loaders import Blob
                    
                    # 初始化豆包视觉模型
                    image_llm = init_chat_model("doubao:doubao-vision", api_key=doubao_api_key)
                    image_parser = LLMImageBlobParser(model=image_llm)
                    
                    # 创建 Blob 对象（LLMImageBlobParser 需要 Blob 对象）
                    # 根据文件扩展名确定 MIME 类型
                    mime_type = detected_type if detected_type.startswith("image/") else f"image/{url.split('.')[-1].lower()}"
                    if mime_type == "image/":
                        mime_type = "image/png"  # 默认
                    
                    blob = Blob(
                        data=content_data,
                        mime_type=mime_type,
                        path=url
                    )
                    
                    # 使用视觉模型解析图片
                    logger.info("使用豆包视觉模型解析图片内容...")
                    parsed_result = image_parser.parse(blob)
                    
                    if parsed_result and hasattr(parsed_result, 'page_content'):
                        image_content = parsed_result.page_content
                        logger.info(f"图片解析成功，内容长度: {len(image_content)} 字符")
                        
                        return {
                            "success": True,
                            "content": f"图片解析结果：\n\n{image_content}\n\n图片URL: {url}",
                            "document_type": "image",
                            "image_url": url,
                            "size_bytes": len(content_data),
                            "parsed": True,
                        }
                    else:
                        logger.warning("视觉模型解析返回空结果")
                        # 回退到提示信息
                        return {
                            "success": True,
                            "content": f"这是一张图片文件。\n\n图片URL: {url}\n\n已尝试使用视觉模型解析，但未获取到内容。请直接基于图片URL进行分析。",
                            "document_type": "image",
                            "image_url": url,
                            "size_bytes": len(content_data),
                            "parsed": False,
                        }
                        
                except ImportError as e:
                    logger.warning(f"视觉模型依赖未安装: {e}")
                    # 回退到提示信息
                    return {
                        "success": True,
                        "content": f"这是一张图片文件。\n\n图片URL: {url}\n\n注意：视觉模型解析功能未启用（缺少依赖或配置）。请使用支持视觉的模型来分析这张图片的内容，或提供图片的文字描述。",
                        "document_type": "image",
                        "image_url": url,
                        "size_bytes": len(content_data),
                        "parsed": False,
                    }
                except Exception as e:
                    logger.error(f"图片解析失败: {e}", exc_info=True)
                    # 回退到提示信息
                    return {
                        "success": True,
                        "content": f"这是一张图片文件。\n\n图片URL: {url}\n\n图片解析过程中出现错误: {str(e)}。请使用支持视觉的模型来分析这张图片的内容，或提供图片的文字描述。",
                        "document_type": "image",
                        "image_url": url,
                        "size_bytes": len(content_data),
                        "parsed": False,
                    }
            else:
                # 未配置视觉模型，返回提示信息
                logger.info("未配置 DOUBAO_API_KEY，返回图片URL供视觉模型使用")
                return {
                    "success": True,
                    "content": f"这是一张图片文件。\n\n图片URL: {url}\n\n注意：当前未配置视觉模型（DOUBAO_API_KEY），无法自动解析图片内容。\n\n请使用支持视觉的模型来分析这张图片的内容，或提供图片的文字描述。\n\n如果图片包含文字内容，建议：\n1. 使用支持视觉的模型（如 GPT-4 Vision、豆包 Vision）直接分析图片\n2. 或者提供图片的文字描述，我可以基于描述生成测试用例",
                    "document_type": "image",
                    "image_url": url,
                    "size_bytes": len(content_data),
                    "parsed": False,
                }

        elif detected_type == "text/plain" or url.lower().endswith(".txt"):
            # 纯文本文件
            try:
                text = content_data.decode('utf-8')
            except UnicodeDecodeError:
                text = content_data.decode('gbk', errors='ignore')

            return {
                "success": True,
                "content": text,
                "document_type": "text",
                "size_bytes": len(content_data),
            }

        else:
            # 不支持的文档类型
            return {
                "success": False,
                "error": f"不支持的文档类型: {detected_type}。建议将文档转换为 PDF 或 TXT 格式。",
                "document_type": detected_type,
            }

    except httpx.HTTPError as e:
        logger.error(f"下载文档失败: {e}")
        return {
            "success": False,
            "error": f"文档下载失败: {str(e)}",
        }
    except Exception as e:
        logger.error(f"文档解析失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"文档解析失败: {str(e)}",
        }
