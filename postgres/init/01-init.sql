-- PostgreSQL 初始化脚本

-- 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建 schema
CREATE SCHEMA IF NOT EXISTS ai_langgraph;

-- 设置默认 schema
SET search_path TO ai_langgraph, public;

-- 创建系统配置表
CREATE TABLE IF NOT EXISTS system_config (
  id SERIAL PRIMARY KEY,
  config_key VARCHAR(100) NOT NULL UNIQUE,
  config_value TEXT,
  description VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为系统配置表添加触发器
DROP TRIGGER IF EXISTS update_system_config_updated_at ON system_config;
CREATE TRIGGER update_system_config_updated_at
    BEFORE UPDATE ON system_config
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 插入初始配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('app_name', 'AI LangGraph', '应用名称'),
('app_version', '1.0.0', '应用版本'),
('initialized_at', NOW()::TEXT, '初始化时间')
ON CONFLICT (config_key) DO UPDATE SET config_value = EXCLUDED.config_value;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 为用户表添加触发器
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 创建向量存储表
CREATE TABLE IF NOT EXISTS vector_store (
  id BIGSERIAL PRIMARY KEY,
  collection_name VARCHAR(100) NOT NULL,
  document_id VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),  -- OpenAI embeddings 维度
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 为向量存储表添加触发器
DROP TRIGGER IF EXISTS update_vector_store_updated_at ON vector_store;
CREATE TRIGGER update_vector_store_updated_at
    BEFORE UPDATE ON vector_store
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 创建向量索引（使用 HNSW 算法）
CREATE INDEX IF NOT EXISTS idx_vector_store_embedding ON vector_store 
USING hnsw (embedding vector_cosine_ops);

-- 创建其他索引
CREATE INDEX IF NOT EXISTS idx_vector_store_collection ON vector_store(collection_name);
CREATE INDEX IF NOT EXISTS idx_vector_store_document ON vector_store(document_id);
CREATE INDEX IF NOT EXISTS idx_vector_store_metadata ON vector_store USING gin(metadata);

-- 创建对话历史表
CREATE TABLE IF NOT EXISTS chat_history (
  id BIGSERIAL PRIMARY KEY,
  session_id VARCHAR(100) NOT NULL,
  user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
  role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_chat_history_session ON chat_history(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_user ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created ON chat_history(created_at);

-- 创建向量搜索函数
CREATE OR REPLACE FUNCTION search_similar_vectors(
  query_embedding vector(1536),
  collection VARCHAR(100),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 10
)
RETURNS TABLE (
  id BIGINT,
  document_id VARCHAR(255),
  content TEXT,
  metadata JSONB,
  similarity FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    v.id,
    v.document_id,
    v.content,
    v.metadata,
    1 - (v.embedding <=> query_embedding) AS similarity
  FROM vector_store v
  WHERE v.collection_name = collection
    AND 1 - (v.embedding <=> query_embedding) > match_threshold
  ORDER BY v.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- 输出初始化完成消息
DO $$
BEGIN
  RAISE NOTICE 'PostgreSQL 数据库初始化完成！pgvector 扩展已启用。';
END $$;

