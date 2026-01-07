import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const responseTimeTrend = new Trend('response_time_trend');

// 测试配置
export const options = {
  // 压力测试：逐步增加负载直到系统极限
  stages: [
    // 阶段1：逐步增加到100个VUs（2分钟）
    { duration: '60s', target: 50 },  // 0-60秒：增加到50个VUs
    { duration: '60s', target: 100 }, // 60-120秒：增加到100个VUs
    
    // 阶段2：继续增加到500个VUs（3分钟）
    { duration: '60s', target: 200 },  // 120-180秒：增加到200个VUs
    { duration: '60s', target: 350 },  // 180-240秒：增加到350个VUs
    { duration: '60s', target: 500 },  // 240-300秒：增加到500个VUs
    
    // 阶段3：保持500个VUs运行2分钟，观察稳定性
    { duration: '120s', target: 500 }, // 300-420秒：保持500个VUs
  ],
  
  // 性能阈值
  thresholds: {
    // 响应时间阈值
    'http_req_duration': [
      'p(95)<2000',  // 95%的请求响应时间应小于2秒
      'p(99)<5000',  // 99%的请求响应时间应小于5秒
    ],
    // 错误率阈值
    'errors': ['rate<0.05'],  // 错误率应小于5%
    // 检查点成功率
    'checks': ['rate>0.95'],  // 检查点成功率应大于95%
  },
  
  // 其他配置
  discardResponseBodies: false,  // 保留响应体用于检查
  noConnectionReuse: false,      // 启用连接复用
  userAgent: 'K6-Stress-Test/1.0',
  
  // 超时设置
  httpDebug: 'full',  // 详细日志（调试时启用）
  
  // 重试配置
  maxRedirects: 5,
  noVUConnectionReuse: false,
  
  // 连接池配置
  batch: 20,
  batchPerHost: 20,
};

// 随机延迟函数，模拟真实用户行为
function getRandomDelay() {
  return Math.random() * 1.5 + 0.5; // 0.5-2秒随机延迟
}

// 测试主函数
export default function () {
  const url = 'https://www.baidu.com/';
  
  // 设置请求头
  const headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
  };
  
  // 发送GET请求
  const response = http.get(url, {
    headers: headers,
    tags: { name: 'Baidu_Homepage' },
    timeout: '30s',  // 30秒超时
  });
  
  // 记录响应时间到自定义指标
  responseTimeTrend.add(response.timings.duration);
  
  // 检查点验证
  const checks = check(response, {
    // 基本检查
    '状态码是200': (r) => r.status === 200,
    '响应时间小于3秒': (r) => r.timings.duration < 3000,
    'HTTP请求成功': (r) => r.status >= 200 && r.status < 400,
    
    // 内容检查
    '页面包含百度字样': (r) => r.body.includes('百度') || r.body.includes('baidu'),
    '响应体不为空': (r) => r.body && r.body.length > 0,
    
    // 性能检查
    'TTFB小于1秒': (r) => r.timings.waiting < 1000,
    '下载时间合理': (r) => r.timings.downloading < 2000,
  });
  
  // 记录错误
  if (!checks) {
    errorRate.add(1);
    console.error(`请求失败: ${response.status} - ${response.url}`);
    console.error(`响应时间: ${response.timings.duration}ms`);
    
    // 记录详细错误信息
    if (response.error) {
      console.error(`错误信息: ${response.error}`);
    }
  } else {
    errorRate.add(0);
  }
  
  // 记录详细指标（调试用）
  if (__ITER % 100 === 0) {
    console.log(`迭代 ${__ITER}: 状态码=${response.status}, 时间=${response.timings.duration}ms, VU=${__VU}`);
  }
  
  // 添加随机延迟，模拟真实用户思考时间
  sleep(getRandomDelay());
}

// 测试后处理函数
export function handleSummary(data) {
  console.log('压力测试完成！');
  console.log(`总请求数: ${data.metrics.http_reqs.values.count}`);
  console.log(`平均RPS: ${data.metrics.http_reqs.values.rate.toFixed(2)}`);
  console.log(`平均响应时间: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms`);
  console.log(`P95响应时间: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms`);
  console.log(`P99响应时间: ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)}ms`);
  console.log(`错误率: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%`);
  console.log(`虚拟用户峰值: ${data.metrics.vus_max.values.value}`);
  
  // 检查阈值是否通过
  const thresholds = data.metrics.checks.passes;
  console.log(`检查点通过率: ${(thresholds / data.metrics.checks.values.count * 100).toFixed(2)}%`);
  
  // 返回JSON格式的摘要
  return {
    'stress_test_summary.json': JSON.stringify(data, null, 2),
  };
}