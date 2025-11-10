"""
任务检测模块
负责检测用户消息的类型和路由目标
"""
from langchain_core.messages import HumanMessage


def detect_test_case_generation_task(messages: list) -> bool:
    """
    检测用户消息是否是测试用例生成任务（不包含自动化执行）

    测试用例生成任务的特征：
    - 包含"编写"、"生成"、"创建"等关键词
    - 包含"测试用例"、"用例"等关键词
    - 不包含"执行"、"运行"等自动化执行关键词

    Args:
        messages: 消息列表

    Returns:
        是否是测试用例生成任务
    """
    generation_keywords = ['编写', '生成', '创建', '写', '设计', '制定']
    testcase_keywords = ['测试用例', '用例', 'test case', 'testcase']
    execution_keywords = ['执行', '运行', 'run', 'execute', '测试报告', '报告']

    # 提取所有文本内容
    text_content = ""
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get('content', '')
            if isinstance(content, str):
                text_content += content + " "
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_content += item.get('text', '') + " "
        elif isinstance(msg, HumanMessage):
            if isinstance(msg.content, str):
                text_content += msg.content + " "

    text_lower = text_content.lower()

    # 检查是否包含生成关键词
    has_generation_keyword = any(keyword in text_content for keyword in generation_keywords)
    # 检查是否包含测试用例关键词
    has_testcase_keyword = any(keyword in text_lower for keyword in testcase_keywords)
    # 检查是否包含执行关键词
    has_execution_keyword = any(keyword in text_content for keyword in execution_keywords)

    # 如果同时包含"编写测试用例"和"执行"，则不是纯测试用例生成任务
    # 应该路由到自动化测试
    is_testcase_generation = has_generation_keyword and has_testcase_keyword and not has_execution_keyword

    if has_generation_keyword and has_testcase_keyword:
        if has_execution_keyword:
            print(f"[DEBUG] ⚠️ 检测到测试用例生成 + 执行任务，应路由到自动化测试")
            print(f"[DEBUG]   - 生成关键词: {has_generation_keyword}")
            print(f"[DEBUG]   - 测试用例关键词: {has_testcase_keyword}")
            print(f"[DEBUG]   - 执行关键词: {has_execution_keyword}")
        else:
            print(f"[DEBUG] ✅ 检测到纯测试用例生成任务")
            print(f"[DEBUG]   - 生成关键词: {has_generation_keyword}")
            print(f"[DEBUG]   - 测试用例关键词: {has_testcase_keyword}")

    return is_testcase_generation


def detect_browser_operation_task(messages: list) -> bool:
    """
    检测用户消息是否是浏览器操作任务（不包括测试）

    浏览器操作任务的特征：
    - 包含"打开"、"访问"、"搜索"等操作词
    - 包含网址或域名
    - 不包含"测试"关键词（如果包含测试关键词，应该走自动化测试流程）

    示例：
    - "打开www.baidu.com 搜索凤凰古城" → True（浏览器操作）
    - "访问https://www.google.com" → True（浏览器操作）
    - "打开网站并执行测试" → False（这是自动化测试，不是普通浏览器操作）

    Args:
        messages: 消息列表

    Returns:
        是否是浏览器操作任务
    """
    # 操作关键词
    action_keywords = ['打开', '访问', '搜索', '查找', '点击', '填写', '输入', '执行', '登录']
    # URL 模式
    url_patterns = ['www.', 'http://', 'https://', '.com', '.cn', '.net', '.org']
    # 测试关键词（如果包含这些，应该走自动化测试流程）
    test_keywords = ['测试', 'test', '自动化', '测试报告', '执行测试', '运行测试']

    # 提取所有文本内容
    text_content = ""
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get('content', '')
            if isinstance(content, str):
                text_content += content + " "
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_content += item.get('text', '') + " "
        elif isinstance(msg, HumanMessage):
            if isinstance(msg.content, str):
                text_content += msg.content + " "

    text_lower = text_content.lower()

    # 检查是否包含操作关键词
    has_action_keyword = any(keyword in text_content for keyword in action_keywords)
    # 检查是否包含URL
    has_url = any(pattern in text_lower for pattern in url_patterns)
    # 检查是否包含测试关键词
    has_test_keyword = any(keyword in text_lower for keyword in test_keywords)

    # 浏览器操作任务的判断逻辑：
    # 有操作关键词 + 有URL + 没有测试关键词
    is_browser_operation = has_action_keyword and has_url and not has_test_keyword

    if is_browser_operation:
        print(f"[DEBUG] ✅ 检测到浏览器操作任务")
        print(f"[DEBUG]   - 操作关键词: {has_action_keyword}")
        print(f"[DEBUG]   - 包含URL: {has_url}")
        print(f"[DEBUG]   - 测试关键词: {has_test_keyword}")

    return is_browser_operation


