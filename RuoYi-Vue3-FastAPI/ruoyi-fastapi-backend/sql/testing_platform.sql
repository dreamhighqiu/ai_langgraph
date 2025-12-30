-- ----------------------------
-- AI智能测试平台数据库表结构
-- ----------------------------

-- ----------------------------
-- 1. 测试项目表
-- ----------------------------
DROP TABLE IF EXISTS `test_project`;
CREATE TABLE `test_project` (
  `project_id` bigint NOT NULL AUTO_INCREMENT COMMENT '项目ID',
  `project_name` varchar(100) NOT NULL COMMENT '项目名称',
  `project_type` varchar(50) NOT NULL DEFAULT 'api' COMMENT '项目类型：performance/ui/api',
  `description` text COMMENT '项目描述',
  `status` char(1) NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
  `del_flag` char(1) NOT NULL DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`project_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='测试项目表';

-- ----------------------------
-- 2. 测试脚本表
-- ----------------------------
DROP TABLE IF EXISTS `test_script`;
CREATE TABLE `test_script` (
  `script_id` bigint NOT NULL AUTO_INCREMENT COMMENT '脚本ID',
  `project_id` bigint NOT NULL COMMENT '项目ID',
  `script_name` varchar(100) NOT NULL COMMENT '脚本名称',
  `script_type` varchar(50) NOT NULL COMMENT '脚本类型：k6/playwright/api',
  `script_content` longtext COMMENT '脚本内容',
  `script_file_path` varchar(500) DEFAULT NULL COMMENT 'MinIO存储路径',
  `version` varchar(20) NOT NULL DEFAULT '1.0.0' COMMENT '版本号',
  `config` json DEFAULT NULL COMMENT '配置参数',
  `agent_id` varchar(100) DEFAULT NULL COMMENT 'Agent ID',
  `generation_prompt` text COMMENT '生成提示词',
  `status` char(1) NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
  `del_flag` char(1) NOT NULL DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
  `create_by` varchar(64) DEFAULT '' COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(64) DEFAULT '' COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`script_id`),
  KEY `idx_project_id` (`project_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='测试脚本表';

-- ----------------------------
-- 3. 测试执行记录表
-- ----------------------------
DROP TABLE IF EXISTS `test_execution`;
CREATE TABLE `test_execution` (
  `execution_id` bigint NOT NULL AUTO_INCREMENT COMMENT '执行ID',
  `script_id` bigint NOT NULL COMMENT '脚本ID',
  `execution_type` varchar(20) NOT NULL DEFAULT 'manual' COMMENT '执行类型：manual/scheduled',
  `execution_status` varchar(20) NOT NULL DEFAULT 'pending' COMMENT '执行状态：pending/running/success/failed/cancelled',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `duration` int DEFAULT NULL COMMENT '执行时长（秒）',
  `thread_id` varchar(100) DEFAULT NULL COMMENT 'LangGraph线程ID',
  `agent_id` varchar(100) DEFAULT NULL COMMENT 'Agent ID',
  `config` json DEFAULT NULL COMMENT '执行配置',
  `result` json DEFAULT NULL COMMENT '执行结果',
  `error_msg` text COMMENT '错误信息',
  `executor` varchar(64) DEFAULT '' COMMENT '执行者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`execution_id`),
  KEY `idx_script_id` (`script_id`),
  KEY `idx_execution_status` (`execution_status`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='测试执行记录表';

-- ----------------------------
-- 4. 测试报告表
-- ----------------------------
DROP TABLE IF EXISTS `test_report`;
CREATE TABLE `test_report` (
  `report_id` bigint NOT NULL AUTO_INCREMENT COMMENT '报告ID',
  `execution_id` bigint NOT NULL COMMENT '执行ID',
  `report_name` varchar(200) NOT NULL COMMENT '报告名称',
  `report_type` varchar(20) NOT NULL COMMENT '报告类型：html/pdf/json/allure',
  `report_path` varchar(500) DEFAULT NULL COMMENT '存储路径',
  `report_size` bigint DEFAULT NULL COMMENT '报告大小（字节）',
  `summary` json DEFAULT NULL COMMENT '报告摘要',
  `metrics` json DEFAULT NULL COMMENT '关键指标',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`report_id`),
  KEY `idx_execution_id` (`execution_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='测试报告表';

-- ----------------------------
-- 5. 菜单SQL (兼容不同版本的 sys_menu 表)
-- ----------------------------
-- 一级菜单：测试管理
INSERT INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) 
VALUES (2000, '测试管理', 0, 5, 'testing', NULL, 1, 0, 'M', '0', '0', '', 'bug', 'admin', NOW(), '', NULL, 'AI智能测试平台');

-- 二级菜单：项目管理
INSERT INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) 
VALUES (2001, '项目管理', 2000, 1, 'project', 'testing/project/index', 1, 0, 'C', '0', '0', 'testing:project:list', 'tree', 'admin', NOW(), '', NULL, '测试项目管理');

-- 二级菜单：脚本管理
INSERT INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) 
VALUES (2002, '脚本管理', 2000, 2, 'script', 'testing/script/index', 1, 0, 'C', '0', '0', 'testing:script:list', 'documentation', 'admin', NOW(), '', NULL, '测试脚本管理');

-- 二级菜单：执行监控
INSERT INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) 
VALUES (2003, '执行监控', 2000, 3, 'execution', 'testing/execution/index', 1, 0, 'C', '0', '0', 'testing:execution:list', 'monitor', 'admin', NOW(), '', NULL, '测试执行监控');

-- 二级菜单：报告管理
INSERT INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) 
VALUES (2004, '报告管理', 2000, 4, 'report', 'testing/report/index', 1, 0, 'C', '0', '0', 'testing:report:list', 'chart', 'admin', NOW(), '', NULL, '测试报告管理');

-- 项目管理按钮权限
INSERT INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES 
(2011, '项目查询', 2001, 1, '', NULL, 1, 0, 'F', '0', '0', 'testing:project:query', '#', 'admin', NOW(), '', NULL, ''),
(2012, '项目新增', 2001, 2, '', NULL, 1, 0, 'F', '0', '0', 'testing:project:add', '#', 'admin', NOW(), '', NULL, ''),
(2013, '项目修改', 2001, 3, '', NULL, 1, 0, 'F', '0', '0', 'testing:project:edit', '#', 'admin', NOW(), '', NULL, ''),
(2014, '项目删除', 2001, 4, '', NULL, 1, 0, 'F', '0', '0', 'testing:project:remove', '#', 'admin', NOW(), '', NULL, '');

-- 脚本管理按钮权限
INSERT INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES 
(2021, '脚本查询', 2002, 1, '', NULL, 1, 0, 'F', '0', '0', 'testing:script:query', '#', 'admin', NOW(), '', NULL, ''),
(2022, '脚本新增', 2002, 2, '', NULL, 1, 0, 'F', '0', '0', 'testing:script:add', '#', 'admin', NOW(), '', NULL, ''),
(2023, '脚本修改', 2002, 3, '', NULL, 1, 0, 'F', '0', '0', 'testing:script:edit', '#', 'admin', NOW(), '', NULL, ''),
(2024, '脚本删除', 2002, 4, '', NULL, 1, 0, 'F', '0', '0', 'testing:script:remove', '#', 'admin', NOW(), '', NULL, ''),
(2025, 'AI生成', 2002, 5, '', NULL, 1, 0, 'F', '0', '0', 'testing:script:generate', '#', 'admin', NOW(), '', NULL, ''),
(2026, '脚本执行', 2002, 6, '', NULL, 1, 0, 'F', '0', '0', 'testing:script:execute', '#', 'admin', NOW(), '', NULL, '');

-- 执行监控按钮权限
INSERT INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES 
(2031, '执行查询', 2003, 1, '', NULL, 1, 0, 'F', '0', '0', 'testing:execution:query', '#', 'admin', NOW(), '', NULL, ''),
(2032, '取消执行', 2003, 2, '', NULL, 1, 0, 'F', '0', '0', 'testing:execution:cancel', '#', 'admin', NOW(), '', NULL, '');

-- 报告管理按钮权限
INSERT INTO `sys_menu` (`menu_id`, `menu_name`, `parent_id`, `order_num`, `path`, `component`, `is_frame`, `is_cache`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `update_by`, `update_time`, `remark`) VALUES 
(2041, '报告查询', 2004, 1, '', NULL, 1, 0, 'F', '0', '0', 'testing:report:query', '#', 'admin', NOW(), '', NULL, ''),
(2042, '报告生成', 2004, 2, '', NULL, 1, 0, 'F', '0', '0', 'testing:report:add', '#', 'admin', NOW(), '', NULL, ''),
(2043, '报告下载', 2004, 3, '', NULL, 1, 0, 'F', '0', '0', 'testing:report:download', '#', 'admin', NOW(), '', NULL, ''),
(2044, '报告删除', 2004, 4, '', NULL, 1, 0, 'F', '0', '0', 'testing:report:remove', '#', 'admin', NOW(), '', NULL, ''),
(2045, '报告对比', 2004, 5, '', NULL, 1, 0, 'F', '0', '0', 'testing:report:compare', '#', 'admin', NOW(), '', NULL, '');

-- ----------------------------
-- 6. 初始化示例数据
-- ----------------------------
-- 示例项目
INSERT INTO `test_project` (`project_name`, `project_type`, `description`, `status`, `create_by`, `create_time`) VALUES 
('示例API测试项目', 'api', '这是一个示例API测试项目，用于演示平台功能', '0', 'admin', NOW()),
('示例性能测试项目', 'performance', '这是一个示例性能测试项目，使用K6进行性能测试', '0', 'admin', NOW()),
('示例UI测试项目', 'ui', '这是一个示例UI测试项目，使用Playwright进行UI自动化测试', '0', 'admin', NOW());
