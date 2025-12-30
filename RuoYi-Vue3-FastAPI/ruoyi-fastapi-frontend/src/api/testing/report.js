import request from '@/utils/request'

// 查询报告列表
export function listReport(query) {
  return request({
    url: '/testing/report/list',
    method: 'get',
    params: query
  })
}

// 查询报告详情
export function getReport(reportId) {
  return request({
    url: '/testing/report/' + reportId,
    method: 'get'
  })
}

// 下载报告
export function downloadReport(reportId) {
  return request({
    url: '/testing/report/' + reportId + '/download',
    method: 'get'
  })
}

// 报告对比
export function compareReports(data) {
  return request({
    url: '/testing/report/compare',
    method: 'post',
    data: data
  })
}

// 生成HTML报告
export function generateHtmlReport(executionId) {
  return request({
    url: '/testing/report/generate/' + executionId,
    method: 'post'
  })
}

// 删除报告
export function delReport(reportId) {
  return request({
    url: '/testing/report/' + reportId,
    method: 'delete'
  })
}

