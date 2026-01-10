-- ============================================================================
-- 菜单图标更新脚本
-- 说明: 为测试管理模块的所有菜单项添加专业的图标
-- 执行方式: 在数据库中执行此脚本
-- ============================================================================

SET NAMES utf8mb4;

-- ============================================================================
-- 更新测试管理模块菜单图标
-- ============================================================================

-- 1. 测试管理根目录 (2900) - 使用文件夹图标
UPDATE sys_menu SET icon = 'folder-opened' WHERE menu_id = 2900;

-- 2. 项目管理 (2901) - 使用公文包图标
UPDATE sys_menu SET icon = 'briefcase' WHERE menu_id = 2901;

-- 3. 测试用例 (3300) - 使用文档图标
UPDATE sys_menu SET icon = 'document' WHERE menu_id = 3300;

-- 4. 需求分析 (3320) - 使用阅读图标
UPDATE sys_menu SET icon = 'reading' WHERE menu_id = 3320;

-- 5. 缺陷分析 (3330) - 使用警告图标
UPDATE sys_menu SET icon = 'warning' WHERE menu_id = 3330;

-- 6. AI智能助手 (3340) - 使用聊天图标
UPDATE sys_menu SET icon = 'chat-dot-round' WHERE menu_id = 3340;

-- 7. 知识库管理 (2920) - 使用收藏图标
UPDATE sys_menu SET icon = 'collection' WHERE menu_id = 2920;

-- ============================================================================
-- 为其他系统菜单添加图标（如果还没有）
-- ============================================================================

-- 首页
UPDATE sys_menu SET icon = 'home-filled' WHERE menu_name = '首页' AND (icon IS NULL OR icon = '' OR icon = '#');

-- 系统管理相关
UPDATE sys_menu SET icon = 'setting' WHERE menu_name LIKE '%系统%' AND menu_type = 'M' AND (icon IS NULL OR icon = '' OR icon = '#');
UPDATE sys_menu SET icon = 'user' WHERE menu_name LIKE '%用户%' AND menu_type = 'C' AND (icon IS NULL OR icon = '' OR icon = '#');
UPDATE sys_menu SET icon = 'user-filled' WHERE menu_name LIKE '%角色%' AND menu_type = 'C' AND (icon IS NULL OR icon = '' OR icon = '#');
UPDATE sys_menu SET icon = 'lock' WHERE menu_name LIKE '%权限%' AND menu_type = 'C' AND (icon IS NULL OR icon = '' OR icon = '#');
UPDATE sys_menu SET icon = 'menu' WHERE menu_name LIKE '%菜单%' AND menu_type = 'C' AND (icon IS NULL OR icon = '' OR icon = '#');
UPDATE sys_menu SET icon = 'tools' WHERE menu_name LIKE '%工具%' AND menu_type = 'C' AND (icon IS NULL OR icon = '' OR icon = '#');
UPDATE sys_menu SET icon = 'monitor' WHERE menu_name LIKE '%监控%' AND menu_type = 'C' AND (icon IS NULL OR icon = '' OR icon = '#');
UPDATE sys_menu SET icon = 'document' WHERE menu_name LIKE '%日志%' AND menu_type = 'C' AND (icon IS NULL OR icon = '' OR icon = '#');

-- ============================================================================
-- 图标说明
-- ============================================================================
-- Element Plus 图标库常用图标:
-- 文件夹: folder, folder-opened, folder-add, folder-remove
-- 文档: document, document-add, document-copy, document-delete, document-checked
-- 用户: user, user-filled
-- 设置: setting, tools
-- 监控: monitor, data-line
-- 图表: data-analysis, pie-chart, histogram
-- 编辑: edit, edit-pen
-- 删除: delete, remove
-- 查看: view, search
-- 添加: plus, circle-plus
-- 警告: warning, warning-filled
-- 成功: success-filled, circle-check
-- 信息: info-filled, message
-- 聊天: chat-dot-round, chat-line-round
-- 阅读: reading, reading-lamp
-- 收藏: collection, star
-- 指南: guide, location-information
-- 首页: home-filled, house
-- 菜单: menu, grid
-- 锁: lock, unlock
-- ============================================================================

SELECT '============================================================' AS '分割线';
SELECT '✅ 菜单图标更新完成!' AS '状态';
SELECT '============================================================' AS '分割线';
SELECT '📌 提示: 请刷新页面或重新登录以查看更新后的图标' AS '提示';
SELECT '============================================================' AS '分割线';

