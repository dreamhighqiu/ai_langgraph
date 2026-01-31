# 🎯 Automation MCP Server

**智能 API 测试变得简单** - 一个全面的模型上下文协议 (MCP) 服务器，为从 QA 工程师到开发人员的每个人提供专业级 API 测试功能。

> 使用 AI 驱动的Agent自动规划、生成和修复您的测试，转变您的 API 测试工作流程。

---

## 📦 快速使用


**对于 Claude Desktop 或其他 MCP 客户端：**

添加到您的 Claude Desktop 配置（macOS 上为 `~/Library/Application Support/Claude/claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "automation-quality": {
      "command": "npx",
      "args": ["当前项目地址/automation-quality-mcp"],
      "env": {
        "NODE_ENV": "production",
        "OUTPUT_DIR": "./api-test-reports"
      }
    }
  }
}
```

---

## 🛠️ 可用工具

我们的 MCP 服务器提供 **7 个强大的工具**用于全面的 API 测试：

### 🤖 AI 驱动的测试工具

| 工具 | 目的                                                       | 何时使用 |
|------|----------------------------------------------------------|-------------|
| **`api_planner`** | 分析 API Schema（OpenAPI/Swagger、GraphQL）并创建包含逼真示例数据的全面测试计划 | 启动新的 API 测试项目、记录 API 行为、验证 API 端点 |
| **`api_generator`** | 使用 AI 驱动的代码生成从测试计划生成可执行测试（Jest、Playwright、Postman）       | 将测试计划转换为 TypeScript 或 JavaScript 中的可运行代码 |
| **`api_healer`** | 通过分析错误和应用修复策略来调试和自动修复失败的测试                               | 测试在 API 更改、模式更新或身份验证问题后中断 |
| **`api_project_setup`** | 检测项目配置（框架和语言）以进行智能测试生成                                   | 在使用 `api_generator` 之前 - 自动检测 Playwright/Jest 和 TypeScript/JavaScript |

### 🔧 核心 API 测试工具

| 工具 | 目的 | 何时使用 |
|------|---------|-------------|
| **`api_request`** | 执行带有验证和请求链接的 HTTP 请求 | 进行单个 API 调用、测试特定端点、链接多个请求 |
| **`api_session_status`** | 查询测试会话状态和日志 | 检查测试序列的进度、查看请求历史 |
| **`api_session_report`** | 生成全面的 HTML 测试报告 | 创建可共享的测试文档，包含详细分析 |

**关键功能：**
- ✅ **智能验证**：自动"预期与实际"比较，包含详细的失败消息
- 🔗 **请求链接**：从一个响应中提取数据并在后续请求中使用
- 📊 **会话跟踪**：监控跨多个请求的多步 API 工作流
- 📈 **可视化报告**：包含时间分析和验证结果的交互式 HTML 报告
- 🎯 **所有 HTTP 方法**：GET、POST、PUT、DELETE、PATCH、OPTIONS、HEAD
- 🔒 **身份验证**：支持 Bearer 令牌、API 密钥、自定义标头
- 🎨 **逼真的示例数据**：自动生成上下文感知的测试数据（名称、电子邮件、日期等）
- 🔍 **可选验证**：通过进行实际 API 调用来验证端点，包含响应时间指标


## 🌐 聊天模式（AI Agent）

您会获得 3 个智能测试助手：

### 1. 🌐 @api-planner - 策略规划师

**提示词：**
[🌐 api-planner.chatmode.md](src/chatmodes/%F0%9F%8C%90%20api-planner.chatmode.md)

**它的作用：** 分析您的 API 并创建全面的测试策略

**最适合：**
- 启动新的测试项目
- 记录 API 行为
- 为复杂工作流创建测试场景
- 安全性和边界情况规划

**示例：分析真实 API**
```
1. 基于当前的提示词构建一个智能体，然后输入以下用户指令：

2. 分析此 API 并创建全面的测试计划：
https://fakerestapi.azurewebsites.net/swagger/v1/swagger.json

3. Agent参考输出：我将调用 API 规划器一次来分析提供的 URL 处的 OpenAPI 模式，并生成包含逼真示例数据的全面测试计划，加上 5 个端点的实时验证；预期结果：保存的测试计划在 ./api-test-reports/fakerest-test-plan.md 和验证摘要。我现在将运行规划器。

```

