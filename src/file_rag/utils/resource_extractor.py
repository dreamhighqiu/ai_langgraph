"""
资源提取器模块 - 统一的图片和PDF资源提取接口

功能：
1. 从消息中提取图片资源
2. 从消息中提取PDF资源
3. 从extracted_content中提取资源
4. 统一的资源信息格式
"""

from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage


def extract_image_from_messages(messages: list) -> Optional[Dict[str, Any]]:
    """
    从消息中提取第一张图片

    返回格式：
    {
        'base64': 'base64_encoded_data',
        'mime_type': 'image/png',
        'filename': 'image.png',
        'source': 'messages'
    }

    支持多种格式：
    1. HumanMessage 对象（content 为列表）
    2. HumanMessage 对象（content 为字符串，尝试从其他属性获取）
    3. 字典格式的消息（来自LangGraph Server）
    4. file类型的图片
    5. image_url类型的图片
    6. image类型的图片
    """
    for msg_idx, message in enumerate(messages):
        # 获取消息内容
        content = None

        # 处理 HumanMessage 对象
        if isinstance(message, HumanMessage):
            content = message.content
            # 如果 content 是字符串，尝试从其他属性获取
            if isinstance(content, str):
                if hasattr(message, '_content_blocks'):
                    content = message._content_blocks
                elif hasattr(message, 'content_blocks'):
                    content = message.content_blocks
                else:
                    continue

        # 处理字典格式的消息
        elif isinstance(message, dict) and message.get('type') == 'human':
            content = message.get('content', [])

        # 如果没有内容，跳过
        if not isinstance(content, list):
            continue

        # 遍历内容块
        for content_block in content:
            if not isinstance(content_block, dict):
                continue

            # 方案1：file类型的图片
            if (content_block.get('type') == 'file' and
                content_block.get('source_type') == 'base64' and
                'image' in content_block.get('mime_type', '')):

                return {
                    'base64': content_block.get('data', ''),
                    'mime_type': content_block.get('mime_type', 'image/png'),
                    'filename': content_block.get('metadata', {}).get('filename', 'image.png'),
                    'source': 'messages_file'
                }

            # 方案2：image_url类型的图片
            if content_block.get('type') == 'image_url':
                image_url = content_block.get('image_url', {}).get('url', '')
                if 'base64,' in image_url:
                    base64_data = image_url.split('base64,')[1]
                    mime_type = image_url.split(';')[0].replace('data:', '')

                    return {
                        'base64': base64_data,
                        'mime_type': mime_type,
                        'filename': content_block.get('image_url', {}).get('metadata', {}).get('name', 'image.png'),
                        'source': 'messages_url'
                    }

            # 方案3：image类型的图片（直接包含base64数据）
            if content_block.get('type') == 'image':
                image_data = content_block.get('image', {})
                if isinstance(image_data, dict):
                    base64_data = image_data.get('base64', '')
                    if base64_data:
                        return {
                            'base64': base64_data,
                            'mime_type': image_data.get('mime_type', 'image/png'),
                            'filename': image_data.get('filename', 'image.png'),
                            'source': 'messages_image'
                        }

    return None


def extract_pdf_from_messages(messages: list) -> Optional[Dict[str, Any]]:
    """
    从消息中提取PDF文件

    返回格式：
    {
        'base64': 'base64_encoded_data',
        'filename': 'document.pdf',
        'source': 'messages'
    }

    支持两种格式：
    1. HumanMessage 对象
    2. 字典格式的消息（来自LangGraph Server）
    """
    print(f"[extract_pdf_from_messages] 开始提取PDF，消息数: {len(messages)}")

    for msg_idx, message in enumerate(messages):
        content = None
        msg_type_str = "unknown"

        # 处理 HumanMessage 对象
        if isinstance(message, HumanMessage):
            msg_type_str = "HumanMessage"
            print(f"[extract_pdf_from_messages] 消息 {msg_idx}: HumanMessage 对象")
            content = message.content
        # 处理字典格式的消息（LangGraph Server 传递的格式）
        elif isinstance(message, dict):
            msg_type = message.get('type', '')
            msg_type_str = f"dict(type={msg_type})"
            print(f"[extract_pdf_from_messages] 消息 {msg_idx}: dict 格式，type={msg_type}")
            # 检查消息类型（可能是 'human' 或其他值）
            if msg_type == 'human' or msg_type == '':
                content = message.get('content', [])
        else:
            msg_type_str = type(message).__name__
            print(f"[extract_pdf_from_messages] 消息 {msg_idx}: 未知类型 {msg_type_str}，跳过")
            continue

        # 如果没有内容或内容不是列表，跳过
        if not isinstance(content, list):
            print(f"[extract_pdf_from_messages] 消息 {msg_idx} ({msg_type_str}): 内容不是列表 (类型: {type(content).__name__})，跳过")
            continue

        print(f"[extract_pdf_from_messages] 消息 {msg_idx} ({msg_type_str}): 内容是列表，长度 {len(content)}")

        # 遍历内容块查找PDF
        for block_idx, content_block in enumerate(content):
            if not isinstance(content_block, dict):
                print(f"[extract_pdf_from_messages]   块 {block_idx}: 不是dict (类型: {type(content_block).__name__})，跳过")
                continue

            block_type = content_block.get('type', '')
            mime_type = content_block.get('mime_type', '')
            source_type = content_block.get('source_type', '')
            print(f"[extract_pdf_from_messages]   块 {block_idx}: type={block_type}, mime_type={mime_type}, source_type={source_type}")

            # 检查是否是PDF文件
            if (content_block.get('type') == 'file' and
                content_block.get('mime_type') == 'application/pdf'):

                # 获取base64数据
                base64_data = content_block.get('data', '')
                print(f"[extract_pdf_from_messages]   ✅ 找到PDF文件，base64长度: {len(base64_data)}")

                # 如果没有base64数据，跳过
                if not base64_data:
                    print(f"[extract_pdf_from_messages]   ⚠️ base64数据为空，跳过")
                    continue

                # 获取文件名
                filename = content_block.get('metadata', {}).get('filename', 'document.pdf')
                if not filename or filename == 'document.pdf':
                    # 尝试从其他字段获取文件名
                    filename = content_block.get('filename', 'document.pdf')

                print(f"[extract_pdf_from_messages]   ✅ 成功提取PDF: {filename}")
                return {
                    'base64': base64_data,
                    'filename': filename,
                    'source': 'messages'
                }

    print(f"[extract_pdf_from_messages] ❌ 未找到PDF文件")
    return None


