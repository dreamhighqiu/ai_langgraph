-- ----------------------------
-- 知识库管理模块菜单数据（完整安装版）
-- 版本：v1.1.0
-- 更新日期：2026-01-01
-- 说明：知识库管理菜单和权限配置（菜单ID：2920-2929）
--       知识库管理为一级目录菜单，包含"知识库列表"二级菜单
-- 使用：mysql -u root -p database_name < knowledge_menu.sql
-- ----------------------------

-- 强烈建议先备份数据库
-- mysqldump -u root -p database_name > backup_$(date +%Y%m%d).sql

SET FOREIGN_KEY_CHECKS = 0;

-- ========== 知识库管理菜单（2920-2929） ==========

-- 1) 清空知识库管理相关菜单与角色绑定
DELETE FROM sys_role_menu WHERE menu_id BETWEEN 2920 AND 2929;
DELETE FROM sys_menu WHERE menu_id BETWEEN 2920 AND 2929;

-- 2) 插入知识库管理主菜单（作为一级目录菜单，parent_id=0，menu_type='M'）
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) 
VALUES
-- 一级菜单：知识库管理（目录类型）
(2920,'知识库管理',0,5,'knowledge',NULL,NULL,1,0,'M','0','0',NULL,'collection','admin',NOW(),'admin',NOW(),'知识库管理 - 支持文档上传和RAG智能问答'),
-- 二级菜单：知识库列表
(2921,'知识库列表',2920,1,'index','testing/knowledge/index',NULL,1,0,'C','0','0','testing:knowledge:list','list','admin',NOW(),'admin',NOW(),'知识库列表管理');

-- 4) 插入知识库管理按钮权限
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, query, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark) 
VALUES
-- 基础权限（绑定到知识库列表菜单）
(2924,'知识库查询',2921,1,'','',NULL,1,0,'F','0','0','testing:knowledge:query',NULL,'admin',NOW(),'admin',NOW(),'查询知识库列表和详情'),
(2925,'知识库新增',2921,2,'','',NULL,1,0,'F','0','0','testing:knowledge:add',NULL,'admin',NOW(),'admin',NOW(),'创建新知识库'),
(2926,'知识库修改',2921,3,'','',NULL,1,0,'F','0','0','testing:knowledge:edit',NULL,'admin',NOW(),'admin',NOW(),'修改知识库信息'),
(2927,'知识库删除',2921,4,'','',NULL,1,0,'F','0','0','testing:knowledge:remove',NULL,'admin',NOW(),'admin',NOW(),'删除知识库及所有文件'),
-- 文件管理权限
(2928,'文件上传',2921,5,'','',NULL,1,0,'F','0','0','testing:knowledge:upload',NULL,'admin',NOW(),'admin',NOW(),'上传文档到知识库'),
(2929,'知识库导出',2921,6,'','',NULL,1,0,'F','0','0','testing:knowledge:export',NULL,'admin',NOW(),'admin',NOW(),'导出知识库数据');

-- 5) 为管理员角色绑定知识库管理权限（role_id=1）
-- 如需为其他角色分配权限，请手动添加或修改 role_id
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE menu_id BETWEEN 2920 AND 2929;

-- 6) 为超级管理员角色绑定（如果存在 role_id=2）
INSERT IGNORE INTO sys_role_menu (role_id, menu_id)
SELECT 2, menu_id FROM sys_menu WHERE menu_id BETWEEN 2920 AND 2929;

SET FOREIGN_KEY_CHECKS = 1;

-- ========== 验证安装 ==========
-- 执行以下查询验证菜单是否安装成功

-- 查看知识库管理菜单结构
SELECT 
    menu_id AS '菜单ID',
    menu_name AS '菜单名称',
    parent_id AS '父菜单ID',
    menu_type AS '菜单类型',
    path AS '路径',
    component AS '组件',
    perms AS '权限标识',
    icon AS '图标',
    visible AS '可见',
    status AS '状态'
