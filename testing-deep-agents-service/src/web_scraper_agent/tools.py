"""Web Scraper Tools - 网站接口数据抓取与入库工具.

用于从指定网站抓取API接口文档数据，并存入向量数据库（知识库）。
支持并发抓取，大幅提升效率。
"""

import os
import asyncio
import httpx
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
from langchain_core.tools import tool
from bs4 import BeautifulSoup


# 从环境变量获取配置
KNOWLEDGE_API_URL = os.getenv("KNOWLEDGE_API_URL", "http://localhost:9621")

# 并发配置
MAX_CONCURRENT_REQUESTS = 10  # 最大并发请求数
REQUEST_DELAY = 0.1  # 请求间隔（秒），避免对目标网站造成压力


class AsyncSemaphoreClient:
    """带信号量限制的异步HTTP客户端，用于控制并发数。"""
    
    def __init__(self, max_concurrent: int = MAX_CONCURRENT_REQUESTS):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
    
    async def fetch(self, url: str, timeout: float = 30.0) -> Tuple[str, Optional[str]]:
        """获取网页内容（带并发控制）。
        
        Args:
            url: 目标URL
            timeout: 超时时间（秒）
        
        Returns:
            (url, html_content) 元组，失败时 html_content 为 None
        """
        async with self.semaphore:
            # 小延迟，避免请求过于密集
            await asyncio.sleep(REQUEST_DELAY)
            
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                try:
                    response = await client.get(url, headers=self.headers)
                    response.raise_for_status()
                    return (url, response.text)
                except httpx.HTTPError as e:
                    print(f"获取页面失败 {url}: {e}")
                    return (url, None)


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


async def _fetch_and_parse_page(
    client: AsyncSemaphoreClient,
    url: str
) -> Optional[Dict[str, Any]]:
    """抓取并解析单个页面。
    
    Args:
        client: 异步HTTP客户端
        url: 页面URL
    
    Returns:
        解析后的文档数据，失败返回None
    """
    url, html_content = await client.fetch(url)
    
    if not html_content:
        return None
    
    api_data = _parse_api_content(html_content, url)
    
    if api_data.get("content") and len(api_data["content"]) > 50:
        return {
            "text": _format_api_document(api_data),
            "source": url,
            "title": api_data.get("title", url.split("/")[-1]),
            "links": _extract_api_links(html_content, url)  # 同时提取新链接
        }
    
    return None


