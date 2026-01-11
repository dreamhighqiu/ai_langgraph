-- ============================================================================
-- 测试平台 v2.0 数据库升级脚本
-- 功能: 支持统一LangGraph服务架构
-- 执行: mysql -u root -p testing_platform < v2.0_upgrade.sql
-- ============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- 1. 创建Agent执行记录表
-- ============================================================================
CREATE TABLE IF NOT EXISTS test_agent_execution (
    execution_id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '执行ID',
    agent_id VARCHAR(50) NOT NULL COMMENT 'Agent ID',
    agent_type VARCHAR(20) NOT NULL COMMENT 'Agent类型(ui_testing/testcase/requirement/defect)',
    
    -- 输入信息
    user_input TEXT COMMENT '用户输入',
    config JSON COMMENT '配置信息',
    
    -- 执行信息
    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态(pending/running/success/failed)',
    thread_id VARCHAR(100) COMMENT 'LangGraph线程ID',
    start_time DATETIME COMMENT '开始时间',
    end_time DATETIME COMMENT '结束时间',
    duration INT COMMENT '执行时长(毫秒)',
    
    -- 输出信息
    output LONGTEXT COMMENT '输出结果',
    error_message TEXT COMMENT '错误信息',
    tool_calls JSON COMMENT '工具调用记录',
    
    -- 元数据
    executor VARCHAR(50) COMMENT '执行人',
    project_id BIGINT COMMENT '关联项目ID',
    related_id BIGINT COMMENT '关联对象ID(如script_id/testcase_id)',
    related_type VARCHAR(20) COMMENT '关联对象类型',
    
    -- 审计字段
    create_by VARCHAR(50) COMMENT '创建者',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by VARCHAR(50) COMMENT '更新者',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark VARCHAR(500) COMMENT '备注',
    
    INDEX idx_agent_id (agent_id),
    INDEX idx_agent_type (agent_type),
    INDEX idx_status (status),
    INDEX idx_executor (executor),
    INDEX idx_project_id (project_id),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent执行记录表';

-- ============================================================================
-- 2. 优化test_script表（如果字段不存在则添加）
-- ============================================================================
-- 添加script_type字段（如果不存在）
SELECT COUNT(*) INTO @col_exists 
FROM information_schema.columns 
WHERE table_schema = DATABASE() 
AND table_name = 'test_script' 
AND column_name = 'script_type';

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE test_script ADD COLUMN script_type VARCHAR(20) NOT NULL DEFAULT "playwright" COMMENT "脚本类型(playwright/api/k6)" AFTER script_content',
    'SELECT "Column script_type already exists" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加索引（如果不存在）
SELECT COUNT(*) INTO @idx_exists
FROM information_schema.statistics
WHERE table_schema = DATABASE()
AND table_name = 'test_script'
AND index_name = 'idx_script_type';

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX idx_script_type ON test_script(script_type)',
    'SELECT "Index idx_script_type already exists" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================================
-- 3. 添加UI自动化菜单 (3340-3359)
-- ============================================================================
-- 清理已有菜单
DELETE FROM sys_role_menu WHERE menu_id BETWEEN 3340 AND 3369;
DELETE FROM sys_menu WHERE menu_id BETWEEN 3340 AND 3369;

-- UI自动化主菜单（一级菜单）
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
(3340, 'UI自动化', 0, 4, 'ui-automation', NULL, NULL, 'UIAutomation', 1, 0, 'M', '0', '0', NULL, 'monitor', 'admin', NOW(), 'admin', NOW(), 'UI自动化测试（一级菜单）'),

-- UI自动化子菜单
(3341, '脚本生成', 3340, 1, 'generate', 'testing/ui-automation/generate', NULL, 'UIGenerate', 1, 0, 'C', '0', '0', 'testing:ui-automation:generate', 'edit', 'admin', NOW(), 'admin', NOW(), 'AI生成UI测试脚本'),
(3342, '脚本管理', 3340, 2, 'scripts', 'testing/ui-automation/scripts', NULL, 'UIScripts', 1, 0, 'C', '0', '0', 'testing:ui-automation:list', 'list', 'admin', NOW(), 'admin', NOW(), 'UI测试脚本管理'),
(3343, '脚本执行', 3340, 3, 'execute', 'testing/ui-automation/execute', NULL, 'UIExecute', 1, 0, 'C', '0', '0', 'testing:ui-automation:execute', 'video-play', 'admin', NOW(), 'admin', NOW(), '执行UI测试脚本'),
(3344, '测试报告', 3340, 4, 'reports', 'testing/ui-automation/reports', NULL, 'UIReports', 1, 0, 'C', '0', '0', 'testing:ui-automation:report', 'document', 'admin', NOW(), 'admin', NOW(), 'UI测试报告'),

-- UI自动化按钮权限
(3351, '脚本新增', 3342, 1, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:ui-automation:add', '#', 'admin', NOW(), 'admin', NOW(), '新增UI脚本'),
(3352, '脚本修改', 3342, 2, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:ui-automation:edit', '#', 'admin', NOW(), 'admin', NOW(), '修改UI脚本'),
(3353, '脚本删除', 3342, 3, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:ui-automation:remove', '#', 'admin', NOW(), 'admin', NOW(), '删除UI脚本'),
(3354, '脚本执行', 3342, 4, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:ui-automation:execute', '#', 'admin', NOW(), 'admin', NOW(), '执行UI脚本'),
(3355, '查看报告', 3344, 5, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:ui-automation:report:view', '#', 'admin', NOW(), 'admin', NOW(), '查看测试报告'),
(3356, '下载报告', 3344, 6, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:ui-automation:report:download', '#', 'admin', NOW(), 'admin', NOW(), '下载测试报告');

-- ============================================================================
-- 4. 添加Agent控制台菜单 (3360-3369)（一级菜单）
-- ============================================================================
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
-- Agent控制台主菜单（一级菜单）
(3360, 'Agent控制台', 0, 5, 'agent-console', NULL, NULL, 'AgentConsole', 1, 0, 'M', '0', '0', NULL, 'robot', 'admin', NOW(), 'admin', NOW(), 'AI Agent管理控制台（一级菜单）'),

-- Agent控制台子菜单
(3361, 'Agent列表', 3360, 1, 'agents', 'testing/agent-console/agents', NULL, 'AgentList', 1, 0, 'C', '0', '0', 'testing:agent:list', 'list', 'admin', NOW(), 'admin', NOW(), 'Agent列表和状态'),
(3362, '执行历史', 3360, 2, 'history', 'testing/agent-console/history', NULL, 'AgentHistory', 1, 0, 'C', '0', '0', 'testing:agent:history', 'time-range', 'admin', NOW(), 'admin', NOW(), 'Agent执行历史'),

-- Agent控制台按钮权限
(3365, '查看Agent', 3361, 1, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:agent:view', '#', 'admin', NOW(), 'admin', NOW(), '查看Agent详情'),
(3366, '启用Agent', 3361, 2, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:agent:enable', '#', 'admin', NOW(), 'admin', NOW(), '启用Agent'),
(3367, '禁用Agent', 3361, 3, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:agent:disable', '#', 'admin', NOW(), 'admin', NOW(), '禁用Agent'),
(3368, '查看执行记录', 3362, 4, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:agent:execution:view', '#', 'admin', NOW(), 'admin', NOW(), '查看执行记录');

-- ============================================================================
-- 5. 为管理员角色授权
-- ============================================================================
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE menu_id BETWEEN 3340 AND 3369
ON DUPLICATE KEY UPDATE role_id=role_id;

-- ============================================================================
-- 6. 升级完成
-- ============================================================================
SET FOREIGN_KEY_CHECKS = 1;

SELECT '✅ 数据库升级完成！' AS message;
SELECT CONCAT('新增表: test_agent_execution') AS info;
SELECT CONCAT('新增菜单: ', COUNT(*), ' 个') AS menu_count FROM sys_menu WHERE menu_id BETWEEN 3340 AND 3369;

-- 显示新增菜单列表
SELECT menu_id, menu_name, perms, icon FROM sys_menu WHERE menu_id BETWEEN 3340 AND 3369 ORDER BY menu_id;

