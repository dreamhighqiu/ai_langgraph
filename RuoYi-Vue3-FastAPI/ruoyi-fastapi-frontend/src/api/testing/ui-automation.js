/**
 * UI自动化（Playwright）专用 API 封装
 * 说明：统一走后端 `/api/testing/*` 前缀
 */
import request from '@/utils/request'

// ==================== 需求管理 ====================

export function getUIRequirementList(query) {
  return request({
    url: '/api/testing/requirement/list',
    method: 'get',
    params: {
      ...query,
      requirement_type: 'ui'
    }
  })
}

export function getUIRequirement(id) {
  return request({
    url: `/api/testing/requirement/${id}`,
    method: 'get'
  })
}

export function addUIRequirement(data) {
  return request({
    url: '/api/testing/requirement',
    method: 'post',
    data: {
      ...data,
      requirement_type: 'ui'
    }
  })
}

export function updateUIRequirement(data) {
  return request({
    url: '/api/testing/requirement',
    method: 'put',
    data
  })
}

export function delUIRequirement(ids) {
  return request({
    url: `/api/testing/requirement/${ids}`,
    method: 'delete'
  })
}

export function generatePlaywrightScript(requirementId, options = {}) {
  return request({
    url: `/api/testing/requirement/generate/${requirementId}`,
    method: 'post',
    data: {
      use_rag: options.use_rag !== false,
      config: options.config || {}
    }
  })
}

export function analyzeUIRequirement(requirementId, analyzeType = 'feasibility') {
  return request({
    url: `/api/testing/requirement/analyze/${requirementId}`,
    method: 'post',
    data: { analyze_type: analyzeType }
  })
}

// ==================== 脚本管理 ====================

export function getPlaywrightScriptList(query) {
  return request({
    url: '/api/testing/script/list',
    method: 'get',
    params: {
      ...query,
      script_type: 'playwright'
    }
  })
}

export function getPlaywrightScript(id) {
  return request({
    url: `/api/testing/script/${id}`,
    method: 'get'
  })
}

export function addPlaywrightScript(data) {
  return request({
    url: '/api/testing/script',
    method: 'post',
    data: {
      ...data,
      script_type: 'playwright'
    }
  })
}

export function updatePlaywrightScript(data) {
  return request({
    url: '/api/testing/script',
    method: 'put',
    data
  })
}

export function delPlaywrightScript(ids) {
  return request({
    url: `/api/testing/script/${ids}`,
    method: 'delete'
  })
}

export function executePlaywrightScript(scriptId, config = {}) {
  return request({
    url: '/api/testing/script/execute',
    method: 'post',
    data: {
      script_id: scriptId,
      config
    }
  })
}

// ==================== 执行管理 ====================

export function getPlaywrightExecutionList(query) {
  return request({
    url: '/api/testing/execution/list',
    method: 'get',
    params: {
      ...query,
      script_type: 'playwright'
    }
  })
}

export function getPlaywrightExecution(id) {
  return request({
    url: `/api/testing/execution/${id}`,
    method: 'get'
  })
}

export function cancelPlaywrightExecution(id) {
  return request({
    url: '/api/testing/execution/cancel',
    method: 'post',
    data: { execution_id: id }
  })
}

export function retryPlaywrightExecution(id) {
  return request({
    url: `/api/testing/execution/${id}/retry`,
    method: 'post'
  })
}

// ==================== 报告管理 ====================

export function getPlaywrightReportList(query) {
  return request({
    url: '/api/testing/report/list',
    method: 'get',
    params: {
      ...query,
      script_type: 'playwright'
    }
  })
}

export function getPlaywrightReport(id) {
  return request({
    url: `/api/testing/report/${id}`,
    method: 'get'
  })
}

export function downloadPlaywrightReport(id) {
  return request({
    url: `/api/testing/report/${id}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

export function delPlaywrightReport(id) {
  return request({
    url: `/api/testing/report/${id}`,
    method: 'delete'
  })
}

export function generatePlaywrightHtmlReport(executionId) {
  return request({
    url: `/api/testing/report/generate/${executionId}`,
    method: 'post'
  })
}

