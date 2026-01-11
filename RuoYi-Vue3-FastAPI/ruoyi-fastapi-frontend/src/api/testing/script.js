/**
 * 测试脚本管理API
 * 通用接口，支持k6/playwright/api三种脚本类型
 */
import request from '@/utils/request'

/**
 * 获取脚本分页列表
 * @param {Object} query - 查询参数
 */
export function listScript(query) {
  return request({
    url: '/api/testing/script/list',
    method: 'get',
    params: {
      script_name: query.script_name,
      script_type: query.script_type,
      project_id: query.project_id,
      requirement_id: query.requirement_id,
      status: query.status,
      page_num: query.page_num || 1,
      page_size: query.page_size || 10
    }
  })
}

/**
 * 获取脚本详情
 * @param {number} scriptId - 脚本ID
 */
export function getScript(scriptId) {
  return request({
    url: `/api/testing/script/${scriptId}`,
    method: 'get'
  })
}

/**
 * 新增脚本
 * @param {Object} data - 脚本数据
 */
export function addScript(data) {
  return request({
    url: '/api/testing/script',
    method: 'post',
    data: {
      project_id: data.project_id,
      requirement_id: data.requirement_id,
      script_name: data.script_name,
      script_type: data.script_type,
      script_content: data.script_content,
      version: data.version || '1.0.0',
      status: data.status || '0',
      description: data.description,
      tags: data.tags,
      remark: data.remark
    }
  })
}

/**
 * 修改脚本
 * @param {Object} data - 脚本数据
 */
export function updateScript(data) {
  return request({
    url: '/api/testing/script',
    method: 'put',
    data: {
      script_id: data.script_id,
      project_id: data.project_id,
      requirement_id: data.requirement_id,
      script_name: data.script_name,
      script_type: data.script_type,
      script_content: data.script_content,
      version: data.version,
      status: data.status,
      description: data.description,
      tags: data.tags,
      remark: data.remark
    }
  })
}

/**
 * 删除脚本
 * @param {string|number} scriptIds - 脚本ID，多个用逗号分隔
 */
export function delScript(scriptIds) {
  return request({
    url: `/api/testing/script/${scriptIds}`,
    method: 'delete'
  })
}

/**
 * AI生成脚本
 * @param {Object} data - 生成参数
 * @param {string} data.script_name - 脚本名称
 * @param {number} data.project_id - 项目ID
 * @param {string} data.script_type - 脚本类型：k6/playwright/api
 * @param {string} data.prompt - 生成提示词
 * @param {Object} data.config - 生成配置
 */
export function generateScript(data) {
  return request({
    url: '/api/testing/script/generate',
    method: 'post',
    data: {
      script_name: data.script_name,
      project_id: data.project_id,
      script_type: data.script_type,
      prompt: data.prompt,
      config: data.config || {},
      use_rag: data.use_rag !== false
    }
  })
}

/**
 * 执行脚本
 * @param {Object} data - 执行参数
 * @param {number} data.script_id - 脚本ID
 * @param {Object} data.config - 执行配置
 */
export function executeScript(data) {
  return request({
    url: '/api/testing/script/execute',
    method: 'post',
    data: {
      script_id: data.script_id,
      config: data.config || {}
    }
  })
}

/**
 * 获取脚本版本历史
 * @param {number} scriptId - 脚本ID
 */
export function getScriptVersions(scriptId) {
  return request({
    url: `/api/testing/script/${scriptId}/versions`,
    method: 'get'
  })
}

/**
 * 验证脚本语法
 * @param {Object} data - 验证参数
 */
export function validateScript(data) {
  return request({
    url: '/api/testing/script/validate',
    method: 'post',
    data: {
      script_type: data.script_type,
      script_content: data.script_content
    }
  })
}

