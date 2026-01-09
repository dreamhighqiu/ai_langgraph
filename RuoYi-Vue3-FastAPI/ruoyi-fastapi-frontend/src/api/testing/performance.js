/**
 * 性能测试（K6）专用API
 */
import request from '@/utils/request'

// ==================== 性能测试需求管理 ====================

/**
 * 获取性能测试需求分页列表
 */
export function getPerformanceRequirementList(query) {
  return request({
    url: '/api/testing/requirement/list',
    method: 'get',
    params: {
      ...query,
      requirement_type: 'performance'
    }
  })
}

/**
 * 获取性能测试需求详情
 */
export function getPerformanceRequirement(id) {
  return request({
    url: `/testing/requirement/${id}`,
    method: 'get'
  })
}

/**
 * 新增性能测试需求
 */
export function addPerformanceRequirement(data) {
  return request({
    url: '/api/testing/requirement',
    method: 'post',
    data: {
      ...data,
      requirement_type: 'performance'
    }
  })
}

/**
 * 修改性能测试需求
 */
export function updatePerformanceRequirement(data) {
  return request({
    url: '/api/testing/requirement',
    method: 'put',
    data
  })
}

/**
 * 删除性能测试需求
 */
export function delPerformanceRequirement(ids) {
  return request({
    url: '/api/testing/requirement',
    method: 'delete',
    data: { requirement_ids: ids }
  })
}

/**
 * AI生成K6性能测试脚本
 */
export function generateK6Script(requirementId, config) {
  return request({
    url: `/testing/requirement/${requirementId}/generate`,
    method: 'post',
    data: {
      use_rag: config?.use_rag || false,
      // K6特有配置
      vus: config?.vus || 10,              // 虚拟用户数
      duration: config?.duration || '30s',  // 测试时长
      thresholds: config?.thresholds || {   // 性能阈值
        http_req_duration: ['p(95)<500'],
        http_req_failed: ['rate<0.01']
      },
      stages: config?.stages || [          // 压力阶段
        { duration: '10s', target: 10 },
        { duration: '30s', target: 100 },
        { duration: '10s', target: 0 }
      ]
    }
  })
}

/**
 * AI分析性能测试需求
 */
export function analyzePerformanceRequirement(requirementId) {
  return request({
    url: `/testing/requirement/${requirementId}/analyze`,
    method: 'post'
  })
}

// ==================== 性能测试脚本管理 ====================

/**
 * 获取K6脚本列表
 */
export function getK6ScriptList(query) {
  return request({
    url: '/api/testing/script/list',
    method: 'get',
    params: {
      ...query,
      script_type: 'k6'
    }
  })
}

/**
 * 获取K6脚本详情
 */
export function getK6Script(id) {
  return request({
    url: `/testing/script/${id}`,
    method: 'get'
  })
}

/**
 * 新增K6脚本
 */
export function addK6Script(data) {
  return request({
    url: '/api/testing/script',
    method: 'post',
    data: {
      ...data,
      script_type: 'k6'
    }
  })
}

/**
 * 更新K6脚本
 */
export function updateK6Script(data) {
  return request({
    url: '/api/testing/script',
    method: 'put',
    data
  })
}

/**
 * 删除K6脚本
 */
export function delK6Script(ids) {
  return request({
    url: '/api/testing/script',
    method: 'delete',
    data: { script_ids: ids }
  })
}

// ==================== K6脚本执行 ====================

/**
 * 执行K6性能测试
 */
export function executeK6Script(scriptId, config) {
  return request({
    url: `/testing/script/${scriptId}/execute`,
    method: 'post',
    data: {
      // K6执行配置
      vus: config?.vus || 10,
      duration: config?.duration || '30s',
      thresholds: config?.thresholds,
      stages: config?.stages,
      env_vars: config?.env_vars || {}
    }
  })
}

/**
 * 获取K6执行记录列表
 */
export function getK6ExecutionList(query) {
  return request({
    url: '/api/testing/execution/list',
    method: 'get',
    params: {
      ...query,
      script_type: 'k6'
    }
  })
}

/**
 * 获取K6执行详情
 */
export function getK6Execution(id) {
  return request({
    url: `/testing/execution/${id}`,
    method: 'get'
  })
}

/**
 * 取消K6执行
 */
export function cancelK6Execution(id) {
  return request({
    url: `/testing/execution/${id}/cancel`,
    method: 'post'
  })
}

/**
 * 重试K6执行
 */
export function retryK6Execution(id) {
  return request({
    url: `/testing/execution/${id}/retry`,
    method: 'post'
  })
}

// ==================== K6性能报告 ====================

/**
 * 获取K6性能报告列表
 */
export function getK6ReportList(query) {
  return request({
    url: '/api/testing/report/list',
    method: 'get',
    params: {
      ...query,
      script_type: 'k6'
    }
  })
}

/**
 * 获取K6性能报告详情
 */
export function getK6Report(id) {
  return request({
    url: `/testing/report/${id}`,
    method: 'get'
  })
}

/**
 * 下载K6性能报告
 */
export function downloadK6Report(id) {
  return request({
    url: `/testing/report/${id}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 删除K6性能报告
 */
export function delK6Report(ids) {
  return request({
    url: '/api/testing/report',
    method: 'delete',
    data: { report_ids: ids }
  })
}

/**
 * 导出K6性能报告（HTML）
 */
export function exportK6ReportHtml(id) {
  return request({
    url: `/testing/report/${id}/export/html`,
    method: 'post'
  })
}

