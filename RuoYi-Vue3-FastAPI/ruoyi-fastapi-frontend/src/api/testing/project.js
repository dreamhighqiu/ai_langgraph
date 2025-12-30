import request from '@/utils/request'

// 查询项目列表
export function listProject(query) {
  return request({
    url: '/testing/project/list',
    method: 'get',
    params: query
  })
}

// 查询所有项目(下拉选择用)
export function listAllProject(status) {
  return request({
    url: '/testing/project/all',
    method: 'get',
    params: { status }
  })
}

// 查询项目详情
export function getProject(projectId) {
  return request({
    url: '/testing/project/' + projectId,
    method: 'get'
  })
}

// 新增项目
export function addProject(data) {
  return request({
    url: '/testing/project',
    method: 'post',
    data: data
  })
}

// 修改项目
export function updateProject(data) {
  return request({
    url: '/testing/project',
    method: 'put',
    data: data
  })
}

// 删除项目
export function delProject(projectIds) {
  return request({
    url: '/testing/project/' + projectIds,
    method: 'delete'
  })
}

// 修改项目状态
export function changeProjectStatus(projectId, status) {
  return request({
    url: '/testing/project/changeStatus',
    method: 'put',
    data: { project_id: projectId, status: status }
  })
}

