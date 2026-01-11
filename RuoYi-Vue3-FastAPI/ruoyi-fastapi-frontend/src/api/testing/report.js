/**
 * 测试报告管理API
 */
import request from '@/utils/request'

/**
 * 获取报告分页列表
 * @param {Object} query - 查询参数
 */
export function listReport(query) {
  return request({
    url: '/api/testing/report/list',
    method: 'get',
    params: {
      report_name: query.report_name,
      report_type: query.report_type,
      script_type: query.script_type,
      project_id: query.project_id,
      execution_id: query.execution_id,
      page_num: query.page_num || 1,
      page_size: query.page_size || 10
    }
  })
}

/**
 * 获取报告详情
 * @param {number} reportId - 报告ID
 */
export function getReport(reportId) {
  return request({
    url: `/api/testing/report/${reportId}`,
    method: 'get'
  })
}

/**
 * 删除报告
 * @param {string|number} reportIds - 报告ID，多个用逗号分隔
 */
export function delReport(reportIds) {
  return request({
    url: `/api/testing/report/${reportIds}`,
    method: 'delete'
  })
}

/**
 * 下载报告
 * @param {number} reportId - 报告ID
 */
export function downloadReport(reportId) {
  return request({
    url: `/api/testing/report/${reportId}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 生成HTML报告
 * @param {number} executionId - 执行ID
 */
export function generateHtmlReport(executionId) {
  return request({
    url: `/api/testing/report/generate/${executionId}`,
    method: 'post'
  })
}

/**
 * 报告对比
 * @param {Object} data - 对比参数
 * @param {Array<number>} data.report_ids - 报告ID列表
 */
export function compareReports(data) {
  return request({
    url: '/api/testing/report/compare',
    method: 'post',
    data: {
      report_ids: data.report_ids
    }
  })
}

/**
 * 导出报告为PDF
 * @param {number} reportId - 报告ID
 */
export function exportReportPdf(reportId) {
  return request({
    url: `/api/testing/report/${reportId}/export/pdf`,
    method: 'post',
    responseType: 'blob'
  })
}

/**
 * 获取报告统计信息
 */
export function getReportStatistics() {
  return request({
    url: '/api/testing/report/statistics',
    method: 'get'
  })
}

