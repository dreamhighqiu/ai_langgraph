import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const responseTimeTrend = new Trend('response_time');
const successRate = new Rate('successful_requests');

// 测试配置
export const options = {
  // 冒烟测试配置
  stages: [
    { duration: '30s', target: 3 }, // 30秒内逐步增加到3个VUs
    { duration: '30s', target: 3 }, // 保持3个VUs运行30秒
  ],
  
  // 阈值设置
  thresholds: {
    // 响应时间阈值
    'http_req_duration': [
      'avg < 100',      // 平均响应时间小于100ms
      'p(95) < 200',    // 95%响应时间小于200ms
    ],
    
    // 错误率阈值
    'errors': ['rate < 0.01'], // 错误率低于1%
    
    // 检查通过率
    'checks': ['rate > 0.99'], // 检查通过率高于99%
    
    // 成功率
    'successful_requests': ['rate > 0.99'], // 成功率高于99%
  },
  
  // 其他配置
  discardResponseBodies: false, // 保留响应体用于验证
  noConnectionReuse: false,     // 启用连接复用
};

// 测试数据
const BASE_URL = 'http://appserver.huice.com';
const API_ENDPOINT = '/cms/home/index';

// 请求头配置
const headers = {
  'access-token': 'test-smoke-token-12345',
  'fecshop-currency': 'USD',
  'fecshop-lang': 'en',
  'Content-Type': 'application/json',
  'User-Agent': 'k6-smoke-test/1.0',
};

// 测试主函数
export default function () {
  // 记录请求开始时间
  const startTime = Date.now();
  
  // 发送GET请求
  const response = http.get(`${BASE_URL}${API_ENDPOINT}`, {
    headers: headers,
    tags: { name: 'cms_home_index' },
  });
  
  // 记录响应时间
  const responseTime = Date.now() - startTime;
  responseTimeTrend.add(responseTime);
  
  // 验证响应
  const checks = {
    // 验证状态码
    '状态码为200': (res) => res.status === 200,
    
    // 验证响应时间合理
    '响应时间合理': (res) => res.timings.duration < 5000, // 5秒内
    
    // 验证响应体不为空
    '响应体不为空': (res) => res.body && res.body.length > 0,
    
    // 验证JSON格式
    '有效的JSON响应': (res) => {
      try {
        JSON.parse(res.body);
        return true;
      } catch (e) {
        return false;
      }
    },
    
    // 验证响应结构
    '响应包含code字段': (res) => {
      try {
        const json = JSON.parse(res.body);
        return json.code !== undefined;
      } catch (e) {
        return false;
      }
    },
    
    // 验证产品数据
    '响应包含产品数据': (res) => {
      try {
        const json = JSON.parse(res.body);
        return json.data !== undefined && json.data.productList !== undefined;
      } catch (e) {
        return false;
      }
    },
    
    // 验证产品列表不为空
    '产品列表不为空': (res) => {
      try {
        const json = JSON.parse(res.body);
        return json.data && 
               json.data.productList && 
               Array.isArray(json.data.productList) && 
               json.data.productList.length > 0;
      } catch (e) {
        return false;
      }
    },
  };
  
  // 执行检查
  const checkResult = check(response, checks);
  
  // 更新成功率指标
  successRate.add(checkResult);
  
  // 更新错误率指标
  if (!checkResult || response.status !== 200) {
    errorRate.add(1);
  } else {
    errorRate.add(0);
  }
  
  // 记录详细日志（仅对失败请求）
  if (!checkResult || response.status !== 200) {
    console.log(`请求失败: ${response.status} - ${response.url}`);
    console.log(`响应体: ${response.body.substring(0, 200)}...`);
  }
  
  // 添加思考时间（模拟用户行为）
  sleep(1);
}

// 测试设置函数（可选）
export function setup() {
  console.log('🚀 开始CMS首页冒烟测试');
  console.log(`📊 测试目标: ${BASE_URL}${API_ENDPOINT}`);
  console.log(`👥 虚拟用户数: 3个VUs`);
  console.log(`⏱️  测试时长: 1分钟`);
  console.log(`🔧 请求头配置:`);
  console.log(`   - access-token: ${headers['access-token']}`);
  console.log(`   - fecshop-currency: ${headers['fecshop-currency']}`);
  console.log(`   - fecshop-lang: ${headers['fecshop-lang']}`);
  console.log('='.repeat(50));
}

// 测试清理函数（可选）
export function teardown(data) {
  console.log('='.repeat(50));
  console.log('✅ CMS首页冒烟测试完成');
  console.log('📈 请查看上方测试摘要获取详细结果');
}