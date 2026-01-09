"""
文档解析工具

参照 ai-test-management 项目实现
支持 PDF、图片、TXT 等多种格式的文档解析

关键功能：
1. PDF 文档解析（支持表格提取）
2. 图片 OCR 识别
3. 文本文件解析
4. URL 下载和解析
"""
import os
import hashlib
from io import BytesIO
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from functools import lru_cache

import httpx
from langchain_core.tools import tool

from utils.log_util import logger


@dataclass
class ParsedDocument:
    """解析后的文档"""
    content: str
    document_type: str
    metadata: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "document_type": self.document_type,
            "metadata": self.metadata,
            "success": self.success,
            "error": self.error
        }


class PDFProcessor:
    """PDF 文档处理器"""
    
    def __init__(self, enable_cache: bool = True):
        """
        初始化 PDF 处理器
        
        Args:
            enable_cache: 是否启用缓存
        """
        self.enable_cache = enable_cache
        self._cache: Dict[str, str] = {}
    
    def _get_cache_key(self, content: bytes) -> str:
        """生成缓存键"""
        return hashlib.md5(content).hexdigest()
    
    def extract_text(self, pdf_content: bytes, filename: str = "document.pdf") -> str:
        """
        从 PDF 中提取文本
        
        Args:
            pdf_content: PDF 文件内容
            filename: 文件名（用于日志）
            
        Returns:
            str: 提取的文本内容
        """
        # 检查缓存
        if self.enable_cache:
            cache_key = self._get_cache_key(pdf_content)
            if cache_key in self._cache:
                logger.info(f"使用缓存的 PDF 解析结果: {filename}")
                return self._cache[cache_key]
        
        text_content = ""
        
        # 方法1: 尝试使用 pymupdf4llm（支持更好的表格提取）
        try:
            import pymupdf4llm
            import fitz
            
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            text_content = pymupdf4llm.to_markdown(doc)
            doc.close()
            
            logger.info(f"使用 pymupdf4llm 成功解析 PDF: {filename}")
            
        except ImportError:
            logger.warning("pymupdf4llm 未安装，尝试使用 PyPDF2")
            
            # 方法2: 使用 PyPDF2
            try:
                from PyPDF2 import PdfReader
                
                reader = PdfReader(BytesIO(pdf_content))
                pages_text = []
                
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append(f"--- 第 {i + 1} 页 ---\n{page_text}")
                
                text_content = "\n\n".join(pages_text)
                logger.info(f"使用 PyPDF2 成功解析 PDF: {filename}")
                
            except ImportError:
                logger.warning("PyPDF2 未安装，尝试使用 pdfplumber")
                
                # 方法3: 使用 pdfplumber
                try:
                    import pdfplumber
                    
                    with pdfplumber.open(BytesIO(pdf_content)) as pdf:
                        pages_text = []
                        for i, page in enumerate(pdf.pages):
                            page_text = page.extract_text()
                            if page_text:
                                pages_text.append(f"--- 第 {i + 1} 页 ---\n{page_text}")
                        
                        text_content = "\n\n".join(pages_text)
                    
                    logger.info(f"使用 pdfplumber 成功解析 PDF: {filename}")
                    
                except ImportError:
                    raise ImportError("请安装 PDF 解析库: pip install pymupdf4llm PyPDF2 pdfplumber")
        
        except Exception as e:
            logger.error(f"PDF 解析失败: {e}")
            raise
        
        # 存入缓存
        if self.enable_cache and text_content:
            self._cache[cache_key] = text_content
        
        return text_content
    
    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()


class ImageProcessor:
    """图片处理器"""
    
    def __init__(self):
        """初始化图片处理器"""
        self._ocr_available = None
    
    def check_ocr_available(self) -> bool:
        """检查 OCR 是否可用"""
        if self._ocr_available is not None:
            return self._ocr_available
        
        try:
            import pytesseract
            from PIL import Image
            self._ocr_available = True
        except ImportError:
            self._ocr_available = False
        
        return self._ocr_available
    
    def extract_text(self, image_content: bytes, filename: str = "image.png") -> str:
        """
        从图片中提取文本（OCR）
        
        Args:
            image_content: 图片内容
            filename: 文件名
            
        Returns:
            str: 提取的文本
        """
        if not self.check_ocr_available():
            return f"[图片文件: {filename}]\n\n提示：OCR 功能不可用，请安装 pytesseract 和 pillow\n或使用支持视觉的大模型分析此图片。"
        
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(BytesIO(image_content))
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            logger.info(f"使用 OCR 成功解析图片: {filename}")
            return text
            
        except Exception as e:
            logger.error(f"图片 OCR 失败: {e}")
            return f"[图片文件: {filename}]\n\nOCR 解析失败: {str(e)}"
    
    def get_image_info(self, image_content: bytes, filename: str = "image.png") -> Dict[str, Any]:
        """获取图片信息"""
        try:
            from PIL import Image
            
            image = Image.open(BytesIO(image_content))
            return {
                "filename": filename,
                "format": image.format,
                "mode": image.mode,
                "width": image.width,
                "height": image.height,
                "size_bytes": len(image_content)
            }
        except Exception as e:
            return {
                "filename": filename,
                "error": str(e),
                "size_bytes": len(image_content)
            }


