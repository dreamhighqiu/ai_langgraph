/**
 * 质量看板API
 */
import request from '@/utils/request'

/**
 * 获取质量看板汇总数据
 * @param {number} days - 统计天数（近N天）
 */
export function getDashboardSummary(days = 7) {
  return request({
    url: '/api/testing/dashboard/summary',
    method: 'get',
    params: { days }
  })
}

