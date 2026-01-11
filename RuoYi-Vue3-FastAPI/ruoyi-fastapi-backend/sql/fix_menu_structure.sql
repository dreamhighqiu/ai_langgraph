-- ============================================================================
-- 测试平台菜单结构修正脚本
-- 问题: UI自动化和Agent控制台应该都是一级菜单，但目前有重复和层级混乱
-- 解决: 
--   1. 删除旧的UI自动化菜单(3100-3143)
--   2. 保留新的UI自动化菜单(3340-3359)并改为一级菜单
--   3. 将Agent控制台(3360-3369)改为一级菜单
-- ============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- 1. 清理旧的UI自动化菜单(3100-3143)
-- ============================================================================
DELETE FROM sys_role_menu WHERE menu_id BETWEEN 3100 AND 3143;
DELETE FROM sys_menu WHERE menu_id BETWEEN 3100 AND 3143;

SELECT '✅ 已删除旧的UI自动化菜单(3100-3143)' AS step1;

-- ============================================================================
-- 2. 将UI自动化(3340)改为一级菜单
-- ============================================================================
UPDATE sys_menu 
SET parent_id = 0, 
    order_num = 4,
    update_time = NOW(),
    remark = 'UI自动化测试（一级菜单）'
WHERE menu_id = 3340;

SELECT '✅ UI自动化已改为一级菜单' AS step2;

-- ============================================================================
-- 3. 将Agent控制台(3360)改为一级菜单
-- ============================================================================
UPDATE sys_menu 
SET parent_id = 0, 
    order_num = 5,
    update_time = NOW(),
    remark = 'AI Agent管理控制台（一级菜单）'
WHERE menu_id = 3360;

SELECT '✅ Agent控制台已改为一级菜单' AS step3;

-- ============================================================================
-- 4. 优化测试管理菜单顺序
-- ============================================================================
-- 测试管理下只保留：项目管理(2901)、知识库管理(2920)
UPDATE sys_menu SET order_num = 1 WHERE menu_id = 2901; -- 项目管理
UPDATE sys_menu SET order_num = 2 WHERE menu_id = 2920; -- 知识库管理

-- 调整一级菜单顺序
UPDATE sys_menu SET order_num = 0 WHERE menu_id = 2900; -- 测试管理
UPDATE sys_menu SET order_num = 1 WHERE menu_id = 3000 AND menu_name = '性能测试'; -- 性能测试（如果存在）
UPDATE sys_menu SET order_num = 2 WHERE menu_id = 3200 AND menu_name = 'API自动化'; -- API自动化（如果存在）

SELECT '✅ 菜单顺序已优化' AS step4;

-- ============================================================================
-- 5. 确保管理员角色有所有权限
-- ============================================================================
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE menu_id BETWEEN 3340 AND 3369
ON DUPLICATE KEY UPDATE role_id=role_id;

SELECT '✅ 管理员角色权限已更新' AS step5;

-- ============================================================================
-- 6. 显示修正后的菜单结构
-- ============================================================================
SET FOREIGN_KEY_CHECKS = 1;

SELECT '
═══════════════════════════════════════════════════════
✅ 菜单结构修正完成！
═══════════════════════════════════════════════════════
' AS message;

-- 显示一级菜单
SELECT '【一级菜单】' AS category, menu_id, menu_name, order_num, icon, path 
FROM sys_menu 
WHERE parent_id = 0 AND menu_id BETWEEN 2900 AND 3999
ORDER BY order_num;

-- 显示测试管理的子菜单
SELECT '【测试管理 - 子菜单】' AS category, menu_id, menu_name, order_num, icon, path 
FROM sys_menu 
WHERE parent_id = 2900
ORDER BY order_num;

-- 显示UI自动化的子菜单
SELECT '【UI自动化 - 子菜单】' AS category, menu_id, menu_name, order_num, icon, component 
FROM sys_menu 
WHERE parent_id = 3340
ORDER BY order_num;

-- 显示Agent控制台的子菜单
SELECT '【Agent控制台 - 子菜单】' AS category, menu_id, menu_name, order_num, icon, component 
FROM sys_menu 
WHERE parent_id = 3360
ORDER BY order_num;

-- 菜单结构说明
SELECT '
【最终菜单结构】
├── 测试管理 (2900) - 一级菜单
│   ├── 项目管理 (2901)
│   └── 知识库管理 (2920)
│
├── 性能测试 (3000) - 一级菜单（如果存在）
│   └── ...
│
├── API自动化 (3200) - 一级菜单（如果存在）
│   └── ...
│
├── UI自动化 (3340) - 一级菜单 ✅
│   ├── 脚本生成 (3341)
│   ├── 脚本管理 (3342)
│   ├── 脚本执行 (3343)
│   └── 测试报告 (3344)
│
└── Agent控制台 (3360) - 一级菜单 ✅
    ├── Agent列表 (3361)
    └── 执行历史 (3362)
' AS structure;

