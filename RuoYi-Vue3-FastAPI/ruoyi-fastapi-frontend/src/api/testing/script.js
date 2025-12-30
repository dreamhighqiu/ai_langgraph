import request from '@/utils/request'

// 查询脚本列表
export function listScript(query) {
  return request({
    url: '/testing/script/list',
    method: 'get',
    params: query
  })
}

// 查询脚本详情
export function getScript(scriptId) {
  return request({
    url: '/testing/script/' + scriptId,
    method: 'get'
  })
}

// 新增脚本
export function addScript(data) {
  return request({
    url: '/testing/script',
    method: 'post',
    data: data
  })
}

// AI生成脚本
export function generateScript(data) {
  return request({
    url: '/testing/script/generate',
    method: 'post',
    data: data
  })
}

// 修改脚本
export function updateScript(data) {
  return request({
    url: '/testing/script',
    method: 'put',
    data: data
  })
}

// 删除脚本
export function delScript(scriptIds) {
  return request({
    url: '/testing/script/' + scriptIds,
    method: 'delete'
  })
}

// 执行脚本
export function executeScript(data) {
  return request({
    url: '/testing/script/execute',
    method: 'post',
    data: data
  })
}

