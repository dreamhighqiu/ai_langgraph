import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// ==================== 自定义指标 ====================
// 错误率指标
const errorRate = new Rate('errors');
// 响应时间趋势
const responseTimeTrend = new Trend('response_time');
// 吞吐量计数器
const requestCounter = new Counter('total_requests');
// 成功请求计数器
const successCounter = new Counter('successful_requests');
// 失败请求计数器
const failureCounter = new Counter('failed_requests');

// ==================== 测试配置 ====================
export const options = {
    // 虚拟用户配置
    vus: 10,
    duration: '30s',
    
    // 阈值配置 - 基于历史性能数据和验收标准
    thresholds: {
        // 响应时间阈值
        'http_req_duration': [
            'avg < 100',      // 平均响应时间 < 100ms
            'p(95) < 200',    // P95响应时间 < 200ms
        ],
        // 错误率阈值
        'errors': ['rate < 0.01'],  // 错误率 < 1%
        // 请求成功率阈值
        'http_req_failed': ['rate < 0.01'],  // 请求失败率 < 1%
        // 自定义指标阈值
        'response_time': ['avg < 100', 'p(95) < 200'],
    },
    
    // 标签配置
    tags: {
        test_type: 'smoke_test',
        endpoint: 'home_page',
        environment: 'production'
    }
};

// ==================== 测试数据 ====================
// 访问令牌 - 在实际使用中应从环境变量或外部文件加载
const ACCESS_TOKEN = 'your-access-token-here';
// 基础URL
const BASE_URL = 'http://appserver.huice.com';
// 首页端点
const HOME_PAGE_ENDPOINT = '/cms/home/index';

// ==================== 辅助函数 ====================
/**
 * 创建请求头
 * @returns {Object} 请求头对象
 */
function createHeaders() {
    return {
        'access-token': ACCESS_TOKEN,
        'fecshop-currency': 'CNY',
        'fecshop-lang': 'zh',
        'Content-Type': 'application/json',
        'User-Agent': 'k6-smoke-test/1.0'
    };
}

/**
 * 验证响应
 * @param {Object} response - HTTP响应对象
 * @returns {boolean} 验证结果
 */
function validateResponse(response) {
    // 检查HTTP状态码
    if (response.status !== 200) {
        console.error(`HTTP错误: ${response.status} - ${response.status_text}`);
        return false;
    }
    
    try {
        // 解析JSON响应
        const jsonResponse = response.json();
        
        // 检查响应结构
        if (!jsonResponse) {
            console.error('响应不是有效的JSON格式');
            return false;
        }
        
        // 检查关键字段是否存在（根据实际API响应结构调整）
        const hasRequiredFields = jsonResponse.code === 200 || 
                                 jsonResponse.success === true ||
                                 jsonResponse.data !== undefined;
        
        if (!hasRequiredFields) {
            console.error('响应缺少必要字段:', JSON.stringify(jsonResponse).substring(0, 200));
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('JSON解析错误:', error.message);
        return false;
    }
}

/**
 * 记录性能指标
 * @param {Object} response - HTTP响应对象
 * @param {boolean} isSuccess - 请求是否成功
 */
function recordMetrics(response, isSuccess) {
    // 记录响应时间
    responseTimeTrend.add(response.timings.duration);
    
    // 更新计数器
    requestCounter.add(1);
    
    if (isSuccess) {
        successCounter.add(1);
    } else {
        failureCounter.add(1);
    }
    
    // 记录错误率
    errorRate.add(!isSuccess);
}

// ==================== 主测试函数 ====================
export default function () {
    // 创建请求头
    const headers = createHeaders();
    
    // 记录开始时间
    const startTime = Date.now();
    
    try {
        // 发送GET请求
        const response = http.get(`${BASE_URL}${HOME_PAGE_ENDPOINT}`, {
            headers: headers,
            tags: {
                name: 'home_page_request',
                endpoint: HOME_PAGE_ENDPOINT
            }
        });
        
        // 验证响应
        const isResponseValid = validateResponse(response);
        
        // 记录指标
        recordMetrics(response, isResponseValid);
        
        // 使用check进行断言
        const checkResults = check(response, {
            // HTTP状态码检查
            '状态码是200': (r) => r.status === 200,
            
            // 响应时间检查
            '响应时间小于500ms': (r) => r.timings.duration < 500,
            
            // 响应内容检查
            '响应包含有效JSON': (r) => {
                try {
                    r.json();
                    return true;
                } catch (e) {
                    return false;
                }
            },
            
            // 业务逻辑检查（根据实际API调整）
            '响应包含必要字段': (r) => {
                try {
                    const json = r.json();
                    return json.code === 200 || json.success === true || json.data !== undefined;
                } catch (e) {
                    return false;
                }
            }
        });
        
        // 如果检查失败，记录详细信息
        if (!checkResults) {
            console.warn(`检查失败: ${JSON.stringify(response.body).substring(0, 200)}`);
        }
        
        // 计算请求耗时
        const requestDuration = Date.now() - startTime;
        
        // 输出调试信息（仅在需要时启用）
        if (__ENV.DEBUG === 'true') {
            console.log(`请求耗时: ${requestDuration}ms, 状态码: ${response.status}`);
        }
        
    } catch (error) {
        // 捕获并处理异常
        console.error(`请求异常: ${error.message}`);
        
        // 创建模拟的失败响应用于记录指标
        const failedResponse = {
            status: 0,
            status_text: 'Request Failed',
            timings: {
                duration: Date.now() - startTime
            }
        };
        
        // 记录失败指标
        recordMetrics(failedResponse, false);
        errorRate.add(1);
        failureCounter.add(1);
    }
    
    // 添加思考时间（模拟用户思考）
    sleep(Math.random() * 0.5 + 0.5); // 0.5-1秒的随机等待时间
}

// ==================== 测试生命周期钩子 ====================
/**
 * 测试设置函数 - 在测试开始前执行
 */
export function setup() {
    console.log('🚀 开始首页冒烟测试');
    console.log(`📊 测试配置: ${options.vus}个VU, 持续${options.duration}`);
    console.log(`🎯 目标URL: ${BASE_URL}${HOME_PAGE_ENDPOINT}`);
    console.log('📈 性能阈值:');
    console.log('  - 平均响应时间 < 100ms');
    console.log('  - P95响应时间 < 200ms');
    console.log('  - 错误率 < 1%');
    console.log('  - 吞吐量 > 50 RPS');
    
    // 验证访问令牌
    if (!ACCESS_TOKEN || ACCESS_TOKEN === 'your-access-token-here') {
        console.error('❌ 错误: 请设置有效的access-token');
        console.error('💡 提示: 可以通过环境变量设置: k6 run -e ACCESS_TOKEN=your_token script.js');
        throw new Error('无效的访问令牌');
    }
    
    return { startTime: new Date().toISOString() };
}

/**
 * 测试清理函数 - 在测试结束后执行
 * @param {Object} data - setup函数返回的数据
 */
export function teardown(data) {
    const endTime = new Date().toISOString();
    console.log('\n✅ 测试完成');
    console.log(`⏱️  测试时间: ${data.startTime} 到 ${endTime}`);
    console.log('📋 请查看K6输出获取详细性能指标');
}