/**
 * 测试执行管理API
 */
import request from '@/utils/request'

/**
 * 获取执行记录分页列表
 * @param {Object} query - 查询参数
 */
export function listExecution(query) {
  return request({
    url: '/api/testing/execution/list',
    method: 'get',
    params: {
      script_id: query.script_id,
      script_type: query.script_type,
      project_id: query.project_id,
      execution_status: query.execution_status,
      execution_type: query.execution_type,
      executor: query.executor,
      page_num: query.page_num || 1,
      page_size: query.page_size || 10
    }
  })
}

/**
 * 获取执行详情
 * @param {number} executionId - 执行ID
 */
export function getExecution(executionId) {
  return request({
    url: `/testing/execution/${executionId}`,
    method: 'get'
  })
}

/**
 * 取消执行
 * @param {Object} data - 取消参数
 * @param {number} data.execution_id - 执行ID
 */
export function cancelExecution(data) {
  return request({
    url: '/api/testing/execution/cancel',
    method: 'post',
    data: {
      execution_id: data.execution_id
    }
  })
}

/**
 * 重试执行
 * @param {number} executionId - 执行ID
 */
export function retryExecution(executionId) {
  return request({
    url: `/testing/execution/${executionId}/retry`,
    method: 'post'
  })
}

/**
 * 获取执行统计信息
 * @param {number} days - 统计天数，默认7天
 */
export function getExecutionStatistics(days = 7) {
  return request({
    url: '/api/testing/execution/statistics',
    method: 'get',
    params: { days }
  })
}

/**
 * 获取执行日志（流式）
 * @param {number} executionId - 执行ID
 */
export function getExecutionLogs(executionId) {
  return request({
    url: `/testing/execution/${executionId}/logs`,
    method: 'get'
  })
}

/**
 * 获取执行的实时状态
 * @param {number} executionId - 执行ID
 */
export function getExecutionStatus(executionId) {
  return request({
    url: `/testing/execution/${executionId}/status`,
    method: 'get'
  })
}

