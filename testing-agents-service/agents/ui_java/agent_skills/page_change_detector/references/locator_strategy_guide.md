# 定位器策略指南

## 定位器优先级（从高到低）

### 1. ⭐⭐⭐⭐⭐ data-testid（最推荐）

```java
// 最稳定，专门用于测试
page.locator("[data-testid='submit-button']")
page.getByTestId("submit-button")
```

**优点**：
- 专门用于测试，与 UI 展示解耦
- 不受样式和文本变化影响
- 开发人员修改 UI 时通常会保留

**使用场景**：
- 所有重要的可交互元素
- 表单输入框、按钮、链接

---

### 2. ⭐⭐⭐⭐ aria-label / aria-* 属性

```java
// 无障碍属性，语义明确
page.getByLabel("用户名")
page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("提交"))
```

**优点**：
- 语义化，便于理解
- 无障碍标准要求，不易被删除
- Playwright 原生支持

**使用场景**：
- 表单字段
- 按钮和链接
- 带无障碍标签的元素

---

### 3. ⭐⭐⭐⭐ Role + Accessible Name

```java
// 基于 ARIA 角色和名称
page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("登录"))
page.getByRole(AriaRole.TEXTBOX, new Page.GetByRoleOptions().setName("搜索"))
page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("首页"))
```

**常用角色**：
- `BUTTON` - 按钮
- `TEXTBOX` - 输入框
- `LINK` - 链接
- `CHECKBOX` - 复选框
- `RADIO` - 单选框
- `COMBOBOX` - 下拉框
- `TABLE` - 表格
- `ROW` - 行
- `CELL` - 单元格

**优点**：
- Playwright 推荐方式
- 语义明确
- 相对稳定

---

### 4. ⭐⭐⭐ placeholder 属性

```java
// 输入框占位符
page.getByPlaceholder("请输入用户名")
page.getByPlaceholder("搜索...")
```

**优点**：
- 对用户可见，不易随意修改
- 语义清晰

**注意**：
- 文本可能被国际化
- 可能被产品需求修改

---

### 5. ⭐⭐⭐ 可见文本

```java
// 基于显示文本
page.getByText("登录")
page.getByText("提交订单")
page.getByText(Pattern.compile(".*保存.*"))  // 正则匹配
```

**优点**：
- 直观，易于理解

**注意**：
- 文本可能被修改
- 可能有多个相同文本的元素
- 建议结合其他定位器使用

---

### 6. ⭐⭐ ID 选择器

```java
// 元素 ID
page.locator("#login-form")
page.locator("#submit-btn")
```

**优点**：
- 简洁
- ID 通常唯一

**注意**：
- ID 可能被开发人员修改
- 动态生成的 ID 不稳定

---

### 7. ⭐ CSS 选择器（最后选择）

```java
// CSS 选择器
page.locator(".btn.btn-primary")
page.locator("form input[type='email']")
page.locator("div.container > button.submit")
```

**优点**：
- 灵活，功能强大

**注意**：
- 依赖 DOM 结构和样式类
- 最容易因 UI 变化而失效
- 避免使用过长的选择器路径

---

## 定位器变更检测策略

### 检测优先级

1. **精确匹配**：data-testid 或 ID 完全匹配
2. **语义匹配**：aria-label 或 role 匹配
3. **文本匹配**：可见文本相似度 > 80%
4. **结构匹配**：CSS 路径相似

### 变更类型判断

| 变更类型 | 判断条件 | 建议操作 |
|----------|----------|----------|
| **属性变更** | 元素存在但属性值改变 | 更新定位器中的属性值 |
| **文本变更** | 文本内容已更改 | 更新基于文本的定位器 |
| **位置变更** | DOM 结构位置改变 | 检查是否影响定位 |
| **元素删除** | 元素不再存在 | 标记为废弃，确认是否移除功能 |
| **元素新增** | 新增可交互元素 | 建议添加定位器方法 |

---

## 最佳实践

### 1. 定位器命名规范

```java
// ✅ 好的命名 - 描述性强
public Locator loginButton() { ... }
public Locator usernameInput() { ... }
public Locator errorMessage() { ... }

// ❌ 不好的命名 - 含义不清
public Locator btn1() { ... }
public Locator input() { ... }
public Locator div() { ... }
```

### 2. 使用链式定位

```java
// ✅ 使用 filter 精确定位
page.getByRole(AriaRole.ROW)
    .filter(new Locator.FilterOptions().setHasText("张三"))
    .getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("编辑"))

// ❌ 避免复杂的 CSS 选择器
page.locator("table tbody tr:nth-child(3) td:last-child button")
```

### 3. 处理动态内容

```java
// ✅ 使用正则表达式
page.getByText(Pattern.compile("订单号.*"))
page.locator("[data-testid^='item-']")  // 以 item- 开头

// ❌ 硬编码动态值
page.getByText("订单号: 123456789")
```

### 4. 定位器文档化

```java
/**
 * 登录按钮
 * 
 * 定位策略: getByRole
 * 稳定性: ⭐⭐⭐⭐
 * 上次更新: 2026-01-31
 */
public Locator loginButton() {
    return page.getByRole(AriaRole.BUTTON, 
        new Page.GetByRoleOptions().setName("登录"));
}
```

---

## 变更维护流程

```
1. 定期执行页面变更检测（建议每次发布后）
          ↓
2. 生成变更报告，审核变更
          ↓
3. 判断变更类型:
   - 属性变更 → 更新定位器
   - 元素删除 → 确认功能移除，标记废弃
   - 元素新增 → 评估是否需要添加测试
          ↓
4. 更新 Page 类代码
          ↓
5. 重新执行测试验证
          ↓
6. 提交代码变更
```

