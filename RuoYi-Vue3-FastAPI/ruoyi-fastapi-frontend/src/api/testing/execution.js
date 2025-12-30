import request from '@/utils/request'

// 查询执行记录列表
export function listExecution(query) {
  return request({
    url: '/testing/execution/list',
    method: 'get',
    params: query
  })
}

// 查询执行详情
export function getExecution(executionId) {
  return request({
    url: '/testing/execution/' + executionId,
    method: 'get'
  })
}

// 查询执行状态
export function getExecutionStatus(executionId) {
  return request({
    url: '/testing/execution/' + executionId + '/status',
    method: 'get'
  })
}

// 获取执行统计数据
export function getExecutionStatistics(days) {
  return request({
    url: '/testing/execution/statistics',
    method: 'get',
    params: { days }
  })
}

// 获取正在运行的执行
export function getRunningExecutions() {
  return request({
    url: '/testing/execution/running',
    method: 'get'
  })
}

// 取消执行
export function cancelExecution(data) {
  return request({
    url: '/testing/execution/cancel',
    method: 'post',
    data: data
  })
}

// 重试执行
export function retryExecution(executionId) {
  return request({
    url: '/testing/execution/' + executionId + '/retry',
    method: 'post'
  })
}