**您会获得：**
- 包含 40+ 个测试场景的全面 markdown 测试计划
- 每个端点的逼真示例请求
- 预期的响应结构
- 错误场景和边界情况
- 准备好进行测试生成

### 2. 🌐 @api-generator - 构建者

**它的作用：** 将测试计划转换为可执行代码

**最适合：**
- 生成 Jest 测试套件
- 创建 Playwright 自动化脚本
- 构建 Postman 集合

**示例：从计划生成测试**
```
1. 一旦您生成了作为 API 规划器模式一部分的测试计划，现在将聊天模式更改为："🌐 api-generator"，打开在上一步中创建的测试计划 MD 文件（以便它可以在上下文中），并输入以下提示
为 Books API 部分创建 TypeScript Playwright 测试

2. Agent输出参考：我将检测项目的测试框架/语言（必需的第一步），以便我可以以正确的布局生成 Playwright TypeScript 测试；预期结果：检测结果，包含建议的框架/语言。然后要求您允许另一个工具"运行 api_project_setup automation-quality (MCP Server)"来捕获项目信息，例如，如果您有一个空项目，它将要求您选择框架/语言，否则如果您的项目是 playwright typescript，它将相应地创建 playwright 测试。

创建的文件：
✅ 包含 Books CRUD 操作
✅ 在屏幕上显示运行测试的说明

测试包括：
- ✅ GET /api/v1/Books - 列出所有书籍
- ✅ GET /api/v1/Books/{id} - 按 ID 获取书籍
- ✅ POST /api/v1/Books - 创建新书籍
- ✅ PUT /api/v1/Books/{id} - 更新书籍
- ✅ DELETE /api/v1/Books/{id} - 删除书籍
- ✅ 无效 ID 的错误处理
- ✅ 必填字段的验证

```

**示例：生成 Postman 集合**
```
您：@🌐 api-generator 从整个测试计划创建 Postman 集合

Agent：为 Fake REST API 创建 Postman 集合...

生成：
✅ postman/FakeRestAPI.postman_collection.json
✅ postman/environment.json（包含基础 URL 变量）

示例集合包括：
- 📁 Books（5 个请求）
- 📁 Users（4 个请求）
- 📁 Authors（4 个请求）
- 📁 Activities（3 个请求）
- 📁 CoverPhotos（4 个请求）

导入到 Postman 并开始测试！
```

### 3. 🌐 @api-healer - 修复者

**它的作用：** 自动诊断和修复失败的测试

**最适合：**
- 在 API 更改后修复损坏的测试
- 更新端点 URL
- 解决身份验证问题
- 模式不匹配更正

**示例：修复失败的测试**
```
您：@🌐 api-healer Books 测试因 404 错误而失败。
请分析并修复它们。

Agent：分析 tests/books.spec.ts 中的测试失败...

发现的问题：
❌ 端点已更改：/api/Books → /api/v1/Books
❌ 响应模式已更新：添加了"pageCount"字段
❌ ID 格式已更改：number → string

应用修复：
✅ 更新了所有端点 URL 以包含 /v1/ 前缀
✅ 更新了响应断言以包含 pageCount
✅ 修复了测试数据中的 ID 类型（42 → "42"）
✅ 将原始文件备份到 tests/books.spec.ts.backup

重新运行测试... ✅ 所有 15 个测试现在都通过了！
```

**示例：修复模式不匹配**
```
您：@🌐 api-healer 修复 tests/users.spec.ts 中的断言错误

Agent：分析断言失败...

发现 3 个模式不匹配：
❌ 预期 userName，API 返回 username（camelCase 问题）
❌ 从响应中删除了密码字段（安全更新）
❌ 添加了新字段：profileImageUrl

修复操作：
✅ 更新了断言：userName → username
✅ 删除了密码字段验证
✅ 将 profileImageUrl 添加到预期响应
✅ 更新了 TypeScript 接口

测试修复成功！✅ 12/12 通过
```

