"""
多模态对话系统中间件模块 - 新架构

为每种对话类型提供专门的中间件
- 图片对话中间件: 处理图片内容
- PDF 对话中间件: 处理 PDF 文件
- 文本对话中间件: 处理普通文本
"""

import logging
import base64
import tempfile
import os
from typing import Any, Dict, List

from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from langchain_core.messages import HumanMessage
from langchain_pymupdf4llm import PyMuPDF4LLMLoader
import fitz

logger = logging.getLogger(__name__)


# ============================================================================
# 图片对话中间件
# ============================================================================

@before_model
def image_chat_middleware(state: AgentState, runtime) -> None:
    """
    图片对话中间件

    处理图片消息，提取图片内容并准备传递给 GPT-4O
    支持图片 URL 和图片文件两种格式
    """
    logger.info("=" * 60)
    logger.info("📸 中间件: 图片对话处理")
    logger.info("=" * 60)

    messages = state.get('messages', [])
    logger.info(f"当前消息数: {len(messages)}")

    if not messages:
        logger.warning("没有消息")
        return None

    modified_messages = []

    # 处理每条消息
    for message in messages:
        if isinstance(message, HumanMessage) and isinstance(message.content, list):
            logger.info("检测到多模态消息，准备处理图片...")
            new_content = []
            image_found = False

            for item in message.content:
                if isinstance(item, dict):
                    # 处理图片 URL
                    if item.get('type') == 'image_url':
                        logger.info("✅ 检测到图片 URL")
                        new_content.append(item)
                        image_found = True
                    # 处理图片文件
                    elif (item.get('type') == 'file' and
                          item.get('mime_type', '').startswith('image/')):
                        logger.info(f"✅ 检测到图片文件: {item.get('mime_type')}")

                        try:
                            # 如果是 base64 编码的图片，转换为 image_url 格式
                            if item.get('data'):
                                image_url = f"data:{item.get('mime_type')};base64,{item.get('data')}"
                                new_content.append({
                                    "type": "image_url",
                                    "image_url": {"url": image_url}
                                })
                                logger.info("✅ 图片文件已转换为 URL 格式")
                            else:
                                new_content.append(item)
                        except Exception as e:
                            logger.error(f"处理图片文件失败: {e}")
                            new_content.append(item)

                        image_found = True
                    else:
                        new_content.append(item)
                else:
                    new_content.append(item)

            if image_found:
                modified_message = HumanMessage(content=new_content)
                modified_messages.append(modified_message)
            else:
                modified_messages.append(message)
        else:
            modified_messages.append(message)

    # 更新 state 中的消息
    state['messages'] = modified_messages
    logger.info("=" * 60)
    return None


# ============================================================================
# PDF 对话中间件
# ============================================================================

def _decode_base64_to_pdf(base64_data: str, filename: str = "temp.pdf") -> str:
    """将 base64 编码的数据转换为 PDF 文件"""
    try:
        pdf_bytes = base64.b64decode(base64_data)
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        logger.info(f"PDF 文件已保存到: {pdf_path}")
        return pdf_path
    except Exception as e:
        logger.error(f"解码 base64 PDF 失败: {e}")
        raise


def _extract_pdf_content(pdf_path: str) -> Dict[str, Any]:
    """使用 PyMuPDF4LLM 提取 PDF 内容"""
    try:
        loader = PyMuPDF4LLMLoader(pdf_path)
        docs = loader.load()
        
        text_content = "\n".join([doc.page_content for doc in docs])
        
        logger.info(f"PDF 文本提取完成，共 {len(docs)} 页")
        
        return {
            "text": text_content,
            "pages": len(docs),
            "documents": docs
        }
    except Exception as e:
        logger.error(f"提取 PDF 内容失败: {e}")
        raise


