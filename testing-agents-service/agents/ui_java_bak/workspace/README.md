# Java Playwright UI 测试 Workspace

此目录是 Java UI 测试 Agent 的工作区，用于存放：

- **生成的 Java 测试文件** (`.java`)
- **测试计划文档** (`.md`)
- **临时文件和中间产物**

## 目录说明

Agent 会在此目录下自动创建和管理文件，例如：

```
workspace/
├── test-plans/                    # 测试计划
│   └── device-inventory-plan.md
├── pageobjects/                   # 生成的 PageObject 类
│   └── DeviceInventoryPage.java
├── helpers/                       # 生成的 Helper 类
│   └── DeviceInventoryHelper.java
└── testcases/                     # 生成的测试用例
    └── DeviceInventoryPageTest.java
```

## 使用建议

1. **不要手动编辑 Agent 生成的文件** - Agent 会自动管理这些文件
2. **定期备份重要文件** - 将满意的测试代码复制到项目测试目录
3. **审查生成的代码** - 确保符合项目规范后再集成

## 清理

可以安全删除此目录下的所有内容，Agent 会根据需要重新创建。

