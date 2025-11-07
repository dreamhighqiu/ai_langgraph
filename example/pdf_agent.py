"""
文件 RAG 调试脚本
用于测试 Agent 中间件功能
可以被 LangGraph API 加载
"""

import logging
import base64
import tempfile
import os
from typing import Optional, List, Dict, Any
from pathlib import Path

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langchain_core.runnables import RunnableConfig, Runnable
from langchain_core.messages import HumanMessage
from langchain_pymupdf4llm import PyMuPDF4LLMLoader

from llm import create_llm

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 LLM 实例
llm_gpt = create_llm(
    model="gpt-4o",
)

llm_deepseek = create_llm(
    model="deepseek-chat",
)


def _decode_base64_to_pdf(base64_data: str, filename: str = "temp.pdf") -> str:
    """
    将 base64 编码的数据转换为 PDF 文件

    参数:
        base64_data: base64 编码的 PDF 数据
        filename: 输出文件名

    返回:
        PDF 文件的临时路径
    """
    try:
        # 解码 base64 数据
        pdf_bytes = base64.b64decode(base64_data)

        # 创建临时文件
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, filename)

        # 写入 PDF 文件
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)

        logger.info(f"PDF 文件已保存到: {pdf_path}")
        return pdf_path
    except Exception as e:
        logger.error(f"解码 base64 PDF 失败: {e}")
        raise


def _extract_pdf_content(pdf_path: str) -> Dict[str, Any]:
    """
    使用 PyMuPDF4LLM 提取 PDF 内容（文本和图片）

    参数:
        pdf_path: PDF 文件路径

    返回:
        包含文本和图片的字典
    """
    try:
        # 使用 PyMuPDF4LLMLoader 加载 PDF
        loader = PyMuPDF4LLMLoader(pdf_path)
        docs = loader.load()

        # 提取文本内容
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
    """
    从 PDF 中提取图片

    参数:
        pdf_path: PDF 文件路径

    返回:
        包含图片信息的列表
    """
    try:
        import fitz  # PyMuPDF

        images = []
        pdf_document = fitz.open(pdf_path)

        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                xref = img[0]
                pix = fitz.Pixmap(pdf_document, xref)

                # 转换为 base64
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


def _analyze_images_with_multimodal(images: List[Dict[str, Any]]) -> List[str]:
    """
    使用多模态 LLM (GPT-4O) 分析提取的图片

    参数:
        images: 包含图片信息的列表

    返回:
        图片分析结果列表
    """
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
                response = llm_gpt.invoke([message])
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


def _process_pdf_middleware(state: AgentState, runtime) -> None:
    """
    在模型调用前的中间件
    处理上传的 PDF 文件，提取文本和图片内容
    将 PDF 文件块替换为提取的文本内容

    参数:
        state: Agent 状态
        runtime: 运行时对象
    """
    logger.info("中间件执行: 模型调用前")
    logger.info(f"当前消息数: {len(state.get('messages', []))}")

    messages = state.get('messages', [])
    modified_messages = []

    # 处理每条消息
    for message in messages:
        if isinstance(message, HumanMessage) and isinstance(message.content, list):
            # 处理消息内容块
            new_content = []
            pdf_found = False

            for content_block in message.content:
                # 检查是否为 PDF 文件
                if (isinstance(content_block, dict) and
                    content_block.get('type') == 'file' and
                    content_block.get('source_type') == 'base64' and
                    content_block.get('mime_type') == 'application/pdf'):

                    logger.info("检测到 PDF 文件，开始处理...")
                    pdf_found = True

                    try:
                        # 获取 base64 数据和文件名
                        base64_data = content_block.get('data', '')
                        filename = content_block.get('metadata', {}).get('filename', 'document.pdf')

                        # 转换 base64 为 PDF 文件
                        pdf_path = _decode_base64_to_pdf(base64_data, filename)

                        # 提取 PDF 文本内容
                        pdf_content = _extract_pdf_content(pdf_path)
                        text_content = pdf_content['text']
                        logger.info(f"PDF 文本提取完成，共 {pdf_content['pages']} 页")

                        # 提取 PDF 中的图片
                        images = _extract_images_from_pdf(pdf_path)
                        logger.info(f"提取到 {len(images)} 张图片")

                        # 使用多模态 LLM 分析图片
                        image_analysis = []
                        if images:
                            image_analysis = _analyze_images_with_multimodal(images)

                        # 构建 PDF 处理结果文本
                        pdf_summary = f"[PDF 文件: {filename}]\n"
                        pdf_summary += f"页数: {pdf_content['pages']}\n"
                        pdf_summary += f"提取的文本内容:\n{text_content}\n"

                        if image_analysis:
                            pdf_summary += f"\n图片分析结果:\n"
                            for analysis in image_analysis:
                                pdf_summary += f"- 第 {analysis['page']} 页图片 {analysis['index']}: {analysis['analysis']}\n"

                        # 将 PDF 文件块替换为文本块
                        new_content.append({
                            "type": "text",
                            "text": pdf_summary
                        })

                        # 清理临时文件
                        if os.path.exists(pdf_path):
                            os.remove(pdf_path)
                            logger.info(f"临时文件已删除: {pdf_path}")

                    except Exception as e:
                        logger.error(f"处理 PDF 文件失败: {e}")
                        # 如果处理失败，添加错误信息
                        new_content.append({
                            "type": "text",
                            "text": f"[PDF 处理失败: {str(e)}]"
                        })
                else:
                    # 保留其他内容块
                    new_content.append(content_block)

            # 如果找到了 PDF，创建新的消息对象
            if pdf_found:
                modified_message = HumanMessage(content=new_content)
                modified_messages.append(modified_message)
            else:
                modified_messages.append(message)
        else:
            # 保留非 HumanMessage 或非列表内容的消息
            modified_messages.append(message)

    # 更新 state 中的消息
    state['messages'] = modified_messages
    logger.info("消息处理完成")

    return None


