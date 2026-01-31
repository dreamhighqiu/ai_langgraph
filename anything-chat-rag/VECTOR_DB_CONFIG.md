# 远程向量数据库配置指南

本文档说明如何配置 LightRAG 使用远程向量数据库，替代默认的本地文件存储（NanoVectorDBStorage）。

## 支持的向量数据库

LightRAG 支持以下远程向量数据库：

1. **Qdrant** - 高性能向量数据库，推荐用于生产环境
2. **Milvus** - 大规模向量搜索
3. **PostgreSQL (pgvector)** - 使用 PostgreSQL + pgvector 扩展
4. **MongoDB Atlas** - MongoDB 云服务的向量搜索
5. **Faiss** - Facebook AI 相似性搜索（通常用于本地，但可配置为远程）

---

## 配置方法

### 1. Qdrant 配置（推荐）

Qdrant 是一个高性能的向量数据库，适合生产环境使用。

#### 步骤 1: 安装依赖

确保已安装 `qdrant-client`：

```bash
pip install qdrant-client
# 或使用 uv
uv pip install qdrant-client
```

#### 步骤 2: 修改 `.env` 文件

在 `anything-chat-rag/.env` 文件中添加以下配置：

```bash
# 使用 Qdrant 作为向量存储
LIGHTRAG_VECTOR_STORAGE=QdrantVectorDBStorage

# Qdrant 服务器地址（本地或远程）
QDRANT_URL=http://localhost:6333
# 如果使用 Qdrant Cloud 或需要 API Key，取消注释下面一行
# QDRANT_API_KEY=your-api-key-here
```

#### 步骤 3: 配置示例

**本地 Qdrant 服务器：**
```bash
QDRANT_URL=http://localhost:6333
```

**Qdrant Cloud：**
```bash
QDRANT_URL=https://your-cluster-id.qdrant.io
QDRANT_API_KEY=your-api-key-here
```

**自托管 Qdrant 服务器：**
```bash
QDRANT_URL=http://your-server-ip:6333
# 如果需要认证
# QDRANT_API_KEY=your-api-key-here
```

---

### 2. Milvus 配置

Milvus 适合大规模向量搜索场景。

#### 步骤 1: 安装依赖

```bash
pip install pymilvus>=2.6.2
# 或使用 uv
uv pip install pymilvus>=2.6.2
```

#### 步骤 2: 修改 `.env` 文件

```bash
# 使用 Milvus 作为向量存储
LIGHTRAG_VECTOR_STORAGE=MilvusVectorDBStorage

# Milvus 服务器地址
MILVUS_URI=http://localhost:19530
MILVUS_DB_NAME=lightrag

# 如果需要认证（Milvus 2.3+）
# MILVUS_USER=root
# MILVUS_PASSWORD=your_password
# 或使用 Token（Milvus Cloud）
# MILVUS_TOKEN=your_token_here
```

#### 步骤 3: 配置示例

**本地 Milvus 服务器：**
```bash
MILVUS_URI=http://localhost:19530
MILVUS_DB_NAME=lightrag
```

**Milvus Cloud：**
```bash
MILVUS_URI=https://your-endpoint.milvus.io
MILVUS_DB_NAME=lightrag
MILVUS_TOKEN=your_token_here
```

**自托管 Milvus 服务器：**
```bash
MILVUS_URI=http://your-server-ip:19530
MILVUS_DB_NAME=lightrag
MILVUS_USER=root
MILVUS_PASSWORD=your_password
```

---

### 3. PostgreSQL (pgvector) 配置

使用 PostgreSQL + pgvector 扩展，适合已有 PostgreSQL 基础设施的场景。

#### 步骤 1: 安装依赖

```bash
pip install psycopg2-binary pgvector
# 或使用 uv
uv pip install psycopg2-binary pgvector
```

#### 步骤 2: 在 PostgreSQL 中启用 pgvector 扩展

连接到 PostgreSQL 数据库并执行：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 步骤 3: 修改 `.env` 文件

```bash
# 使用 PostgreSQL 作为向量存储
LIGHTRAG_VECTOR_STORAGE=PGVectorStorage

# PostgreSQL 连接配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=your_database
POSTGRES_MAX_CONNECTIONS=12

# 向量索引类型：HNSW, IVFFlat, VCHORDRQ
POSTGRES_VECTOR_INDEX_TYPE=HNSW
POSTGRES_HNSW_M=16
POSTGRES_HNSW_EF=200

# SSL 配置（可选，用于远程连接）
# POSTGRES_SSL_MODE=require
# POSTGRES_SSL_CERT=/path/to/client-cert.pem
# POSTGRES_SSL_KEY=/path/to/client-key.pem
# POSTGRES_SSL_ROOT_CERT=/path/to/ca-cert.pem
```

#### 步骤 4: 配置示例

**本地 PostgreSQL：**
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=lightrag
```

**远程 PostgreSQL（如 Supabase）：**
```bash
POSTGRES_HOST=db.your-project.supabase.co
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=postgres
POSTGRES_SSL_MODE=require
# Supabase 特定配置
# POSTGRES_SERVER_SETTINGS="options=reference%3D[project-ref]"
```

---

### 4. MongoDB Atlas 配置

MongoDB Atlas 提供云端的向量搜索功能。

#### 步骤 1: 安装依赖

```bash
pip install pymongo
# 或使用 uv
uv pip install pymongo
```

#### 步骤 2: 修改 `.env` 文件

```bash
# 使用 MongoDB 作为向量存储
LIGHTRAG_VECTOR_STORAGE=MongoVectorDBStorage

