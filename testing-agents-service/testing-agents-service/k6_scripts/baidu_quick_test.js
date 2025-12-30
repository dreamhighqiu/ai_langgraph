// 简化测试脚本，验证基本功能
import http from 'k6/http';
import { check, sleep } from 'k6';

// 简单配置，用于快速验证
export const options = {
    vus: 1,
    duration: '5s',
    thresholds: {
        'http_req_duration': ['p(95)<5000'],
        'http_req_failed': ['rate<0.1'],
    },
};

export default function () {
    const url = 'https://www.baidu.com/';
    
    const headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    };
    
    const response = http.get(url, { headers: headers });
    
    check(response, {
        '状态码是200': (r) => r.status === 200,
        '响应时间合理': (r) => r.timings.duration < 5000,
        '页面包含百度': (r) => {
            if (!r.body) return false;
            return r.body.toString().includes('百度') || r.body.toString().includes('baidu');
        },
    });
    
    sleep(1);
}