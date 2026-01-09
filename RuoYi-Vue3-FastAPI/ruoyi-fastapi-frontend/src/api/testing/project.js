import request from '@/utils/request'

// 查询项目列表
export function listProject(query) {
  // 兼容前端传入的驼峰字段，统一转换为后端需要的下划线
  const params = {
    project_id: query?.projectId ?? query?.project_id,
    project_name: query?.projectName ?? query?.project_name,
    project_type: query?.projectType ?? query?.project_type,
    status: query?.status,
    begin_time: query?.beginTime ?? query?.begin_time,
    end_time: query?.endTime ?? query?.end_time,
    page_num: query?.pageNum ?? query?.page_num ?? 1,
    page_size: query?.pageSize ?? query?.page_size ?? 10
  }
  return request({
    url: '/api/testing/project/list',
    method: 'get',
    params
  })
}

// 查询所有项目(下拉选择用)
export function listAllProject(status) {
  return request({
    url: '/api/testing/project/all',
    method: 'get',
    params: { status }
  })
}

// 查询项目详情
export function getProject(projectId) {
  return request({
    url: '/api/testing/project/' + projectId,
    method: 'get'
  })
}

// 新增项目
export function addProject(data) {
  return request({
    url: '/api/testing/project',
    method: 'post',
    data: {
      project_name: data.projectName,
      project_type: data.projectType,
      description: data.description,
      status: data.status,
      remark: data.remark
    }
  })
}

// 修改项目
export function updateProject(data) {
  return request({
    url: '/api/testing/project',
    method: 'put',
    data: {
      project_id: data.projectId,
      project_name: data.projectName,
      project_type: data.projectType,
      description: data.description,
      status: data.status,
      remark: data.remark
    }
  })
}

// 删除项目
export function delProject(projectIds) {
  return request({
    url: '/api/testing/project/' + projectIds,
    method: 'delete'
  })
}

// 修改项目状态
export function changeProjectStatus(projectId, status) {
  return request({
    url: '/api/testing/project/changeStatus',
    method: 'put',
    // Backend expects snake_case keys
    data: { project_id: projectId, status: status }
  })
}
