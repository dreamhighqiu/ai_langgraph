-- ----------------------------
-- 测试管理模块菜单数据（完整版 v2.0）
-- 说明：
--   1. 项目管理（2900-2919）
--   2. 知识库管理（2920-2929）- 新增
--   3. 性能测试/UI自动化/API自动化（3000-3299）
-- ----------------------------

-- 强烈建议先备份
-- mysqldump -h47.110.95.246 -uroot -proot123456 ai_db > ai_db_backup.sql

SET FOREIGN_KEY_CHECKS = 0;

-- ========== 第一部分：项目管理 + 知识库管理（2900-2999） ==========
-- 1) 清空项目管理和知识库管理相关菜单与角色绑定
DELETE FROM sys_role_menu WHERE menu_id BETWEEN 2900 AND 2999;
DELETE FROM sys_menu WHERE menu_id BETWEEN 2900 AND 2999;

-- 2) 插入测试管理根目录和项目管理菜单
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
(2900,'测试管理',0,0,'testing',NULL,NULL,1,0,'M','0','0',NULL,'folder-opened','admin',NOW(),'admin',NOW(),'测试管理根目录'),
(2901,'项目管理',2900,1,'project','testing/project/index',NULL,1,0,'C','0','0','testing:project:list','folder-opened','admin',NOW(),'admin',NOW(),'测试项目管理');

-- 3) 插入项目管理按钮权限
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
(2911,'项目查询',2901,1,'','',NULL,1,0,'F','0','0','testing:project:query',NULL,'admin',NOW(),'admin',NOW(),NULL),
(2912,'项目新增',2901,2,'','',NULL,1,0,'F','0','0','testing:project:add',NULL,'admin',NOW(),'admin',NOW(),NULL),
(2913,'项目修改',2901,3,'','',NULL,1,0,'F','0','0','testing:project:edit',NULL,'admin',NOW(),'admin',NOW(),NULL),
(2914,'项目删除',2901,4,'','',NULL,1,0,'F','0','0','testing:project:remove',NULL,'admin',NOW(),'admin',NOW(),NULL),
(2915,'项目导出',2901,5,'','',NULL,1,0,'F','0','0','testing:project:export',NULL,'admin',NOW(),'admin',NOW(),NULL),
(2916,'项目导入',2901,6,'','',NULL,1,0,'F','0','0','testing:project:import',NULL,'admin',NOW(),'admin',NOW(),NULL);

-- 4) 插入知识库管理菜单（2920-2929）
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
(2920,'知识库管理',2900,4,'knowledge','testing/knowledge/index',NULL,1,0,'C','0','0','testing:knowledge:list','collection','admin',NOW(),'admin',NOW(),'知识库管理菜单');

-- 5) 插入知识库管理按钮权限（2921-2926）
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
(2921,'知识库查询',2920,1,'','',NULL,1,0,'F','0','0','testing:knowledge:query',NULL,'admin',NOW(),'admin',NOW(),'知识库查询权限'),
(2922,'知识库新增',2920,2,'','',NULL,1,0,'F','0','0','testing:knowledge:add',NULL,'admin',NOW(),'admin',NOW(),'知识库新增权限'),
(2923,'知识库修改',2920,3,'','',NULL,1,0,'F','0','0','testing:knowledge:edit',NULL,'admin',NOW(),'admin',NOW(),'知识库修改权限'),
(2924,'知识库删除',2920,4,'','',NULL,1,0,'F','0','0','testing:knowledge:remove',NULL,'admin',NOW(),'admin',NOW(),'知识库删除权限'),
(2925,'文件上传',2920,5,'','',NULL,1,0,'F','0','0','testing:knowledge:upload',NULL,'admin',NOW(),'admin',NOW(),'文件上传权限'),
(2926,'知识库导出',2920,6,'','',NULL,1,0,'F','0','0','testing:knowledge:export',NULL,'admin',NOW(),'admin',NOW(),'知识库导出权限');

-- 6) 为管理员角色绑定项目管理和知识库管理权限（role_id=1）
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE menu_id BETWEEN 2900 AND 2999;


