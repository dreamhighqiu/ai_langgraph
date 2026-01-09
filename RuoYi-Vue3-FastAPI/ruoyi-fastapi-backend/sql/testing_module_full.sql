-- ============================================================================
-- 测试管理模块完整数据库脚本
-- 版本: 4.0 (完整菜单 + 按钮权限 + 数据表)
-- 说明: 包含测试管理、项目管理、测试用例、需求分析、缺陷分析的完整菜单和按钮
-- 执行方式: 
--   方式1: MySQL客户端执行 source /path/to/testing_module_full.sql
--   方式2: 在 DBeaver/Navicat 等工具中直接执行
-- ============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- 第一部分：菜单权限配置（完整版）
-- ============================================================================

-- 1. 清理已有测试管理相关菜单（2900-2999 + 3300-3499）
DELETE FROM sys_role_menu WHERE menu_id BETWEEN 2900 AND 2999;
DELETE FROM sys_role_menu WHERE menu_id BETWEEN 3300 AND 3499;
DELETE FROM sys_menu WHERE menu_id BETWEEN 2900 AND 2999;
DELETE FROM sys_menu WHERE menu_id BETWEEN 3300 AND 3499;

-- ============================================================================
-- 2. 测试管理根目录 (2900)
-- ============================================================================
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
(2900, '测试管理', 0, 5, 'testing', NULL, NULL, 'Testing', 1, 0, 'M', '0', '0', NULL, 'folder-opened', 'admin', NOW(), 'admin', NOW(), '测试管理根目录');

