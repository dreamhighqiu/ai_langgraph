import request from '@/utils/request'

/**
 * AI生成UI自动化测试脚本
 * @param {Object} data 生成参数
 */
export function generateUIScript(data) {
  return request({
    url: '/api/testing/ui-automation/generate',
    method: 'post',
    data: data
  })
}

/**
 * 获取UI自动化脚本列表
 * @param {Object} query 查询参数
 */
export function listUIScripts(query) {
  return request({
    url: '/api/testing/ui-automation/scripts',
    method: 'get',
    params: query
  })
}

/**
 * 获取UI自动化脚本详情
 * @param {Number} scriptId 脚本ID
 */
export function getUIScript(scriptId) {
  return request({
    url: `/api/testing/ui-automation/scripts/${scriptId}`,
    method: 'get'
  })
}

/**
 * 执行UI自动化脚本
 * @param {Object} data 执行参数
 */
export function executeUIScript(data) {
  return request({
    url: '/api/testing/ui-automation/execute',
    method: 'post',
    data: data
  })
}

/**
 * 获取执行详情
 * @param {Number} executionId 执行ID
 */
export function getUIExecution(executionId) {
  return request({
    url: `/api/testing/ui-automation/executions/${executionId}`,
    method: 'get'
  })
}

/**
 * 获取执行报告列表
 * @param {Number} executionId 执行ID
 */
export function getUIExecutionReports(executionId) {
  return request({
    url: `/api/testing/ui-automation/executions/${executionId}/reports`,
    method: 'get'
  })
}

/**
 * 下载测试报告
 * @param {Number} reportId 报告ID
 */
export function downloadUIReport(reportId) {
  return request({
    url: `/api/testing/ui-automation/reports/${reportId}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 删除UI自动化脚本
 * @param {Number} scriptId 脚本ID
 */
export function deleteUIScript(scriptId) {
  return request({
    url: `/api/testing/ui-automation/scripts/${scriptId}`,
    method: 'delete'
  })
}