def detect_automated_test_task(messages: list) -> bool:
    """
    检测用户消息是否是自动化测试执行任务

    自动化测试任务的特征（必须同时满足）：
    - 包含"测试"、"自动化"、"测试报告"等明确的测试关键词
    - 包含"打开"、"访问"、"登录"等操作词 OR 包含网址

    注意：只有明确提到"测试"相关词汇时才视为自动化测试任务
    普通的"打开网站"请求会被视为浏览器操作任务

    Args:
        messages: 消息列表

    Returns:
        是否是自动化测试任务
    """
    # 测试关键词（必须包含）
    test_keywords = ['测试', 'test', '自动化', '测试报告', '执行测试', '运行测试']
    # 操作关键词
    action_keywords = ['打开', '访问', '登录', '点击', '填写', '输入', '执行', '搜索']
    # URL 模式
    url_patterns = ['www.', 'http://', 'https://', '.com', '.cn', '.net', '.org']

    # 提取所有文本内容
    text_content = ""
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get('content', '')
            if isinstance(content, str):
                text_content += content + " "
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_content += item.get('text', '') + " "
        elif isinstance(msg, HumanMessage):
            if isinstance(msg.content, str):
                text_content += msg.content + " "

    text_lower = text_content.lower()

    # 检查是否包含测试关键词（必须）
    has_test_keyword = any(keyword in text_lower for keyword in test_keywords)
    # 检查是否包含操作关键词
    has_action_keyword = any(keyword in text_content for keyword in action_keywords)
    # 检查是否包含URL
    has_url = any(pattern in text_lower for pattern in url_patterns)

    # 自动化测试任务的判断逻辑（更严格）：
    # 必须包含测试关键词 + (操作关键词 OR URL)
    # 这样可以避免把普通的"打开网站"请求误判为自动化测试
    is_automated_test = has_test_keyword and (has_action_keyword or has_url)

    if is_automated_test:
        print(f"[DEBUG] ✅ 检测到自动化测试任务")
        print(f"[DEBUG]   - 测试关键词: {has_test_keyword}")
        print(f"[DEBUG]   - 操作关键词: {has_action_keyword}")
        print(f"[DEBUG]   - 包含URL: {has_url}")

    return is_automated_test