-- ============================================================================
-- 3. 项目管理菜单 (2901) + 按钮权限 (2911-2919)
-- ============================================================================
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
-- 项目管理菜单
(2901, '项目管理', 2900, 1, 'project', 'testing/project/index', NULL, 'TestProject', 1, 0, 'C', '0', '0', 'testing:project:list', 'folder', 'admin', NOW(), 'admin', NOW(), '测试项目管理'),
-- 项目管理按钮
(2911, '项目查询', 2901, 1, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:project:query', '#', 'admin', NOW(), 'admin', NOW(), '项目查询'),
(2912, '项目新增', 2901, 2, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:project:add', '#', 'admin', NOW(), 'admin', NOW(), '项目新增'),
(2913, '项目修改', 2901, 3, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:project:edit', '#', 'admin', NOW(), 'admin', NOW(), '项目修改'),
(2914, '项目删除', 2901, 4, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:project:remove', '#', 'admin', NOW(), 'admin', NOW(), '项目删除'),
(2915, '项目导出', 2901, 5, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:project:export', '#', 'admin', NOW(), 'admin', NOW(), '项目导出'),
(2916, '项目导入', 2901, 6, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:project:import', '#', 'admin', NOW(), 'admin', NOW(), '项目导入');

-- ============================================================================
-- 4. 测试用例管理菜单 (3300) + 按钮权限 (3301-3319)
-- ============================================================================
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
-- 测试用例菜单
(3300, '测试用例', 2900, 2, 'test-case', 'testing/test-case/index', NULL, 'TestCase', 1, 0, 'C', '0', '0', 'testing:testcase:list', 'document', 'admin', NOW(), 'admin', NOW(), '测试用例管理'),
-- 测试用例按钮
(3301, '用例查询', 3300, 1, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:testcase:query', '#', 'admin', NOW(), 'admin', NOW(), '测试用例查询'),
(3302, '用例新增', 3300, 2, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:testcase:add', '#', 'admin', NOW(), 'admin', NOW(), '测试用例新增'),
(3303, '用例修改', 3300, 3, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:testcase:edit', '#', 'admin', NOW(), 'admin', NOW(), '测试用例修改'),
(3304, '用例删除', 3300, 4, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:testcase:remove', '#', 'admin', NOW(), 'admin', NOW(), '测试用例删除'),
(3305, '用例导出', 3300, 5, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:testcase:export', '#', 'admin', NOW(), 'admin', NOW(), '测试用例导出'),
(3306, '用例导入', 3300, 6, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:testcase:import', '#', 'admin', NOW(), 'admin', NOW(), '测试用例导入'),
(3307, 'AI生成用例', 3300, 7, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:testcase:generate', '#', 'admin', NOW(), 'admin', NOW(), 'AI智能生成测试用例'),
(3308, '用例批量操作', 3300, 8, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:testcase:batch', '#', 'admin', NOW(), 'admin', NOW(), '测试用例批量操作'),
(3309, '用例移动/复制', 3300, 9, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:testcase:move', '#', 'admin', NOW(), 'admin', NOW(), '测试用例移动/复制'),
-- 文件夹管理按钮（属于测试用例子功能）
(3310, '文件夹列表', 3300, 10, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:folder:list', '#', 'admin', NOW(), 'admin', NOW(), '文件夹列表'),
(3311, '文件夹新增', 3300, 11, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:folder:add', '#', 'admin', NOW(), 'admin', NOW(), '文件夹新增'),
(3312, '文件夹修改', 3300, 12, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:folder:edit', '#', 'admin', NOW(), 'admin', NOW(), '文件夹修改'),
(3313, '文件夹删除', 3300, 13, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:folder:remove', '#', 'admin', NOW(), 'admin', NOW(), '文件夹删除'),
(3314, '文件夹移动', 3300, 14, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:folder:move', '#', 'admin', NOW(), 'admin', NOW(), '文件夹移动');

-- ============================================================================
-- 5. 需求分析菜单 (3320) + 按钮权限 (3321-3329)
-- ============================================================================
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
-- 需求分析菜单
(3320, '需求分析', 2900, 3, 'requirement-analysis', 'testing/requirement-analysis/index', NULL, 'RequirementAnalysis', 1, 0, 'C', '0', '0', 'testing:requirement:list', 'reading', 'admin', NOW(), 'admin', NOW(), '需求分析管理'),
-- 需求分析按钮
(3321, '需求查询', 3320, 1, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:requirement:query', '#', 'admin', NOW(), 'admin', NOW(), '需求分析查询'),
(3322, '需求新增', 3320, 2, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:requirement:add', '#', 'admin', NOW(), 'admin', NOW(), '需求分析新增'),
(3323, '需求修改', 3320, 3, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:requirement:edit', '#', 'admin', NOW(), 'admin', NOW(), '需求分析修改'),
(3324, '需求删除', 3320, 4, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:requirement:remove', '#', 'admin', NOW(), 'admin', NOW(), '需求分析删除'),
(3325, '需求导出', 3320, 5, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:requirement:export', '#', 'admin', NOW(), 'admin', NOW(), '需求分析导出'),
(3326, '需求导入', 3320, 6, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:requirement:import', '#', 'admin', NOW(), 'admin', NOW(), '需求分析导入'),
(3327, 'AI分析需求', 3320, 7, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:requirement:analyze', '#', 'admin', NOW(), 'admin', NOW(), 'AI智能分析需求'),
(3328, 'AI生成测试', 3320, 8, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:requirement:generate', '#', 'admin', NOW(), 'admin', NOW(), 'AI根据需求生成测试'),
(3329, '下载分析报告', 3320, 9, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:requirement:download', '#', 'admin', NOW(), 'admin', NOW(), '下载需求分析报告');

-- ============================================================================
-- 6. 缺陷分析菜单 (3330) + 按钮权限 (3331-3339)
-- ============================================================================
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
-- 缺陷分析菜单
(3330, '缺陷分析', 2900, 4, 'defect-analysis', 'testing/defect-analysis/index', NULL, 'DefectAnalysis', 1, 0, 'C', '0', '0', 'testing:defect:list', 'warning', 'admin', NOW(), 'admin', NOW(), '缺陷分析管理'),
-- 缺陷分析按钮
(3331, '缺陷查询', 3330, 1, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:defect:query', '#', 'admin', NOW(), 'admin', NOW(), '缺陷分析查询'),
(3332, '缺陷新增', 3330, 2, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:defect:add', '#', 'admin', NOW(), 'admin', NOW(), '缺陷分析新增'),
(3333, '缺陷修改', 3330, 3, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:defect:edit', '#', 'admin', NOW(), 'admin', NOW(), '缺陷分析修改'),
(3334, '缺陷删除', 3330, 4, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:defect:remove', '#', 'admin', NOW(), 'admin', NOW(), '缺陷分析删除'),
(3335, '缺陷导出', 3330, 5, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:defect:export', '#', 'admin', NOW(), 'admin', NOW(), '缺陷分析导出'),
(3336, '缺陷导入', 3330, 6, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:defect:import', '#', 'admin', NOW(), 'admin', NOW(), '缺陷分析导入'),
(3337, 'AI分析缺陷', 3330, 7, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:defect:analyze', '#', 'admin', NOW(), 'admin', NOW(), 'AI智能分析缺陷'),
(3338, '查看思维导图', 3330, 8, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:defect:mindmap', '#', 'admin', NOW(), 'admin', NOW(), '查看缺陷思维导图'),
(3339, '下载分析报告', 3330, 9, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:defect:download', '#', 'admin', NOW(), 'admin', NOW(), '下载缺陷分析报告');

-- ============================================================================
-- 7. AI智能助手菜单 (3340) + 按钮权限 (3341-3349)
-- ============================================================================
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
-- AI助手菜单（隐藏，作为按钮权限控制使用）
(3340, 'AI智能助手', 2900, 5, 'ai-chat', '', NULL, 'AIChat', 1, 0, 'M', '1', '0', 'testing:ai:chat', 'chat-dot-round', 'admin', NOW(), 'admin', NOW(), 'AI智能对话助手'),
-- AI助手按钮
(3341, 'AI对话', 3340, 1, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:ai:chat', '#', 'admin', NOW(), 'admin', NOW(), 'AI智能对话'),
(3342, '线程管理', 3340, 2, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:ai:thread', '#', 'admin', NOW(), 'admin', NOW(), 'AI对话线程管理'),
(3343, '历史记录', 3340, 3, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:ai:history', '#', 'admin', NOW(), 'admin', NOW(), 'AI对话历史记录');

-- ============================================================================
-- 8. 知识库管理菜单 (2920) + 按钮权限 (2921-2929)
-- ============================================================================
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
-- 知识库管理菜单
(2920, '知识库管理', 2900, 6, 'knowledge', 'testing/knowledge/index', NULL, 'Knowledge', 1, 0, 'C', '0', '0', 'testing:knowledge:list', 'collection', 'admin', NOW(), 'admin', NOW(), '知识库管理'),
-- 知识库管理按钮
(2921, '知识库查询', 2920, 1, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:knowledge:query', '#', 'admin', NOW(), 'admin', NOW(), '知识库查询'),
(2922, '知识库新增', 2920, 2, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:knowledge:add', '#', 'admin', NOW(), 'admin', NOW(), '知识库新增'),
(2923, '知识库修改', 2920, 3, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:knowledge:edit', '#', 'admin', NOW(), 'admin', NOW(), '知识库修改'),
(2924, '知识库删除', 2920, 4, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:knowledge:remove', '#', 'admin', NOW(), 'admin', NOW(), '知识库删除'),
(2925, '文件上传', 2920, 5, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:knowledge:upload', '#', 'admin', NOW(), 'admin', NOW(), '知识库文件上传'),
(2926, '知识库导出', 2920, 6, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:knowledge:export', '#', 'admin', NOW(), 'admin', NOW(), '知识库导出'),
(2927, '知识库检索', 2920, 7, '', '', NULL, '', 1, 0, 'F', '0', '0', 'testing:knowledge:search', '#', 'admin', NOW(), 'admin', NOW(), '知识库RAG检索');

-- ============================================================================
-- 9. 为管理员角色绑定所有权限（role_id=1 是超级管理员）
-- ============================================================================
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE menu_id BETWEEN 2900 AND 2999;

INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE menu_id BETWEEN 3300 AND 3399;


-- ============================================================================
-- 第二部分：数据库表创建
-- ============================================================================

-- 1. 测试项目表（如果不存在则创建）
CREATE TABLE IF NOT EXISTS test_project (
    project_id      INT             NOT NULL AUTO_INCREMENT COMMENT '项目ID',
    project_name    VARCHAR(200)    NOT NULL                COMMENT '项目名称',
    project_key     VARCHAR(50)                             COMMENT '项目标识',
    description     TEXT                                    COMMENT '项目描述',
    status          VARCHAR(20)     DEFAULT '0'             COMMENT '状态(0正常 1停用)',
    create_by       VARCHAR(64)     DEFAULT ''              COMMENT '创建者',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by       VARCHAR(64)     DEFAULT ''              COMMENT '更新者',
    update_time     DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark          VARCHAR(500)    DEFAULT ''              COMMENT '备注',
    PRIMARY KEY (project_id),
    INDEX idx_project_name (project_name),
    INDEX idx_project_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='测试项目表';


-- 2. 文件夹表
CREATE TABLE IF NOT EXISTS test_folder (
    folder_id       INT             NOT NULL AUTO_INCREMENT COMMENT '文件夹ID',
    project_id      INT             NOT NULL                COMMENT '所属项目ID',
    parent_id       INT                                     COMMENT '父文件夹ID',
    folder_name     VARCHAR(255)    NOT NULL                COMMENT '文件夹名称',
    description     TEXT                                    COMMENT '文件夹描述',
    order_num       INT             DEFAULT 0               COMMENT '显示顺序',
    status          VARCHAR(20)     DEFAULT '0'             COMMENT '状态(0正常 1停用)',
    create_by       VARCHAR(64)     DEFAULT ''              COMMENT '创建者',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by       VARCHAR(64)     DEFAULT ''              COMMENT '更新者',
    update_time     DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark          VARCHAR(500)    DEFAULT ''              COMMENT '备注',
    PRIMARY KEY (folder_id),
    INDEX idx_folder_project_id (project_id),
    INDEX idx_folder_parent_id (parent_id),
    INDEX idx_folder_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='测试用例文件夹表';


-- 3. 测试用例表
CREATE TABLE IF NOT EXISTS test_case (
    case_id             INT             NOT NULL AUTO_INCREMENT COMMENT '用例ID',
    project_id          INT             NOT NULL                COMMENT '项目ID',
    folder_id           INT                                     COMMENT '文件夹ID',
    case_identifier     VARCHAR(50)                             COMMENT '用例标识',
    case_name           VARCHAR(500)    NOT NULL                COMMENT '用例名称',
    case_type           VARCHAR(50)     DEFAULT 'functional'    COMMENT '用例类型',
    priority            VARCHAR(20)     DEFAULT 'medium'        COMMENT '优先级(high/medium/low)',
    status              VARCHAR(20)     DEFAULT 'draft'         COMMENT '状态(draft/pending/approved/deprecated)',
    preconditions       TEXT                                    COMMENT '前置条件',
    test_case_steps     JSON                                    COMMENT '测试步骤(JSON)',
    expected_result     TEXT                                    COMMENT '预期结果',
    actual_result       TEXT                                    COMMENT '实际结果',
    test_data           JSON                                    COMMENT '测试数据(JSON)',
    -- BDD 格式字段
    bdd_feature         TEXT                                    COMMENT 'BDD Feature',
    bdd_scenario        TEXT                                    COMMENT 'BDD Scenario',
    bdd_given           TEXT                                    COMMENT 'BDD Given',
    bdd_when            TEXT                                    COMMENT 'BDD When',
    bdd_then            TEXT                                    COMMENT 'BDD Then',
    -- 自动化相关
    is_automated        TINYINT         DEFAULT 0               COMMENT '是否已自动化(0否 1是)',
    automation_script_id INT                                    COMMENT '自动化脚本ID',
    -- 其他
    tags                VARCHAR(500)                            COMMENT '标签(逗号分隔)',
    create_by           VARCHAR(64)     DEFAULT ''              COMMENT '创建者',
    create_time         DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by           VARCHAR(64)     DEFAULT ''              COMMENT '更新者',
    update_time         DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark              VARCHAR(500)    DEFAULT ''              COMMENT '备注',
    PRIMARY KEY (case_id),
    INDEX idx_case_project_id (project_id),
    INDEX idx_case_folder_id (folder_id),
    INDEX idx_case_status (status),
    INDEX idx_case_priority (priority),
    INDEX idx_case_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='测试用例表';


-- 4. 需求分析表
CREATE TABLE IF NOT EXISTS test_requirement_analysis (
    requirement_id          INT             NOT NULL AUTO_INCREMENT COMMENT '需求ID',
    project_id              INT             NOT NULL                COMMENT '项目ID',
    knowledge_id            INT                                     COMMENT '关联知识库ID',
    requirement_identifier  VARCHAR(50)                             COMMENT '需求标识',
    requirement_name        VARCHAR(200)    NOT NULL                COMMENT '需求名称',
    requirement_type        VARCHAR(50)     DEFAULT 'functional'    COMMENT '需求类型',
    priority                VARCHAR(20)     DEFAULT 'medium'        COMMENT '优先级',
    module                  VARCHAR(200)                            COMMENT '所属模块',
    description             TEXT                                    COMMENT '需求描述',
    acceptance_criteria     TEXT                                    COMMENT '验收标准',
    functional_requirements TEXT                                    COMMENT '功能需求',
    non_functional_requirements TEXT                                COMMENT '非功能需求',
    business_rules          TEXT                                    COMMENT '业务规则',
    dependencies            JSON                                    COMMENT '依赖关系(JSON)',
    stakeholders            JSON                                    COMMENT '干系人(JSON)',
    use_rag                 TINYINT         DEFAULT 0               COMMENT '是否使用RAG(0否1是)',
    rag_context             TEXT                                    COMMENT 'RAG检索上下文',
    status                  VARCHAR(20)     DEFAULT 'draft'         COMMENT '状态(draft/pending/approved/rejected)',
    tags                    VARCHAR(500)                            COMMENT '标签(逗号分隔)',
    create_by               VARCHAR(64)     DEFAULT ''              COMMENT '创建者',
    create_time             DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by               VARCHAR(64)     DEFAULT ''              COMMENT '更新者',
    update_time             DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark                  VARCHAR(500)    DEFAULT ''              COMMENT '备注',
    PRIMARY KEY (requirement_id),
    INDEX idx_req_project_id (project_id),
    INDEX idx_req_status (status),
    INDEX idx_req_priority (priority),
    INDEX idx_req_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='需求分析表';


-- 5. 缺陷分析表
CREATE TABLE IF NOT EXISTS test_defect_analysis (
    analysis_id             INT             NOT NULL AUTO_INCREMENT COMMENT '分析ID',
    project_id              INT             NOT NULL                COMMENT '项目ID',
    knowledge_id            INT                                     COMMENT '关联知识库ID',
    defect_id               VARCHAR(100)                            COMMENT '关联缺陷ID',
    analysis_name           VARCHAR(200)    NOT NULL                COMMENT '分析名称',
    defect_title            VARCHAR(200)                            COMMENT '缺陷标题',
    defect_description      TEXT                                    COMMENT '缺陷描述',
    severity                VARCHAR(20)     DEFAULT 'medium'        COMMENT '严重程度(critical/high/medium/low)',
    priority                VARCHAR(20)     DEFAULT 'medium'        COMMENT '优先级(urgent/high/medium/low)',
    defect_type             VARCHAR(50)                             COMMENT '缺陷类型',
    category                VARCHAR(100)                            COMMENT '详细分类',
    affected_phase          VARCHAR(50)                             COMMENT '影响阶段',
    detection_phase         VARCHAR(50)                             COMMENT '发现阶段',
    executive_summary       TEXT                                    COMMENT '缺陷概述',
    root_cause_analysis     JSON                                    COMMENT '根本原因分析(JSON)',
    impact_analysis         JSON                                    COMMENT '影响分析(JSON)',
    reproduction_steps      JSON                                    COMMENT '复现步骤(JSON)',
    affected_modules        JSON                                    COMMENT '受影响模块(JSON)',
    fix_suggestions         JSON                                    COMMENT '修复建议(JSON)',
    test_suggestions        JSON                                    COMMENT '测试建议(JSON)',
    prevention_measures     JSON                                    COMMENT '预防措施(JSON)',
    similar_defects         JSON                                    COMMENT '相似缺陷(JSON)',
    use_rag                 TINYINT         DEFAULT 0               COMMENT '是否使用RAG(0否1是)',
    rag_context             TEXT                                    COMMENT 'RAG检索上下文',
    mindmap_data            JSON                                    COMMENT '思维导图数据(JSON)',
    mindmap_url             VARCHAR(500)                            COMMENT '思维导图图片URL',
    status                  VARCHAR(20)     DEFAULT 'draft'         COMMENT '状态(draft/analyzing/completed/failed)',
    process_status          VARCHAR(20)                             COMMENT '处理状态',
    error_message           TEXT                                    COMMENT '错误信息',
    fix_status              VARCHAR(20)                             COMMENT '修复状态',
    fix_time_estimate       VARCHAR(50)                             COMMENT '预计修复时间',
    actual_fix_time         DATETIME                                COMMENT '实际修复时间',
    tags                    VARCHAR(500)                            COMMENT '标签(逗号分隔)',
    create_by               VARCHAR(64)     DEFAULT ''              COMMENT '创建者',
    create_time             DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by               VARCHAR(64)     DEFAULT ''              COMMENT '更新者',
    update_time             DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark                  VARCHAR(500)    DEFAULT ''              COMMENT '备注',
    PRIMARY KEY (analysis_id),
    INDEX idx_defect_project_id (project_id),
    INDEX idx_defect_severity (severity),
    INDEX idx_defect_priority (priority),
    INDEX idx_defect_status (status),
    INDEX idx_defect_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='缺陷分析表';


-- 6. 测试步骤表（独立表，便于管理和查询）
CREATE TABLE IF NOT EXISTS test_case_step (
    step_id             INT             NOT NULL AUTO_INCREMENT COMMENT '步骤ID',
    case_id             INT             NOT NULL                COMMENT '测试用例ID',
    step_number         INT             NOT NULL                COMMENT '步骤序号',
    action              TEXT            NOT NULL                COMMENT '操作步骤描述',
    expected_result     TEXT                                    COMMENT '预期结果',
    actual_result       TEXT                                    COMMENT '实际结果(执行时填写)',
    status              VARCHAR(20)     DEFAULT 'pending'       COMMENT '步骤状态(pending/passed/failed/blocked)',
    step_type           VARCHAR(20)                             COMMENT 'BDD步骤类型(given/when/then/and/but)',
    test_data           TEXT                                    COMMENT '测试数据',
    screenshot          VARCHAR(500)                            COMMENT '截图路径',
    notes               TEXT                                    COMMENT '备注',
    create_by           VARCHAR(64)     DEFAULT ''              COMMENT '创建者',
    create_time         DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by           VARCHAR(64)     DEFAULT ''              COMMENT '更新者',
    update_time         DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (step_id),
    INDEX idx_step_case_id (case_id),
    INDEX idx_step_number (step_number),
    CONSTRAINT fk_step_case_id FOREIGN KEY (case_id) REFERENCES test_case(case_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='测试用例步骤表';


-- 7. 测试计划表
CREATE TABLE IF NOT EXISTS test_plan (
    plan_id             INT             NOT NULL AUTO_INCREMENT COMMENT '计划ID',
    identifier          VARCHAR(50)     UNIQUE                  COMMENT '计划标识符(如TP-001)',
    project_id          INT             NOT NULL                COMMENT '项目ID',
    name                VARCHAR(200)    NOT NULL                COMMENT '计划名称',
    description         TEXT                                    COMMENT '计划描述',
    scope               TEXT                                    COMMENT '测试范围',
    objectives          TEXT                                    COMMENT '测试目标',
    start_date          DATE                                    COMMENT '开始日期',
    end_date            DATE                                    COMMENT '结束日期',
    status              VARCHAR(20)     DEFAULT 'draft'         COMMENT '状态(draft/ready/in_progress/completed/archived)',
    owner               VARCHAR(100)                            COMMENT '负责人',
    testers             JSON                                    COMMENT '测试人员列表',
    test_environment    TEXT                                    COMMENT '测试环境描述',
    test_data_requirements TEXT                                 COMMENT '测试数据需求',
    entry_criteria      TEXT                                    COMMENT '入口标准',
    exit_criteria       TEXT                                    COMMENT '出口标准',
    risks               JSON                                    COMMENT '风险列表',
    mitigations         JSON                                    COMMENT '缓解措施',
    total_cases         INT             DEFAULT 0               COMMENT '总用例数',
    executed_cases      INT             DEFAULT 0               COMMENT '已执行用例数',
    passed_cases        INT             DEFAULT 0               COMMENT '通过用例数',
    failed_cases        INT             DEFAULT 0               COMMENT '失败用例数',
    blocked_cases       INT             DEFAULT 0               COMMENT '阻塞用例数',
    progress            INT             DEFAULT 0               COMMENT '进度百分比',
    version             INT             DEFAULT 1               COMMENT '版本号(乐观锁)',
    create_by           VARCHAR(64)     DEFAULT ''              COMMENT '创建者',
    create_time         DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by           VARCHAR(64)     DEFAULT ''              COMMENT '更新者',
    update_time         DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    remark              VARCHAR(500)    DEFAULT ''              COMMENT '备注',
    PRIMARY KEY (plan_id),
    INDEX idx_plan_project_id (project_id),
    INDEX idx_plan_status (status),
    INDEX idx_plan_start_date (start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='测试计划表';


-- 8. 测试运行表
CREATE TABLE IF NOT EXISTS test_run (
    run_id              INT             NOT NULL AUTO_INCREMENT COMMENT '运行ID',
    identifier          VARCHAR(50)     UNIQUE                  COMMENT '运行标识符(如TR-001)',
    plan_id             INT                                     COMMENT '测试计划ID',
    project_id          INT             NOT NULL                COMMENT '项目ID',
    name                VARCHAR(200)    NOT NULL                COMMENT '运行名称',
    description         TEXT                                    COMMENT '运行描述',
    status              VARCHAR(20)     DEFAULT 'pending'       COMMENT '状态(pending/running/completed/aborted)',
    assigned_to         VARCHAR(100)                            COMMENT '分配给',
    started_at          DATETIME                                COMMENT '开始时间',
    completed_at        DATETIME                                COMMENT '完成时间',
    total_cases         INT             DEFAULT 0               COMMENT '总用例数',
    passed              INT             DEFAULT 0               COMMENT '通过数',
    failed              INT             DEFAULT 0               COMMENT '失败数',
    blocked             INT             DEFAULT 0               COMMENT '阻塞数',
    skipped             INT             DEFAULT 0               COMMENT '跳过数',
    environment         VARCHAR(200)                            COMMENT '测试环境',
    build_version       VARCHAR(100)                            COMMENT '构建版本',
    create_by           VARCHAR(64)     DEFAULT ''              COMMENT '创建者',
    create_time         DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by           VARCHAR(64)     DEFAULT ''              COMMENT '更新者',
    update_time         DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (run_id),
    INDEX idx_run_plan_id (plan_id),
    INDEX idx_run_project_id (project_id),
    INDEX idx_run_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='测试运行表';


-- 9. 测试结果表
CREATE TABLE IF NOT EXISTS test_result (
    result_id           INT             NOT NULL AUTO_INCREMENT COMMENT '结果ID',
    case_id             INT             NOT NULL                COMMENT '测试用例ID',
    plan_id             INT                                     COMMENT '测试计划ID',
    run_id              INT                                     COMMENT '测试运行ID',
    project_id          INT             NOT NULL                COMMENT '项目ID',
    status              VARCHAR(20)     DEFAULT 'pending'       COMMENT '状态(pending/passed/failed/blocked/skipped/retest)',
    executed_by         VARCHAR(100)                            COMMENT '执行人',
    executed_at         DATETIME                                COMMENT '执行时间',
    duration            FLOAT           DEFAULT 0               COMMENT '执行时长(秒)',
    step_results        JSON                                    COMMENT '步骤执行结果列表',
    defect_ids          JSON                                    COMMENT '关联的缺陷ID列表',
    attachments         JSON                                    COMMENT '附件列表',
    comment             TEXT                                    COMMENT '执行备注',
    actual_result       TEXT                                    COMMENT '实际结果',
    environment         VARCHAR(200)                            COMMENT '执行环境',
    browser             VARCHAR(100)                            COMMENT '浏览器',
    device              VARCHAR(100)                            COMMENT '设备',
    is_automated        TINYINT         DEFAULT 0               COMMENT '是否自动化执行',
    automation_log      TEXT                                    COMMENT '自动化执行日志',
    version             INT             DEFAULT 1               COMMENT '版本号',
    create_by           VARCHAR(64)     DEFAULT ''              COMMENT '创建者',
    create_time         DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by           VARCHAR(64)     DEFAULT ''              COMMENT '更新者',
    update_time         DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (result_id),
    INDEX idx_result_case_id (case_id),
    INDEX idx_result_plan_id (plan_id),
    INDEX idx_result_run_id (run_id),
    INDEX idx_result_status (status),
    INDEX idx_result_executed_at (executed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='测试结果表';


-- 10. 审计日志表
CREATE TABLE IF NOT EXISTS test_audit_log (
    log_id              INT             NOT NULL AUTO_INCREMENT COMMENT '日志ID',
    entity_type         VARCHAR(50)     NOT NULL                COMMENT '实体类型(test_case/test_plan/project等)',
    entity_id           INT             NOT NULL                COMMENT '实体ID',
    entity_identifier   VARCHAR(100)                            COMMENT '实体标识符',
    action              VARCHAR(50)     NOT NULL                COMMENT '操作类型(create/update/delete/execute等)',
    action_desc         VARCHAR(200)                            COMMENT '操作描述',
    old_value           JSON                                    COMMENT '变更前的值',
    new_value           JSON                                    COMMENT '变更后的值',
    diff                JSON                                    COMMENT '差异详情',
    user_id             INT                                     COMMENT '操作人ID',
    user_name           VARCHAR(100)                            COMMENT '操作人姓名',
    ip_address          VARCHAR(50)                             COMMENT 'IP地址',
    user_agent          VARCHAR(500)                            COMMENT '用户代理',
    project_id          INT                                     COMMENT '项目ID',
    created_at          DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (log_id),
    INDEX idx_audit_entity_type (entity_type),
    INDEX idx_audit_entity_id (entity_id),
    INDEX idx_audit_action (action),
    INDEX idx_audit_user_id (user_id),
    INDEX idx_audit_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='审计日志表';


-- 11. 版本历史表
CREATE TABLE IF NOT EXISTS test_version_history (
    history_id          INT             NOT NULL AUTO_INCREMENT COMMENT '历史ID',
    entity_type         VARCHAR(50)     NOT NULL                COMMENT '实体类型',
    entity_id           INT             NOT NULL                COMMENT '实体ID',
    version_number      INT             NOT NULL                COMMENT '版本号',
    snapshot            JSON            NOT NULL                COMMENT '实体快照',
    change_summary      VARCHAR(500)                            COMMENT '变更摘要',
    change_details      JSON                                    COMMENT '变更详情',
    created_by          VARCHAR(100)                            COMMENT '创建人',
    created_at          DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (history_id),
    INDEX idx_version_entity_type (entity_type),
    INDEX idx_version_entity_id (entity_id),
    INDEX idx_version_number (version_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='版本历史表';


-- 12. AI对话线程表
CREATE TABLE IF NOT EXISTS test_ai_thread (
    thread_id           VARCHAR(100)    NOT NULL                COMMENT '线程ID',
    user_id             INT                                     COMMENT '用户ID',
    assistant_id        VARCHAR(100)                            COMMENT '助手ID',
    title               VARCHAR(200)    DEFAULT '新对话'         COMMENT '对话标题',
    project_id          INT                                     COMMENT '关联项目ID',
    folder_id           INT                                     COMMENT '关联文件夹ID',
    status              VARCHAR(20)     DEFAULT 'active'        COMMENT '状态(active/archived/deleted)',
    has_interrupt       TINYINT         DEFAULT 0               COMMENT '是否有中断',
    message_count       INT             DEFAULT 0               COMMENT '消息数量',
    metadata            JSON                                    COMMENT '元数据(JSON)',
    create_time         DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time         DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (thread_id),
    INDEX idx_thread_user_id (user_id),
    INDEX idx_thread_project_id (project_id),
    INDEX idx_thread_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='AI对话线程表';


SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- 执行完成提示
-- ============================================================================
SELECT '============================================================' AS '分割线';
SELECT '✅ 测试管理模块数据库初始化完成!' AS '状态';
SELECT '============================================================' AS '分割线';
SELECT '📂 菜单配置清单:' AS '类型', 
       '2900-测试管理根目录' AS '说明';
SELECT '📁 项目管理(2901)' AS '菜单', 
       '2911-2916 按钮权限' AS '按钮';
SELECT '📄 测试用例(3300)' AS '菜单', 
       '3301-3314 按钮权限(含文件夹)' AS '按钮';
SELECT '📖 需求分析(3320)' AS '菜单', 
       '3321-3329 按钮权限' AS '按钮';
SELECT '⚠️ 缺陷分析(3330)' AS '菜单', 
       '3331-3339 按钮权限' AS '按钮';
SELECT '🤖 AI智能助手(3340)' AS '菜单', 
       '3341-3343 按钮权限' AS '按钮';
SELECT '📚 知识库管理(2920)' AS '菜单', 
       '2921-2927 按钮权限' AS '按钮';
SELECT '============================================================' AS '分割线';
SELECT '📌 数据表: test_project, test_folder, test_case, test_requirement_analysis, test_defect_analysis, test_ai_thread' AS '表清单';
SELECT '📌 请重新登录系统以刷新菜单权限' AS '提示';
SELECT '============================================================' AS '分割线';
