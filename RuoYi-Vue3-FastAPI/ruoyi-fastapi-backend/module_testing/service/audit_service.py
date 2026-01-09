"""
审计日志服务

提供审计日志记录和版本控制功能
"""
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.entity.do.audit_log_do import AuditLogDO, VersionHistoryDO
from utils.log_util import logger


class AuditService:
    """审计日志服务"""
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        entity_type: str,
        entity_id: int,
        action: str,
        user_id: Optional[int] = None,
        user_name: Optional[str] = None,
        entity_identifier: Optional[str] = None,
        action_desc: Optional[str] = None,
        old_value: Optional[Dict] = None,
        new_value: Optional[Dict] = None,
        project_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLogDO:
        """
        记录审计日志
        
        Args:
            db: 数据库会话
            entity_type: 实体类型
            entity_id: 实体ID
            action: 操作类型
            user_id: 用户ID
            user_name: 用户名
            entity_identifier: 实体标识符
            action_desc: 操作描述
            old_value: 旧值
            new_value: 新值
            project_id: 项目ID
            ip_address: IP地址
            user_agent: 用户代理
            
        Returns:
            AuditLogDO: 审计日志记录
        """
        try:
            # 计算差异
            diff = None
            if old_value and new_value:
                diff = AuditService._compute_diff(old_value, new_value)
            
            audit_log = AuditLogDO(
                entity_type=entity_type,
                entity_id=entity_id,
                entity_identifier=entity_identifier,
                action=action,
                action_desc=action_desc,
                old_value=old_value,
                new_value=new_value,
                diff=diff,
                user_id=user_id,
                user_name=user_name,
                ip_address=ip_address,
                user_agent=user_agent,
                project_id=project_id
            )
            
            db.add(audit_log)
            await db.commit()
            await db.refresh(audit_log)
            
            logger.info(f"审计日志已记录: {entity_type}#{entity_id} - {action}")
            return audit_log
            
        except Exception as e:
            logger.error(f"记录审计日志失败: {e}")
            await db.rollback()
            raise
    
    @staticmethod
    async def save_version(
        db: AsyncSession,
        entity_type: str,
        entity_id: int,
        version_number: int,
        snapshot: Dict[str, Any],
        change_summary: Optional[str] = None,
        change_details: Optional[Dict] = None,
        created_by: Optional[str] = None
    ) -> VersionHistoryDO:
        """
        保存版本历史
        
        Args:
            db: 数据库会话
            entity_type: 实体类型
            entity_id: 实体ID
            version_number: 版本号
            snapshot: 实体快照
            change_summary: 变更摘要
            change_details: 变更详情
            created_by: 创建人
            
        Returns:
            VersionHistoryDO: 版本历史记录
        """
        try:
            version_history = VersionHistoryDO(
                entity_type=entity_type,
                entity_id=entity_id,
                version_number=version_number,
                snapshot=snapshot,
                change_summary=change_summary,
                change_details=change_details,
                created_by=created_by
            )
            
            db.add(version_history)
            await db.commit()
            await db.refresh(version_history)
            
            logger.info(f"版本历史已保存: {entity_type}#{entity_id} v{version_number}")
            return version_history
            
        except Exception as e:
            logger.error(f"保存版本历史失败: {e}")
            await db.rollback()
            raise
    
    @staticmethod
    async def get_audit_logs(
        db: AsyncSession,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        action: Optional[str] = None,
        user_id: Optional[int] = None,
        project_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        查询审计日志
        
        Args:
            db: 数据库会话
            entity_type: 实体类型
            entity_id: 实体ID
            action: 操作类型
            user_id: 用户ID
            project_id: 项目ID
            start_time: 开始时间
            end_time: 结束时间
            page: 页码
            page_size: 每页数量
            
        Returns:
            dict: 分页结果
        """
        try:
            query = select(AuditLogDO)
            
            if entity_type:
                query = query.where(AuditLogDO.entity_type == entity_type)
            if entity_id:
                query = query.where(AuditLogDO.entity_id == entity_id)
            if action:
                query = query.where(AuditLogDO.action == action)
            if user_id:
                query = query.where(AuditLogDO.user_id == user_id)
            if project_id:
                query = query.where(AuditLogDO.project_id == project_id)
            if start_time:
                query = query.where(AuditLogDO.created_at >= start_time)
            if end_time:
                query = query.where(AuditLogDO.created_at <= end_time)
            
            # 排序和分页
            query = query.order_by(desc(AuditLogDO.created_at))
            query = query.offset((page - 1) * page_size).limit(page_size)
            
            result = await db.execute(query)
            logs = result.scalars().all()
            
            return {
                'list': [log.to_dict() for log in logs],
                'page': page,
                'page_size': page_size
            }
            
        except Exception as e:
            logger.error(f"查询审计日志失败: {e}")
            raise
    
    @staticmethod
    async def get_version_history(
        db: AsyncSession,
        entity_type: str,
        entity_id: int
    ) -> List[Dict[str, Any]]:
        """
        获取版本历史
        
        Args:
            db: 数据库会话
            entity_type: 实体类型
            entity_id: 实体ID
            
        Returns:
            list: 版本历史列表
        """
        try:
            query = select(VersionHistoryDO).where(
                VersionHistoryDO.entity_type == entity_type,
                VersionHistoryDO.entity_id == entity_id
            ).order_by(desc(VersionHistoryDO.version_number))
            
            result = await db.execute(query)
            versions = result.scalars().all()
            
            return [v.to_dict() for v in versions]
            
        except Exception as e:
            logger.error(f"获取版本历史失败: {e}")
            raise
    
    @staticmethod
    async def get_version_snapshot(
        db: AsyncSession,
        entity_type: str,
        entity_id: int,
        version_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        获取指定版本的快照
        
        Args:
            db: 数据库会话
            entity_type: 实体类型
            entity_id: 实体ID
            version_number: 版本号
            
        Returns:
            dict: 版本快照
        """
        try:
            query = select(VersionHistoryDO).where(
                VersionHistoryDO.entity_type == entity_type,
                VersionHistoryDO.entity_id == entity_id,
                VersionHistoryDO.version_number == version_number
            )
            
            result = await db.execute(query)
            version = result.scalar_one_or_none()
            
            return version.snapshot if version else None
            
        except Exception as e:
            logger.error(f"获取版本快照失败: {e}")
            raise
    
    @staticmethod
    def _compute_diff(old_value: Dict, new_value: Dict) -> Dict:
        """计算两个字典的差异"""
        diff = {
            'added': {},
            'removed': {},
            'changed': {}
        }
        
        all_keys = set(old_value.keys()) | set(new_value.keys())
        
        for key in all_keys:
            old_val = old_value.get(key)
            new_val = new_value.get(key)
            
            if key not in old_value:
                diff['added'][key] = new_val
            elif key not in new_value:
                diff['removed'][key] = old_val
            elif old_val != new_val:
                diff['changed'][key] = {
                    'old': old_val,
                    'new': new_val
                }
        
        return diff


# 便捷装饰器（用于自动记录审计日志）
def audit_log(action: str, entity_type: str, action_desc: Optional[str] = None):
    """
    审计日志装饰器
    
    使用示例:
        @audit_log(action='create', entity_type='test_case', action_desc='创建测试用例')
        async def create_test_case(db, data, user):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 执行原函数
            result = await func(*args, **kwargs)
            
            # 记录审计日志（需要从参数中提取必要信息）
            # 这里简化处理，实际使用时需要根据函数签名适配
            
            return result
        return wrapper
    return decorator