class DocumentParser:
    """文档解析器"""
    
    def __init__(self, enable_cache: bool = True):
        """
        初始化文档解析器
        
        Args:
            enable_cache: 是否启用缓存
        """
        self.pdf_processor = PDFProcessor(enable_cache=enable_cache)
        self.image_processor = ImageProcessor()
    
    async def parse_from_url(
        self,
        url: str,
        document_type: Optional[str] = None,
        timeout: float = 60.0
    ) -> ParsedDocument:
        """
        从 URL 下载并解析文档
        
        Args:
            url: 文档 URL
            document_type: 文档类型（可选，自动检测）
            timeout: 下载超时时间
            
        Returns:
            ParsedDocument: 解析结果
        """
        try:
            logger.info(f"开始下载文档: {url}")
            
            # 下载文档
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
            
            content = response.content
            content_type = document_type or response.headers.get("content-type", "")
            
            # 从 URL 获取文件名
            filename = url.split("/")[-1].split("?")[0] or "document"
            
            logger.info(f"文档下载完成，大小: {len(content)} 字节，类型: {content_type}")
            
            return await self.parse_content(content, content_type, filename)
            
        except httpx.HTTPError as e:
            logger.error(f"文档下载失败: {e}")
            return ParsedDocument(
                content="",
                document_type="unknown",
                metadata={"url": url},
                success=False,
                error=f"文档下载失败: {str(e)}"
            )
        except Exception as e:
            logger.error(f"文档解析失败: {e}")
            return ParsedDocument(
                content="",
                document_type="unknown",
                metadata={"url": url},
                success=False,
                error=f"文档解析失败: {str(e)}"
            )
    
    async def parse_content(
        self,
        content: bytes,
        content_type: str,
        filename: str = "document"
    ) -> ParsedDocument:
        """
        解析文档内容
        
        Args:
            content: 文档内容
            content_type: 内容类型
            filename: 文件名
            
        Returns:
            ParsedDocument: 解析结果
        """
        metadata = {
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(content)
        }
        
        # 检测文档类型
        is_pdf = (
            content_type == "application/pdf" or 
            filename.lower().endswith(".pdf") or
            content[:4] == b'%PDF'
        )
        
        is_image = (
            content_type.startswith("image/") or
            any(filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"])
        )
        
        is_text = (
            content_type == "text/plain" or
            filename.lower().endswith(".txt") or
            content_type.startswith("text/")
        )
        
        try:
            if is_pdf:
                text = self.pdf_processor.extract_text(content, filename)
                return ParsedDocument(
                    content=text,
                    document_type="pdf",
                    metadata=metadata,
                    success=True
                )
            
            elif is_image:
                # 获取图片信息
                image_info = self.image_processor.get_image_info(content, filename)
                metadata.update(image_info)
                
                # 尝试 OCR
                text = self.image_processor.extract_text(content, filename)
                
                return ParsedDocument(
                    content=text,
                    document_type="image",
                    metadata=metadata,
                    success=True
                )
            
            elif is_text:
                # 尝试多种编码
                for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                    try:
                        text = content.decode(encoding)
                        metadata["encoding"] = encoding
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    text = content.decode('utf-8', errors='replace')
                    metadata["encoding"] = "utf-8 (with errors)"
                
                return ParsedDocument(
                    content=text,
                    document_type="text",
                    metadata=metadata,
                    success=True
                )
            
            else:
                return ParsedDocument(
                    content="",
                    document_type="unsupported",
                    metadata=metadata,
                    success=False,
                    error=f"不支持的文档类型: {content_type}。支持的类型: PDF, 图片, 文本"
                )
                
        except Exception as e:
            logger.error(f"文档解析失败: {e}")
            return ParsedDocument(
                content="",
                document_type="unknown",
                metadata=metadata,
                success=False,
                error=f"文档解析失败: {str(e)}"
            )


# 全局实例
_document_parser: Optional[DocumentParser] = None


def get_document_parser() -> DocumentParser:
    """获取文档解析器单例"""
    global _document_parser
    if _document_parser is None:
        _document_parser = DocumentParser()
    return _document_parser


# ============ 工具函数 ============

@tool
async def parse_document_from_url(
    url: str,
    document_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    从 URL 下载并解析文档内容
    
    支持的文档类型：
    - PDF: 使用 pymupdf4llm/PyPDF2/pdfplumber 解析
    - 图片: 使用 OCR 提取文字（需要安装 pytesseract）
    - 文本: 自动检测编码并解析
    
    Args:
        url: 文档的 URL（通常是 MinIO 预签名 URL）
        document_type: 文档 MIME 类型（可选，自动检测）
        
    Returns:
        dict: 包含解析结果的字典
            - success: bool, 是否成功
            - content: str, 解析的文本内容
            - document_type: str, 文档类型
            - metadata: dict, 文档元信息
            - error: str, 错误信息（如果失败）
    
    Examples:
        >>> result = await parse_document_from_url("http://example.com/doc.pdf")
        >>> if result["success"]:
        >>>     print(result["content"])
    """
    parser = get_document_parser()
    result = await parser.parse_from_url(url, document_type)
    return result.to_dict()


@tool
async def parse_document_content(
    content_base64: str,
    content_type: str,
    filename: str = "document"
) -> Dict[str, Any]:
    """
    解析 Base64 编码的文档内容
    
    Args:
        content_base64: Base64 编码的文档内容
        content_type: 内容类型
        filename: 文件名
        
    Returns:
        dict: 解析结果
    """
    import base64
    
    try:
        content = base64.b64decode(content_base64)
    except Exception as e:
        return {
            "success": False,
            "error": f"Base64 解码失败: {str(e)}",
            "content": "",
            "document_type": "unknown",
            "metadata": {}
        }
    
    parser = get_document_parser()
    result = await parser.parse_content(content, content_type, filename)
    return result.to_dict()

