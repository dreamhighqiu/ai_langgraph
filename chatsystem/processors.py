"""
多模态处理器模块
用于处理图片、PDF 和普通文本对话
"""

import logging
import base64
import tempfile
from typing import List, Optional, Any, Dict
from pathlib import Path

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from chatsystem.types import FileType, ProcessorType
from chatsystem.llm_factory import create_llm

logger = logging.getLogger(__name__)


class BaseProcessor:
    """处理器基类"""

    processor_type: ProcessorType
    model_name: str = "gpt-4o"

    def __init__(self, model_name: Optional[str] = None):
        """初始化处理器"""
        if model_name:
            self.model_name = model_name
        self._llm = None

    @property
    def llm(self):
        """延迟创建 LLM 实例"""
        if self._llm is None:
            self._llm = create_llm(model=self.model_name)
        return self._llm

    def process(self, messages: List[Any]) -> str:
        """处理消息"""
        raise NotImplementedError


class ImageProcessor(BaseProcessor):
    """图片处理器"""
    
    processor_type = ProcessorType.IMAGE
    model_name = "gpt-4o"
    
    @staticmethod
    def _extract_images_from_message(message: Any) -> List[Dict[str, Any]]:
        """从消息中提取图片"""
        images = []

        if not hasattr(message, 'content'):
            return images

        content = message.content
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    # 格式 1: 文件上传的图片
                    if item.get('type') == 'file':
                        if item.get('mime_type', '').startswith('image/'):
                            images.append(item)

                    # 格式 2: 前端直接上传的图片（image_url 格式）
                    elif item.get('type') == 'image_url':
                        images.append(item)

        return images
    
    @staticmethod
    def _build_multimodal_message(text: str, images: List[Dict[str, Any]]) -> HumanMessage:
        """构建多模态消息"""
        content = [{"type": "text", "text": text}]

        for image in images:
            # 格式 1: 文件上传的图片（需要转换为 data URL）
            if image.get('type') == 'file':
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{image.get('mime_type', 'image/png')};base64,{image.get('data', '')}"
                    }
                })

            # 格式 2: 前端直接上传的图片（已经是 image_url 格式）
            elif image.get('type') == 'image_url':
                content.append(image)

        return HumanMessage(content=content)
    
    def process(self, messages: List[Any]) -> str:
        """处理图片对话"""
        logger.info("处理图片对话")

        if not messages:
            return "没有消息"

        last_message = messages[-1]
        images = self._extract_images_from_message(last_message)

        if not images:
            logger.warning("未找到图片")
            return "未找到图片"

        logger.info(f"找到 {len(images)} 张图片")

        # 获取文本内容
        text_content = ""
        if hasattr(last_message, 'content') and isinstance(last_message.content, list):
            for item in last_message.content:
                if isinstance(item, dict) and item.get('type') == 'text':
                    text_content = item.get('text', '')
                    break

        # 如果没有文本内容，使用默认提示
        if not text_content:
            text_content = "请分析这张图片"

        logger.info(f"文本内容: {text_content}")

        # 构建多模态消息
        multimodal_message = self._build_multimodal_message(text_content, images)

        logger.info(f"多模态消息已构建，包含 {len(images)} 张图片")

        # 调用 LLM
        response = self.llm.invoke([multimodal_message])

        logger.info(f"图片处理完成，响应长度: {len(response.content)}")
        return response.content


