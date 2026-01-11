-- 添加知识库查询模式字段
-- 执行时间: 2026-01-11

ALTER TABLE test_knowledge ADD COLUMN query_mode VARCHAR(20) DEFAULT 'mix' COMMENT 'RAG查询模式：local-实体关系/global-全局模式/hybrid-混合模式/naive-向量搜索/mix-推荐模式/bypass-直接查询';