-- ========== 第二部分：性能测试/API自动化（3000-3299）==========
-- 注意：UI自动化菜单(3340-3359)在v2.0_upgrade.sql中定义
-- 1) 清空测试相关菜单与角色绑定
DELETE FROM sys_role_menu WHERE menu_id BETWEEN 3000 AND 3299;
DELETE FROM sys_menu WHERE menu_id BETWEEN 3000 AND 3299;

-- 2) 重新插入菜单（性能 / API）
-- 注意：UI自动化菜单(3340-3359)在v2.0_upgrade.sql中定义，请勿在此重复定义
-- menu_type: M=目录, C=菜单, F=按钮；is_frame=1 代表内部路由
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
-- 性能测试
(3000,'性能测试',0,1,'performance',NULL,NULL,1,0,'M','0','0',NULL,'dashboard','admin',NOW(),'admin',NOW(),'性能测试根目录'),
(3001,'需求管理',3000,1,'requirement','testing/performance/requirement',NULL,1,0,'C','0','0','testing:requirement:list','list','admin',NOW(),'admin',NOW(),'性能测试需求管理'),
(3002,'脚本管理',3000,2,'script','testing/performance/script',NULL,1,0,'C','0','0','testing:script:list','edit','admin',NOW(),'admin',NOW(),'性能测试脚本管理'),
(3003,'脚本执行',3000,3,'execution','testing/performance/execution',NULL,1,0,'C','0','0','testing:execution:list','play','admin',NOW(),'admin',NOW(),'性能测试脚本执行'),
(3004,'报告管理',3000,4,'report','testing/performance/report',NULL,1,0,'C','0','0','testing:report:list','document','admin',NOW(),'admin',NOW(),'性能测试报告管理'),

-- API 自动化
(3200,'API自动化',0,2,'api-automation',NULL,NULL,1,0,'M','0','0',NULL,'api','admin',NOW(),'admin',NOW(),'API 自动化根目录'),
(3201,'需求管理',3200,1,'requirement','testing/api-automation/requirement',NULL,1,0,'C','0','0','testing:requirement:list','list','admin',NOW(),'admin',NOW(),'API自动化需求管理'),
(3202,'脚本管理',3200,2,'script','testing/api-automation/script',NULL,1,0,'C','0','0','testing:script:list','edit','admin',NOW(),'admin',NOW(),'API自动化脚本管理'),
(3203,'脚本执行',3200,3,'execution','testing/api-automation/execution',NULL,1,0,'C','0','0','testing:execution:list','play','admin',NOW(),'admin',NOW(),'API自动化脚本执行'),
(3204,'报告管理',3200,4,'report','testing/api-automation/report',NULL,1,0,'C','0','0','testing:report:list','document','admin',NOW(),'admin',NOW(),'API自动化报告管理');

-- 3) 插入按钮权限（性能 + API 共用同一权限标识）
-- 注意：UI自动化按钮权限(3351-3356)在v2.0_upgrade.sql中定义
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) VALUES
-- 性能按钮 3011-3044
(3011,'需求查询',3001,1,'','',NULL,1,0,'F','0','0','testing:requirement:query',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3012,'需求新增',3001,2,'','',NULL,1,0,'F','0','0','testing:requirement:add',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3013,'需求修改',3001,3,'','',NULL,1,0,'F','0','0','testing:requirement:edit',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3014,'需求删除',3001,4,'','',NULL,1,0,'F','0','0','testing:requirement:remove',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3015,'AI生成脚本',3001,5,'','',NULL,1,0,'F','0','0','testing:requirement:generate',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3016,'AI需求分析',3001,6,'','',NULL,1,0,'F','0','0','testing:requirement:analyze',NULL,'admin',NOW(),'admin',NOW(),NULL),