class PDFProcessor(BaseProcessor):
    """PDF 处理器"""
    
    processor_type = ProcessorType.PDF
    model_name = "gpt-4o"
    
    @staticmethod
    def _decode_base64_to_pdf(base64_data: str, filename: str) -> str:
        """将 base64 数据转换为 PDF 文件"""
        try:
            pdf_data = base64.b64decode(base64_data)
            temp_file = tempfile.NamedTemporaryFile(
                suffix=".pdf",
                delete=False,
                prefix=Path(filename).stem
            )
            temp_file.write(pdf_data)
            temp_file.close()
            logger.info(f"PDF 文件已保存到: {temp_file.name}")
            return temp_file.name
        except Exception as e:
            logger.error(f"PDF 解码失败: {e}")
            raise
    
    @staticmethod
    def _extract_pdf_text(pdf_path: str) -> str:
        """提取 PDF 文本"""
        try:
            import pymupdf4llm
            md_text = pymupdf4llm.to_markdown(pdf_path)
            logger.info(f"PDF 文本提取完成")
            return md_text
        except Exception as e:
            logger.error(f"PDF 文本提取失败: {e}")
            return ""
    
    @staticmethod
    def _extract_pdf_images(pdf_path: str) -> List[Dict[str, Any]]:
        """从 PDF 中提取图片"""
        try:
            import fitz
            images = []
            doc = fitz.open(pdf_path)

            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)

                    # 转换为 base64
                    img_data = pix.tobytes("png")
                    img_base64 = base64.b64encode(img_data).decode('utf-8')

                    images.append({
                        "page": page_num + 1,
                        "index": img_index,
                        "base64": img_base64,
                        "mime_type": "image/png"
                    })

            doc.close()
            logger.info(f"从 PDF 中提取了 {len(images)} 张图片")
            return images
        except Exception as e:
            logger.error(f"PDF 图片提取失败: {e}")
            return []

    @staticmethod
    def _analyze_images_with_multimodal(llm, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """使用多模态 LLM (GPT-4O) 分析提取的图片"""
        try:
            analysis_results = []

            for img_info in images:
                try:
                    # 构建多模态消息
                    message = HumanMessage(
                        content=[
                            {
                                "type": "text",
                                "text": "请分析这张图片的内容，提供详细的描述。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_info['base64']}"
                                }
                            }
                        ]
                    )

                    # 调用 GPT-4O 进行分析
                    response = llm.invoke([message])
                    analysis_text = response.content

                    result = {
                        "page": img_info["page"],
                        "index": img_info["index"],
                        "analysis": analysis_text
                    }
                    analysis_results.append(result)

                    logger.info(f"第 {img_info['page']} 页第 {img_info['index']} 张图片分析完成")

                except Exception as e:
                    logger.error(f"分析图片失败 (第 {img_info['page']} 页): {e}")
                    continue

            logger.info(f"共分析了 {len(analysis_results)} 张图片")
            return analysis_results

        except Exception as e:
            logger.error(f"多模态图片分析失败: {e}")
            return []
    
    def process(self, messages: List[Any]) -> str:
        """处理 PDF 对话"""
        logger.info("处理 PDF 对话")

        if not messages:
            return "没有消息"

        last_message = messages[-1]

        # 提取 PDF 数据
        pdf_data = None
        pdf_filename = "document.pdf"

        if hasattr(last_message, 'content') and isinstance(last_message.content, list):
            for item in last_message.content:
                if isinstance(item, dict) and item.get('type') == 'file':
                    mime_type = item.get('mime_type', '')
                    filename = item.get('metadata', {}).get('filename', '')

                    # 方法 1: 通过 MIME 类型检测
                    is_pdf_by_mime = (mime_type == 'application/pdf' or
                                     mime_type.startswith('application/pdf'))

                    # 方法 2: 通过文件名检测（后备方案）
                    is_pdf_by_filename = filename.lower().endswith('.pdf')

                    if is_pdf_by_mime or is_pdf_by_filename:
                        pdf_data = item.get('data')
                        pdf_filename = filename or 'document.pdf'

                        if is_pdf_by_filename and not is_pdf_by_mime:
                            logger.info(f"通过文件名检测到 PDF: {filename}")

                        break

        if not pdf_data:
            logger.warning("未找到 PDF 数据")
            return "未找到 PDF 数据"

        # 解码并保存 PDF
        pdf_path = self._decode_base64_to_pdf(pdf_data, pdf_filename)

        try:
            # 提取文本
            pdf_text = self._extract_pdf_text(pdf_path)
            logger.info(f"PDF 文本提取完成")

            # 提取图片
            images = self._extract_pdf_images(pdf_path)
            logger.info(f"提取到 {len(images)} 张图片")

            # 使用多模态 LLM 分析图片
            image_analysis = []
            if images:
                image_analysis = self._analyze_images_with_multimodal(self.llm, images)

            # 构建 PDF 处理结果文本
            pdf_summary = f"[PDF 文件: {pdf_filename}]\n"
            pdf_summary += f"提取的文本内容:\n{pdf_text}\n"

            if image_analysis:
                pdf_summary += f"\n图片分析结果:\n"
                for analysis in image_analysis:
                    pdf_summary += f"- 第 {analysis['page']} 页图片 {analysis['index']}: {analysis['analysis']}\n"

            # 构建最终消息
            message = HumanMessage(content=pdf_summary)

            # 调用 LLM 进行最终总结
            response = self.llm.invoke([message])

            logger.info(f"PDF 处理完成，响应长度: {len(response.content)}")
            return response.content

        finally:
            # 清理临时文件
            try:
                Path(pdf_path).unlink()
                logger.info(f"临时文件已删除: {pdf_path}")
            except Exception as e:
                logger.warning(f"删除临时文件失败: {e}")


class TextProcessor(BaseProcessor):
    """文本处理器"""

    processor_type = ProcessorType.TEXT
    model_name = "deepseek-chat"

    @staticmethod
    def _clean_messages_for_text_model(messages: List[Any]) -> List[Any]:
        """
        清理消息，移除不支持的多模态内容
        文本模型只支持文本内容
        """
        cleaned_messages = []

        for message in messages:
            if hasattr(message, 'content') and isinstance(message.content, list):
                # 提取文本内容
                text_parts = []
                for item in message.content:
                    if isinstance(item, dict):
                        if item.get('type') == 'text':
                            text_parts.append(item.get('text', ''))
                        elif item.get('type') == 'file':
                            # 对于文件，添加文件名提示
                            filename = item.get('metadata', {}).get('filename', '文件')
                            text_parts.append(f"[上传的文件: {filename}]")

                # 如果有文本内容，创建新消息
                if text_parts:
                    combined_text = '\n'.join(text_parts)
                    new_message = HumanMessage(content=combined_text)
                    cleaned_messages.append(new_message)
            else:
                # 保留非列表内容的消息
                cleaned_messages.append(message)

        return cleaned_messages

    def process(self, messages: List[Any]) -> str:
        """处理普通文本对话"""
        logger.info("处理普通文本对话")

        if not messages:
            return "没有消息"

        # 清理消息，移除不支持的多模态内容
        cleaned_messages = self._clean_messages_for_text_model(messages)

        # 调用 LLM
        response = self.llm.invoke(cleaned_messages)

        logger.info(f"文本处理完成，响应长度: {len(response.content)}")
        return response.content


# 处理器工厂
class ProcessorFactory:
    """处理器工厂"""
    
    _processors = {
        FileType.IMAGE: ImageProcessor,
        FileType.PDF: PDFProcessor,
        FileType.TEXT: TextProcessor,
    }
    
    @classmethod
    def create_processor(cls, file_type: FileType) -> BaseProcessor:
        """创建处理器"""
        processor_class = cls._processors.get(file_type)
        if not processor_class:
            logger.warning(f"未知的文件类型: {file_type}")
            return TextProcessor()
        return processor_class()
    
    @classmethod
    def register_processor(cls, file_type: FileType, processor_class):
        """注册处理器"""
        cls._processors[file_type] = processor_class
        logger.info(f"处理器已注册: {file_type} -> {processor_class.__name__}")

