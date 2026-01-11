import request from '@/utils/request'

// 查询知识库列表
export function listKnowledge(query) {
  return request({
    url: '/api/testing/knowledge/list',
    method: 'get',
    params: query
  })
}

// 查询知识库详细
export function getKnowledge(knowledgeId) {
  return request({
    url: '/api/testing/knowledge/' + knowledgeId,
    method: 'get'
  })
}

// 新增知识库
export function addKnowledge(data) {
  return request({
    url: '/api/testing/knowledge/create',
    method: 'post',
    data: data
  })
}

// 修改知识库
export function updateKnowledge(data) {
  return request({
    url: '/api/testing/knowledge/update',
    method: 'put',
    data: data
  })
}

// 删除知识库
export function delKnowledge(knowledgeIds) {
  return request({
    url: '/api/testing/knowledge/' + knowledgeIds,
    method: 'delete'
  })
}

// 获取知识库统计
export function getKnowledgeStats(knowledgeId) {
  return request({
    url: '/api/testing/knowledge/' + knowledgeId + '/stats',
    method: 'get'
  })
}

// 通过项目ID获取知识库
export function getKnowledgeByProject(projectId) {
  return request({
    url: '/api/testing/knowledge/project/' + projectId,
    method: 'get'
  })
}

// 通过项目ID上传文件
export function uploadFileByProject(projectId, data) {
  return request({
    url: '/api/testing/knowledge/project/' + projectId + '/files/upload',
    method: 'post',
    data: data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 上传文件到知识库
export function uploadFile(knowledgeId, data) {
  return request({
    url: '/api/testing/knowledge/' + knowledgeId + '/files/upload',
    method: 'post',
    data: data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 查询文件列表
export function getFileList(knowledgeId, query) {
  return request({
    url: '/api/testing/knowledge/' + knowledgeId + '/files',
    method: 'get',
    params: query
  })
}

// 查询项目文件列表
export function getFileListByProject(projectId, query) {
  return request({
    url: '/api/testing/knowledge/project/' + projectId + '/files',
    method: 'get',
    params: query
  })
}

// 查询所有项目的文件列表
export function getAllFilesList(query) {
  return request({
    url: '/api/testing/knowledge/files/all',
    method: 'get',
    params: query
  })
}

// 下载文件
export function downloadFile(fileId, preview = false) {
  return request({
    url: '/api/testing/knowledge/files/' + fileId + '/download',
    method: 'get',
    params: { preview },
    responseType: 'blob'
  })
}

// 删除文件
export function deleteFile(fileId) {
  return request({
    url: '/api/testing/knowledge/files/' + fileId,
    method: 'delete'
  })
}

// 通过项目ID查询知识库
export function queryKnowledgeByProject(projectId, data) {
  return request({
    url: '/api/testing/knowledge/project/' + projectId + '/query',
    method: 'post',
    data: data
  })
}

// 查询知识库
export function queryKnowledge(knowledgeId, data) {
  return request({
    url: '/api/testing/knowledge/' + knowledgeId + '/query',
    method: 'post',
    data: data
  })
}

// 获取项目RAG文档列表
export function getProjectRagDocuments(projectId, query) {
  return request({
    url: '/api/testing/knowledge/project/' + projectId + '/rag-documents',
    method: 'get',
    params: query
  })
}

// 获取所有RAG文档列表
export function getAllRagDocuments(query) {
  return request({
    url: '/api/testing/knowledge/rag-documents/all',
    method: 'get',
    params: query
  })
}

// 获取知识库RAG文档列表
export function getKnowledgeRagDocuments(knowledgeId, query) {
  return request({
    url: '/api/testing/knowledge/' + knowledgeId + '/rag-documents',
    method: 'get',
    params: query
  })
}

// 根据RAG文档ID获取文件信息
export function getRagDocumentFile(docId, preview = false) {
  return request({
    url: '/api/testing/knowledge/rag-documents/' + docId + '/file',
    method: 'get',
    params: { preview }
  })
}

// 获取处理器状态
export function getProcessorStatus() {
  return request({
    url: '/api/testing/knowledge/processor/status',
    method: 'get'
  })
}

// 重启处理器
export function restartProcessor() {
  return request({
    url: '/api/testing/knowledge/processor/restart',
    method: 'post'
  })
}
