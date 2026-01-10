"""
测试用例服务层
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.test_case_dao import TestCaseDao
from module_testing.dao.folder_dao import FolderDao
from module_testing.entity.do.test_case_do import TestCaseDO
from module_testing.entity.vo.test_case_vo import (
    TestCaseCreateVO, TestCaseUpdateVO, TestCaseQueryVO
)
from utils.log_util import logger


class TestCaseService:
    """测试用例服务"""

    def __init__(self):
        self.test_case_dao = TestCaseDao()
        self.folder_dao = FolderDao()

    async def create_test_case(
        self, 
        db: AsyncSession, 
        test_case_vo: TestCaseCreateVO,
        user_name: str,
        auto_commit: bool = True
    ) -> TestCaseDO:
        """
        创建测试用例
        
        Args:
            db: 数据库会话
            test_case_vo: 测试用例创建 VO
            user_name: 创建者用户名
            auto_commit: 是否自动提交事务（默认 True，工具调用时设为 False）
        """
        try:
            # 生成用例标识符（添加重试机制，防止连接丢失）
            max_retries = 2
            identifier = None
            last_error = None
            for attempt in range(max_retries):
                try:
                    identifier = await self.test_case_dao.get_next_identifier(db, test_case_vo.project_id)
                    break
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        logger.warning(f"获取用例标识符失败（尝试 {attempt + 1}/{max_retries}），重试中: {str(e)}")
                        await asyncio.sleep(0.2)  # 短暂等待后重试
                    else:
                        logger.error(f"获取用例标识符失败，已重试 {max_retries} 次: {str(e)}")
                        raise
            
            if not identifier:
                raise ValueError(f"无法生成用例标识符: {last_error}")
            
            # 处理测试步骤
            test_case_steps = None
            if test_case_vo.test_case_steps:
                test_case_steps = json.dumps([step.model_dump() for step in test_case_vo.test_case_steps], ensure_ascii=False)
            
            # 处理 BDD 步骤
            given_steps = json.dumps(test_case_vo.given_steps or [], ensure_ascii=False)
            when_steps = json.dumps(test_case_vo.when_steps or [], ensure_ascii=False)
            then_steps = json.dumps(test_case_vo.then_steps or [], ensure_ascii=False)
            
            # 处理标签
            tags = ','.join(test_case_vo.tags) if test_case_vo.tags else None
            
            # 创建DO对象
            test_case_do = TestCaseDO(
                project_id=test_case_vo.project_id,
                folder_id=test_case_vo.folder_id,
                case_identifier=identifier,
                case_name=test_case_vo.case_name,
                case_type=test_case_vo.case_type or 'functional',
                template=test_case_vo.template or 'test_case',
                description=test_case_vo.description,
                preconditions=test_case_vo.preconditions,
                test_data=test_case_vo.test_data,
                expected_results=test_case_vo.expected_results,
                test_case_steps=test_case_steps,
                feature=test_case_vo.feature,
                scenario=test_case_vo.scenario,
                background=test_case_vo.background,
                given_steps=given_steps,
                when_steps=when_steps,
                then_steps=then_steps,
                priority=test_case_vo.priority or 'medium',
                severity=test_case_vo.severity,
                tags=tags,
                status='draft',
                execution_status='not_run',
                execution_count=0,
                pass_count=0,
                fail_count=0,
                create_by=user_name,
                create_time=datetime.now(),
                remark=test_case_vo.remark
            )
            
            # 保存到数据库
            result = await self.test_case_dao.insert(db, test_case_do)
            
            # 更新文件夹的测试用例数量
            if test_case_vo.folder_id:
                await self.folder_dao.increment_case_count(db, test_case_vo.folder_id, 1)
            
            # 只有在 auto_commit=True 时才提交（用于 HTTP 请求场景）
            # 工具调用时 auto_commit=False，由 get_db_session() 上下文管理器处理 commit
            if auto_commit:
                await db.commit()
            
            logger.info(f"创建测试用例成功: {identifier} (用户: {user_name})")
            return result
            
        except Exception as e:
            if auto_commit:
                await db.rollback()
            logger.error(f"创建测试用例失败: {str(e)}")
            raise

    async def update_test_case(
        self,
        db: AsyncSession,
        case_id: int,
        test_case_vo: TestCaseUpdateVO,
        user_name: str
    ) -> TestCaseDO:
        """更新测试用例"""
        try:
            test_case = await self.test_case_dao.select_by_id(db, case_id)
            if not test_case:
                raise ValueError(f"测试用例不存在: {case_id}")
            
            # 更新基本字段
            if test_case_vo.case_name is not None:
                test_case.case_name = test_case_vo.case_name
            if test_case_vo.case_type is not None:
                test_case.case_type = test_case_vo.case_type
            if test_case_vo.description is not None:
                test_case.description = test_case_vo.description
            if test_case_vo.preconditions is not None:
                test_case.preconditions = test_case_vo.preconditions
            if test_case_vo.test_data is not None:
                test_case.test_data = test_case_vo.test_data
            if test_case_vo.expected_results is not None:
                test_case.expected_results = test_case_vo.expected_results
            if test_case_vo.priority is not None:
                test_case.priority = test_case_vo.priority
            if test_case_vo.severity is not None:
                test_case.severity = test_case_vo.severity
            if test_case_vo.status is not None:
                test_case.status = test_case_vo.status
            if test_case_vo.remark is not None:
                test_case.remark = test_case_vo.remark
            
            # 更新测试步骤
            if test_case_vo.test_case_steps is not None:
                test_case.test_case_steps = json.dumps(
                    [step.model_dump() for step in test_case_vo.test_case_steps], 
                    ensure_ascii=False
                )
            
            # 更新 BDD 字段
            if test_case_vo.feature is not None:
                test_case.feature = test_case_vo.feature
            if test_case_vo.scenario is not None:
                test_case.scenario = test_case_vo.scenario
            if test_case_vo.background is not None:
                test_case.background = test_case_vo.background
            if test_case_vo.given_steps is not None:
                test_case.given_steps = json.dumps(test_case_vo.given_steps, ensure_ascii=False)
            if test_case_vo.when_steps is not None:
                test_case.when_steps = json.dumps(test_case_vo.when_steps, ensure_ascii=False)
            if test_case_vo.then_steps is not None:
                test_case.then_steps = json.dumps(test_case_vo.then_steps, ensure_ascii=False)
            
            # 更新标签
            if test_case_vo.tags is not None:
                test_case.tags = ','.join(test_case_vo.tags) if test_case_vo.tags else None
            
            test_case.update_by = user_name
            test_case.update_time = datetime.now()
            
            result = await self.test_case_dao.update(db, test_case)
            await db.commit()
            
            logger.info(f"更新测试用例成功: {case_id}")
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"更新测试用例失败: {str(e)}")
            raise

    async def delete_test_case(self, db: AsyncSession, case_id: int) -> bool:
        """删除测试用例"""
        try:
            test_case = await self.test_case_dao.select_by_id(db, case_id)
            if not test_case:
                return False
            
            folder_id = test_case.folder_id
            
            result = await self.test_case_dao.delete(db, case_id)
            
            # 更新文件夹的测试用例数量
            if folder_id:
                await self.folder_dao.increment_case_count(db, folder_id, -1)
            
            await db.commit()
            logger.info(f"删除测试用例成功: {case_id}")
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"删除测试用例失败: {str(e)}")
            raise

    async def get_test_case(self, db: AsyncSession, case_id: int) -> Optional[TestCaseDO]:
        """获取测试用例详情"""
        return await self.test_case_dao.select_by_id(db, case_id)

    async def query_test_case_list(
        self,
        db: AsyncSession,
        query_vo: TestCaseQueryVO
    ) -> tuple[List[TestCaseDO], int]:
        """查询测试用例列表"""
        query_params = query_vo.model_dump(exclude_none=True, exclude={'page_num', 'page_size'})
        return await self.test_case_dao.select_list(
            db,
            query_params,
            query_vo.page_num,
            query_vo.page_size
        )

    async def batch_create_test_cases(
        self,
        db: AsyncSession,
        test_cases: List[TestCaseCreateVO],
        user_name: str
    ) -> List[TestCaseDO]:
        """批量创建测试用例"""
        try:
            results = []
            folder_counts = {}  # 记录每个文件夹新增的用例数
            
            for test_case_vo in test_cases:
                # 生成用例标识符
                identifier = await self.test_case_dao.get_next_identifier(db, test_case_vo.project_id)
                
                # 处理测试步骤
                test_case_steps = None
                if test_case_vo.test_case_steps:
                    test_case_steps = json.dumps([step.model_dump() for step in test_case_vo.test_case_steps], ensure_ascii=False)
                
                # 处理标签
                tags = ','.join(test_case_vo.tags) if test_case_vo.tags else None
                
                test_case_do = TestCaseDO(
                    project_id=test_case_vo.project_id,
                    folder_id=test_case_vo.folder_id,
                    case_identifier=identifier,
                    case_name=test_case_vo.case_name,
                    case_type=test_case_vo.case_type or 'functional',
                    template=test_case_vo.template or 'test_case',
                    description=test_case_vo.description,
                    preconditions=test_case_vo.preconditions,
                    test_data=test_case_vo.test_data,
                    expected_results=test_case_vo.expected_results,
                    test_case_steps=test_case_steps,
                    feature=test_case_vo.feature,
                    scenario=test_case_vo.scenario,
                    background=test_case_vo.background,
                    given_steps=json.dumps(test_case_vo.given_steps or [], ensure_ascii=False),
                    when_steps=json.dumps(test_case_vo.when_steps or [], ensure_ascii=False),
                    then_steps=json.dumps(test_case_vo.then_steps or [], ensure_ascii=False),
                    priority=test_case_vo.priority or 'medium',
                    severity=test_case_vo.severity,
                    tags=tags,
                    status='draft',
                    execution_status='not_run',
                    execution_count=0,
                    pass_count=0,
                    fail_count=0,
                    create_by=user_name,
                    create_time=datetime.now(),
                    remark=test_case_vo.remark
                )
                
                result = await self.test_case_dao.insert(db, test_case_do)
                results.append(result)
                
                # 记录文件夹计数
                if test_case_vo.folder_id:
                    folder_counts[test_case_vo.folder_id] = folder_counts.get(test_case_vo.folder_id, 0) + 1
            
            # 更新文件夹的测试用例数量
            for folder_id, count in folder_counts.items():
                await self.folder_dao.increment_case_count(db, folder_id, count)
            
            await db.commit()
            
            logger.info(f"批量创建测试用例成功: {len(results)} 个")
            return results
            
        except Exception as e:
            await db.rollback()
            logger.error(f"批量创建测试用例失败: {str(e)}")
            raise

    async def move_test_case(
        self,
        db: AsyncSession,
        case_id: int,
        folder_id: Optional[int],
        user_name: str
    ) -> TestCaseDO:
        """移动测试用例到指定文件夹"""
        try:
            test_case = await self.test_case_dao.select_by_id(db, case_id)
            if not test_case:
                raise ValueError(f"测试用例不存在: {case_id}")
            
            old_folder_id = test_case.folder_id
            
            # 验证目标文件夹
            if folder_id:
                folder = await self.folder_dao.select_by_id(db, folder_id)
                if not folder:
                    raise ValueError(f"目标文件夹不存在: {folder_id}")
                if folder.project_id != test_case.project_id:
                    raise ValueError("不能移动到其他项目的文件夹")
            
            test_case.folder_id = folder_id
            test_case.update_by = user_name
            test_case.update_time = datetime.now()
            
            await self.test_case_dao.update(db, test_case)
            
            # 更新文件夹计数
            if old_folder_id:
                await self.folder_dao.increment_case_count(db, old_folder_id, -1)
            if folder_id:
                await self.folder_dao.increment_case_count(db, folder_id, 1)
            
            await db.commit()
            
            logger.info(f"移动测试用例成功: {case_id} -> 文件夹 {folder_id}")
            return test_case
            
        except Exception as e:
            await db.rollback()
            logger.error(f"移动测试用例失败: {str(e)}")
            raise

    async def copy_test_case(
        self,
        db: AsyncSession,
        case_id: int,
        folder_id: Optional[int],
        user_name: str
    ) -> TestCaseDO:
        """复制测试用例"""
        try:
            original = await self.test_case_dao.select_by_id(db, case_id)
            if not original:
                raise ValueError(f"测试用例不存在: {case_id}")
            
            # 验证目标文件夹
            target_folder_id = folder_id if folder_id is not None else original.folder_id
            if target_folder_id:
                folder = await self.folder_dao.select_by_id(db, target_folder_id)
                if not folder:
                    raise ValueError(f"目标文件夹不存在: {target_folder_id}")
                if folder.project_id != original.project_id:
                    raise ValueError("不能复制到其他项目的文件夹")
            
            # 生成新标识符
            identifier = await self.test_case_dao.get_next_identifier(db, original.project_id)
            
            # 创建副本
            copy_case = TestCaseDO(
                project_id=original.project_id,
                folder_id=target_folder_id,
                case_identifier=identifier,
                case_name=f"{original.case_name} (副本)",
                case_type=original.case_type,
                template=original.template,
                description=original.description,
                preconditions=original.preconditions,
                test_data=original.test_data,
                expected_results=original.expected_results,
                test_case_steps=original.test_case_steps,
                feature=original.feature,
                scenario=original.scenario,
                background=original.background,
                given_steps=original.given_steps,
                when_steps=original.when_steps,
                then_steps=original.then_steps,
                priority=original.priority,
                severity=original.severity,
                tags=original.tags,
                status='draft',
                execution_status='not_run',
                execution_count=0,
                pass_count=0,
                fail_count=0,
                create_by=user_name,
                create_time=datetime.now()
            )
            
            result = await self.test_case_dao.insert(db, copy_case)
            
            # 更新文件夹计数
            if target_folder_id:
                await self.folder_dao.increment_case_count(db, target_folder_id, 1)
            
            await db.commit()
            
            logger.info(f"复制测试用例成功: {case_id} -> {result.case_id}")
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"复制测试用例失败: {str(e)}")
            raise

    async def change_status(
        self,
        db: AsyncSession,
        case_id: int,
        status: str,
        user_name: str
    ) -> bool:
        """修改测试用例状态"""
        try:
            test_case = await self.test_case_dao.select_by_id(db, case_id)
            if not test_case:
                raise ValueError(f"测试用例不存在: {case_id}")
            
            valid_statuses = ['draft', 'active', 'deprecated']
            if status not in valid_statuses:
                raise ValueError(f"无效的状态值: {status}")
            
            test_case.status = status
            test_case.update_by = user_name
            test_case.update_time = datetime.now()
            
            await self.test_case_dao.update(db, test_case)
            await db.commit()
            
            logger.info(f"修改测试用例状态成功: {case_id} -> {status}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"修改测试用例状态失败: {str(e)}")
            raise

    async def get_project_stats(self, db: AsyncSession, project_id: int) -> Dict[str, Any]:
        """获取项目测试用例统计"""
        total = await self.test_case_dao.count_by_project(db, project_id)
        
        # 按状态统计
        status_stats = await self.test_case_dao.count_by_status(db, project_id)
        
        # 按优先级统计
        priority_stats = await self.test_case_dao.count_by_priority(db, project_id)
        
        return {
            'total': total,
            'by_status': status_stats,
            'by_priority': priority_stats
        }
