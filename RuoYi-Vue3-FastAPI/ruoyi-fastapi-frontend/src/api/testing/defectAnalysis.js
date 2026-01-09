import request from '@/utils/request'

// 查询缺陷分析列表
export function listDefectAnalysis(query) {
  return request({
    url: '/api/testing/defect-analysis/list',
    method: 'get',
    params: query
  })
}

// 查询缺陷分析详细
export function getDefectAnalysis(analysisId) {
  return request({
    url: '/api/testing/defect-analysis/detail/' + analysisId,
    method: 'get'
  })
}

// 新增缺陷分析
export function addDefectAnalysis(data) {
  return request({
    url: '/api/testing/defect-analysis/create',
    method: 'post',
    data: data
  })
}

// 修改缺陷分析
export function updateDefectAnalysis(analysisId, data) {
  return request({
    url: '/api/testing/defect-analysis/update/' + analysisId,
    method: 'put',
    data: data
  })
}

// 删除缺陷分析
export function delDefectAnalysis(analysisId) {
  return request({
    url: '/api/testing/defect-analysis/delete/' + analysisId,
    method: 'delete'
  })
}
