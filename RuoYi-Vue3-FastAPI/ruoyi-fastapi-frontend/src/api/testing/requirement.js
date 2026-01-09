/**
 * 测试需求管理API
 * 通用接口，支持性能测试、UI自动化、API自动化三种类型
 */
import request from '@/utils/request'

/**
 * 获取需求分页列表
 * @param {Object} query - 查询参数
 * @param {string} query.requirementName - 需求名称
 * @param {string} query.requirementType - 需求类型：performance/ui/api
 * @param {number} query.projectId - 项目ID
 * @param {string} query.priority - 优先级：low/medium/high
 * @param {string} query.status - 状态：0待处理/1进行中/2已完成/3已关闭
 * @param {number} query.pageNum - 页码
 * @param {number} query.pageSize - 每页数量
 */
export function listRequirement(query) {
  return request({
    url: '/api/testing/requirement/list',
    method: 'get',
    params: {
      requirement_name: query.requirementName,
      requirement_type: query.requirementType,
      project_id: query.projectId,
      priority: query.priority,
      status: query.status,
      page_num: query.pageNum || 1,
      page_size: query.pageSize || 10
    }
  })
}

/**
 * 获取需求详情
 * @param {number} requirementId - 需求ID
 */
export function getRequirement(requirementId) {
  return request({
    url: `/testing/requirement/${requirementId}`,
    method: 'get'
  })
}

/**
 * 新增需求
 * @param {Object} data - 需求数据
 */
export function addRequirement(data) {
  const acceptance = data.acceptanceCriteria
  const normalizedAcceptance =
    acceptance === undefined || acceptance === null || acceptance === ''
      ? null
      : typeof acceptance === 'string'
        ? { text: acceptance }
        : acceptance
  return request({
    url: '/testing/requirement',
    method: 'post',
    data: {
      project_id: data.projectId,
      requirement_name: data.requirementName,
      requirement_type: data.requirementType,
      description: data.description,
      acceptance_criteria: normalizedAcceptance,
      priority: data.priority || 'medium',
      status: data.status || '0',
      tags: data.tags,
      remark: data.remark
    }
  })
}

/**
 * 修改需求
 * @param {Object} data - 需求数据
 */
export function updateRequirement(data) {
  const acceptance = data.acceptanceCriteria
  const normalizedAcceptance =
    acceptance === undefined || acceptance === null || acceptance === ''
      ? null
      : typeof acceptance === 'string'
        ? { text: acceptance }
        : acceptance
  return request({
    url: '/testing/requirement',
    method: 'put',
    data: {
      requirement_id: data.requirementId,
      project_id: data.projectId,
      requirement_name: data.requirementName,
      requirement_type: data.requirementType,
      description: data.description,
      acceptance_criteria: normalizedAcceptance,
      priority: data.priority,
      status: data.status,
      tags: data.tags,
      remark: data.remark
    }
  })
}

/**
 * 删除需求
 * @param {string|number} requirementIds - 需求ID，多个用逗号分隔
 */
export function delRequirement(requirementIds) {
  return request({
    url: `/testing/requirement/${requirementIds}`,
    method: 'delete'
  })
}

/**
 * 从需求生成脚本（AI功能）
 * @param {number} requirementId - 需求ID
 * @param {Object} options - 生成选项
 * @param {boolean} options.useRag - 是否使用RAG增强
 * @param {Object} options.config - 生成配置
 */
export function generateScriptFromRequirement(requirementId, options = {}) {
  return request({
    url: `/testing/requirement/generate/${requirementId}`,
    method: 'post',
    data: {
      use_rag: options.useRag !== false,
      config: options.config || {}
    }
  })
}

/**
 * AI分析需求
 * @param {number} requirementId - 需求ID
 * @param {string} analyzeType - 分析类型：feasibility/complexity/risk
 */
export function analyzeRequirement(requirementId, analyzeType = 'feasibility') {
  return request({
    url: `/testing/requirement/analyze/${requirementId}`,
    method: 'post',
    data: {
      analyze_type: analyzeType
    }
  })
}

/**
 * 获取需求统计信息
 * @param {number} projectId - 可选的项目ID过滤
 */
export function getRequirementStatistics(projectId) {
  return request({
    url: '/api/testing/requirement/statistics',
    method: 'get',
    params: { project_id: projectId }
  })
}