---

## 💡 使用示例 - E2E 测试场景

### 场景 1：测试 Fake REST API（完整工作流）

**真实示例使用：https://fakerestapi.azurewebsites.net**

**步骤 1：规划您的测试**
```
@🌐 api-planner 分析位于以下位置的 OpenAPI 规范
https://fakerestapi.azurewebsites.net/swagger/v1/swagger.json
并创建专注于 Books 和 Authors 端点的全面测试计划
```

**会发生什么：**
- ✅ Agent分析 Fake REST API 模式
- ✅ 识别 5 种资源类型（Books、Authors、Users、Activities、CoverPhotos）
- ✅ 创建 40+ 个测试场景，涵盖：
  - 快乐路径（获取所有书籍、按 ID 获取书籍、创建书籍）
  - 错误情况（无效 ID 的 404、错误数据的 400）
  - 边界情况（空列表、ID 边界）
  - 数据验证（响应模式检查）
- ✅ 生成逼真的示例数据：
  ```json
  {
    "id": 1,
    "title": "The Great Gatsby",
    "description": "A classic American novel",
    "pageCount": 180,
    "excerpt": "In my younger and more vulnerable years...",
    "publishDate": "1925-04-10T00:00:00Z"
  }
  ```

**步骤 2：生成可执行测试**
```
@🌐 api-generator 从测试计划创建 TypeScript Playwright 测试，
专注于 Books API 部分
```

**您会获得：**
- `tests/books.spec.ts` - 完整的 Books CRUD 测试套件
  ```typescript
  import { test, expect } from '@playwright/test';

  test.describe('Books API', () => {
    test('GET /api/v1/Books - 应该返回所有书籍', async ({ request }) => {
      const response = await request.get('https://fakerestapi.azurewebsites.net/api/v1/Books');
      expect(response.ok()).toBeTruthy();
      expect(response.status()).toBe(200);
      const books = await response.json();
      expect(Array.isArray(books)).toBeTruthy();
    });

    test('POST /api/v1/Books - 应该创建新书籍', async ({ request }) => {
      const newBook = {
        id: 201,
        title: "Test Book",
        pageCount: 350
      };
      const response = await request.post('https://fakerestapi.azurewebsites.net/api/v1/Books', {
        data: newBook
      });
      expect(response.status()).toBe(200);
    });
  });
  ```

**步骤 3：运行和修复测试**
```
# 运行测试
npx playwright test tests/books.spec.ts

# 如果任何测试因 API 更改而失败：
@🌐 api-healer 修复 tests/books.spec.ts 中的失败测试
```

**修复者修复的内容：**
- ✅ 端点 URL 更新（如果 API 版本更改）
- ✅ 响应模式更正（新增/删除的字段）
- ✅ 数据类型调整（字符串与数字 ID）
- ✅ 状态代码更新

### 场景 2：使用 Postman 快速 API 文档

**目标：** 为 Fake REST API 生成现成的 Postman 集合

```
步骤 1：
@🌐 api-planner 从以下位置创建测试计划
https://fakerestapi.azurewebsites.net/swagger/v1/swagger.json
启用验证以测试实际端点

步骤 2：
@🌐 api-generator 从测试计划创建 Postman 集合
包含所有端点和示例请求

步骤 3：
将生成的集合导入到 Postman 并开始测试！
```

**您会获得：**
- 📦 `postman/FakeRestAPI.postman_collection.json` - 完整集合
- 🌍 `postman/environment.json` - 环境变量
- ✅ 20+ 个跨所有资源类型的预配置请求
- 📝 包含逼真数据的示例请求体
- ✔️ 包含响应验证测试

**结果：** 专业的 Postman 集合，准备好与您的团队共享

---

## 🔧 调用单个工具

### 何时使用单个工具

**在以下情况下使用Agent（@api-planner、@api-generator、@api-healer）：**
- 您想要 AI 协助和建议
- 您正在处理复杂的多步工作流
- 您需要解释和最佳实践

