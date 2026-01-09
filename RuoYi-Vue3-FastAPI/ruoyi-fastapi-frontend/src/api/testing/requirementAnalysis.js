import request from '@/utils/request'

// 查询需求分析列表
export function listRequirementAnalysis(query) {
  return request({
    url: '/api/testing/requirement/list',
    method: 'get',
    params: query
  })
}

// 查询需求分析详细
export function getRequirementAnalysis(requirementId) {
  return request({
    url: '/api/testing/requirement/detail/' + requirementId,
    method: 'get'
  })
}

// 新增需求分析
export function addRequirementAnalysis(data) {
  return request({
    url: '/api/testing/requirement/create',
    method: 'post',
    data: data
  })
}

// 修改需求分析
export function updateRequirementAnalysis(requirementId, data) {
  return request({
    url: '/api/testing/requirement/update/' + requirementId,
    method: 'put',
    data: data
  })
}

// 删除需求分析
export function delRequirementAnalysis(requirementId) {
  return request({
    url: '/api/testing/requirement/delete/' + requirementId,
    method: 'delete'
  })
}

// AI分析需求
export function analyzeRequirement(data) {
  return request({
    url: '/api/testing/requirement/ai-generate',
    method: 'post',
    data: data
  })
}

// 下载需求分析
export function downloadRequirement(requirementId, format = 'json') {
  return request({
    url: '/api/testing/requirement/download/' + requirementId,
    method: 'get',
    params: { format }
  })
}
