# K6首页冒烟测试脚本使用说明

## 脚本概述
这是一个用于首页冒烟测试的K6性能测试脚本，针对 `http://appserver.huice.com/cms/home/index` 接口进行测试。

## 脚本特性
1. ✅ 10个虚拟用户，持续30秒
2. ✅ 基于access-token的认证
3. ✅ 完整的请求头配置
4. ✅ 性能阈值监控
5. ✅ 错误处理和断言
6. ✅ 自定义指标收集
7. ✅ 测试生命周期管理

## 使用方法

### 1. 安装K6
```bash
# macOS
brew install k6

# Windows
choco install k6

# Linux
sudo apt-get update && sudo apt-get install k6
```

### 2. 设置访问令牌
脚本需要有效的access-token才能运行。有以下几种设置方式：

#### 方式一：修改脚本中的常量
```javascript
// 在脚本中修改
const ACCESS_TOKEN = 'your-actual-access-token';
```

#### 方式二：通过环境变量传递（推荐）
```bash
# 运行测试时传递环境变量
k6 run -e ACCESS_TOKEN=your_token_here /k6_scripts/home_page_smoke_test.js
```

#### 方式三：使用.env文件
```bash
# 创建.env文件
echo "ACCESS_TOKEN=your_token_here" > .env

# 运行测试
k6 run --env-file=.env /k6_scripts/home_page_smoke_test.js
```

### 3. 运行测试
```bash
# 基本运行
k6 run /k6_scripts/home_page_smoke_test.js

# 启用调试模式
k6 run -e DEBUG=true /k6_scripts/home_page_smoke_test.js

# 输出详细结果
k6 run --summary-export=results.json /k6_scripts/home_page_smoke_test.js

# 并行运行多个实例
k6 run --vus 10 --duration 30s /k6_scripts/home_page_smoke_test.js
```

### 4. 查看结果
脚本运行后会显示以下信息：
- ✅ 测试配置信息
- 📊 性能指标汇总
- ⚠️  阈值检查结果
- 📈 自定义指标统计

## 性能阈值配置
脚本配置了以下性能阈值：
- 平均响应时间：< 100ms
- P95响应时间：< 200ms
- 错误率：< 1%
- 请求失败率：< 1%

## 自定义指标
脚本收集以下自定义指标：
- `errors`: 错误率
- `response_time`: 响应时间趋势
- `total_requests`: 总请求数
- `successful_requests`: 成功请求数
- `failed_requests`: 失败请求数

## 断言检查
脚本包含以下断言：
1. HTTP状态码为200
2. 响应时间小于500ms
3. 响应包含有效的JSON格式
4. 响应包含必要的业务字段

## 调试模式
启用调试模式可以查看详细的请求信息：
```bash
k6 run -e DEBUG=true /k6_scripts/home_page_smoke_test.js
```

## 常见问题

### Q1: 如何修改测试目标URL？
修改脚本中的 `BASE_URL` 和 `HOME_PAGE_ENDPOINT` 常量。

### Q2: 如何调整虚拟用户数量？
修改 `options.vus` 值或使用命令行参数：
```bash
k6 run --vus 20 --duration 60s /k6_scripts/home_page_smoke_test.js
```

### Q3: 如何修改性能阈值？
在 `options.thresholds` 部分调整相应的阈值配置。

### Q4: 如何添加更多的断言？
在 `check()` 函数中添加新的检查条件。

### Q5: 如何处理不同的认证方式？
修改 `createHeaders()` 函数中的请求头配置。

## 最佳实践建议

### 1. 测试环境准备
- 确保测试环境稳定
- 准备有效的access-token
- 确认API接口可用

### 2. 测试执行
- 先从低负载开始测试
- 逐步增加虚拟用户数量
- 监控系统资源使用情况

### 3. 结果分析
- 关注阈值是否达标
- 分析错误原因
- 记录性能基线数据

### 4. 持续集成
可以将此脚本集成到CI/CD流程中：
```yaml
# GitHub Actions示例
- name: Run Smoke Test
  run: k6 run /k6_scripts/home_page_smoke_test.js
```

## 脚本结构说明
```
home_page_smoke_test.js
├── 自定义指标定义
├── 测试配置(options)
├── 测试数据常量
├── 辅助函数
│   ├── createHeaders()
│   ├── validateResponse()
│   └── recordMetrics()
├── 主测试函数(default)
└── 生命周期钩子
    ├── setup()
    └── teardown()
```

## 支持与反馈
如果在使用过程中遇到问题，请检查：
1. access-token是否正确
2. 网络连接是否正常
3. 目标服务是否可用
4. K6版本是否兼容

如需进一步定制，可以根据实际需求修改脚本中的相关配置。