**在以下情况下使用单个工具：**
- 您需要对参数进行精确控制
- 您在 CI/CD 中自动化测试
- 您与其他工具集成
- 您想编写重复任务的脚本

### 工具 1：`api_planner`

**目的：** 分析 API 模式并生成包含逼真示例数据的全面测试计划

**基本用法：**
```javascript
// 在 Claude Desktop 或 MCP 客户端中
{
  "tool": "api_planner",
  "parameters": {
    "schemaUrl": "https://api.example.com/swagger.json",
    "schemaType": "openapi",
    "outputPath": "./test-plan.md"
  }
}
```

**带端点验证：**
```javascript
{
  "tool": "api_planner",
  "parameters": {
    "schemaUrl": "https://petstore3.swagger.io/api/v3/openapi.json",
    "schemaType": "openapi",
    "outputPath": "./api-test-plan.md",
    "includeAuth": true,
    "includeSecurity": true,
    "includeErrorHandling": true,
    "testCategories": ["functional", "security", "edge-cases"],
    "validateEndpoints": true,
    "validationSampleSize": 3,
    "validationTimeout": 5000
  }
}
```

**参数说明：**
- `schemaUrl` - 获取 API 模式的 URL（OpenAPI/Swagger、GraphQL 内省端点）
- `schemaContent` - 直接模式内容作为 JSON/YAML 字符串（schemaUrl 的替代方案）
- `schemaType` - 模式类型：`openapi`、`swagger`、`graphql`、`auto`（默认：auto）
- `apiBaseUrl` - API 的基础 URL（如果提供，覆盖模式 baseUrl）
- `includeAuth` - 包含身份验证测试场景（默认：true）
- `includeSecurity` - 包含安全测试场景（默认：true）
- `includeErrorHandling` - 包含错误处理场景（默认：true）
- `outputPath` - 保存测试计划的文件路径（默认：./api-test-plan.md）
- `testCategories` - 测试类型：`functional`、`security`、`performance`、`integration`、`edge-cases`
- `validateEndpoints` - 进行实际 API 调用以验证端点（默认：false）
- `validationSampleSize` - 要验证的端点数，使用 -1 表示全部（默认：3）
- `validationTimeout` - 每个验证请求的超时时间（毫秒）（默认：5000）

### 工具 2：`api_generator`

**目的：** 使用 AI 从测试计划生成可执行测试（Playwright、Jest、Postman）

**生成 Playwright 测试：**
```javascript
{
  "tool": "api_generator",
  "parameters": {
    "testPlanPath": "./test-plan.md",
    "outputFormat": "playwright",
    "outputDir": "./tests",
    "includeSetup": true,
    "language": "typescript"
  }
}
```

**生成 Jest 测试：**
```javascript
{
  "tool": "api_generator",
  "parameters": {
    "testPlanPath": "./test-plan.md",
    "outputFormat": "jest",
    "outputDir": "./tests",
    "testFramework": "jest",
    "baseUrl": "https://api.example.com"
  }
}
```

**生成 Postman 集合：**
```javascript
{
  "tool": "api_generator",
  "parameters": {
    "testPlanPath": "./test-plan.md",
    "outputFormat": "postman",
    "outputDir": "./postman",
    "includeAuth": true
  }
}
```

**生成所有格式：**
```javascript
{
  "tool": "api_generator",
  "parameters": {
    "testPlanPath": "./test-plan.md",
    "outputFormat": "all",
    "outputDir": "./tests",
    "language": "typescript"
  }
}
```

**参数说明：**
- `testPlanPath` - 测试计划 markdown 文件的路径
- `testPlanContent` - 直接测试计划内容作为 markdown（testPlanPath 的替代方案）
- `outputFormat` - 格式：`playwright`、`postman`、`jest`、`all`（默认：all）
- `outputDir` - 保存生成的测试的目录（默认：./tests）
- `sessionId` - 用于跟踪生成的测试的会话 ID
- `includeAuth` - 包含身份验证设置（默认：true）
- `includeSetup` - 包含测试设置/拆卸代码（默认：true）
- `testFramework` - 框架：`jest`、`mocha`、`playwright-test`
- `baseUrl` - API 的基础 URL（可选）
- `language` - 语言：`javascript`、`typescript`（默认：typescript）

