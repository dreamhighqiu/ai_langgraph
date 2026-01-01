-- 知识库管理相关表

-- 1. 知识库表
DROP TABLE IF EXISTS `test_knowledge`;
CREATE TABLE `test_knowledge` (
    `knowledge_id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '知识库ID',
    `project_id` INT(11) NOT NULL COMMENT '所属项目ID',
    `knowledge_name` VARCHAR(100) NOT NULL COMMENT '知识库名称',
    `collection_name` VARCHAR(255) NOT NULL COMMENT 'Milvus Collection 名称 (workspace)',
    `description` TEXT NULL COMMENT '知识库描述',
    `file_count` INT(11) NOT NULL DEFAULT 0 COMMENT '文件数量',
    `vector_count` INT(11) NOT NULL DEFAULT 0 COMMENT '向量数量',
    `status` CHAR(1) NOT NULL DEFAULT '0' COMMENT '状态：0正常 1停用',
    `create_by` VARCHAR(64) NULL COMMENT '创建者',
    `create_time` DATETIME NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by` VARCHAR(64) NULL COMMENT '更新者',
    `update_time` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark` VARCHAR(500) NULL COMMENT '备注',
    PRIMARY KEY (`knowledge_id`),
    UNIQUE KEY `uk_collection_name` (`collection_name`),
    KEY `idx_project_id` (`project_id`),
    KEY `idx_status` (`status`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识库表';

-- 2. 知识库文件表
DROP TABLE IF EXISTS `test_knowledge_file`;
CREATE TABLE `test_knowledge_file` (
    `file_id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '文件ID',
    `knowledge_id` INT(11) NOT NULL COMMENT '知识库ID',
    `file_name` VARCHAR(255) NOT NULL COMMENT '文件名称',
    `file_path` VARCHAR(500) NOT NULL COMMENT 'MinIO存储路径',
    `file_size` BIGINT NOT NULL DEFAULT 0 COMMENT '文件大小（字节）',
    `doc_id` VARCHAR(255) NULL COMMENT 'LightRAG 文档ID',
    `process_status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '处理状态：pending/processing/completed/failed',
    `process_progress` INT(11) NOT NULL DEFAULT 0 COMMENT '处理进度 0-100',
    `process_start_time` DATETIME NULL COMMENT '处理开始时间',
    `process_end_time` DATETIME NULL COMMENT '处理结束时间',
    `error_msg` TEXT NULL COMMENT '错误信息',
    `vector_count` INT(11) NOT NULL DEFAULT 0 COMMENT '生成向量数量',
    `create_by` VARCHAR(64) NULL COMMENT '创建者',
    `create_time` DATETIME NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`file_id`),
    KEY `idx_knowledge_id` (`knowledge_id`),
    KEY `idx_process_status` (`process_status`),
    KEY `idx_doc_id` (`doc_id`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识库文件表';

-- 3. 添加外键约束（可选）
-- ALTER TABLE `test_knowledge` 
--     ADD CONSTRAINT `fk_knowledge_project` 
--     FOREIGN KEY (`project_id`) REFERENCES `test_project`(`project_id`) ON DELETE CASCADE;

-- ALTER TABLE `test_knowledge_file` 
--     ADD CONSTRAINT `fk_file_knowledge` 
--     FOREIGN KEY (`knowledge_id`) REFERENCES `test_knowledge`(`knowledge_id`) ON DELETE CASCADE;

-- 4. 插入测试数据（可选）
-- INSERT INTO `test_knowledge` 
--     (`project_id`, `knowledge_name`, `collection_name`, `description`, `status`)
-- VALUES
--     (1, '测试知识库1', 'project_1_kb_1', '这是一个测试知识库', '0'),
--     (1, '测试知识库2', 'project_1_kb_2', '这是另一个测试知识库', '0');