(3021,'脚本查询',3002,1,'','',NULL,1,0,'F','0','0','testing:script:query',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3022,'脚本新增',3002,2,'','',NULL,1,0,'F','0','0','testing:script:add',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3023,'脚本修改',3002,3,'','',NULL,1,0,'F','0','0','testing:script:edit',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3024,'脚本删除',3002,4,'','',NULL,1,0,'F','0','0','testing:script:remove',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3025,'脚本执行',3002,5,'','',NULL,1,0,'F','0','0','testing:script:execute',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3026,'AI生成脚本',3002,6,'','',NULL,1,0,'F','0','0','testing:script:generate',NULL,'admin',NOW(),'admin',NOW(),NULL),

(3031,'执行查询',3003,1,'','',NULL,1,0,'F','0','0','testing:execution:query',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3032,'取消执行',3003,2,'','',NULL,1,0,'F','0','0','testing:execution:cancel',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3033,'重试执行',3003,3,'','',NULL,1,0,'F','0','0','testing:execution:retry',NULL,'admin',NOW(),'admin',NOW(),NULL),

(3041,'报告查询',3004,1,'','',NULL,1,0,'F','0','0','testing:report:query',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3042,'报告下载',3004,2,'','',NULL,1,0,'F','0','0','testing:report:download',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3043,'报告删除',3004,3,'','',NULL,1,0,'F','0','0','testing:report:remove',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3044,'报告对比',3004,4,'','',NULL,1,0,'F','0','0','testing:report:compare',NULL,'admin',NOW(),'admin',NOW(),NULL),

-- 注意：UI自动化按钮权限(3351-3356)在v2.0_upgrade.sql中定义，已移除3111-3143

-- API 按钮 3211-3243（同权限标识）
(3211,'需求查询',3201,1,'','',NULL,1,0,'F','0','0','testing:requirement:query',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3212,'需求新增',3201,2,'','',NULL,1,0,'F','0','0','testing:requirement:add',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3213,'需求修改',3201,3,'','',NULL,1,0,'F','0','0','testing:requirement:edit',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3214,'需求删除',3201,4,'','',NULL,1,0,'F','0','0','testing:requirement:remove',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3215,'AI生成脚本',3201,5,'','',NULL,1,0,'F','0','0','testing:requirement:generate',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3216,'AI需求分析',3201,6,'','',NULL,1,0,'F','0','0','testing:requirement:analyze',NULL,'admin',NOW(),'admin',NOW(),NULL),

(3221,'脚本查询',3202,1,'','',NULL,1,0,'F','0','0','testing:script:query',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3222,'脚本新增',3202,2,'','',NULL,1,0,'F','0','0','testing:script:add',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3223,'脚本修改',3202,3,'','',NULL,1,0,'F','0','0','testing:script:edit',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3224,'脚本删除',3202,4,'','',NULL,1,0,'F','0','0','testing:script:remove',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3225,'脚本执行',3202,5,'','',NULL,1,0,'F','0','0','testing:script:execute',NULL,'admin',NOW(),'admin',NOW(),NULL),

(3231,'执行查询',3203,1,'','',NULL,1,0,'F','0','0','testing:execution:query',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3232,'取消执行',3203,2,'','',NULL,1,0,'F','0','0','testing:execution:cancel',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3233,'重试执行',3203,3,'','',NULL,1,0,'F','0','0','testing:execution:retry',NULL,'admin',NOW(),'admin',NOW(),NULL),

(3241,'报告查询',3204,1,'','',NULL,1,0,'F','0','0','testing:report:query',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3242,'报告下载',3204,2,'','',NULL,1,0,'F','0','0','testing:report:download',NULL,'admin',NOW(),'admin',NOW(),NULL),
(3243,'报告删除',3204,3,'','',NULL,1,0,'F','0','0','testing:report:remove',NULL,'admin',NOW(),'admin',NOW(),NULL);

-- 4) 角色绑定（管理员 role_id=1；如有其他角色请按需添加）
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE menu_id BETWEEN 3000 AND 3299;

SET FOREIGN_KEY_CHECKS = 1;

-- 5) 可选：清空业务数据（慎用，若要保留数据则不要执行）
-- DELETE FROM test_execution;
-- DELETE FROM test_report;
-- DELETE FROM test_script;
-- DELETE FROM test_requirement;

