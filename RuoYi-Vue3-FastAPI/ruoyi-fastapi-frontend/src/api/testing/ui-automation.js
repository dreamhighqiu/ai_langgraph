/**
 * UI自动化（Playwright）专用API
 */
import request from '@/utils/request'

// ==================== UI自动化需求管理 ====================

/**
 * 获取UI自动化需求分页列表
 */
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

/**
 * 获取UI自动化需求详情
 */
export function getUIRequirement(id) {
  return request({
    url: `/testing/requirement/${id}`,
    method: 'get'
  })
}

/**
 * 新增UI自动化需求
 */
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

/**
 * 修改UI自动化需求
 */
export function updateUIRequirement(data) {
  return request({
    url: '/api/testing/requirement',
    method: 'put',
    data
  })
}

/**
 * 删除UI自动化需求
 */
export function delUIRequirement(ids) {
  return request({
    url: '/api/testing/requirement',
    method: 'delete',
    data: { requirement_ids: ids }
  })
}

/**
 * AI生成Playwright UI自动化脚本
 */
export function generatePlaywrightScript(requirementId, config) {
  return request({
    url: `/testing/requirement/${requirementId}/generate`,
    method: 'post',
    data: {
      use_rag: config?.use_rag || false,
      // Playwright特有配置
      browser: config?.browser || 'chromium',  // chromium, firefox, webkit
      headless: config?.headless !== false,    // 默认无头模式
      viewport: config?.viewport || { width: 1280, height: 720 },
      screenshot: config?.screenshot !== false, // 失败时截图
      video: config?.video || false,           // 录制视频
      slow_mo: config?.slow_mo || 0,          // 减慢执行速度(ms)
      timeout: config?.timeout || 30000        // 操作超时(ms)
    }
  })
}

/**
 * AI分析UI自动化需求
 */
export function analyzeUIRequirement(requirementId) {
  return request({
    url: `/testing/requirement/${requirementId}/analyze`,
    method: 'post'
  })
}

// ==================== UI自动化脚本管理 ====================

/**
 * 获取Playwright脚本列表
 */
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

/**
 * 获取Playwright脚本详情
 */
export function getPlaywrightScript(id) {
  return request({
    url: `/testing/script/${id}`,
    method: 'get'
  })
}

/**
 * 新增Playwright脚本
 */
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

/**
 * 更新Playwright脚本
 */
export function updatePlaywrightScript(data) {
  return request({
    url: '/api/testing/script',
    method: 'put',
    data
  })
}

/**
 * 删除Playwright脚本
 */
export function delPlaywrightScript(ids) {
  return request({
    url: '/api/testing/script',
    method: 'delete',
    data: { script_ids: ids }
  })
}

// ==================== Playwright脚本执行 ====================

/**
 * 执行Playwright UI自动化测试
 */
export function executePlaywrightScript(scriptId, config) {
  return request({
    url: `/testing/script/${scriptId}/execute`,
    method: 'post',
    data: {
      // Playwright执行配置
      browser: config?.browser || 'chromium',
      headless: config?.headless !== false,
      viewport: config?.viewport,
      screenshot: config?.screenshot !== false,
      video: config?.video || false,
      slow_mo: config?.slow_mo || 0,
      timeout: config?.timeout || 30000,
      env_vars: config?.env_vars || {}
    }
  })
}

/**
 * 获取Playwright执行记录列表
 */
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

/**
 * 获取Playwright执行详情
 */
export function getPlaywrightExecution(id) {
  return request({
    url: `/testing/execution/${id}`,
    method: 'get'
  })
}

/**
 * 取消Playwright执行
 */
export function cancelPlaywrightExecution(id) {
  return request({
    url: `/testing/execution/${id}/cancel`,
    method: 'post'
  })
}

/**
 * 重试Playwright执行
 */
export function retryPlaywrightExecution(id) {
  return request({
    url: `/testing/execution/${id}/retry`,
    method: 'post'
  })
}

// ==================== Playwright测试报告 ====================

/**
 * 获取Playwright测试报告列表
 */
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

/**
 * 获取Playwright测试报告详情
 */
export function getPlaywrightReport(id) {
  return request({
    url: `/testing/report/${id}`,
    method: 'get'
  })
}

/**
 * 获取测试截图列表
 */
export function getTestScreenshots(reportId) {
  return request({
    url: `/testing/report/${reportId}/screenshots`,
    method: 'get'
  })
}

/**
 * 获取测试视频URL
 */
export function getTestVideo(reportId) {
  return request({
    url: `/testing/report/${reportId}/video`,
    method: 'get'
  })
}

/**
 * 下载Playwright测试报告
 */
export function downloadPlaywrightReport(id) {
  return request({
    url: `/testing/report/${id}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 删除Playwright测试报告
 */
export function delPlaywrightReport(ids) {
  return request({
    url: '/api/testing/report',
    method: 'delete',
    data: { report_ids: ids }
  })
}

/**
 * 导出Playwright测试报告（HTML）
 */
export function exportPlaywrightReportHtml(id) {
  return request({
    url: `/testing/report/${id}/export/html`,
    method: 'post'
  })
}

