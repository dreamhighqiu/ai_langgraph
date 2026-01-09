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

// ==================== AI 缺陷分析相关 API ====================

// AI 分析缺陷
export function aiAnalyzeDefect(data) {
  return request({
    url: '/api/testing/ai-defect/analyze',
    method: 'post',
    data: data
  })
}

// AI 缺陷分类
export function aiClassifyDefect(data) {
  return request({
    url: '/api/testing/ai-defect/classify',
    method: 'post',
    data: data
  })
}

// 查找相似缺陷
export function findSimilarDefects(data) {
  return request({
    url: '/api/testing/ai-defect/find-similar',
    method: 'post',
    data: data
  })
}

// 保存缺陷分析结果
export function saveDefectAnalysisResult(data) {
  return request({
    url: '/api/testing/ai-defect/save-analysis',
    method: 'post',
    data: data
  })
}

// 获取缺陷分析历史
export function getDefectAnalysisHistory(params) {
  return request({
    url: '/api/testing/ai-defect/history',
    method: 'get',
    params: params
  })
}

// 生成回归测试用例
export function generateRegressionCases(data) {
  return request({
    url: '/api/testing/ai-defect/generate-regression-cases',
    method: 'post',
    data: data
  })
}