# MongoDB 连接字符串
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DATABASE=LightRAG
```

#### 步骤 3: 配置示例

**MongoDB Atlas：**
```bash
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DATABASE=LightRAG
```

**自托管 MongoDB：**
```bash
MONGO_URI=mongodb://username:password@your-server-ip:27017/
MONGO_DATABASE=LightRAG
```

---

## 完整配置示例

以下是一个完整的 `.env` 配置示例，使用 Qdrant 作为远程向量数据库：

```bash
# ============================================
# 向量数据库配置
# ============================================
# 使用 Qdrant 作为向量存储
LIGHTRAG_VECTOR_STORAGE=QdrantVectorDBStorage

# Qdrant 服务器配置
QDRANT_URL=http://your-qdrant-server:6333
# QDRANT_API_KEY=your-api-key-if-needed

# ============================================
# 嵌入模型配置（必须与向量数据库维度匹配）
# ============================================
EMBEDDING_BINDING=openai
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIM=3072
EMBEDDING_BINDING_HOST=https://api.openai.com/v1
EMBEDDING_BINDING_API_KEY=your_api_key

# ============================================
# LLM 配置
# ============================================
LLM_BINDING=openai
LLM_MODEL=gpt-4o
LLM_BINDING_HOST=https://api.openai.com/v1
LLM_BINDING_API_KEY=your_api_key

# ============================================
# 服务器配置
# ============================================
HOST=0.0.0.0
PORT=9621
```

---

## 重要注意事项

### 1. 嵌入维度匹配

**⚠️ 重要**：切换向量数据库时，必须确保嵌入模型的维度与现有数据匹配。

- 如果之前使用 `text-embedding-3-large` (3072 维)，新配置必须使用相同的维度
- 如果之前使用 `qwen3-embedding:0.6b` (1024 维)，新配置必须使用相同的维度

**解决方案**：
- 如果维度不匹配，需要清空向量数据库并重新索引文档
- 或使用 `clear_vector_storage.sh` 脚本清空本地存储后重新处理

### 2. 工作空间隔离

LightRAG 支持工作空间（workspace）来隔离不同实例的数据：

```bash
# 设置工作空间名称（可选）
WORKSPACE=my_workspace
```

### 3. 连接池和性能

对于生产环境，建议调整连接池大小：

**PostgreSQL：**
```bash
POSTGRES_MAX_CONNECTIONS=12
```

**MongoDB：**
- 连接池大小在 MongoDB URI 中配置

**Milvus：**
- 使用默认连接池，通常足够

### 4. 数据迁移

从本地存储迁移到远程向量数据库：

1. **备份现有数据**（如果需要）
2. **配置新的向量数据库**
3. **重新处理所有文档**（因为存储格式不同，无法直接迁移）
4. **验证数据完整性**

---

## 验证配置

配置完成后，启动 LightRAG 服务器并检查日志：

```bash
cd anything-chat-rag
python -m lightrag.server
```

查看日志中是否显示：
- ✅ 成功连接到向量数据库
- ✅ 集合/表创建成功
- ✅ 初始化完成

如果出现连接错误，请检查：
1. 网络连接是否正常
2. 认证信息是否正确
3. 防火墙规则是否允许连接
4. 向量数据库服务是否正在运行

---

## 故障排除

### 问题 1: 连接超时

**症状**：无法连接到远程向量数据库

**解决方案**：
- 检查网络连接
- 验证服务器地址和端口
- 检查防火墙设置
- 增加连接超时时间（如果支持）

### 问题 2: 认证失败

**症状**：认证错误

**解决方案**：
- 验证用户名、密码或 API Key
- 检查用户权限
- 确认认证方式（Token vs User/Password）

### 问题 3: 维度不匹配

**症状**：嵌入维度错误

**解决方案**：
- 确保 `EMBEDDING_DIM` 与嵌入模型实际维度匹配
- 清空向量数据库并重新索引

### 问题 4: 集合/表已存在

**症状**：集合或表已存在错误

**解决方案**：
- 删除现有集合/表（如果数据可以重新生成）
- 或使用不同的工作空间名称

---

## 推荐配置

根据使用场景选择：

| 场景 | 推荐向量数据库 | 理由 |
|------|---------------|------|
| 小规模部署（< 10万向量） | Qdrant | 简单易用，性能好 |
| 中等规模（10万-100万向量） | Qdrant 或 Milvus | 性能优秀 |
| 大规模（> 100万向量） | Milvus | 专为大规模设计 |
| 已有 PostgreSQL 基础设施 | PostgreSQL (pgvector) | 统一数据库管理 |
| 云原生部署 | Qdrant Cloud 或 Milvus Cloud | 托管服务，无需运维 |
| 成本敏感 | PostgreSQL (pgvector) | 开源，成本低 |

---

## 更多信息

- [LightRAG 官方文档](https://github.com/HKUDS/LightRAG)
- [Qdrant 文档](https://qdrant.tech/documentation/)
- [Milvus 文档](https://milvus.io/docs)
- [pgvector 文档](https://github.com/pgvector/pgvector)

