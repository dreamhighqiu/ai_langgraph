import request from '@/utils/request'

// 查询文件夹树
export function getFolderTree(projectId) {
  // 确保 projectId 是有效的数字
  if (!projectId || projectId === null || projectId === undefined) {
    return Promise.reject(new Error('项目ID不能为空'))
  }
  return request({
    url: '/api/testing/folder/tree',
    method: 'get',
    params: { projectId: Number(projectId) }
  })
}

// 查询文件夹列表
export function listFolder(query) {
  return request({
    url: '/api/testing/folder/list',
    method: 'get',
    params: query
  })
}

// 查询文件夹详细
export function getFolder(folderId) {
  return request({
    url: '/api/testing/folder/' + folderId,
    method: 'get'
  })
}

// 新增文件夹
export function addFolder(data) {
  return request({
    url: '/api/testing/folder',
    method: 'post',
    data: data
  })
}

// 修改文件夹
export function updateFolder(data) {
  return request({
    url: '/api/testing/folder',
    method: 'put',
    data: data
  })
}

// 删除文件夹
export function delFolder(folderId) {
  return request({
    url: '/api/testing/folder/' + folderId,
    method: 'delete'
  })
}

// 移动文件夹
export function moveFolder(folderId, targetParentId) {
  return request({
    url: '/api/testing/folder/move',
    method: 'put',
    data: { folderId, targetParentId }
  })
}