### 工具 3：`api_healer`

**目的：** 调试和自动修复失败的 API 测试

**修复特定测试文件：**
```javascript
{
  "tool": "api_healer",
  "parameters": {
    "testPath": "./tests/auth.test.js",
    "testType": "auto",
    "autoFix": true,
    "backupOriginal": true
  }
}
```

**修复多个测试文件：**
```javascript
{
  "tool": "api_healer",
  "parameters": {
    "testFiles": ["./tests/auth.test.js", "./tests/users.test.js"],
    "testType": "playwright",
    "healingStrategies": ["schema-update", "endpoint-fix", "auth-repair"]
  }
}
```

**仅分析（不修复）：**
```javascript
{
  "tool": "api_healer",
  "parameters": {
    "testPath": "./tests/api.test.js",
    "analysisOnly": true
  }
}
```

**参数说明：**
- `testPath` - 要修复的特定测试文件的路径
- `testFiles` - 测试文件路径数组（testPath 的替代方案）
- `testType` - 类型：`jest`、`playwright`、`postman`、`auto`（默认：auto）
- `sessionId` - 用于跟踪修复过程的会话 ID
- `maxHealingAttempts` - 每个测试的最大尝试次数（默认：3）
- `autoFix` - 自动应用修复（默认：true）
- `backupOriginal` - 创建备份文件（默认：true）
- `analysisOnly` - 仅分析而不修复（默认：false）
- `healingStrategies` - 特定策略：`schema-update`、`endpoint-fix`、`auth-repair`、`data-correction`、`assertion-update`

### 工具 4：`api_project_setup`

**目的：** 检测项目配置以进行测试生成

**检测项目配置：**
```javascript
{
  "tool": "api_project_setup",
  "parameters": {
    "outputDir": "./tests"
  }
}
```

**它的作用：**
- 扫描 `playwright.config.ts/js`、`jest.config.ts/js`、`tsconfig.json`
- 自动检测框架（Playwright/Jest）和语言（TypeScript/JavaScript）
- 返回配置或在不明确时提示用户
- **必须在 `api_generator` 之前调用**以获得最佳测试生成

**响应（自动检测时）：**
```json
{
  "success": true,
  "autoDetected": true,
  "config": {
    "framework": "playwright",
    "language": "typescript",
    "hasTypeScript": true,
    "hasPlaywrightConfig": true,
    "configFiles": ["playwright.config.ts", "tsconfig.json"]
  },
  "nextStep": "使用 outputFormat: 'playwright' 和 language: 'typescript' 调用 api_generator"
}
```

**响应（需要用户输入时）：**
```json
{
  "success": true,
  "needsUserInput": true,
  "prompts": [
    {
      "name": "framework",
      "question": "您想使用哪个测试框架？",
      "choices": ["playwright", "jest", "postman", "all"]
    },
    {
      "name": "language",
      "question": "您想使用哪种语言？",
      "choices": ["typescript", "javascript"]
    }
  ]
}
```

**参数：**
- `outputDir` - 测试目录（默认：`./tests`）。用于定位项目根目录
- `promptUser` - 即使检测到配置也强制用户提示（默认：false）

### 工具 5：`api_request`

**目的：** 执行带有验证的单个 HTTP 请求

**简单 GET 请求：**
```javascript
{
  "tool": "api_request",
  "parameters": {
    "method": "GET",
    "url": "https://api.example.com/users/1",
    "expect": {
      "status": 200,
      "contentType": "application/json"
    }
  }
}
```

**带身份验证的 POST：**
```javascript
{
  "tool": "api_request",
  "parameters": {
    "method": "POST",
    "url": "https://api.example.com/users",
    "headers": {
      "Authorization": "Bearer your-token-here",
      "Content-Type": "application/json"
    },
    "data": {
      "name": "John Doe",
      "email": "john@example.com"
    },
    "expect": {
      "status": 201,
      "body": {
        "name": "John Doe",
        "email": "john@example.com"
      }
    }
  }
}
```

