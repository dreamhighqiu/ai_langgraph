"""
PDF 处理工具模块
负责 PDF 文件的内容提取和图片提取
"""
import base64
import tempfile
import os
from langchain_pymupdf4llm import PyMuPDF4LLMLoader


def extract_pdf_images(base64_data: str) -> list:
    """
    从base64编码的PDF数据中提取所有图片

    Args:
        base64_data: base64编码的PDF数据

    Returns:
        图片列表，每个图片是一个base64编码的字符串
    """
    import fitz  # PyMuPDF

    tmp_file_path = None
    images = []

    try:
        # 解码base64数据
        pdf_bytes = base64.b64decode(base64_data)

        # 创建临时文件来保存PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name

        # 打开PDF文件
        pdf_document = fitz.open(tmp_file_path)

        # 遍历每一页
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            image_list = page.get_images()

            print(f"[DEBUG] 第 {page_num + 1} 页找到 {len(image_list)} 张图片")

            # 提取每张图片
            for img_index, img in enumerate(image_list):
                xref = img[0]  # 图片的xref
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]

                # 转换为base64
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                images.append({
                    'page': page_num + 1,
                    'index': img_index + 1,
                    'data': image_base64,
                    'ext': base_image["ext"]  # 图片格式，如 png, jpeg
                })

        pdf_document.close()
        print(f"[DEBUG] 总共提取了 {len(images)} 张图片")

        return images

    except Exception as e:
        print(f"PDF图片提取错误: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        # 确保临时文件被清理
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.unlink(tmp_file_path)
                print(f"[DEBUG] 临时文件已清理: {tmp_file_path}")
            except Exception as cleanup_error:
                print(f"[WARNING] 清理临时文件失败: {cleanup_error}")


def extract_pdf_content(base64_data: str) -> str:
    """
    从base64编码的PDF数据中提取文本内容

    Args:
        base64_data: base64编码的PDF数据

    Returns:
        提取的文本内容（Markdown格式）
    """
    tmp_file_path = None
    try:
        # 解码base64数据
        pdf_bytes = base64.b64decode(base64_data)

        # 创建临时文件来保存PDF
        # 使用 with 语句确保文件句柄被正确关闭
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name
        # 文件句柄在这里已经关闭，Windows 可以访问该文件

        # 使用PyMuPDF4LLM加载和提取内容
        loader = PyMuPDF4LLMLoader(tmp_file_path)
        documents = loader.load()

        # 合并所有页面的内容
        content = "\n\n".join([doc.page_content for doc in documents])

        return content
    except Exception as e:
        print(f"PDF提取错误: {e}")
        import traceback
        traceback.print_exc()
        return f"PDF内容提取失败: {str(e)}"
    finally:
        # 确保临时文件被清理
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.unlink(tmp_file_path)
                print(f"[DEBUG] 临时文件已清理: {tmp_file_path}")
            except Exception as cleanup_error:
                print(f"[WARNING] 清理临时文件失败: {cleanup_error}")

