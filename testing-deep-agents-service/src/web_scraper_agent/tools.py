"""Web Scraper Tools - 网站接口数据抓取与入库工具.

用于从指定网站抓取API接口文档数据，并存入向量数据库（知识库）。
"""

import os
import re
import asyncio
import httpx
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from langchain_core.tools import tool
from bs4 import BeautifulSoup


# 从环境变量获取配置
KNOWLEDGE_API_URL = os.getenv("KNOWLEDGE_API_URL", "http://localhost:9621")


async def _fetch_page_content(url: str, timeout: float = 30.0) -> Optional[str]:
    """获取网页内容。
    
    Args:
        url: 目标URL
        timeout: 超时时间（秒）
    
    Returns:
        网页HTML内容，失败返回None
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            print(f"获取页面失败 {url}: {e}")
            return None


def _extract_api_links(html_content: str, base_url: str) -> List[str]:
    """从HTML内容中提取API文档链接。
    
    Args:
        html_content: HTML内容
        base_url: 基础URL用于拼接相对路径
    
    Returns:
        API文档链接列表
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()
    
    # 查找所有链接
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # 过滤出API相关的链接
        if 'api' in href.lower() or 'server-api' in href.lower():
            full_url = urljoin(base_url, href)
            # 确保是同一域名下的链接
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                links.add(full_url)
    
    return list(links)


