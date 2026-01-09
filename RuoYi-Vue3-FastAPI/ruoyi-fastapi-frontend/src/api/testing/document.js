/**
 * 文档上传 API
 * 用于 AI 测试用例生成功能
 * 文档会上传到 MinIO，然后返回 URL 供 AI Agent 解析
 */
import request from '@/utils/request'

/**
 * 上传文档到项目知识库（MinIO）
 * @param {number} projectId 项目ID
 * @param {File} file 文件对象
 * @param {string} remark 备注（可选）
 * @returns {Promise} 返回文件信息，包含 URL
 */
export function uploadDocument(projectId, file, remark = '') {
  const formData = new FormData()
  formData.append('file', file)
  if (remark) {
    formData.append('remark', remark)
  }
  
  return request({
    url: `/api/testing/knowledge/project/${projectId}/files/upload`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 60000 // 文件上传可能需要更长时间
  })
}

/**
 * 上传文档并获取预签名 URL（用于 AI 处理）
 * @param {number} projectId 项目ID
 * @param {File} file 文件对象
 * @returns {Promise<{success: boolean, data: {url: string, file_name: string, file_size: number, content_type: string}}>}
 */
export async function uploadDocumentForAI(projectId, file) {
  try {
    const response = await uploadDocument(projectId, file, 'AI测试用例生成')
    
    if (response.code === 200 && response.data) {
      // 构造 AI 需要的格式
      return {
        success: true,
        data: {
          file_id: response.data.file_id,
          object_name: response.data.object_name || response.data.file_path,
          file_name: response.data.file_name || file.name,
          file_size: response.data.file_size || file.size,
          content_type: response.data.content_type || file.type,
          url: response.data.file_url || response.data.url || ''
        }
      }
    }
    
    return {
      success: false,
      message: response.msg || '上传失败'
    }
  } catch (error) {
    console.error('文档上传失败:', error)
    return {
      success: false,
      message: error.message || '上传失败'
    }
  }
}

/**
 * 获取文件预签名 URL（用于下载/预览）
 * @param {number} fileId 文件ID
 * @param {boolean} preview 是否预览模式
 * @returns {Promise}
 */
export function getFileUrl(fileId, preview = false) {
  return request({
    url: `/api/testing/knowledge/files/${fileId}/download`,
    method: 'get',
    params: { preview }
  })
}

/**
 * 删除文件
 * @param {number} fileId 文件ID
 * @returns {Promise}
 */
export function deleteDocument(fileId) {
  return request({
    url: `/api/testing/knowledge/files/${fileId}`,
    method: 'delete'
  })
}

