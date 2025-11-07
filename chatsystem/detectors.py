"""
文件类型检测模块
用于识别用户上传的文件类型，支持图片、PDF 和普通文本
"""

import logging
from typing import Optional, Any, List
from pathlib import Path

from chatsystem.types import FileType

# 配置日志
logger = logging.getLogger(__name__)


class FileTypeDetector:
    """
    文件类型检测器
    
    支持的图片格式: jpg, jpeg, png, gif, webp, bmp, svg
    支持的 PDF 格式: pdf
    支持的文本格式: txt, md, json, xml, csv, html
    """
    
    # 图片 MIME 类型
    IMAGE_MIME_TYPES = {
        "image/jpeg", "image/jpg", "image/png", "image/gif",
        "image/webp", "image/bmp", "image/svg+xml",
    }
    
    # PDF MIME 类型
    PDF_MIME_TYPES = {"application/pdf"}
    
    # 文本 MIME 类型
    TEXT_MIME_TYPES = {
        "text/plain", "text/markdown", "text/json", "text/xml",
        "text/csv", "text/html", "application/json", "application/xml",
    }
    
    # 文件扩展名映射
    EXTENSION_MAPPING = {
        # 图片
        ".jpg": FileType.IMAGE, ".jpeg": FileType.IMAGE,
        ".png": FileType.IMAGE, ".gif": FileType.IMAGE,
        ".webp": FileType.IMAGE, ".bmp": FileType.IMAGE,
        ".svg": FileType.IMAGE,
        # PDF
        ".pdf": FileType.PDF,
        # 文本
        ".txt": FileType.TEXT, ".md": FileType.TEXT,
        ".markdown": FileType.TEXT, ".json": FileType.TEXT,
        ".xml": FileType.TEXT, ".csv": FileType.TEXT,
        ".html": FileType.TEXT,
    }
    
    @classmethod
    def detect_from_mime_type(cls, mime_type: str) -> FileType:
        """根据 MIME 类型检测文件类型"""
        if mime_type in cls.IMAGE_MIME_TYPES:
            return FileType.IMAGE
        elif mime_type in cls.PDF_MIME_TYPES:
            return FileType.PDF
        elif mime_type in cls.TEXT_MIME_TYPES:
            return FileType.TEXT
        return FileType.UNKNOWN
    
    @classmethod
    def detect_from_extension(cls, filename: str) -> FileType:
        """根据文件扩展名检测文件类型"""
        ext = Path(filename).suffix.lower()
        return cls.EXTENSION_MAPPING.get(ext, FileType.UNKNOWN)
    
    @classmethod
    def detect_from_message(cls, message: Any) -> FileType:
        """
        从消息对象检测文件类型

        检测优先级:
        1. 检查是否有文件内容（file 类型）
        2. 检查是否有图片 URL（image_url 类型）
        3. 检查是否是纯文本

        关键: 如果消息中没有任何文件或图片，则认为是文本消息
        """
        if not message:
            logger.debug("消息为空，返回 UNKNOWN")
            return FileType.UNKNOWN

        # 处理 HumanMessage 对象
        if hasattr(message, 'content'):
            content = message.content
            logger.debug(f"消息内容类型: {type(content)}")

            # 如果 content 是列表（多模态消息）
            if isinstance(content, list):
                logger.debug(f"检测到列表内容，共 {len(content)} 项")

                # 首先检查是否有文件或图片
                for item in content:
                    if isinstance(item, dict):
                        # 检查文件类型
                        if item.get('type') == 'file':
                            mime_type = item.get('mime_type', '')
                            file_type = cls.detect_from_mime_type(mime_type)

                            # 如果 MIME 类型检测失败，尝试通过文件名检测
                            if file_type == FileType.UNKNOWN:
                                filename = item.get('metadata', {}).get('filename', '')
                                if filename:
                                    file_type = cls.detect_from_extension(filename)
                                    logger.debug(f"通过文件名检测: {filename} -> {file_type.value}")

                            if file_type != FileType.UNKNOWN:
                                logger.debug(f"检测到文件类型: {file_type.value}")
                                return file_type

                        # 检查直接上传的图片（前端 LangChain 标准格式）
                        elif item.get('type') == 'image_url':
                            logger.debug("检测到 image_url 类型（LangChain 标准格式）")
                            return FileType.IMAGE

                # 如果列表中没有文件或图片，检查是否有文本内容
                # 如果列表中只有文本，则认为是文本消息
                has_text = any(
                    isinstance(item, dict) and item.get('type') == 'text'
                    for item in content
                )
                if has_text:
                    logger.debug("列表中检测到文本内容，返回 TEXT")
                    return FileType.TEXT

                # 如果列表为空或只有其他类型，返回 UNKNOWN
                logger.debug("列表中没有文件、图片或文本，返回 UNKNOWN")
                return FileType.UNKNOWN

            # 如果 content 是字符串（普通文本）
            elif isinstance(content, str):
                logger.debug(f"检测到字符串内容，长度: {len(content)}")
                return FileType.TEXT

            # 如果 content 是其他类型，尝试转换为字符串
            else:
                logger.debug(f"检测到其他类型内容: {type(content)}")
                # 如果能转换为字符串且非空，则认为是文本
                try:
                    str_content = str(content)
                    if str_content and str_content.strip():
                        logger.debug("其他类型内容可转换为文本，返回 TEXT")
                        return FileType.TEXT
                except:
                    pass

        logger.debug("无法检测文件类型，返回 UNKNOWN")
        return FileType.UNKNOWN
    
    @classmethod
    def detect_from_messages(cls, messages: List[Any]) -> FileType:
        """
        从消息列表检测文件类型
        优先级: IMAGE > PDF > TEXT
        """
        detected_types = []
        
        for message in messages:
            file_type = cls.detect_from_message(message)
            if file_type != FileType.UNKNOWN:
                detected_types.append(file_type)
        
        # 按优先级返回
        if FileType.IMAGE in detected_types:
            return FileType.IMAGE
        elif FileType.PDF in detected_types:
            return FileType.PDF
        elif FileType.TEXT in detected_types:
            return FileType.TEXT
        
        return FileType.UNKNOWN