def _extract_images_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """从 PDF 中提取图片"""
    try:
        images = []
        pdf_document = fitz.open(pdf_path)
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                pix = fitz.Pixmap(pdf_document, xref)
                
                img_data = pix.tobytes("png")
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                
                images.append({
                    "page": page_num + 1,
                    "index": img_index,
                    "base64": img_base64,
                    "mime_type": "image/png"
                })
        
        pdf_document.close()
        logger.info(f"从 PDF 中提取了 {len(images)} 张图片")
        return images
    except Exception as e:
        logger.error(f"提取 PDF 图片失败: {e}")
        return []


@before_model
def pdf_chat_middleware(state: AgentState, runtime) -> None:
    """
    PDF 对话中间件
    
    处理 PDF 文件，提取文本和图片内容
    """
    logger.info("=" * 60)
    logger.info("📄 中间件: PDF 对话处理")
    logger.info("=" * 60)
    
    messages = state.get('messages', [])
    logger.info(f"当前消息数: {len(messages)}")
    
    if not messages:
        logger.warning("没有消息")
        return None
    
    modified_messages = []
    
    for message in messages:
        if isinstance(message, HumanMessage) and isinstance(message.content, list):
            new_content = []
            pdf_found = False
            
            for content_block in message.content:
                # 检查是否为 PDF 文件
                if (isinstance(content_block, dict) and
                    content_block.get('type') == 'file' and
                    content_block.get('mime_type') == 'application/pdf'):

                    logger.info("检测到 PDF 文件，开始处理...")
                    pdf_found = True

                    try:
                        base64_data = content_block.get('data', '')
                        filename = content_block.get('metadata', {}).get('filename', 'document.pdf')

                        # 转换 base64 为 PDF 文件
                        pdf_path = _decode_base64_to_pdf(base64_data, filename)

                        # 提取 PDF 文本内容
                        pdf_content = _extract_pdf_content(pdf_path)
                        text_content = pdf_content['text']

                        # 提取 PDF 中的图片
                        images = _extract_images_from_pdf(pdf_path)

                        # 构建 PDF 处理结果文本
                        pdf_summary = f"[PDF 文件: {filename}]\n"
                        pdf_summary += f"页数: {pdf_content['pages']}\n"
                        pdf_summary += f"提取的文本内容:\n{text_content}\n"

                        if images:
                            pdf_summary += f"\n图片数量: {len(images)}\n"
                            for img_info in images:
                                pdf_summary += f"  - 第 {img_info['page']} 页图片 {img_info['index']}\n"

                        new_content.append({
                            "type": "text",
                            "text": pdf_summary
                        })

                        # 清理临时文件
                        if os.path.exists(pdf_path):
                            os.remove(pdf_path)
                            logger.info(f"临时文件已删除: {pdf_path}")

                        logger.info("✅ PDF 处理完成")

                    except Exception as e:
                        logger.error(f"处理 PDF 文件失败: {e}")
                        new_content.append({
                            "type": "text",
                            "text": f"[PDF 处理失败: {str(e)}]"
                        })
                else:
                    # 保留其他内容块
                    new_content.append(content_block)
            
            if pdf_found:
                modified_message = HumanMessage(content=new_content)
                modified_messages.append(modified_message)
            else:
                modified_messages.append(message)
        else:
            modified_messages.append(message)
    
    # 更新 state 中的消息
    state['messages'] = modified_messages
    logger.info("=" * 60)
    
    return None


# ============================================================================
# 文本对话中间件
# ============================================================================

@before_model
def text_chat_middleware(state: AgentState, runtime) -> None:
    """
    文本对话中间件
    
    处理普通文本消息
    """
    logger.info("=" * 60)
    logger.info("📝 中间件: 文本对话处理")
    logger.info("=" * 60)
    
    messages = state.get('messages', [])
    logger.info(f"当前消息数: {len(messages)}")
    
    if not messages:
        logger.warning("没有消息")
        return None
    
    # 获取最后一条消息
    last_message = messages[-1]
    
    if isinstance(last_message, HumanMessage):
        if isinstance(last_message.content, str):
            logger.info(f"✅ 检测到文本消息，长度: {len(last_message.content)}")
        elif isinstance(last_message.content, list):
            logger.info(f"✅ 检测到列表消息，项数: {len(last_message.content)}")
    
    logger.info("=" * 60)
    return None