FROM sys_menu 
WHERE menu_id BETWEEN 2920 AND 2929
ORDER BY menu_id;

-- 查看角色绑定情况
SELECT 
    rm.role_id AS '角色ID',
    r.role_name AS '角色名称',
    COUNT(rm.menu_id) AS '绑定菜单数'
FROM sys_role_menu rm
LEFT JOIN sys_role r ON rm.role_id = r.role_id
WHERE rm.menu_id BETWEEN 2920 AND 2929
GROUP BY rm.role_id, r.role_name
ORDER BY rm.role_id;

-- ========== 使用说明 ==========
/*
菜单结构：
  知识库管理（2920）- 一级目录菜单
    └─ 知识库列表（2921）- testing:knowledge:list
         ├─ 知识库查询（2924）- testing:knowledge:query
         ├─ 知识库新增（2925）- testing:knowledge:add
         ├─ 知识库修改（2926）- testing:knowledge:edit
         ├─ 知识库删除（2927）- testing:knowledge:remove
         ├─ 文件上传（2928）- testing:knowledge:upload
         └─ 知识库导出（2929）- testing:knowledge:export

权限说明：
  - testing:knowledge:list   查看知识库列表页面
  - testing:knowledge:query  查询知识库详情和统计信息
  - testing:knowledge:add    创建新知识库
  - testing:knowledge:edit   修改知识库信息和状态
  - testing:knowledge:remove 删除知识库、文件
  - testing:knowledge:upload 上传文档文件

功能特性：
  1. 支持项目级知识库管理
  2. 支持多种文档格式上传（PDF、DOCX、TXT、MD等）
  3. 自动向量化处理（基于LightRAG）
  4. RAG智能问答（4种查询模式）
  5. 实时处理状态追踪
  6. Milvus Collection隔离

前端页面：
  - /knowledge/index              知识库列表（二级菜单）
  - /knowledge/files/:knowledgeId 文件管理（通过知识库列表页面跳转）
  - /knowledge/chat/:knowledgeId   RAG问答（通过知识库列表页面跳转）

后端API：
  - POST   /testing/knowledge/create              创建知识库
  - GET    /testing/knowledge/list                查询列表
  - GET    /testing/knowledge/{id}                获取详情
  - PUT    /testing/knowledge/update              更新知识库
  - DELETE /testing/knowledge/{id}                删除知识库
  - GET    /testing/knowledge/{id}/stats          获取统计
  - POST   /testing/knowledge/{id}/files/upload   上传文件
  - GET    /testing/knowledge/{id}/files          文件列表
  - DELETE /testing/knowledge/files/{file_id}     删除文件
  - POST   /testing/knowledge/{id}/query          RAG查询

依赖服务：
  1. MySQL 5.7+        关系数据库
  2. Milvus 2.3+       向量数据库
  3. MinIO             对象存储
  4. anything-chat-rag LightRAG服务

相关文档：
  - README.md                  完整功能文档
  - QUICK_START.md             快速开始指南
  - DEPLOYMENT_GUIDE.md        部署指南
  - API_EXAMPLES.md            API使用示例
  - FRONTEND_GUIDE.md          前端集成指南

更多信息请查看：
  ruoyi-fastapi-backend/module_testing/README.md
*/

-- ========== 卸载说明 ==========
/*
如需卸载知识库管理模块，请执行以下命令：

-- 1. 删除角色菜单绑定
DELETE FROM sys_role_menu WHERE menu_id BETWEEN 2920 AND 2929;

-- 2. 删除菜单数据
DELETE FROM sys_menu WHERE menu_id BETWEEN 2920 AND 2929;

-- 3. （可选）删除业务数据
-- 警告：此操作会删除所有知识库数据，请谨慎！
-- DELETE FROM test_knowledge_file;
-- DELETE FROM test_knowledge;

注意：卸载前请确保已备份重要数据！
*/