def extract_image_from_extracted_content(extracted_content: str) -> Optional[Dict[str, Any]]:
    """
    从extracted_content中提取图片信息

    支持两种格式：
    1. Base64 data URL: data:image/png;base64,iVBORw0KGgo...
    2. 图片分析结果文本
    """
    if not extracted_content:
        return None

    # 方案1：检查是否是base64 data URL
    if extracted_content.startswith('data:image'):
        if 'base64,' in extracted_content:
            try:
                base64_data = extracted_content.split('base64,')[1].split('\n')[0]
                mime_type = extracted_content.split(';')[0].replace('data:', '')
                
                return {
                    'base64': base64_data,
                    'mime_type': mime_type,
                    'filename': 'extracted_image.png',
                    'source': 'extracted_content_url',
                    'is_analysis': False
                }
            except Exception as e:
                print(f"[资源提取] 解析base64 data URL失败: {e}")
                return None

    # 方案2：检查是否是图片分析结果
    # 如果extracted_content包含图片分析的关键词，则认为是分析结果
    analysis_keywords = ['图片', '界面', '元素', '功能', '交互', '布局', '内容', '分析']
    if any(keyword in extracted_content for keyword in analysis_keywords):
        return {
            'analysis': extracted_content,
            'source': 'extracted_content_analysis',
            'is_analysis': True
        }

    return None


def extract_pdf_metadata(messages: list) -> Optional[Dict[str, Any]]:
    """
    从消息中提取PDF的元数据（不包括base64数据）

    返回格式：
    {
        'filename': 'document.pdf',
        'mime_type': 'application/pdf',
        'has_data': True/False
    }
    """
    for message in messages:
        if isinstance(message, HumanMessage) and isinstance(message.content, list):
            for content_block in message.content:
                if (isinstance(content_block, dict) and
                    content_block.get('type') == 'file' and
                    content_block.get('mime_type') == 'application/pdf'):
                    
                    return {
                        'filename': content_block.get('metadata', {}).get('filename', 'document.pdf'),
                        'mime_type': 'application/pdf',
                        'has_data': bool(content_block.get('data', ''))
                    }

    return None


def extract_image_metadata(messages: list) -> Optional[Dict[str, Any]]:
    """
    从消息中提取图片的元数据（不包括base64数据）

    返回格式：
    {
        'filename': 'image.png',
        'mime_type': 'image/png',
        'has_data': True/False,
        'type': 'file' or 'image_url'
    }
    """
    for message in messages:
        if isinstance(message, HumanMessage) and isinstance(message.content, list):
            for content_block in message.content:
                if not isinstance(content_block, dict):
                    continue

                # file类型的图片
                if (content_block.get('type') == 'file' and
                    'image' in content_block.get('mime_type', '')):
                    
                    return {
                        'filename': content_block.get('metadata', {}).get('filename', 'image.png'),
                        'mime_type': content_block.get('mime_type', 'image/png'),
                        'has_data': bool(content_block.get('data', '')),
                        'type': 'file'
                    }

                # image_url类型的图片
                if content_block.get('type') == 'image_url':
                    image_url = content_block.get('image_url', {}).get('url', '')
                    mime_type = image_url.split(';')[0].replace('data:', '') if ';' in image_url else 'image/png'
                    
                    return {
                        'filename': content_block.get('image_url', {}).get('metadata', {}).get('name', 'image.png'),
                        'mime_type': mime_type,
                        'has_data': 'base64,' in image_url,
                        'type': 'image_url'
                    }

    return None


def get_resource_summary(messages: list, extracted_content: str = "") -> Dict[str, Any]:
    """
    获取资源摘要信息

    返回格式：
    {
        'has_image': bool,
        'has_pdf': bool,
        'has_extracted_content': bool,
        'image_info': {...} or None,
        'pdf_info': {...} or None,
        'extracted_content_info': {...} or None
    }
    """
    return {
        'has_image': extract_image_metadata(messages) is not None,
        'has_pdf': extract_pdf_metadata(messages) is not None,
        'has_extracted_content': bool(extracted_content),
        'image_info': extract_image_metadata(messages),
        'pdf_info': extract_pdf_metadata(messages),
        'extracted_content_info': extract_image_from_extracted_content(extracted_content)
    }