**请求链接（在下一个请求中使用响应）：**
```javascript
{
  "tool": "api_request",
  "parameters": {
    "sessionId": "user-workflow",
    "chain": [
      {
        "name": "create_user",
        "method": "POST",
        "url": "https://api.example.com/users",
        "data": { "name": "Jane Doe" },
        "extract": { "userId": "id" }
      },
      {
        "name": "get_user",
        "method": "GET",
        "url": "https://api.example.com/users/{{ create_user.userId }}",
        "expect": { "status": 200 }
      }
    ]
  }
}
```

**参数说明：**
- `method` - HTTP 方法（GET、POST、PUT、DELETE、PATCH 等）
- `url` - 目标端点
- `headers` - 自定义标头（身份验证、内容类型）
- `data` - POST/PUT/PATCH 的请求体
- `expect` - 验证规则（状态、标头、体）
- `sessionId` - 分组相关请求
- `chain` - 按顺序执行多个请求

### 工具 6：`api_session_status`

**目的：** 检查 API 测试会话的状态

**检查会话进度：**
```javascript
{
  "tool": "api_session_status",
  "parameters": {
    "sessionId": "user-workflow"
  }
}
```

**响应示例：**
```json
{
  "sessionId": "user-workflow",
  "totalRequests": 5,
  "successfulRequests": 4,
  "failedRequests": 1,
  "status": "completed",
  "startTime": "2025-10-23T10:00:00Z",
  "endTime": "2025-10-23T10:05:00Z",
  "duration": "5 minutes"
}
```

### 工具 7：`api_session_report`

**目的：** 生成全面的 HTML 测试报告

**生成报告：**
```javascript
{
  "tool": "api_session_report",
  "parameters": {
    "sessionId": "user-workflow",
    "outputPath": "./reports/user-workflow-report.html",
    "includeCharts": true
  }
}
```

**您会获得：**
- 📊 可视化图表（成功率、响应时间）
- 📋 请求/响应详情
- ✅ 验证结果（通过/失败，包含差异）
- 🕐 时间信息
- 📸 屏幕截图（如适用）

---
---

## ⚙️ 配置

### 环境变量

```bash
NODE_ENV=production              # 在生产模式下运行（默认）
OUTPUT_DIR=./api-test-reports    # 保存报告的位置（默认）
MCP_FEATURES_ENABLEDEBUGMODE=true # 启用详细日志记录
```

### 命令行选项

```bash
npx 当前项目目录/mcp-server [options]

选项：
  --help, -h        显示帮助信息
  --version, -v     显示版本号
  --agents          为 GitHub Copilot 安装 AI 测试Agent
  --debug           启用调试模式，包含详细日志
  --verbose         显示详细的安装输出
  --port <number>   指定服务器端口（如果需要）
```

### VS Code MCP 配置

运行 `--agents` 后，此文件在 `.vscode/mcp.json` 处创建：

```json
{
  "servers": {
    "automation-quality": {
      "type": "stdio",
      "command": "npx",
      "args": ["当前项目目录/mcp-server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "NODE_ENV": "production",
        "OUTPUT_DIR": "./api-test-reports"
      }
    }
  }
}
```

### 输出目录位置

- **VS Code/本地项目**：项目中的 `./api-test-reports`
- **Claude Desktop**：主目录中的 `~/.mcp-browser-control`
- **自定义位置**：设置 `OUTPUT_DIR` 环境变量

---

---

## � 故障排除

### 常见运行时问题

<details>
<summary><strong>API 测试报告未出现在预期位置</strong></summary>

**解决方案：**
- 检查配置的 `OUTPUT_DIR` 环境变量
- 对于 Claude Desktop：查看 `~/.mcp-browser-control/`
- 对于 VS Code：查看项目中的 `./api-test-reports/`
- 设置自定义位置：`OUTPUT_DIR=/your/custom/path`

