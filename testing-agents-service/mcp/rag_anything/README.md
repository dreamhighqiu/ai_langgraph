# RAG Anything MCP Server

一个专业的 MCP（Model Context Protocol）服务器实现，基于 RAG Anything 框架，提供完整的多模态 RAG（检索增强生成）功能。

## 🌟 主要特性

### 📄 多格式文档处理
- 支持 PDF、Office 文档、图片、文本等多种格式
- 自动文档解析和内容提取
- 支持 OCR 处理扫描文档

### 🎨 多模态内容处理
- 自动提取和处理图像、表格、公式等多模态内容
- 图像处理（ImageModalProcessor）
- 表格处理（TableModalProcessor）
- 公式处理（EquationModalProcessor）

### 🔍 混合检索
- 支持多种查询模式：local、global、hybrid、naive、mix、bypass
- 知识图谱构建和查询
- 向量相似度搜索

### 🤖 VLM 增强查询
- 使用视觉语言模型增强查询结果
- 自动分析检索到的文档中的图像
- 支持多模态查询

### ⚡ 高性能处理
- 并发文档处理
- 批量操作支持
- 可配置的工作线程数

## 🚀 快速开始

### 安装

```bash
# 进入项目目录
cd testing-agents-service

# 安装依赖（如果使用独立安装）
# pip install -e .
# 注意：MCP 服务现在集成在 testing-agents-service 中，通常不需要单独安装
```

### 配置

创建 `.env` 文件：

```env
# LLM 配置
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

# 嵌入配置
USE_OLLAMA_EMBEDDING=true
EMBEDDING_MODEL=qwen3-embedding:0.6b
EMBEDDING_HOST=http://localhost:11434
EMBEDDING_DIM=1024

# RAG 配置
RAG_WORKING_DIR=./rag_storage
RAG_PARSER=docling
RAG_PARSE_METHOD=auto
RAG_ENABLE_IMAGE=true
RAG_ENABLE_TABLE=true
RAG_ENABLE_EQUATION=true
RAG_LOAD_EXISTING=true
RAG_MAX_CONCURRENT=2

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8001
SERVER_SSE_MODE=true
DEBUG=false
```

### 启动服务器

```bash
# 进入 testing-agents-service 目录
cd testing-agents-service

# 使用 SSE 模式启动
python -m mcp.rag_anything.server --sse --port 8001

# 或使用标准 MCP 模式
python -m mcp.rag_anything.server
```

## 📚 MCP 工具参考

### 文档处理

#### `process_document`
处理单个文档并插入知识库。

**参数：**
- `file_path` (string): 文档文件路径
- `parse_method` (string, optional): 解析方法 (auto, ocr, txt)

**返回：** 处理结果 (JSON)

**示例：**
```json
{
  "success": true,
  "result": {...},
  "file_path": "/path/to/document.pdf"
}
```

#### `process_folder`
批量处理文件夹中的所有文档。

**参数：**
- `folder_path` (string): 文件夹路径
- `recursive` (boolean): 是否递归处理子文件夹
- `parse_method` (string, optional): 解析方法

**返回：** 处理结果 (JSON)

### 查询

#### `query`
执行文本查询。

**参数：**
- `query_text` (string): 查询文本
- `mode` (string): 查询模式 (local, global, hybrid, naive, mix, bypass)
- `top_k` (integer): 返回结果数量

**返回：** 查询结果 (JSON)

**查询模式说明：**
| 模式 | 说明 | 速度 | 精度 |
|------|------|------|------|
| local | 实体和关系搜索 | 快 | 高 |
| global | 主题和摘要搜索 | 中 | 中 |
| hybrid | 混合搜索 | 中 | 高 |
| naive | 向量相似度 | 快 | 低 |
| mix | 多策略混合 | 慢 | 高 |
| bypass | 直接 LLM | 快 | 中 |

#### `query_with_multimodal`
执行多模态查询（文本 + 图像/表格/公式）。

**参数：**
- `query_text` (string): 查询文本
- `multimodal_content` (string, optional): JSON 格式的多模态内容
- `mode` (string): 查询模式

**多模态内容格式：**
```json
[
  {
    "type": "image",
    "img_path": "/path/to/image.jpg"
  },
  {
    "type": "table",
    "table_data": "Name,Age\nAlice,25\nBob,30"
  }
]
```

### 配置和状态

#### `get_config`
获取当前配置信息。

**返回：** 配置详情 (JSON)

#### `get_processor_status`
获取处理器状态和信息。

