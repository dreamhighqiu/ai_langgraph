"""
PDF 处理工具模块

功能：
1. 将 base64 编码的 PDF 转换为文件
2. 提取 PDF 文本内容
3. 从 PDF 中提取图片
4. 使用多模态 LLM 分析图片
"""
import logging
import base64
import tempfile
import os
from typing import Optional, List, Dict, Any

from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


def decode_base64_to_pdf(base64_data: str, filename: str = "temp.pdf") -> str:
    """
    将 base64 编码的数据转换为 PDF 文件

    Args:
        base64_data: base64 编码的 PDF 数据
        filename: 输出文件名

    Returns:
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


def extract_pdf_content(pdf_path: str) -> Dict[str, Any]:
    """
    使用 PyMuPDF4LLM 提取 PDF 内容（文本和图片）

    Args:
        pdf_path: PDF 文件路径

    Returns:
        包含文本和图片的字典
    """
    try:
        # 延迟导入 PyMuPDF4LLMLoader
        from langchain_pymupdf4llm import PyMuPDF4LLMLoader

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


def extract_images_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    从 PDF 中提取图片

    Args:
        pdf_path: PDF 文件路径

    Returns:
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


def analyze_images_with_multimodal(images: List[Dict[str, Any]], llm) -> List[str]:
    """
    使用多模态 LLM 分析提取的图片

    Args:
        images: 包含图片信息的列表
        llm: 多模态 LLM 实例

    Returns:
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

                # 调用多模态 LLM 进行分析
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


def process_pdf_file(base64_data: str, filename: str, llm) -> Dict[str, Any]:
    """
    完整的 PDF 处理流程

    Args:
        base64_data: base64 编码的 PDF 数据
        filename: PDF 文件名
        llm: 多模态 LLM 实例

    Returns:
        包含 PDF 处理结果的字典
    """
    pdf_path = None
    try:
        # 1. 转换 base64 为 PDF 文件
        pdf_path = decode_base64_to_pdf(base64_data, filename)

        # 2. 提取 PDF 文本内容
        pdf_content = extract_pdf_content(pdf_path)
        text_content = pdf_content['text']
        logger.info(f"PDF 文本提取完成，共 {pdf_content['pages']} 页")

        # 3. 提取 PDF 中的图片
        images = extract_images_from_pdf(pdf_path)
        logger.info(f"提取到 {len(images)} 张图片")

        # 4. 使用多模态 LLM 分析图片
        image_analysis = []
        if images:
            image_analysis = analyze_images_with_multimodal(images, llm)

        # 5. 构建 PDF 处理结果
        pdf_summary = f"[PDF 文件: {filename}]\n"
        pdf_summary += f"页数: {pdf_content['pages']}\n"
        pdf_summary += f"提取的文本内容:\n{text_content}\n"

        if image_analysis:
            pdf_summary += f"\n图片分析结果:\n"
            for analysis in image_analysis:
                pdf_summary += f"- 第 {analysis['page']} 页图片 {analysis['index']}: {analysis['analysis']}\n"

        return {
            "success": True,
            "filename": filename,
            "pages": pdf_content['pages'],
            "text": text_content,
            "images": len(images),
            "image_analysis": image_analysis,
            "summary": pdf_summary
        }

    except Exception as e:
        logger.error(f"处理 PDF 文件失败: {e}")
        return {
            "success": False,
            "filename": filename,
            "error": str(e),
            "summary": f"[PDF 处理失败: {str(e)}]"
        }

    finally:
        # 清理临时文件
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
                logger.info(f"临时文件已删除: {pdf_path}")
            except Exception as e:
                logger.warning(f"删除临时文件失败: {e}")

