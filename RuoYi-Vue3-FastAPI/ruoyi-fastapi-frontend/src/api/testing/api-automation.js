/**
 * API自动化（REST API）专用API
 */
import request from '@/utils/request'

// ==================== API自动化需求管理 ====================

/**
 * 获取API自动化需求分页列表
 */
export function getAPIRequirementList(query) {
  return request({
    url: '/api/testing/requirement/list',
    method: 'get',
    params: {
      ...query,
      requirement_type: 'api'
    }
  })
}

/**
 * 获取API自动化需求详情
 */
export function getAPIRequirement(id) {
  return request({
    url: `/testing/requirement/${id}`,
    method: 'get'
  })
}

/**
 * 新增API自动化需求
 */
export function addAPIRequirement(data) {
  return request({
    url: '/api/testing/requirement',
    method: 'post',
    data: {
      ...data,
      requirement_type: 'api'
    }
  })
}

/**
 * 修改API自动化需求
 */
export function updateAPIRequirement(data) {
  return request({
    url: '/api/testing/requirement',
    method: 'put',
    data
  })
}

/**
 * 删除API自动化需求
 */
export function delAPIRequirement(ids) {
  return request({
    url: '/api/testing/requirement',
    method: 'delete',
    data: { requirement_ids: ids }
  })
}

/**
 * AI生成REST API自动化脚本
 */
export function generateRestAPIScript(requirementId, config) {
  return request({
    url: `/testing/requirement/${requirementId}/generate`,
    method: 'post',
    data: {
      use_rag: config?.use_rag || false,
      // REST API特有配置
      base_url: config?.base_url || '',           // 基础URL
      auth_type: config?.auth_type || 'none',     // none, bearer, basic, api_key
      headers: config?.headers || {},              // 默认Headers
      timeout: config?.timeout || 10000,          // 请求超时(ms)
      retry: config?.retry || 3,                  // 重试次数
      assertions: config?.assertions || [         // 断言规则
        { type: 'status_code', expected: 200 },
        { type: 'response_time', operator: '<', value: 1000 }
      ]
    }
  })
}

/**
 * AI分析API自动化需求
 */
export function analyzeAPIRequirement(requirementId) {
  return request({
    url: `/testing/requirement/${requirementId}/analyze`,
    method: 'post'
  })
}

// ==================== API自动化脚本管理 ====================

/**
 * 获取REST API脚本列表
 */
export function getRestAPIScriptList(query) {
  return request({
    url: '/api/testing/script/list',
    method: 'get',
    params: {
      ...query,
      script_type: 'rest_api'
    }
  })
}

/**
 * 获取REST API脚本详情
 */
export function getRestAPIScript(id) {
  return request({
    url: `/testing/script/${id}`,
    method: 'get'
  })
}

/**
 * 新增REST API脚本
 */
export function addRestAPIScript(data) {
  return request({
    url: '/api/testing/script',
    method: 'post',
    data: {
      ...data,
      script_type: 'rest_api'
    }
  })
}

/**
 * 更新REST API脚本
 */
export function updateRestAPIScript(data) {
  return request({
    url: '/api/testing/script',
    method: 'put',
    data
  })
}

/**
 * 删除REST API脚本
 */
export function delRestAPIScript(ids) {
  return request({
    url: '/api/testing/script',
    method: 'delete',
    data: { script_ids: ids }
  })
}

// ==================== REST API脚本执行 ====================

/**
 * 执行REST API自动化测试
 */
export function executeRestAPIScript(scriptId, config) {
  return request({
    url: `/testing/script/${scriptId}/execute`,
    method: 'post',
    data: {
      // REST API执行配置
      base_url: config?.base_url || '',
      auth_type: config?.auth_type || 'none',
      auth_config: config?.auth_config || {},
      headers: config?.headers || {},
      timeout: config?.timeout || 10000,
      retry: config?.retry || 3,
      parallel: config?.parallel || false,        // 并行执行
      env_vars: config?.env_vars || {}
    }
  })
}

/**
 * 获取REST API执行记录列表
 */
export function getRestAPIExecutionList(query) {
  return request({
    url: '/api/testing/execution/list',
    method: 'get',
    params: {
      ...query,
      script_type: 'rest_api'
    }
  })
}

/**
 * 获取REST API执行详情
 */
export function getRestAPIExecution(id) {
  return request({
    url: `/testing/execution/${id}`,
    method: 'get'
  })
}

/**
 * 取消REST API执行
 */
export function cancelRestAPIExecution(id) {
  return request({
    url: `/testing/execution/${id}/cancel`,
    method: 'post'
  })
}

/**
 * 重试REST API执行
 */
export function retryRestAPIExecution(id) {
  return request({
    url: `/testing/execution/${id}/retry`,
    method: 'post'
  })
}

// ==================== REST API测试报告 ====================

/**
 * 获取REST API测试报告列表
 */
export function getRestAPIReportList(query) {
  return request({
    url: '/api/testing/report/list',
    method: 'get',
    params: {
      ...query,
      script_type: 'rest_api'
    }
  })
}

/**
 * 获取REST API测试报告详情
 */
export function getRestAPIReport(id) {
  return request({
    url: `/testing/report/${id}`,
    method: 'get'
  })
}

/**
 * 获取API请求/响应详情
 */
export function getAPIRequestDetails(reportId) {
  return request({
    url: `/testing/report/${reportId}/requests`,
    method: 'get'
  })
}

/**
 * 下载REST API测试报告
 */
export function downloadRestAPIReport(id) {
  return request({
    url: `/testing/report/${id}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 删除REST API测试报告
 */
export function delRestAPIReport(ids) {
  return request({
    url: '/api/testing/report',
    method: 'delete',
    data: { report_ids: ids }
  })
}

/**
 * 导出REST API测试报告（HTML）
 */
export function exportRestAPIReportHtml(id) {
  return request({
    url: `/testing/report/${id}/export/html`,
    method: 'post'
  })
}

/**
 * 导出为Postman Collection
 */
export function exportPostmanCollection(scriptIds) {
  return request({
    url: '/api/testing/script/export/postman',
    method: 'post',
    data: { script_ids: scriptIds },
    responseType: 'blob'
  })
}

/**
 * 从Swagger导入API定义
 */
export function importFromSwagger(swaggerUrl) {
  return request({
    url: '/api/testing/script/import/swagger',
    method: 'post',
    data: { swagger_url: swaggerUrl }
  })
}

