

# API Healer 工具代码修复原理分析

## 一、工具概述

`api-healer.js` 是一个 **自动化API测试修复工具**，它通过分析失败的测试用例，自动识别错误类型并应用相应的修复策略。

---

## 二、核心工作流程

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  输入测试文件    │───▶│  运行测试       │───▶│  解析错误       │───▶│  生成修复       │
│  (testPath)     │    │  (_runTests)    │    │  (_parseErrors) │    │  (_generateFixes)│
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                                              │
                                                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  返回结果       │◀───│  验证修复       │◀───│  重新运行测试   │◀───│  应用修复       │
│                 │    │  (循环检查)     │    │  (_runTests)    │    │  (_applyFix)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 三、五大修复策略

工具支持 **5种修复策略**（`healingStrategies`）：

| 策略名称 | 说明 | 触发条件 |
|---------|------|----------|
| `schema-update` | 更新API响应结构断言 | API返回数据结构变化 |
| `endpoint-fix` | 修复API端点URL | HTTP 404 错误 |
| `auth-repair` | 修复认证问题 | HTTP 401/403 错误 |
| `data-correction` | 修正请求数据 | HTTP 4xx 客户端错误 |
| `assertion-update` | 更新测试断言 | 断言失败 |

---

## 四、错误识别机制

### 4.1 支持的测试框架

工具会**自动检测**测试类型：

```javascript
// 代码位置: _detectTestType() 方法
if (content.includes('@playwright/test')) return 'playwright';
if (content.includes('describe(') && content.includes('jest')) return 'jest';
if (testFile.endsWith('.postman_collection.json')) return 'postman';
```

### 4.2 错误类型识别

工具能识别 **6种错误类型**：

| 错误类型 | 识别特征 | 示例 |
|---------|----------|------|
| `http-error` | `status code XXX` | `Request failed with status code 404` |
| `assertion-error` | `expect().toBe` | `expect(200).toBe(201)` |
| `network-error` | `ECONNREFUSED` | 服务器连接被拒绝 |
| `auth-error` | `401`, `403`, `Unauthorized` | 认证失败 |
| `timeout-error` | `timeout`, `ETIMEDOUT` | 请求超时 |
| `api-error` | `apiRequestContext` | Playwright API错误 |

---

## 五、修复生成逻辑

### 5.1 端点修复 (`endpoint-fix`)

**触发条件**：HTTP 404 错误

```javascript
async _generateEndpointFix(error, testContent) {
    // 查找测试中的URL模式
    const urlMatches = testContent.match(/['"`]([^'"`]*\/[^'"`]*)['"`]/g);
    
    return {
        type: 'endpoint-fix',
        description: 'Update endpoint URL to match current API',
        pattern: urlMatches[0],          // 原始URL
        replacement: urlMatches[0],      // 新URL（需要实现端点发现）
        confidence: 0.5
    };
}
```

**例子**：
```javascript
// 原始测试代码
await request.get('/api/v1/users');  // 返回 404

// 修复后
await request.get('/api/v2/users');  // 新版本API
```

### 5.2 认证修复 (`auth-repair`)

**触发条件**：HTTP 401/403 或包含 "Unauthorized"

```javascript
async _generateAuthFix(error, testContent) {
    return {
        type: 'auth-repair',
        description: 'Update authentication method or refresh tokens',
        pattern: /Authorization['":\s]+['"`]([^'"`]*)['"`]/,
        replacement: 'Authorization: "Bearer {{updated_token}}"',
        confidence: 0.8
    };
}
```

**例子**：
```javascript
// 原始测试代码
headers: { Authorization: "Bearer expired_token_123" }  // 401 Unauthorized

// 修复后
headers: { Authorization: "Bearer {{updated_token}}" }
```

### 5.3 断言修复 (`assertion-update`)

**触发条件**：`expect().toBe()` 失败

```javascript
async _generateAssertionFix(error, testContent) {
    // 从错误信息中提取 expected vs actual
    const expectMatch = error.message.match(/expect\(([^)]+)\)\.toBe\(([^)]+)\)/);
    
    return {
        type: 'assertion-update',
        description: 'Update assertion to match actual API response',
        pattern: expectMatch[0],
        replacement: `expect(${expectMatch[1]}).toBe(/* actual value */)`,
        confidence: 0.9
    };
}
```

**例子**：
```javascript
// 原始断言
expect(response.status).toBe(200);  // 实际返回 201

// 修复后
expect(response.status).toBe(201);
```

### 5.4 超时修复 (`timeout-fix`)

**触发条件**：包含 "timeout" 或 "ETIMEDOUT"

```javascript
_generateTimeoutFix(error, testContent) {
    return {
        type: 'timeout-fix',
        description: 'Increase timeout values',
        pattern: /timeout:\s*\d+/,
        replacement: 'timeout: 30000',  // 增加到30秒
        confidence: 0.7
    };
}
```

**例子**：
```javascript
// 原始代码
test('slow api', { timeout: 5000 }, async () => { ... });  // 超时