</details>

## � 其他资源

### 文档

- 📖 [入门指南](docs/getting-started.md) - 完整的设置演练
- 🔧 [工具参考](docs/api/tool-reference.md) - 详细的工具文档
- 🎯 [API 工具使用指南](docs/api_tools_usage.md) - 高级示例和模式
- 🔷 [GraphQL 支持指南](GRAPHQL-SUPPORT.md) - GraphQL 测试功能和特性
- �‍💻 [开发者指南](docs/development/adding-tools.md) - 扩展服务器
- ⚙️ [配置指南](docs/development/configuration.md) - 高级设置
- � [示例](docs/examples/) - 真实世界的使用示例


## 🏗️ 架构

### 项目结构

```
automation-mcp-server/
├── src/
│   ├── tools/
│   │   ├── api/              # API 测试工具
│   │   │   ├── api-planner.js
│   │   │   ├── api-generator.js
│   │   │   ├── api-healer.js
│   │   │   ├── api-project-setup.js
│   │   │   ├── api-request.js
│   │   │   ├── api-session-status.js
│   │   │   └── api-session-report.js
│   │   └── base/             # 工具框架
│   ├── chatmodes/            # AI Agent定义
│   │   ├── 🌐 api-planner.chatmode.md
│   │   ├── 🌐 api-generator.chatmode.md
│   │   └── 🌐 api-healer.chatmode.md
│   ├── config/               # 配置管理
│   └── utils/                # 实用函数
├── docs/                     # 文档
├── mcpServer.js             # 主 MCP 服务器
└── cli.js                   # 命令行界面
```

### 关键功能

- **🔍 自动工具发现**：工具自动加载和注册
- **⚙️ 配置系统**：基于环境的配置，具有合理的默认值
- **🛡️ 错误处理**：全面的验证和详细的错误报告
- **📊 会话管理**：跟踪和管理多步 API 测试工作流

---

## 🔒 安全考虑

### 安全态势

- **✅ 仅 API 模式**：默认启用以进行安全部署
- **✅ 标准 HTTP 库**：所有请求都使用受信任的 Node.js 库
- **✅ 无文件系统访问**：API 工具仅写入配置的输出目录
- **✅ 无浏览器自动化**：仅 API 模式中没有浏览器进程

### 生产部署最佳实践

```json
{
  "mcpServers": {
    "automation-quality": {
      "command": "npx",
      "args": ["当前项目路径/mcp-server"],
      "env": {
        "NODE_ENV": "production",
        "OUTPUT_DIR": "~/api-test-reports"
      }
    }
  }
}
```

### 安全建议

1. **📁 安全输出目录**：在报告目录上设置适当的权限
2. **🔄 定期更新**：保持包更新以获取安全补丁
3. **🌍 环境分离**：对开发和生产使用不同的配置
4. **📊 监控**：在初始部署期间启用调试模式以监控使用情况
5. **� API 密钥**：永远不要将 API 密钥或令牌提交到版本控制
6. **🌐 网络安全**：对生产 API 测试使用 HTTPS 端点

---

## 👨‍💻 自定义开发

### 添加新工具

1. 在 `src/tools/api/` 中创建工具文件
2. 扩展 `ToolBase` 类
3. 定义工具架构和实现
4. 工具自动发现！

**示例工具结构：**
```javascript
const ToolBase = require('../base/ToolBase');

class MyApiTool extends ToolBase {
  static definition = {
    name: "my_api_tool",
    description: "执行自定义 API 测试操作",
    input_schema: {
      type: "object",
      properties: {
        endpoint: { type: "string", description: "API 端点 URL" }
      },
      required: ["endpoint"]
    }
  };

  async execute(parameters) {
    // 实现
    return {
      success: true,
      data: { /* 结果 */ }
    };
  }
}

module.exports = MyApiTool;
```

### 运行测试

```bash
# 运行测试套件
npm test

# 运行 MCP 检查器进行开发
npm run inspector

# 在调试模式下启动服务器
npm run dev
```