@tool
async def scrape_api_documentation(
    start_url: str,
    max_pages: int = 30,
    concurrent_requests: int = 10,
) -> str:
    """从指定网站并发抓取API接口文档数据。

    此工具会从给定的起始URL开始，使用并发方式快速抓取网站上的API接口文档内容，
    并对抓取的数据进行整理，输出适合存储到知识库的文档列表。

    工具会自动：
    1. 从起始页面提取所有API相关链接
    2. 使用多个并发请求同时抓取多个页面（默认10个并发）
    3. 解析并整理API接口信息（接口描述、参数、请求/响应示例等）
    4. 返回整理好的文档列表（JSON格式）

    并发优化：
    - 使用信号量控制并发数，避免对目标网站造成过大压力
    - 相比串行抓取，速度提升约5-10倍

    Args:
        start_url: 起始URL，通常是API文档的首页或目录页
        max_pages: 最大抓取页面数，默认30，防止过度抓取
        concurrent_requests: 并发请求数，默认10

    Returns:
        JSON格式的字符串，包含抓取到的API文档列表
    """
    import json
    
    results = []
    visited_urls = set()
    urls_to_visit = set()
    
    # 限制参数范围
    max_pages = min(max_pages, 50)
    concurrent_requests = min(concurrent_requests, 20)
    
    # 创建带并发控制的客户端
    client = AsyncSemaphoreClient(max_concurrent=concurrent_requests)
    
    # 先抓取起始页面，提取所有链接
    _, start_html = await client.fetch(start_url)
    if not start_html:
        return json.dumps({
            "status": "error",
            "message": f"无法访问起始页面: {start_url}",
            "documents": []
        }, ensure_ascii=False)
    
    # 解析起始页面
    start_data = _parse_api_content(start_html, start_url)
    if start_data.get("content"):
        results.append({
            "text": _format_api_document(start_data),
            "source": start_url,
            "title": start_data.get("title", "API文档首页")
        })
    visited_urls.add(start_url)
    
    # 提取API文档链接
    api_links = _extract_api_links(start_html, start_url)
    urls_to_visit.update(api_links)
    
    # 分批并发抓取
    while urls_to_visit and len(visited_urls) < max_pages:
        # 获取下一批要抓取的URL
        batch_size = min(concurrent_requests, max_pages - len(visited_urls))
        batch_urls = []
        
        for url in list(urls_to_visit):
            if url not in visited_urls:
                batch_urls.append(url)
                visited_urls.add(url)
                urls_to_visit.discard(url)
                if len(batch_urls) >= batch_size:
                    break
        
        if not batch_urls:
            break
        
        # 并发抓取这一批URL
        tasks = [_fetch_and_parse_page(client, url) for url in batch_urls]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for result in batch_results:
            if isinstance(result, Exception):
                print(f"抓取出错: {result}")
                continue
            
            if result:
                # 添加文档结果
                doc_data = {
                    "text": result["text"],
                    "source": result["source"],
                    "title": result["title"]
                }
                results.append(doc_data)
                
                # 添加新发现的链接
                for link in result.get("links", []):
                    if link not in visited_urls:
                        urls_to_visit.add(link)
    
    # 返回结果
    summary = {
        "status": "success",
        "message": f"成功抓取 {len(results)} 个API文档页面（并发模式）",
        "total_pages_visited": len(visited_urls),
        "documents": results
    }
    
    return json.dumps(summary, ensure_ascii=False)


async def _store_single_document(
    client: httpx.AsyncClient,
    text: str,
    file_source: str,
    semaphore: asyncio.Semaphore
) -> Dict[str, Any]:
    """存储单个文档到知识库（带并发控制）。
    
    Args:
        client: HTTP客户端
        text: 文档文本
        file_source: 文档来源
        semaphore: 并发控制信号量
    
    Returns:
        入库结果
    """
    async with semaphore:
        try:
            payload = {
                "texts": [text],
                "file_sources": [file_source]
            }
            
            response = await client.post(
                f"{KNOWLEDGE_API_URL}/documents/texts",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "source": file_source,
                "status": result.get("status", "unknown"),
                "message": result.get("message", ""),
                "track_id": result.get("track_id", "")
            }
        except Exception as e:
            return {
                "source": file_source,
                "status": "error",
                "message": str(e),
                "track_id": ""
            }


