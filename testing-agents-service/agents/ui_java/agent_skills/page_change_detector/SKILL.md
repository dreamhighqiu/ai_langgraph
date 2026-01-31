# 页面变更检测器 (Page Change Detector) Skill

**使用 Playwright MCP 获取页面元素，与现有 PageObject 对比，检测定位器变化，生成全新的 Page 类。**

## 核心原理

```
┌─────────────────┐     ┌────────────────────────┐     ┌─────────────────┐
│   Playwright    │     │   Page Change          │     │   输出          │
│   MCP 工具      │ ──▶ │   Detector             │ ──▶ │                 │
│                 │     │                        │     │                 │
│ browser_snapshot│     │ 1. 获取页面所有元素    │     │ - 变更报告      │
│ browser_navigate│     │ 2. 解析旧 PageObject   │     │ - 新 PageObject │
│ 等              │     │ 3. 智能对比匹配        │     │                 │
└─────────────────┘     │ 4. 生成变更报告        │     └─────────────────┘
                        │ 5. 生成新 Page 类      │
                        └────────────────────────┘
```

## 使用 Playwright MCP 获取页面元素

### 步骤 1: 导航到目标页面

使用 `browser_navigate` 工具打开目标页面：

```
Tool: browser_navigate
Args: {"url": "https://chat.deepseek.com/dashboard"}
```

### 步骤 2: 获取页面快照

使用 `browser_snapshot` 工具获取页面所有可见元素：

```
Tool: browser_snapshot
```

返回的数据包含所有可交互元素：
```json
{
  "elements": [
    {
      "tag": "button",
      "text": "登录",
      "role": "button",
      "aria-label": "登录按钮",
      "data-testid": "login-btn",
      "selector": "[data-testid='login-btn']"
    },
    {
      "tag": "input",
      "placeholder": "请输入用户名",
      "role": "textbox",
      "type": "text",
      "selector": "input[placeholder='请输入用户名']"
    }
  ]
}
```

### 步骤 3: 解析旧 PageObject

读取现有的 Java PageObject 文件，提取所有定位器方法：

```java
// 旧的 DashboardPage.java
public class DashboardPage {
    public Locator loginButton() {
        return page.locator("#old-login-btn");  // 旧定位器
    }
    
    public Locator usernameInput() {
        return page.getByPlaceholder("用户名");  // 旧定位器
    }
}
```

### 步骤 4: 智能对比

将 Playwright MCP 获取的元素与旧 PageObject 的定位器对比：

| 方法名 | 旧定位器 | 新定位器（来自 MCP） | 状态 |
|--------|----------|---------------------|------|
| loginButton | #old-login-btn | [data-testid='login-btn'] | ⚠️ 变更 |
| usernameInput | placeholder='用户名' | placeholder='请输入用户名' | ⚠️ 变更 |
| - | - | [data-testid='logout-btn'] | ➕ 新增 |

### 步骤 5: 生成全新 PageObject

```java
/**
 * DashboardPage - 自动生成于 2026-01-31 14:30:25
 * URL: https://chat.deepseek.com/dashboard
 * 
 * 变更记录:
 * - loginButton: #old-login-btn → [data-testid='login-btn']
 * - usernameInput: placeholder 文本已更新
 * - 新增: logoutButton
 */
public class DashboardPage {
    private final Page page;
    
    public DashboardPage(Page page) {
        this.page = page;
    }
    
    /**
     * 登录按钮
     * @变更 选择器已更新
     */
    public Locator loginButton() {
        return page.locator("[data-testid='login-btn']");
    }
    
    /**
     * 用户名输入框
     * @变更 placeholder 文本已更新
     */
    public Locator usernameInput() {
        return page.getByPlaceholder("请输入用户名");
    }
    
    /**
     * 登出按钮
     * @新增 2026-01-31
     */
    public Locator logoutButton() {
        return page.locator("[data-testid='logout-btn']");
    }
}
```

---

## 完整工作流程

```
1. 用户提供: URL + 旧的 PageObject.java 文件
         ↓
2. 调用 browser_navigate 打开目标页面
         ↓
3. 调用 browser_snapshot 获取所有可见元素
         ↓
4. 解析旧 PageObject 文件，提取定位器
         ↓
5. 执行智能对比（按名称、文本、属性匹配）
         ↓
6. 生成变更对比报告 (HTML)
         ↓
7. 生成全新的 PageObject.java 文件
         ↓
8. 保存到工作区: {page_name}_{timestamp}/
```

---

## 工作区目录结构

每次检测会创建独立的工作区，便于管理：

```
workspace/
├── dashboard_20260131_143025/         # 基于 URL 和时间戳
│   ├── pageobjects/
│   │   ├── DashboardPage_Original.java    # 原始文件备份
│   │   └── DashboardPage.java             # 新生成的文件
│   ├── reports/
│   │   └── ChangeReport_20260131_143025.html
│   └── README.md
│
├── login_20260131_150012/
│   ├── pageobjects/
│   │   └── LoginPage.java
│   └── reports/
│       └── ChangeReport_20260131_150012.html
│
└── profile_20260131_161045/
    └── ...
```

---

## 输入要求

### 1. 目标页面 URL
```
https://chat.deepseek.com/dashboard
```

### 2. 旧的 PageObject 文件

