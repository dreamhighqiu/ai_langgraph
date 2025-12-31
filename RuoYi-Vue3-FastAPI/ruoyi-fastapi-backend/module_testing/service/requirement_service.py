"""
需求服务V2 - 基于真实 LangGraph API 实现
"""
import json
from typing import Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.requirement_dao import RequirementDAO
from module_testing.dao.script_dao import ScriptDAO
from module_testing.agents.agent_manager import get_agent_manager
from utils.log_util import logger


# Agent类型映射（与需求类型对应）
REQUIREMENT_TYPE_TO_AGENT = {
    'performance': 'k6_agent',
    'ui': 'ui_automation_agent',
    'api': 'rest_api_agent'
}

REQUIREMENT_TYPE_TO_SCRIPT = {
    'performance': {
        'script_type': 'k6',
        'file_extension': '.js',
        'default_name': 'k6_test'
    },
    'ui': {
        'script_type': 'playwright',
        'file_extension': '.spec.ts',
        'default_name': 'ui_test'
    },
    'api': {
        'script_type': 'api',
        'file_extension': '.py',
        'default_name': 'api_test'
    }
}


class RequirementService:
    """需求服务 - 完整实现"""
    
    @staticmethod
    async def get_requirement_list(
        db: AsyncSession,
        query_params: dict,
        is_page: bool = True
    ) -> dict:
        """
        获取需求列表
        
        Args:
            db: 数据库会话
            query_params: 查询参数
            is_page: 是否分页
            
        Returns:
            需求列表（分页或全部）
        """
        return await RequirementDAO.get_requirements(db, query_params, is_page)
    
    @staticmethod
    async def get_requirement_by_id(db: AsyncSession, requirement_id: int):
        """获取需求详情"""
        return await RequirementDAO.get_requirement_by_id(db, requirement_id)
    
    @staticmethod
    async def create_requirement(
        db: AsyncSession,
        requirement_data: dict,
        current_user: str = ''
    ):
        """创建需求"""
        requirement_data['create_by'] = current_user
        requirement_data['create_time'] = datetime.now()
        
        requirement = await RequirementDAO.add_requirement(db, requirement_data)
        await db.commit()
        await db.refresh(requirement)
        
        logger.info(f"创建需求成功: {requirement.requirement_name} [ID: {requirement.requirement_id}]")
        return requirement
    
    @staticmethod
    async def update_requirement(
        db: AsyncSession,
        requirement_id: int,
        requirement_data: dict,
        current_user: str = ''
    ):
        """更新需求"""
        requirement_data['update_by'] = current_user
        requirement_data['update_time'] = datetime.now()
        
        requirement = await RequirementDAO.update_requirement(db, requirement_id, requirement_data)
        await db.commit()
        await db.refresh(requirement)
        
        logger.info(f"更新需求成功: ID {requirement_id}")
        return requirement
    
    @staticmethod
    async def delete_requirements(db: AsyncSession, requirement_ids: list[int]) -> int:
        """删除需求"""
        count = await RequirementDAO.delete_requirements(db, requirement_ids)
        await db.commit()
        
        logger.info(f"删除需求成功: {requirement_ids}, 数量: {count}")
        return count
    
    @staticmethod
    async def generate_script_from_requirement(
        db: AsyncSession,
        requirement_id: int,
        config: Optional[dict] = None,
        use_rag: bool = True,
        current_user: str = ''
    ) -> dict:
        """
        从需求生成脚本 - 核心AI功能（真实实现）
        
        完整流程：
        1. 获取需求详情
        2. 根据需求类型选择Agent
        3. 调用LangGraph API生成脚本
        4. 保存脚本到本地或MinIO
        5. 创建脚本记录
        
        Args:
            db: 数据库会话
            requirement_id: 需求ID
            config: 生成配置
            use_rag: 是否使用RAG增强
            current_user: 当前用户
            
        Returns:
            包含脚本ID、路径和内容的字典
        """
        try:
            # 1. 获取需求详情
            requirement = await RequirementDAO.get_requirement_by_id(db, requirement_id)
            if not requirement:
                return {
                    'success': False,
                    'error': f"需求不存在: {requirement_id}"
                }
            
            # 提取ORM对象属性
            req_id = requirement.requirement_id
            req_name = requirement.requirement_name
            req_type = requirement.requirement_type
            req_desc = requirement.description
            req_criteria = requirement.acceptance_criteria
            req_priority = requirement.priority
            project_id = requirement.project_id
            
            logger.info(f"开始生成脚本 - 需求: {req_name} [{req_type}]")
            
            # 2. 获取Agent和脚本配置
            agent_id = REQUIREMENT_TYPE_TO_AGENT.get(req_type)
            if not agent_id:
                return {
                    'success': False,
                    'error': f"不支持的需求类型: {req_type}"
                }
            
            script_config = REQUIREMENT_TYPE_TO_SCRIPT.get(req_type, {})
            script_type = script_config.get('script_type')
            file_extension = script_config.get('file_extension')
            default_name = script_config.get('default_name')
            
            # 3. 调用Agent Manager生成脚本
            agent_manager = get_agent_manager()
            
            # 构建需求数据（用于Agent）
            requirement_dict = {
                'requirement_id': req_id,
                'requirement_name': req_name,
                'requirement_type': req_type,
                'description': req_desc,
                'acceptance_criteria': req_criteria,
                'priority': req_priority
            }
            
            # 生成脚本
            generation_result = await agent_manager.generate_script(
                agent_id=agent_id,
                requirement=requirement_dict,
                config=config
            )
            
            if not generation_result.get('success'):
                error_msg = generation_result.get('error', 'Agent生成脚本失败')
                logger.error(f"生成脚本失败: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'agent_id': agent_id
                }
            
            script_content = generation_result.get('script_content', '')
            full_response = generation_result.get('full_response', '')
            thread_id = generation_result.get('thread_id')
            
            logger.info(f"Agent生成脚本成功: {len(script_content)} 字符")
            
            # 4. 生成脚本名称和路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            script_name = f"{default_name}_{req_name}_{timestamp}"
            script_filename = f"{script_name}{file_extension}"
            
            # 5. 保存脚本到本地
            local_dir = Path(f"storage/scripts/{req_type}")
            local_dir.mkdir(parents=True, exist_ok=True)
            local_path = local_dir / script_filename
            local_path.write_text(script_content, encoding='utf-8')
            script_url = str(local_path)
            
            logger.info(f"脚本已保存到: {script_url}")
            
            # 6. 创建脚本记录
            script_data = {
                'project_id': project_id,
                'requirement_id': req_id,
                'script_name': script_name,
                'script_type': script_type,
                'script_path': script_url,
                'script_content': script_content,
                'version': '1.0.0',
                'status': '0',  # 草稿状态
                'description': f"从需求[{req_name}] 自动生成",
                'tags': json.dumps([req_type, 'ai_generated', agent_id]),
                'ai_generated': '1',
                'generation_config': json.dumps({
                    'agent_id': agent_id,
                    'thread_id': thread_id,
                    'use_rag': use_rag,
                    'config': config or {},
                    'generated_at': datetime.now().isoformat()
                }),
                'create_by': current_user,
                'create_time': datetime.now()
            }
            
            script = await ScriptDAO.add_script(db, script_data)
            await db.commit()
            await db.refresh(script)
            
            logger.info(f"脚本记录已创建: ID {script.script_id}")
            
            # 7. 返回成功结果
            return {
                'success': True,
                'script_id': script.script_id,
                'script_name': script.script_name,
                'script_path': script_url,
                'script_content': script_content,
                'script_type': script_type,
                'agent_id': agent_id,
                'thread_id': thread_id,
                'mode': 'langgraph_api',
                'full_response': full_response,
                'message': f'成功使用 {agent_id} 生成{req_type}测试脚本'
            }
            
        except Exception as e:
            logger.error(f"生成脚本异常: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'生成脚本失败: {str(e)}'
            }
    
    @staticmethod
    async def analyze_requirement(
        db: AsyncSession,
        requirement_id: int,
        analyze_type: str = 'feasibility'
    ) -> dict:
        """
        AI分析需求 - 真实实现
        
        Args:
            db: 数据库会话
            requirement_id: 需求ID
            analyze_type: 分析类型 (feasibility/complexity/risk)
            
        Returns:
            分析结果
        """
        try:
            # 1. 获取需求详情
            requirement = await RequirementDAO.get_requirement_by_id(db, requirement_id)
            if not requirement:
                return {
                    'success': False,
                    'error': f"需求不存在: {requirement_id}"
                }
            
            # 提取属性
            req_name = requirement.requirement_name
            req_type = requirement.requirement_type
            req_desc = requirement.description
            req_criteria = requirement.acceptance_criteria
            
            logger.info(f"开始分析需求 - {req_name} [{analyze_type}]")
            
            # 2. 构建需求字典
            requirement_dict = {
                'requirement_id': requirement.requirement_id,
                'requirement_name': req_name,
                'requirement_type': req_type,
                'description': req_desc,
                'acceptance_criteria': req_criteria
            }
            
            # 3. 调用Agent Manager进行分析
            agent_manager = get_agent_manager()
            analysis_result = await agent_manager.analyze_requirement(
                requirement=requirement_dict,
                analysis_type=analyze_type
            )
            
            if analysis_result.get('success'):
                logger.info(f"需求分析成功: {req_name}")
                return {
                    'success': True,
                    'analyze_type': analyze_type,
                    'analysis': analysis_result.get('analysis'),
                    'agent_id': analysis_result.get('agent_id'),
                    'analyzed_at': analysis_result.get('analyzed_at')
                }
            else:
                return {
                    'success': False,
                    'error': analysis_result.get('error', '分析失败'),
                    'analyze_type': analyze_type
                }
                
        except Exception as e:
            logger.error(f"需求分析异常: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'分析失败: {str(e)}',
                'analyze_type': analyze_type
            }
    
    @staticmethod
    async def get_requirement_statistics(
        db: AsyncSession,
        project_id: Optional[int] = None
    ) -> dict:
        """
        获取需求统计信息
        
        Args:
            db: 数据库会话
            project_id: 可选的项目ID过滤
            
        Returns:
            统计信息字典
        """
        try:
            query_params = {'project_id': project_id} if project_id else {}
            
            # 获取所有需求
            all_requirements_result = await RequirementDAO.get_requirements(
                db, query_params, is_page=False
            )
            all_requirements = all_requirements_result.get('rows', [])
            
            # 统计各种状态和类型
            stats = {
                'total': len(all_requirements),
                'by_status': {
                    'pending': 0,      # 待处理
                    'in_progress': 0,  # 进行中
                    'completed': 0,    # 已完成
                    'closed': 0        # 已关闭
                },
                'by_type': {
                    'performance': 0,
                    'ui': 0,
                    'api': 0
                },
                'by_priority': {
                    'low': 0,
                    'medium': 0,
                    'high': 0
                }
            }
            
            for req in all_requirements:
                # 状态统计
                status_map = {'0': 'pending', '1': 'in_progress', '2': 'completed', '3': 'closed'}
                status_key = status_map.get(req.get('status', '0'), 'pending')
                stats['by_status'][status_key] += 1
                
                # 类型统计
                req_type = req.get('requirement_type', '')
                if req_type in stats['by_type']:
                    stats['by_type'][req_type] += 1
                
                # 优先级统计
                priority = req.get('priority', 'medium')
                if priority in stats['by_priority']:
                    stats['by_priority'][priority] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"获取需求统计失败: {e}")
            return {
                'total': 0,
                'by_status': {},
                'by_type': {},
                'by_priority': {},
                'error': str(e)
            }