**返回：** 处理器状态 (JSON)

#### `get_knowledge_base_stats`
获取知识库统计信息。

**返回：** 统计信息 (JSON)

#### `list_supported_formats`
列出支持的文件格式。

**返回：** 支持的格式列表 (JSON)

## 🏗️ 架构

```
MCP Server
├── FastMCP 框架
├── RAGAnythingConnector
│   ├── LLM 模型函数
│   ├── 视觉模型函数
│   ├── 嵌入函数
│   └── RAGAnything 实例
├── 文档处理层
├── 查询层
└── 知识库层
    ├── LightRAG
    ├── 向量存储
    └── 知识图谱
```

## 📋 支持的文件格式

### 文档
- PDF (.pdf)
- Word (.doc, .docx)
- PowerPoint (.ppt, .pptx)
- Excel (.xls, .xlsx)
- 文本 (.txt, .md)
- HTML (.html, .htm)

### 图像
- PNG, JPEG, BMP, TIFF, GIF, WebP

## 🔧 环境变量配置

### LLM 配置
- `LLM_PROVIDER`: LLM 提供商 (默认: deepseek)
- `LLM_MODEL`: 模型名称 (默认: deepseek-chat)
- `LLM_API_KEY`: API 密钥
- `LLM_BASE_URL`: API 基础 URL
- `LLM_TEMPERATURE`: 温度参数 (默认: 0.7)
- `LLM_MAX_TOKENS`: 最大 token 数 (默认: 4096)

### 嵌入配置
- `USE_OLLAMA_EMBEDDING`: 是否使用 Ollama (默认: true)
- `EMBEDDING_MODEL`: 嵌入模型 (默认: qwen3-embedding:0.6b)
- `EMBEDDING_HOST`: Ollama 主机 (默认: http://localhost:11434)
- `EMBEDDING_DIM`: 嵌入维度 (默认: 1024)

### RAG 配置
- `RAG_WORKING_DIR`: 工作目录 (默认: ./rag_storage)
- `RAG_PARSER`: 解析器 (docling 或 mineru)
- `RAG_PARSE_METHOD`: 解析方法 (auto, ocr, txt)
- `RAG_ENABLE_IMAGE`: 启用图像处理 (默认: true)
- `RAG_ENABLE_TABLE`: 启用表格处理 (默认: true)
- `RAG_ENABLE_EQUATION`: 启用公式处理 (默认: true)
- `RAG_LOAD_EXISTING`: 加载现有知识库 (默认: true)
- `RAG_MAX_CONCURRENT`: 最大并发文件数 (默认: 2)

## 🧪 测试

```bash
# 运行测试
python test_rag_server.py
```

## 🐛 故障排除

### 连接到 Ollama 失败
1. 确保 Ollama 服务正在运行
2. 检查 `EMBEDDING_HOST` 配置
3. 尝试访问 `http://localhost:11434/api/tags`

### LLM API 错误
1. 验证 `LLM_API_KEY` 正确性
2. 检查 `LLM_BASE_URL` 可访问性
3. 确保模型名称正确

### 文档处理失败
1. 检查文件格式是否支持
2. 尝试使用 `parse_method="ocr"`
3. 查看错误日志

## 📈 性能指标

基于典型配置的参考数据：

- **文档处理**：~10-50 页/分钟
- **查询响应**：~1-5 秒
- **批量处理加速**：~4x（使用 4 个 workers）

## 🎯 最佳实践

1. **文档处理**
   - 使用 `process_folder` 处理大量文件
   - 设置合适的 `RAG_MAX_CONCURRENT` 值
   - 使用 `parse_method="auto"` 自动选择最佳方法

2. **查询优化**
   - 精确查询使用 `mode="local"`
   - 概览查询使用 `mode="global"`
   - 通用查询使用 `mode="hybrid"`（推荐）

3. **知识库管理**
   - 定期检查统计信息
   - 使用 `RAG_LOAD_EXISTING=true` 保留已有知识库
   - 新项目使用 `RAG_LOAD_EXISTING=false`

## 🔗 相关资源

- [RAGAnything GitHub](https://github.com/HKUDS/RAG-Anything)
- [LightRAG 文档](https://github.com/HKUDS/LightRAG)
- [MCP 规范](https://modelcontextprotocol.io/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)

## 📝 许可证

本项目遵循 RAGAnything 项目的许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**版本**: 0.1.0  
**最后更新**: 2024 年 11 月 22 日