可以通过以下方式提供：
- 文件路径: `workspace/DashboardPage.java`
- 直接粘贴代码内容

```java
public class DashboardPage {
    private final Page page;
    
    public DashboardPage(Page page) {
        this.page = page;
    }
    
    public Locator loginButton() {
        return page.locator("#login-btn");
    }
    
    public Locator usernameInput() {
        return page.getByLabel("用户名");
    }
}
```

---

## 输出内容

### 1. 变更对比报告 (HTML)

可视化展示：
- 变更元素数量统计
- 每个定位器的前后对比
- 变更原因分析
- 建议的修复操作

### 2. 全新的 PageObject 类

特点：
- 使用 Playwright MCP 获取的最新定位器
- 保留原有方法名（便于代码兼容）
- 添加变更注释和时间戳
- 新增元素自动生成方法
- 已删除元素标记为 @Deprecated

### 3. 变更摘要

```
📊 变更检测摘要
━━━━━━━━━━━━━━━━
URL: https://chat.deepseek.com/dashboard
检测时间: 2026-01-31 14:30:25

📈 统计
├── 总元素数: 25
├── 变更元素: 3
├── 新增元素: 2
└── 删除元素: 1

🔄 变更详情
1. loginButton: 选择器已更新
   旧: #login-btn
   新: [data-testid='login-btn']

2. usernameInput: placeholder 文本变化
   旧: getByLabel("用户名")
   新: getByPlaceholder("请输入用户名")

➕ 新增
- logoutButton
- settingsButton

❌ 已删除
- oldHelpLink
```

---

## Playwright MCP 工具使用指南

### 常用工具

| 工具名 | 用途 | 示例 |
|--------|------|------|
| `browser_navigate` | 导航到目标 URL | `{"url": "https://..."}` |
| `browser_snapshot` | 获取页面元素快照 | 无参数 |
| `browser_click` | 点击元素（如需登录） | `{"element": "Login button"}` |
| `browser_type` | 输入文本 | `{"element": "...", "text": "..."}` |

### 获取元素的最佳实践

1. **等待页面加载完成**
   ```
   browser_navigate → 等待 → browser_snapshot
   ```

2. **处理需要登录的页面**
   ```
   browser_navigate → browser_type (用户名) → browser_type (密码) → browser_click (登录) → browser_snapshot
   ```

3. **获取动态加载的元素**
   ```
   browser_snapshot → 检查元素 → 如果不完整 → 等待 → 再次 browser_snapshot
   ```

---

## 定位器选择策略

从 Playwright MCP 返回的元素中，按以下优先级选择定位器：

1. **data-testid** (最优)
   ```java
   page.locator("[data-testid='submit-btn']")
   ```

2. **aria-label**
   ```java
   page.getByLabel("提交")
   ```

3. **role + name**
   ```java
   page.getByRole(AriaRole.BUTTON, new Options().setName("提交"))
   ```

4. **placeholder**
   ```java
   page.getByPlaceholder("请输入...")
   ```

5. **text**
   ```java
   page.getByText("登录")
   ```

6. **CSS selector** (最后选择)
   ```java
   page.locator(".btn-primary")
   ```

---

## 示例对话

### 用户输入：
```
检测页面变更:
URL: https://chat.deepseek.com
旧的 Page 类: DashboardPage.java (workspace 目录下)
```

### Agent 执行流程：

1. **导航到页面**
   ```
   调用 browser_navigate: {"url": "https://chat.deepseek.com"}
   ```

2. **获取页面快照**
   ```
   调用 browser_snapshot
   → 获取到 35 个可交互元素
   ```

3. **读取旧 PageObject**
   ```
   读取 workspace/DashboardPage.java
   → 解析出 12 个定位器方法
   ```

4. **执行对比**
   ```
   匹配结果:
   - 10 个未变化
   - 2 个已变更
   - 5 个新增元素
   ```

5. **生成输出**
   ```
   创建工作区: dashboard_20260131_143025/
   生成报告: reports/ChangeReport.html
   生成新 Page: pageobjects/DashboardPage.java
   ```

### Agent 输出：
```
✅ 页面变更检测完成！

📂 工作区: dashboard_20260131_143025/

📊 检测结果:
- 变更元素: 2
- 新增元素: 5
- 已删除: 0

📄 生成文件:
1. pageobjects/DashboardPage.java (全新 PageObject)
2. reports/ChangeReport.html (变更对比报告)

🔧 主要变更:
1. sendButton: 选择器已更新
   旧: .send-btn
   新: [data-testid='send-message']

2. chatInput: placeholder 已更新
   旧: "输入消息"
   新: "发送消息给 DeepSeek"

➕ 新增方法:
- newChatButton()
- historyPanel()
- settingsButton()
- userAvatar()
- modelSelector()
```

---

## 与其他 Skill 的协作

### 与 Generator 协作
检测到变更后，可以使用 Generator 重新生成相关的测试用例：

```
Page Change Detector (检测变更)
         ↓
新的 PageObject 类
         ↓
Generator (更新测试代码中的引用)
```

### 与 Healer 协作
当测试失败时，可以先检测页面变更：

```
测试失败
         ↓
Page Change Detector (检测是否有定位器变化)
         ↓
生成新的 PageObject
         ↓
Healer (修复测试代码)
```