def _parse_api_content(html_content: str, url: str) -> Dict[str, Any]:
    """解析API文档页面内容。
    
    Args:
        html_content: HTML内容
        url: 页面URL
    
    Returns:
        解析后的API数据字典
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取标题
    title = ""
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text(strip=True)
    
    # 提取主要内容区域
    content_area = soup.find('div', class_='content') or soup.find('article') or soup.find('main')
    
    if not content_area:
        # 尝试找包含API内容的区域
        content_area = soup.find('div', class_='markdown-body') or soup.find('body')
    
    content_text = ""
    if content_area:
        # 清理内容，移除脚本和样式
        for script in content_area.find_all(['script', 'style']):
            script.decompose()
        
        # 提取文本内容，保留结构
        content_parts = []
        
        # 处理标题
        for tag in content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = int(tag.name[1])
            prefix = '#' * level
            content_parts.append(f"\n{prefix} {tag.get_text(strip=True)}\n")
        
        # 处理段落
        for p in content_area.find_all('p'):
            text = p.get_text(strip=True)
            if text:
                content_parts.append(text)
        
        # 处理代码块
        for code in content_area.find_all(['pre', 'code']):
            code_text = code.get_text()
            if code_text.strip():
                content_parts.append(f"\n```\n{code_text}\n```\n")
        
        # 处理表格
        for table in content_area.find_all('table'):
            table_text = _parse_table(table)
            if table_text:
                content_parts.append(f"\n{table_text}\n")
        
        # 处理列表
        for ul in content_area.find_all(['ul', 'ol']):
            for li in ul.find_all('li'):
                text = li.get_text(strip=True)
                if text:
                    content_parts.append(f"- {text}")
        
        content_text = "\n".join(content_parts)
        
        # 如果提取的内容太少，使用纯文本
        if len(content_text) < 100:
            content_text = content_area.get_text(separator='\n', strip=True)
    
    return {
        "title": title,
        "url": url,
        "content": content_text,
    }


def _parse_table(table) -> str:
    """解析HTML表格为文本格式。
    
    Args:
        table: BeautifulSoup table元素
    
    Returns:
        表格文本表示
    """
    rows = []
    
    # 处理表头
    headers = []
    thead = table.find('thead')
    if thead:
        for th in thead.find_all(['th', 'td']):
            headers.append(th.get_text(strip=True))
    
    # 如果没有thead，尝试从第一行获取
    if not headers:
        first_row = table.find('tr')
        if first_row:
            for cell in first_row.find_all(['th', 'td']):
                headers.append(cell.get_text(strip=True))
    
    if headers:
        rows.append(" | ".join(headers))
        rows.append("-" * 50)
    
    # 处理表格内容
    tbody = table.find('tbody') or table
    for tr in tbody.find_all('tr'):
        cells = []
        for td in tr.find_all(['td', 'th']):
            cells.append(td.get_text(strip=True))
        if cells and cells != headers:
            rows.append(" | ".join(cells))
    
    return "\n".join(rows)


def _format_api_document(api_data: Dict[str, Any], max_content_length: int = 3000) -> str:
    """将API数据格式化为文档文本。
    
    Args:
        api_data: API数据字典
        max_content_length: 单个文档内容最大长度（字符数）
    
    Returns:
        格式化后的文档文本
    """
    parts = []
    
    if api_data.get("title"):
        parts.append(f"# {api_data['title']}")
    
    if api_data.get("url"):
        parts.append(f"\n> 文档来源: {api_data['url']}")
    
    if api_data.get("content"):
        content = api_data['content']
        # 截断过长的内容
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n\n... [内容已截断] ..."
        parts.append(f"\n{content}")
    
    return "\n".join(parts)


@tool
async def scrape_api_documentation(
    start_url: str,
    max_pages: int = 30,
) -> str:
    """从指定网站抓取API接口文档数据。

    此工具会从给定的起始URL开始，抓取网站上的API接口文档内容，
    并对抓取的数据进行整理，输出适合存储到知识库的文档列表。

    工具会自动：
    1. 从起始页面提取所有API相关链接
    2. 遍历抓取每个API页面的详细内容
    3. 解析并整理API接口信息（接口描述、参数、请求/响应示例等）
    4. 返回整理好的文档列表（JSON格式）

    注意：为避免超出LLM上下文限制，工具会自动：
    - 限制最大抓取页面数（默认30页）
    - 截断单个文档过长的内容（每个文档最多3000字符）
    - 返回精简的摘要信息

    Args:
        start_url: 起始URL，通常是API文档的首页或目录页
        max_pages: 最大抓取页面数，默认30，防止过度抓取

    Returns:
        JSON格式的字符串，包含抓取到的API文档列表（精简版）
    """
    import json
    
    results = []
    visited_urls = set()
    urls_to_visit = [start_url]
    
    # 限制最大页面数，避免数据过大
    max_pages = min(max_pages, 30)
    
    # 先抓取起始页面，提取所有链接
    start_html = await _fetch_page_content(start_url)
    if not start_html:
        return json.dumps({
            "status": "error",
            "message": f"无法访问起始页面: {start_url}",
            "documents": []
        }, ensure_ascii=False)
    
    # 提取API文档链接
    api_links = _extract_api_links(start_html, start_url)
    urls_to_visit.extend(api_links)
    
    # 解析起始页面
    start_data = _parse_api_content(start_html, start_url)
    if start_data.get("content"):
        results.append({
            "text": _format_api_document(start_data),
            "source": start_url,
            "title": start_data.get("title", "API文档首页")
        })
    visited_urls.add(start_url)
    
    # 遍历抓取其他页面
    for url in urls_to_visit:
        if url in visited_urls:
            continue
        if len(visited_urls) >= max_pages:
            break
        
        visited_urls.add(url)
        
        # 添加延迟，避免请求过快
        await asyncio.sleep(0.3)
        
        html_content = await _fetch_page_content(url)
        if not html_content:
            continue
        
        # 解析页面内容
        api_data = _parse_api_content(html_content, url)
        
        if api_data.get("content") and len(api_data["content"]) > 50:
            results.append({
                "text": _format_api_document(api_data),
                "source": url,
                "title": api_data.get("title", url.split("/")[-1])
            })
            
            # 从当前页面提取更多链接
            more_links = _extract_api_links(html_content, url)
            for link in more_links:
                if link not in visited_urls and link not in urls_to_visit:
                    urls_to_visit.append(link)
    
    # 返回精简的摘要信息给LLM，完整数据直接传递给入库工具
    summary = {
        "status": "success",
        "message": f"成功抓取 {len(results)} 个API文档页面",
        "total_pages_visited": len(visited_urls),
        "documents": results
    }
    
    return json.dumps(summary, ensure_ascii=False)


@tool
async def store_documents_to_knowledge_base(
    documents_json: str,
) -> str:
    """将抓取的文档数据存入向量数据库（知识库）。

    此工具接收 scrape_api_documentation 工具输出的JSON数据，
    调用 anything-chat-rag 的 /documents/texts 接口将文档批量存入知识库。

    接口说明：
    - POST /documents/texts
    - 请求体: {"texts": ["文本1", "文本2", ...], "file_sources": ["来源1", "来源2", ...]}
    - 返回: {"status": "success/duplicated/error", "message": "...", "track_id": "..."}

    Args:
        documents_json: scrape_api_documentation 工具输出的JSON字符串，
                       包含 documents 数组，每个元素有 text, source, title 字段

    Returns:
        入库操作的结果信息（精简版）
    """
    import json
    
    try:
        data = json.loads(documents_json)
    except json.JSONDecodeError as e:
        return f"JSON解析错误: {e}"
    
    if data.get("status") == "error":
        return f"文档数据有误: {data.get('message', '未知错误')}"
    
    documents = data.get("documents", [])
    if not documents:
        return "没有需要入库的文档数据"
    
    # 准备请求数据
    texts = []
    file_sources = []
    titles = []
    
    for doc in documents:
        text = doc.get("text", "").strip()
        source = doc.get("source", "unknown_source")
        title = doc.get("title", "")
        
        if text:
            texts.append(text)
            file_sources.append(source)
            titles.append(title)
    
    if not texts:
        return "没有有效的文本内容可入库"
    
    # 调用 /documents/texts 接口
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            payload = {
                "texts": texts,
                "file_sources": file_sources
            }
            
            response = await client.post(
                f"{KNOWLEDGE_API_URL}/documents/texts",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            
            status = result.get("status", "unknown")
            message = result.get("message", "")
            track_id = result.get("track_id", "")
            
            # 构建文档列表摘要（只显示标题）
            doc_list = "\n".join([f"  - {t}" for t in titles[:10]])
            if len(titles) > 10:
                doc_list += f"\n  ... 还有 {len(titles) - 10} 个文档"
            
            if status == "success":
                return f"""✅ 文档入库成功！

- 状态: {status}
- 消息: {message}
- 追踪ID: {track_id}
- 入库文档数: {len(texts)}

已入库的文档:
{doc_list}

提示: 文档正在后台处理中，可使用 track_id 查询处理进度。"""
            
            elif status == "duplicated":
                return f"""⚠️ 文档已存在

- 状态: {status}
- 消息: {message}

部分或全部文档已存在于知识库中，未重复入库。"""
            
            else:
                return f"""❌ 入库失败

- 状态: {status}
- 消息: {message}"""
                
        except httpx.HTTPError as e:
            return f"调用知识库API失败: {str(e)}"
        except Exception as e:
            return f"入库过程出错: {str(e)}"


# 导出所有工具
web_scraper_tools = [
    scrape_api_documentation,
    store_documents_to_knowledge_base,
]
