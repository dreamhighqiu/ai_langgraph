# Playwright MCP 元素获取指南

本指南详细说明如何使用 Playwright MCP 工具获取页面元素，用于页面变更检测。

## 核心工具

### 1. browser_navigate - 导航到目标页面

```
Tool: browser_navigate
Args: {"url": "https://chat.deepseek.com"}
```

**返回**: 页面加载状态

### 2. browser_snapshot - 获取页面元素快照

```
Tool: browser_snapshot
Args: {} (无参数)
```

**返回格式**:
```
- [ref=e1] button "新建对话"
- [ref=e2] textbox [placeholder="发送消息给 DeepSeek"]
- [ref=e3] button "发送" [disabled]
- [ref=e4] link "设置" [href="/settings"]
- [ref=e5] button [aria-label="用户菜单"]
- [ref=e6] img [alt="用户头像"]
```

### 3. browser_click - 点击元素

```
Tool: browser_click
Args: {"element": "登录按钮", "ref": "e1"}
```

### 4. browser_type - 输入文本

```
Tool: browser_type
Args: {"element": "用户名输入框", "text": "testuser", "ref": "e2"}
```

---

## 完整工作流示例

### 场景: 检测 DeepSeek Chat 页面变更

#### Step 1: 导航到页面
```
调用: browser_navigate
参数: {"url": "https://chat.deepseek.com"}
```

#### Step 2: 等待页面加载（可选登录）
如果需要登录才能看到完整页面：
```
调用: browser_type
参数: {"element": "用户名", "text": "user@example.com"}

调用: browser_type  
参数: {"element": "密码", "text": "password123"}

调用: browser_click
参数: {"element": "登录按钮"}
```

#### Step 3: 获取页面元素快照
```
调用: browser_snapshot
```

返回示例:
```
页面快照 - https://chat.deepseek.com

可交互元素:
- [ref=e1] button "新建对话" [data-testid="new-chat"]
- [ref=e2] textbox [placeholder="发送消息给 DeepSeek"] 
- [ref=e3] button "发送" [aria-label="发送消息"]
- [ref=e4] navigation
  - [ref=e5] link "历史记录"
  - [ref=e6] link "设置"
  - [ref=e7] link "帮助"
- [ref=e8] button [aria-label="用户菜单"]
  - [ref=e9] img [alt="头像"]
- [ref=e10] combobox "模型选择" [value="deepseek-chat"]
```

---

## 元素属性解析

从 browser_snapshot 返回的元素中提取关键属性：

| 属性 | 用途 | 示例 |
|------|------|------|
| ref | 唯一引用 ID | e1, e2, e3 |
| tag | 元素类型 | button, input, link |
| text | 元素文本 | "新建对话" |
| placeholder | 输入框占位符 | "发送消息给 DeepSeek" |
| aria-label | 无障碍标签 | "发送消息" |
| data-testid | 测试 ID | "new-chat" |
| href | 链接地址 | "/settings" |
| value | 当前值 | "deepseek-chat" |
| disabled | 是否禁用 | true/false |

---

## 定位器生成优先级

从 MCP 元素属性生成 Java 定位器的优先级：

### 1. data-testid (最优 - 稳定性最高)
```java
// MCP: [data-testid="new-chat"]
page.locator("[data-testid='new-chat']")
```

### 2. aria-label (语义化 - 推荐)
```java
// MCP: [aria-label="发送消息"]
page.getByLabel("发送消息")
```

### 3. Role + Name (语义化)
```java
// MCP: button "新建对话"
page.getByRole(AriaRole.BUTTON, new Options().setName("新建对话"))
```

### 4. Placeholder (输入框)
```java
// MCP: textbox [placeholder="发送消息给 DeepSeek"]
page.getByPlaceholder("发送消息给 DeepSeek")
```

### 5. Text (文本匹配)
```java
// MCP: link "设置"
page.getByText("设置")
```

### 6. CSS Selector (最后选择)
```java
// MCP: button.primary-btn
page.locator("button.primary-btn")
```

---

## 处理特殊情况

### 1. 动态加载的元素

某些元素可能在初始快照中不存在，需要等待加载：

```
// 第一次快照
browser_snapshot → 缺少某些元素

// 等待后再次快照
browser_click("展开更多") → browser_snapshot → 获取完整元素
```

### 2. 需要滚动才能看到的元素

```
// 滚动到底部
browser_scroll(direction="down")
browser_snapshot
```

### 3. 弹窗/模态框中的元素

```
// 打开弹窗
browser_click("设置按钮")
// 获取弹窗内元素
browser_snapshot
```

### 4. iframe 中的元素

```
// 切换到 iframe
browser_switch_frame(ref="iframe-e1")
browser_snapshot
```

---

## 元素匹配策略

### 与旧 PageObject 方法匹配

| 匹配因素 | 权重 | 说明 |
|----------|------|------|
| data-testid 匹配 | 高 | testid 相同则高度确定 |
| 方法名包含元素文本 | 中 | loginButton ↔ "登录" |
| 定位器内容相似 | 中 | 选择器部分匹配 |
| 元素类型相同 | 低 | 都是 button |

### 匹配示例

旧方法:
```java
public Locator loginButton() {
    return page.locator("#old-login-btn");
}
```

MCP 元素:
```
- [ref=e1] button "登录" [data-testid="login-btn"]
```

匹配分析:
- 方法名 "loginButton" 包含 "login" ✓
- 元素文本 "登录" 对应 "login" ✓
- 元素类型 button ✓
- **匹配置信度: 85%**

生成新定位器:
```java
public Locator loginButton() {
    return page.locator("[data-testid='login-btn']");
}
```

---

## 最佳实践

### 1. 完整获取页面状态
```
browser_navigate → 等待加载 → browser_snapshot
```

### 2. 处理登录保护页面
```
browser_navigate → 登录流程 → browser_snapshot
```

### 3. 获取多状态元素
```
browser_snapshot (初始状态)
browser_click (触发状态变化)
browser_snapshot (新状态)
```

### 4. 验证元素变更
```
browser_snapshot → 对比旧 PageObject → 生成变更报告
```

---

## 常见问题

### Q: browser_snapshot 返回空或不完整？

**可能原因**:
1. 页面未完全加载
2. 需要登录
3. 元素在 iframe 中
4. 元素需要滚动才可见

**解决方案**:
```
// 等待特定元素出现
browser_wait_for(selector="main-content")
browser_snapshot
```

### Q: 如何获取隐藏元素？

browser_snapshot 默认只返回**可见**元素。对于隐藏元素：
```
// 触发显示
browser_click("展开按钮")
browser_snapshot
```

### Q: 元素定位器不稳定怎么办？

优先使用更稳定的属性：
1. data-testid > aria-label > text > CSS class
2. 避免使用基于位置的选择器（如 nth-child）
3. 使用组合选择器增加唯一性

