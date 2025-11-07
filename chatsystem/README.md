# 多模态对话系统 (ChatSystem)

完整的多模态对话系统，支持图片、PDF 和普通文本的智能对话。基于 LangGraph 实现条件路由，自动选择合适的处理节点。

## 核心特性

### 1. 文件类型自动检测
- **图片**: jpg, jpeg, png, gif, webp, bmp, svg
- **PDF**: application/pdf
- **文本**: txt, md, json, xml, csv, html

### 2. 智能路由
- 图片对话 → GPT-4O (多模态分析)
- PDF 对话 → GPT-4O (文档分析 + 图片提取)
- 普通对话 → DeepSeek (通用对话)

### 3. 模块化设计
- **types.py**: 类型定义和数据结构
- **detectors.py**: 文件类型检测
- **processors.py**: 多模态处理器
- **llm_factory.py**: LLM 工厂
- **core.py**: 核心对话系统

## 快速开始

### 基本使用

```python
from langchain_core.messages import HumanMessage
from chatsystem import get_chat_system

# 创建对话系统
system = get_chat_system()

# 普通文本对话
messages = [HumanMessage(content="你好，请介绍一下自己")]
result = system.chat(messages)
print(result['response'])
```

### 使用便捷函数

```python
from chatsystem import chat, get_response

# 方式 1：获取完整结果
messages = [HumanMessage(content="什么是人工智能?")]
result = chat(messages)
print(f"文件类型: {result['file_type'].value}")
print(f"响应: {result['response']}")

# 方式 2：只获取响应文本
response = get_response(messages)
print(response)
```

### 图片对话

```python
messages = [HumanMessage(content=[
    {"type": "text", "text": "这是什么?"},
    {
        "type": "file",
        "mime_type": "image/png",
        "data": "base64_encoded_image_data",
        "metadata": {"filename": "image.png"}
    }
])]
result = chat(messages)
print(result['response'])
```

### PDF 对话

```python
messages = [HumanMessage(content=[
    {"type": "text", "text": "分析这个 PDF 文件"},
    {
        "type": "file",
        "mime_type": "application/pdf",
        "data": "base64_encoded_pdf_data",
        "metadata": {"filename": "document.pdf"}
    }
])]
result = chat(messages)
print(result['response'])
```

## 模块说明

### types.py - 类型定义

```python
from chatsystem import FileType, ProcessorType, ChatMessage, ChatResult

# 文件类型
FileType.IMAGE    # 图片
FileType.PDF      # PDF
FileType.TEXT     # 文本
FileType.UNKNOWN  # 未知

# 处理器类型
ProcessorType.IMAGE  # 图片处理器
ProcessorType.PDF    # PDF 处理器
ProcessorType.TEXT   # 文本处理器
```

### detectors.py - 文件类型检测

```python
from chatsystem import FileTypeDetector

# 根据 MIME 类型检测
FileTypeDetector.detect_from_mime_type("image/png")

# 根据文件扩展名检测
FileTypeDetector.detect_from_extension("document.pdf")

# 从消息对象检测
FileTypeDetector.detect_from_message(message)

# 从消息列表检测
FileTypeDetector.detect_from_messages(messages)
```

### processors.py - 处理器

```python
from chatsystem import ProcessorFactory, ImageProcessor, PDFProcessor, TextProcessor

# 使用工厂创建处理器
processor = ProcessorFactory.create_processor(FileType.IMAGE)

# 或直接创建
image_processor = ImageProcessor()
pdf_processor = PDFProcessor()
text_processor = TextProcessor()

# 处理消息
response = processor.process(messages)
```

### llm_factory.py - LLM 工厂

```python
from chatsystem import LLMFactory, create_llm, get_llm

# 创建 LLM 实例
llm = create_llm(model="gpt-4o", temperature=0.7)

# 获取缓存的实例
llm = get_llm(model="gpt-4o")

# 使用工厂
llm = LLMFactory.create_llm(model="deepseek-chat")
```

### core.py - 核心系统

```python
from chatsystem import MultimodalChatSystem, get_chat_system

# 创建系统实例
system = MultimodalChatSystem()

# 或获取全局实例
system = get_chat_system()

# 执行对话
result = system.chat(messages)

# 获取响应
response = system.get_response(messages)
```

## 系统架构

### 处理流程

```
START
  ↓
检测文件类型 (detect_file_type)
  ↓
条件路由 (route_by_file_type)
  ├→ 图片 → process_image (GPT-4O)
  ├→ PDF → process_pdf (GPT-4O)
  └→ 文本 → process_text (DeepSeek)
  ↓
END
```

### 返回结果结构

```python
{
    "messages": [...],              # 消息列表
    "file_type": FileType.TEXT,     # 检测到的文件类型
    "processor_type": ProcessorType.TEXT,  # 使用的处理器类型
    "current_node": "process_text", # 使用的处理节点
    "response": "..."               # 对话响应
}
```

## 配置

### 环境变量

```bash
# .env 文件
ONE_API_KEY=your_api_key
ONE_API_BASE_URL=http://your_api_base_url
```

### 模型配置

- **GPT-4O**: 用于图片和 PDF 处理
- **DeepSeek**: 用于普通文本对话
- 温度: 0.7 (可自定义)
- 最大 Token: 2000 (可自定义)

## 扩展

### 添加新的处理器

```python
from chatsystem import BaseProcessor, ProcessorFactory, FileType

class CustomProcessor(BaseProcessor):
    processor_type = ProcessorType.CUSTOM
    model_name = "custom-model"
    
    def process(self, messages):
        # 实现处理逻辑
        return "response"

# 注册处理器
ProcessorFactory.register_processor(FileType.CUSTOM, CustomProcessor)
```

### 自定义 LLM

```python
from chatsystem import LLMFactory

# 创建自定义 LLM
llm = LLMFactory.create_llm(
    model="custom-model",
    temperature=0.5,
    max_tokens=4000
)
```

## 性能指标

- 文本对话: < 2 秒
- 图片分析: < 5 秒
- PDF 处理: 取决于页数和图片数量

## 许可证

MIT License