# 创建一个自定义的 runnable 来包装 LLM，处理 PDF 消息
class PDFProcessingRunnable(Runnable):
    """
    包装 LLM 的 Runnable，在调用前处理 PDF 消息
    """

    def __init__(self, llm):
        self.llm = llm

    def invoke(self, input, config=None):
        """处理输入并调用 LLM"""
        # 如果输入是消息列表，处理 PDF
        if isinstance(input, list):
            messages = input
            processed_messages = self._process_messages(messages)
            return self.llm.invoke(processed_messages, config)
        return self.llm.invoke(input, config)

    def _process_messages(self, messages):
        """处理消息中的 PDF 文件"""
        processed = []
        for message in messages:
            if isinstance(message, HumanMessage) and isinstance(message.content, list):
                new_content = []
                for block in message.content:
                    if (isinstance(block, dict) and
                        block.get('type') == 'file' and
                        block.get('source_type') == 'base64' and
                        block.get('mime_type') == 'application/pdf'):
                        # 处理 PDF
                        try:
                            base64_data = block.get('data', '')
                            filename = block.get('metadata', {}).get('filename', 'document.pdf')
                            pdf_path = _decode_base64_to_pdf(base64_data, filename)
                            pdf_content = _extract_pdf_content(pdf_path)
                            images = _extract_images_from_pdf(pdf_path)

                            pdf_summary = f"[PDF 文件: {filename}]\n"
                            pdf_summary += f"页数: {pdf_content['pages']}\n"
                            pdf_summary += f"提取的文本内容:\n{pdf_content['text']}\n"

                            if images:
                                image_analysis = _analyze_images_with_multimodal(images)
                                if image_analysis:
                                    pdf_summary += f"\n图片分析结果:\n"
                                    for analysis in image_analysis:
                                        pdf_summary += f"- 第 {analysis['page']} 页图片 {analysis['index']}: {analysis['analysis']}\n"

                            new_content.append({"type": "text", "text": pdf_summary})

                            if os.path.exists(pdf_path):
                                os.remove(pdf_path)
                        except Exception as e:
                            logger.error(f"处理 PDF 失败: {e}")
                            new_content.append({"type": "text", "text": f"[PDF 处理失败: {str(e)}]"})
                    else:
                        new_content.append(block)

                processed.append(HumanMessage(content=new_content))
            else:
                processed.append(message)

        return processed

    @property
    def InputType(self):
        return self.llm.InputType

    @property
    def OutputType(self):
        return self.llm.OutputType


# 为 Agent 创建装饰的中间件
add_messages_middleware = before_model(_process_pdf_middleware)

# 使用 PDF 处理 runnable 包装 LLM
llm_deepseek_with_pdf = PDFProcessingRunnable(llm_deepseek)

agent_pdf = create_agent(
        model=llm_deepseek_with_pdf,
        tools=[],
        middleware=[add_messages_middleware],
    )
    