-- ----------------------------
-- AI多智能体助手外链菜单
-- 版本：v1.0.0
-- 更新日期：2026-01-01
-- 说明：添加AI多智能体助手外链菜单（菜单ID：2931）
-- 使用：mysql -u root -p database_name < ai_assistant_menu.sql
-- ----------------------------

-- 强烈建议先备份数据库
-- mysqldump -u root -p database_name > backup_$(date +%Y%m%d).sql

SET FOREIGN_KEY_CHECKS = 0;

-- ========== AI多智能体助手菜单（2931） ==========

-- 1) 清空AI多智能体助手相关菜单与角色绑定
DELETE FROM sys_role_menu WHERE menu_id = 2931;
DELETE FROM sys_menu WHERE menu_id = 2931;

-- 2) 插入AI多智能体助手外链菜单
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) 
VALUES
-- 一级菜单：AI多智能体助手（外链，is_frame=0表示外链）
(2931,'AI多智能体助手',0,6,'http://127.0.0.1:3200/?assistantId=chat_rag_agent',NULL,NULL,0,0,'C','0','0',NULL,'chat-dot-round','admin',NOW(),'admin',NOW(),'AI多智能体助手 - 外链到智能体助手系统');

-- 3) 为管理员角色绑定AI多智能体助手菜单（role_id=1）
INSERT INTO sys_role_menu (role_id, menu_id)
VALUES (1, 2931);

-- 4) 为超级管理员角色绑定（如果存在 role_id=2）
INSERT IGNORE INTO sys_role_menu (role_id, menu_id)
VALUES (2, 2931);

SET FOREIGN_KEY_CHECKS = 1;

-- ========== 验证安装 ==========
-- 执行以下查询验证菜单是否安装成功

-- 查看AI多智能体助手菜单
SELECT 
    menu_id AS '菜单ID',
    menu_name AS '菜单名称',
    parent_id AS '父菜单ID',
    menu_type AS '菜单类型',
    path AS '路径（外链URL）',
    is_frame AS '是否外链（0=是，1=否）',
    component AS '组件',
    perms AS '权限标识',
    icon AS '图标',
    visible AS '可见',
    status AS '状态'
FROM sys_menu 
WHERE menu_id = 2931;

-- 查看角色绑定情况
SELECT 
    rm.role_id AS '角色ID',
    r.role_name AS '角色名称',
    m.menu_name AS '菜单名称'
FROM sys_role_menu rm
LEFT JOIN sys_role r ON rm.role_id = r.role_id
LEFT JOIN sys_menu m ON rm.menu_id = m.menu_id
WHERE rm.menu_id = 2931
ORDER BY rm.role_id;

-- ========== 使用说明 ==========
/*
菜单配置说明：
  - 菜单ID：2931
  - 菜单名称：AI多智能体助手
  - 菜单类型：C（菜单）
  - 外链URL：http://127.0.0.1:3200/?assistantId=chat_rag_agent
  - is_frame：0（外链，会在新窗口或iframe中打开）
  - parent_id：0（一级菜单）
  - order_num：6（排序号，可根据需要调整）
  - icon：chat-dot-round（图标，可根据需要修改）

注意事项：
  1. is_frame=0 表示外链，点击菜单会在新窗口或iframe中打开
  2. 如果需要在当前窗口打开，可以设置 is_frame=1，但需要前端路由支持
  3. 外链URL可以根据实际部署情况修改
  4. 如需修改菜单顺序，调整 order_num 值即可
*/

-- ========== 卸载说明 ==========
/*
如需卸载AI多智能体助手菜单，请执行以下命令：

-- 1. 删除角色菜单绑定
DELETE FROM sys_role_menu WHERE menu_id = 2931;

-- 2. 删除菜单数据
DELETE FROM sys_menu WHERE menu_id = 2931;

注意：卸载前请确保已备份重要数据！
*/

