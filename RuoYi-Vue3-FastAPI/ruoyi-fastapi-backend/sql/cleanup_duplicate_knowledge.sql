-- ----------------------------
-- 清理重复的知识库数据（项目与知识库一对一）
-- 版本：v1.0.0
-- 更新日期：2026-01-01
-- 说明：清理一个项目有多个知识库的情况，保留最新的一个
-- 使用：mysql -u root -p database_name < cleanup_duplicate_knowledge.sql
-- ----------------------------

-- 强烈建议先备份数据库
-- mysqldump -u root -p database_name > backup_$(date +%Y%m%d).sql

SET FOREIGN_KEY_CHECKS = 0;

-- 查找有多个知识库的项目
SELECT 
    project_id,
    COUNT(*) as knowledge_count,
    GROUP_CONCAT(knowledge_id ORDER BY create_time DESC) as knowledge_ids
FROM test_knowledge
GROUP BY project_id
HAVING COUNT(*) > 1;

-- 为每个项目保留最新的知识库，删除其他的
-- 注意：这个操作会删除旧的知识库及其文件，请谨慎执行
-- 建议先手动检查上面的查询结果，确认要删除的知识库ID

-- 示例：删除项目3的旧知识库（保留最新的）
-- DELETE FROM test_knowledge_file WHERE knowledge_id IN (2, 3);
-- DELETE FROM test_knowledge WHERE project_id = 3 AND knowledge_id NOT IN (
--     SELECT knowledge_id FROM (
--         SELECT knowledge_id 
--         FROM test_knowledge 
--         WHERE project_id = 3 
--         ORDER BY create_time DESC 
--         LIMIT 1
--     ) AS latest
-- );

-- 更新所有知识库的 collection_name 为 project_{project_id} 格式
-- 确保 workspace 与项目ID一一对应
UPDATE test_knowledge
SET collection_name = CONCAT('project_', project_id)
WHERE collection_name NOT LIKE CONCAT('project_', project_id);

SET FOREIGN_KEY_CHECKS = 1;