def detect_file_type(messages: list) -> str:
    """
    智能检测消息类型和路由目标

    优先级：
    1. 检测文件类型（图片、PDF）
    2. 检测是否是测试用例生成任务（编写测试用例）
    3. 检测是否是自动化测试任务（打开网站执行测试 + 测试关键词）
    4. 检测是否是浏览器操作任务（打开网站 + 无测试关键词）
    5. 默认为普通文本对话

    Args:
        messages: 消息列表（可能是 BaseMessage 对象或 dict）

    Returns:
        文件类型: "image", "pdf", "testcase_generation", "automated_test", "browser_operation", "text"
    """
    print(f"[DEBUG] 消息列表长度: {len(messages)}")

    # 第一步：检测是否有文件上传
    has_file = False
    file_type = None

    # 遍历所有消息，查找用户消息
    for idx, msg in enumerate(messages):
        print(f"[DEBUG] 消息 {idx}: 类型={type(msg).__name__}")

        # 处理 dict 格式的消息（LangGraph Server 传递的格式）
        if isinstance(msg, dict):
            role = msg.get('role', '')
            content = msg.get('content', '')
            print(f"[DEBUG] Dict消息 - role='{role}', content类型={type(content).__name__}")

            # 不管 role 是什么，只要 content 是列表就检查
            if isinstance(content, list):
                print(f"[DEBUG] 内容是列表，长度: {len(content)}")
                for i, item in enumerate(content):
                    print(f"[DEBUG] 项目 {i}: {type(item).__name__}")
                    if isinstance(item, dict):
                        item_type = item.get('type', '')
                        print(f"[DEBUG] 项目类型: '{item_type}'")

                        # 检查是否是文件类型
                        if item_type == 'file':
                            mime_type = item.get('mime_type', '')
                            print(f"[DEBUG] 文件 MIME 类型: {mime_type}")
                            if 'pdf' in mime_type.lower():
                                print(f"[DEBUG] ✅ 检测到 PDF 文件")
                                has_file = True
                                file_type = "pdf"
                            elif 'image' in mime_type.lower():
                                print(f"[DEBUG] ✅ 检测到图片文件（通过 file 类型）")
                                has_file = True
                                file_type = "image"
                        # 检查是否是图片类型
                        elif item_type == 'image_url':
                            print(f"[DEBUG] ✅ 检测到图片（通过 image_url 类型）")
                            has_file = True
                            file_type = "image"
                        # 检查是否是 image 类型
                        elif item_type == 'image':
                            print(f"[DEBUG] ✅ 检测到图片（通过 image 类型）")
                            has_file = True
                            file_type = "image"
            # 如果content是字符串，继续查找
            elif isinstance(content, str):
                print(f"[DEBUG] 内容是字符串: {content[:100] if len(content) > 100 else content}")
                continue

        # 处理 BaseMessage 对象格式
        elif isinstance(msg, HumanMessage):
            content = msg.content
            print(f"[DEBUG] HumanMessage - 内容类型: {type(content).__name__}")

            # 如果content是字符串，继续查找
            if isinstance(content, str):
                print(f"[DEBUG] 内容是字符串: {content[:100] if len(content) > 100 else content}")
                continue

            # 如果content是列表，检查是否包含文件
            if isinstance(content, list):
                print(f"[DEBUG] 内容是列表，长度: {len(content)}")
                for i, item in enumerate(content):
                    print(f"[DEBUG] 项目 {i}: {type(item).__name__}")
                    if isinstance(item, dict):
                        item_type = item.get('type', '')
                        print(f"[DEBUG] 项目类型: {item_type}")

                        # 检查是否是文件类型
                        if item_type == 'file':
                            mime_type = item.get('mime_type', '')
                            print(f"[DEBUG] 文件 MIME 类型: {mime_type}")
                            if 'pdf' in mime_type.lower():
                                print(f"[DEBUG] ✅ 检测到 PDF 文件")
                                has_file = True
                                file_type = "pdf"
                            elif 'image' in mime_type.lower():
                                print(f"[DEBUG] ✅ 检测到图片文件（通过 file 类型）")
                                has_file = True
                                file_type = "image"
                        # 检查是否是图片类型
                        elif item_type == 'image_url':
                            print(f"[DEBUG] ✅ 检测到图片（通过 image_url 类型）")
                            has_file = True
                            file_type = "image"
                        # 检查是否是 image 类型
                        elif item_type == 'image':
                            print(f"[DEBUG] ✅ 检测到图片（通过 image 类型）")
                            has_file = True
                            file_type = "image"

    # 第二步：如果有文件上传，检查是否是测试用例生成任务
    if has_file:
        if detect_test_case_generation_task(messages):
            print(f"[DEBUG] 🎯 路由决策: {file_type} + 测试用例生成 → testcase_generation")
            return "testcase_generation"
        else:
            # 有文件但不是测试用例生成，走普通文件处理流程
            print(f"[DEBUG] 🎯 路由决策: {file_type} 文件 → {file_type}")
            return file_type

    # 第三步：没有文件上传，检查是否是测试用例生成任务
    if detect_test_case_generation_task(messages):
        print(f"[DEBUG] 🎯 路由决策: 纯文本 + 测试用例生成 → testcase_generation")
        return "testcase_generation"

    # 第四步：检查是否是自动化测试任务（包含"测试"关键词）
    if detect_automated_test_task(messages):
        print(f"[DEBUG] 🎯 路由决策: 自动化测试任务 → automated_test")
        return "automated_test"

    # 第五步：检查是否是浏览器操作任务（不包含"测试"关键词）
    if detect_browser_operation_task(messages):
        print(f"[DEBUG] 🎯 路由决策: 浏览器操作任务 → browser_operation")
        return "browser_operation"

    # 第六步：默认为普通文本对话
    print(f"[DEBUG] 🎯 路由决策: 普通对话 → text")
    return "text"

