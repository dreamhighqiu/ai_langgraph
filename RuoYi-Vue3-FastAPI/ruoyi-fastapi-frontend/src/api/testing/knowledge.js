import request from '@/utils/request'

// 查询知识库列表
export function listKnowledge(query) {
  const params = {
    page_num: query?.pageNum ?? query?.page_num ?? 1,
    page_size: query?.pageSize ?? query?.page_size ?? 10,
    project_id: query?.projectId ?? query?.project_id,
    knowledge_name: query?.knowledgeName ?? query?.knowledge_name,
    status: query?.status
  }
  return request({
    url: '/testing/knowledge/list',
    method: 'get',
    params
  })
}

// 查询知识库详情
export function getKnowledge(knowledgeId) {
  return request({
    url: '/testing/knowledge/' + knowledgeId,
    method: 'get'
  })
}

// 新增知识库
export function createKnowledge(data) {
  return request({
    url: '/testing/knowledge/create',
    method: 'post',
    data: {
      project_id: data.projectId,
      knowledge_name: data.knowledgeName,
      description: data.description,
      remark: data.remark
    }
  })
}

// 修改知识库
export function updateKnowledge(data) {
  return request({
    url: '/testing/knowledge/update',
    method: 'put',
    data: {
      knowledge_id: data.knowledgeId,
      knowledge_name: data.knowledgeName,
      description: data.description,
      status: data.status,
      remark: data.remark
    }
  })
}

// 删除知识库（支持单个ID或ID数组）
export function deleteKnowledge(knowledgeIds) {
  // 如果是数组，转换为逗号分隔的字符串
  const ids = Array.isArray(knowledgeIds) ? knowledgeIds.join(',') : knowledgeIds;
  return request({
    url: '/testing/knowledge/' + ids,
    method: 'delete'
  })
}

// 获取知识库统计信息
export function getKnowledgeStats(knowledgeId) {
  return request({
    url: '/testing/knowledge/' + knowledgeId + '/stats',
    method: 'get'
  })
}

// 上传文件到知识库
export function uploadKnowledgeFile(knowledgeId, formData) {
  return request({
    url: '/testing/knowledge/' + knowledgeId + '/files/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 60000 // 上传超时时间 60秒
  })
}

// 查询知识库文件列表
export function listKnowledgeFiles(knowledgeId, query) {
  const params = {
    page_num: query?.pageNum ?? query?.page_num ?? 1,
    page_size: query?.pageSize ?? query?.page_size ?? 10,
    file_name: query?.fileName ?? query?.file_name,
    process_status: query?.processStatus ?? query?.process_status
  }
  return request({
    url: '/testing/knowledge/' + knowledgeId + '/files',
    method: 'get',
    params
  })
}

// 删除知识库文件
export function deleteKnowledgeFile(fileId) {
  return request({
    url: '/testing/knowledge/files/' + fileId,
    method: 'delete'
  })
}

// 获取文件下载URL
export function getFileDownloadUrl(fileId) {
  return request({
    url: '/testing/knowledge/files/' + fileId + '/download',
    method: 'get'
  })
}

// 获取项目RAG处理后的文档列表
export function getProjectRagDocuments(projectId, params) {
  return request({
    url: '/testing/knowledge/project/' + projectId + '/rag-documents',
    method: 'get',
    params
  })
}

// 获取知识库RAG处理后的文档列表
export function getKnowledgeRagDocuments(knowledgeId, params) {
  return request({
    url: '/testing/knowledge/' + knowledgeId + '/rag-documents',
    method: 'get',
    params
  })
}

// 知识库查询（RAG）
export function queryKnowledge(knowledgeId, data) {
  return request({
    url: '/testing/knowledge/' + knowledgeId + '/query',
    method: 'post',
    data: {
      query: data.query,
      mode: data.mode || 'hybrid',
      top_k: data.topK ?? data.top_k
    },
    timeout: 60000 // 查询超时时间 60秒
  })
}