@tool
async def store_documents_to_knowledge_base(
    documents_json: str,
    concurrent_uploads: int = 5,
) -> str:
    """并发将抓取的文档数据存入向量数据库（知识库）。

    此工具接收 scrape_api_documentation 工具输出的JSON数据，
    使用并发方式调用 anything-chat-rag 的 /documents/texts 接口将文档批量存入知识库。

    并发优化：
    - 支持多个文档同时入库（默认5个并发）
    - 相比串行入库，速度提升约3-5倍

    接口说明：
    - POST /documents/texts
    - 请求体: {"texts": ["文本1", ...], "file_sources": ["来源1", ...]}
    - 返回: {"status": "success/duplicated/error", "message": "...", "track_id": "..."}

    Args:
        documents_json: scrape_api_documentation 工具输出的JSON字符串，
                       包含 documents 数组，每个元素有 text, source, title 字段
        concurrent_uploads: 并发上传数，默认5

    Returns:
        入库操作的结果信息
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
    
    # 限制并发数
    concurrent_uploads = min(concurrent_uploads, 10)
    semaphore = asyncio.Semaphore(concurrent_uploads)
    
    # 准备文档数据
    doc_items = []
    for doc in documents:
        text = doc.get("text", "").strip()
        source = doc.get("source", "unknown_source")
        title = doc.get("title", "")
        
        if text:
            doc_items.append({
                "text": text,
                "source": source,
                "title": title
            })
    
    if not doc_items:
        return "没有有效的文本内容可入库"
    
    # 并发入库
    async with httpx.AsyncClient(timeout=120.0) as client:
        tasks = [
            _store_single_document(client, item["text"], item["source"], semaphore)
            for item in doc_items
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 统计结果
    success_count = 0
    duplicated_count = 0
    error_count = 0
    track_ids = []
    errors = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            error_count += 1
            errors.append(f"{doc_items[i]['title']}: {str(result)}")
        elif result.get("status") == "success":
            success_count += 1
            if result.get("track_id"):
                track_ids.append(result["track_id"])
        elif result.get("status") == "duplicated":
            duplicated_count += 1
        else:
            error_count += 1
            errors.append(f"{result.get('source', 'unknown')}: {result.get('message', 'unknown error')}")
    
    # 构建文档列表摘要
    doc_list = "\n".join([f"  - {item['title']}" for item in doc_items[:10]])
    if len(doc_items) > 10:
        doc_list += f"\n  ... 还有 {len(doc_items) - 10} 个文档"
    
    # 返回结果
    status_emoji = "✅" if error_count == 0 else "⚠️" if success_count > 0 else "❌"
    
    result_msg = f"""{status_emoji} 并发入库完成！

- 总文档数: {len(doc_items)}
- 成功: {success_count}
- 重复跳过: {duplicated_count}
- 失败: {error_count}
- 并发数: {concurrent_uploads}

已处理的文档:
{doc_list}"""
    
    if track_ids:
        result_msg += f"\n\n追踪ID（前5个）: {', '.join(track_ids[:5])}"
    
    if errors:
        result_msg += f"\n\n错误详情:\n" + "\n".join(errors[:5])
        if len(errors) > 5:
            result_msg += f"\n... 还有 {len(errors) - 5} 个错误"
    
    result_msg += "\n\n提示: 文档正在后台处理中。"
    
    return result_msg


@tool
async def scrape_and_store_api_docs(
    start_url: str,
    max_pages: int = 30,
    concurrent_requests: int = 10,
) -> str:
    """一键抓取并入库API文档（高效并发版）。

    此工具将抓取和入库合并为一个操作，使用并发方式：
    1. 并发抓取指定网站的API文档
    2. 并发将文档存入知识库

    这是最高效的方式，适合一次性完成整个流程。

    Args:
        start_url: 起始URL，通常是API文档的首页或目录页
        max_pages: 最大抓取页面数，默认30
        concurrent_requests: 并发请求数，默认10

    Returns:
        抓取和入库的完整结果
    """
    import json
    
    # 第一步：并发抓取
    scrape_result = await scrape_api_documentation.ainvoke({
        "start_url": start_url,
        "max_pages": max_pages,
        "concurrent_requests": concurrent_requests
    })
    
    try:
        scrape_data = json.loads(scrape_result)
    except json.JSONDecodeError:
        return f"抓取结果解析失败: {scrape_result}"
    
    if scrape_data.get("status") == "error":
        return f"抓取失败: {scrape_data.get('message', '未知错误')}"
    
    doc_count = len(scrape_data.get("documents", []))
    if doc_count == 0:
        return "未抓取到任何API文档"
    
    # 第二步：并发入库
    store_result = await store_documents_to_knowledge_base.ainvoke({
        "documents_json": scrape_result,
        "concurrent_uploads": min(concurrent_requests, 5)
    })
    
    return f"""🚀 抓取并入库完成！

【抓取阶段】
- 状态: {scrape_data.get('status')}
- 抓取页面数: {scrape_data.get('total_pages_visited', 0)}
- 文档数: {doc_count}

【入库阶段】
{store_result}"""


# 导出所有工具
web_scraper_tools = [
    scrape_api_documentation,
    store_documents_to_knowledge_base,
    scrape_and_store_api_docs,
]