// 修复后  
test('slow api', { timeout: 30000 }, async () => { ... });
```

---

## 六、迭代修复机制

工具采用**循环修复**机制，最多尝试 `maxHealingAttempts` 次（默认3次）：

```javascript
for (let attempt = 1; attempt <= options.maxHealingAttempts && testErrors.length > 0; attempt++) {
    // 1. 生成修复方案
    const fixes = await this._generateFixes(testErrors, testFile, options);
    
    // 2. 应用修复
    for (const fix of fixes) {
        await this._applyFix(fix, testFile);
    }
    
    // 3. 重新运行测试
    testErrors = await this._runTests(testFile, options.testType);
    
    // 4. 如果没有错误了，停止修复
    if (testErrors.length === 0) {
        result.success = true;
        result.finalStatus = 'healed';
        break;
    }
}
```

---

## 七、完整使用示例

### 7.1 调用参数

```javascript
{
    "testPath": "./tests/api/user.test.js",     // 测试文件路径
    "testType": "jest",                          // 测试框架类型
    "maxHealingAttempts": 3,                     // 最大修复尝试次数
    "autoFix": true,                             // 自动应用修复
    "backupOriginal": true,                      // 备份原始文件
    "analysisOnly": false,                       // 仅分析不修复
    "healingStrategies": [                       // 启用的修复策略
        "endpoint-fix", 
        "assertion-update"
    ]
}
```

### 7.2 返回结果

```javascript
{
    "success": true,
    "message": "API healing completed for 1 files",
    "sessionId": "api-heal-1702900000000",
    "totalFiles": 1,
    "processedFiles": 1,
    "fixedFiles": 1,
    "failedFiles": 0,
    "results": [
        {
            "file": "./tests/api/user.test.js",
            "success": true,
            "healingAttempts": 2,
            "appliedFixes": [
                {
                    "type": "endpoint-fix",
                    "description": "Update endpoint URL to match current API",
                    "confidence": 0.5
                },
                {
                    "type": "assertion-update", 
                    "description": "Update assertion to match actual API response",
                    "confidence": 0.9
                }
            ],
            "finalStatus": "healed",
            "backupPath": "./tests/api/user.test.js.backup.1702900000000"
        }
    ]
}
```

---

## 八、工作流程图

```
                              ┌──────────────────────┐
                              │    输入测试文件       │
                              └──────────┬───────────┘
                                         │
                              ┌──────────▼───────────┐
                              │   创建备份文件        │
                              │   (backupOriginal)   │
                              └──────────┬───────────┘
                                         │
                              ┌──────────▼───────────┐
                              │   运行测试 (Jest/    │
                              │   Playwright)        │
                              └──────────┬───────────┘
                                         │
                          ┌──────────────┼──────────────┐
                          │              │              │
                    ┌─────▼─────┐ ┌──────▼──────┐ ┌─────▼─────┐
                    │  无错误    │ │ analysisOnly│ │  有错误    │
                    │  直接返回  │ │  仅分析返回  │ │  进入修复  │
                    └───────────┘ └─────────────┘ └─────┬─────┘
                                                        │
                              ┌─────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ 解析错误类型       │
                    │ http-error        │
                    │ assertion-error   │
                    │ auth-error        │
                    │ timeout-error     │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │ 生成修复方案       │
                    │ _generateFixes()  │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │ 应用修复          │
                    │ _applyFix()       │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
            ┌───────│ 重新运行测试      │◄───────┐
            │       └─────────┬─────────┘        │
            │                 │                  │
      ┌─────▼─────┐    ┌──────▼──────┐    ┌─────┴─────┐
      │  测试通过  │    │ 仍有错误    │    │ 达到最大   │
      │  healed   │    │ 继续修复    │───▶│ 尝试次数   │
      └───────────┘    └─────────────┘    └───────────┘
                                                │
                                         ┌──────▼──────┐
                                         │ partially-  │
                                         │ healed      │
                                         └─────────────┘
```

---

## 九、设计特点总结

| 特点 | 说明 |
|------|------|
| **自动检测** | 自动识别Jest/Playwright/Postman测试框架 |
| **模式匹配** | 使用正则表达式识别和修复代码 |
| **置信度评分** | 每个修复方案都有confidence分数 |
| **安全备份** | 修复前自动备份原文件 |
| **迭代修复** | 支持多轮修复直到测试通过 |
| **分析模式** | 支持仅分析不修复(`analysisOnly`) |
| **实时API验证** | 可调用`api-request`工具验证端点 |
