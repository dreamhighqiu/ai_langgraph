import request from '@/utils/request'

/**
 * AI生成UI自动化测试脚本
 * @param {Object} data 生成参数（驼峰格式）
 */
export function generateUIScript(data) {
  // 转换为后端需要的下划线格式
  return request({
    url: '/api/testing/ui-automation/generate',
    method: 'post',
    data: {
      project_id: data.projectId || data.project_id,
      requirement_id: data.requirementId || data.requirement_id,
      script_name: data.scriptName || data.script_name,
      generation_prompt: data.generationPrompt || data.generation_prompt,
      language: data.language || 'typescript',
      browser: data.browser || 'chromium',
      agent_id: data.agentId || data.agent_id,
      config: data.config,
      use_rag: data.useRag !== undefined ? (data.useRag ? true : false) : false
    }
  })
}

/**
 * 获取UI自动化脚本列表
 * @param {Object} query 查询参数（支持驼峰和下划线）
 */
export function listUIScripts(query) {
  const params = {
    page_num: query.pageNum || query.page_num || 1,
    page_size: query.pageSize || query.page_size || 10,
    project_id: query.projectId || query.project_id,
    requirement_id: query.requirementId || query.requirement_id,
    script_name: query.scriptName || query.script_name,
    language: query.language,
    browser: query.browser,
    status: query.status,
    agent_id: query.agentId || query.agent_id,
    begin_time: query.beginTime || query.begin_time,
    end_time: query.endTime || query.end_time
  }
  // 移除undefined值
  Object.keys(params).forEach(key => params[key] === undefined && delete params[key])
  
  return request({
    url: '/api/testing/ui-automation/scripts',
    method: 'get',
    params
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
 * @param {Object} data 执行参数（支持驼峰和下划线）
 */
export function executeUIScript(data) {
  return request({
    url: '/api/testing/ui-automation/execute',
    method: 'post',
    data: {
      script_id: data.scriptId || data.script_id,
      execution_type: data.executionType || data.execution_type || 'manual',
      browser: data.browser || 'chromium',
      headless: data.headless !== undefined ? data.headless : true,
      config: data.config,
      env_vars: data.envVars || data.env_vars,
      timeout: data.timeout
    }
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

/**
 * 获取UI自动化执行列表
 * @param {Object} query 查询参数
 */
export function listUIExecutions(query) {
  const params = {
    page_num: query.pageNum || query.page_num || 1,
    page_size: query.pageSize || query.page_size || 10,
    script_name: query.scriptName || query.script_name,
    execution_type: query.executionType || query.execution_type || 'ui',
    status: query.status,
    begin_time: query.beginTime || query.begin_time,
    end_time: query.endTime || query.end_time
  }
  // 移除undefined值
  Object.keys(params).forEach(key => params[key] === undefined && delete params[key])
  
  return request({
    url: '/api/testing/ui-automation/executions',
    method: 'get',
    params
  })
}

/**
 * 获取UI自动化报告列表
 * @param {Object} query 查询参数
 */
export function listUIReports(query) {
  const params = {
    page_num: query.pageNum || query.page_num || 1,
    page_size: query.pageSize || query.page_size || 10,
    report_name: query.reportName || query.report_name,
    report_type: query.reportType || query.report_type || 'ui',
    begin_time: query.beginTime || query.begin_time,
    end_time: query.endTime || query.end_time
  }
  // 移除undefined值
  Object.keys(params).forEach(key => params[key] === undefined && delete params[key])
  
  return request({
    url: '/api/testing/ui-automation/reports',
    method: 'get',
    params
  })
}

/**
 * 删除UI自动化报告
 * @param {Number} reportId 报告ID
 */
export function deleteUIReport(reportId) {
  return request({
    url: `/api/testing/ui-automation/reports/${reportId}`,
    method: 'delete'
  })
}

