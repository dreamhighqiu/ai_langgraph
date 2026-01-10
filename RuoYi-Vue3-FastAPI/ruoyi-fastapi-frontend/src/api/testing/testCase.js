import request from '@/utils/request'

// 查询测试用例列表
export function listTestCase(query) {
  return request({
    url: '/api/testing/test-case/list',
    method: 'get',
    params: query
  })
}

// 查询测试用例详细
export function getTestCase(caseId) {
  return request({
    url: '/api/testing/test-case/' + caseId,
    method: 'get'
  })
}

// 新增测试用例
export function addTestCase(data) {
  return request({
    url: '/api/testing/test-case',
    method: 'post',
    data: data
  })
}

// 修改测试用例
export function updateTestCase(caseId, data) {
  return request({
    url: '/api/testing/test-case/' + caseId,
    method: 'put',
    data: data
  })
}

// 删除测试用例
export function delTestCase(caseId) {
  return request({
    url: '/api/testing/test-case/' + caseId,
    method: 'delete'
  })
}

// 批量创建测试用例
export function batchCreateTestCase(data) {
  return request({
    url: '/api/testing/test-case/batch',
    method: 'post',
    data: data
  })
}

// 移动测试用例到指定文件夹
export function moveTestCase(caseId, folderId) {
  return request({
    url: '/api/testing/test-case/move/' + caseId,
    method: 'put',
    data: { folder_id: folderId }
  })
}

// 复制测试用例
export function copyTestCase(caseId, folderId) {
  return request({
    url: '/api/testing/test-case/copy/' + caseId,
    method: 'post',
    data: { folder_id: folderId }
  })
}

// 修改测试用例状态
export function changeTestCaseStatus(caseId, status) {
  return request({
    url: '/api/testing/test-case/status/' + caseId,
    method: 'put',
    data: { status }
  })
}

// 统计项目测试用例数量
export function getProjectTestCaseStats(projectId) {
  return request({
    url: '/api/testing/test-case/count/' + projectId,
    method: 'get'
  })
}

// ==================== AI 生成测试用例相关 API ====================

// AI 生成测试用例
export function aiGenerateTestCase(data) {
  return request({
    url: '/api/testing/ai-testcase/generate',
    method: 'post',
    data: data
  })
}

// AI 从文档生成测试用例
export function aiGenerateFromDoc(data) {
  return request({
    url: '/api/testing/ai-testcase/generate-from-doc',
    method: 'post',
    data: data
  })
}

// 批量创建 AI 生成的测试用例
export function batchCreateFromAI(data) {
  return request({
    url: '/api/testing/ai-testcase/batch-create',
    method: 'post',
    data: data
  })
}

// 获取 AI 生成建议
export function getAISuggestions(projectId, context) {
  return request({
    url: '/api/testing/ai-testcase/suggestions',
    method: 'get',
    params: { project_id: projectId, context }
  })
}

// ==================== 导出相关 API ====================

// 导出测试用例为Excel
export function exportTestCaseToExcel(params) {
  return request({
    url: '/api/testing/test-case/export/excel',
    method: 'get',
    params: params,
    responseType: 'blob'
  })
}

// 导出测试用例为XMind
export function exportTestCaseToXMind(params) {
  return request({
    url: '/api/testing/test-case/export/xmind',
    method: 'get',
    params: params,
    responseType: 'blob'
  })
}