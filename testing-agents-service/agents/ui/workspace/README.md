# DeepSeek网站自动化测试项目

## 项目概述
这是一个使用Playwright for Java框架为DeepSeek官方网站（https://www.deepseek.com/）创建的自动化测试套件。

## 功能特性
- ✅ 完整的页面功能测试
- ✅ 多语言切换测试
- ✅ 链接有效性验证
- ✅ 响应式设计测试
- ✅ 性能测试
- ✅ 截图功能（测试失败时自动截图）

## 技术栈
- **测试框架**: Playwright for Java 1.45.0
- **断言库**: AssertJ 3.25.3
- **测试运行器**: JUnit 5.10.0
- **构建工具**: Maven
- **Java版本**: JDK 11+

## 项目结构
```
deepseek-automation-tests/
├── src/test/java/
│   ├── com/deepseek/tests/
│   │   ├── base/              # 基础测试类
│   │   │   └── BaseTest.java
│   │   ├── pages/             # 页面对象模型
│   │   │   └── HomePage.java
│   │   ├── tests/             # 测试用例
│   │   │   └── DeepSeekFunctionalTests.java
│   │   └── utils/             # 工具类
│   │       └── TestData.java
├── src/test/resources/        # 配置文件
│   └── config.properties
├── pom.xml                    # Maven配置
└── README.md
```

## 测试用例覆盖

### 功能测试 (10个测试用例)
1. **TC-001**: 验证首页正常加载
2. **TC-002**: 验证语言切换功能
3. **TC-003**: 验证主要功能链接
4. **TC-004**: 验证社交媒体链接
5. **TC-005**: 验证法律信息和备案
6. **TC-006**: 验证公告链接
7. **TC-007**: 验证页面性能
8. **TC-008**: 验证响应式设计
9. **TC-009**: 验证页面内容完整性
10. **TC-010**: 验证导航功能

### 测试标签
- `@Tag("smoke")`: 冒烟测试
- `@Tag("regression")`: 回归测试
- `@Tag("integration")`: 集成测试
- `@Tag("performance")`: 性能测试
- `@Tag("responsive")`: 响应式测试
- `@Tag("screenshot")`: 需要截图的测试

## 环境要求

### 系统要求
- Java JDK 11或更高版本
- Maven 3.6或更高版本
- 稳定的网络连接

### 浏览器要求
- Chrome/Chromium浏览器
- Playwright会自动安装所需的浏览器

## 安装和运行

### 1. 克隆项目
```bash
git clone <repository-url>
cd deepseek-automation-tests
```

### 2. 安装依赖
```bash
mvn clean install
```

### 3. 运行所有测试
```bash
mvn test
```

### 4. 运行特定测试类
```bash
mvn test -Dtest=DeepSeekFunctionalTests
```

### 5. 运行带标签的测试
```bash
# 运行冒烟测试
mvn test -Dgroups=smoke

# 运行回归测试
mvn test -Dgroups=regression
```

### 6. 生成测试报告
```bash
mvn surefire-report:report
```

## 配置说明

### 浏览器配置 (config.properties)
```properties
# 浏览器设置
browser=chromium      # 可选: chromium, firefox, webkit
headless=false        # 是否无头模式
slow.mo=100           # 操作延迟(毫秒)
timeout=30000         # 超时时间(毫秒)

# 测试设置
screenshot.on.failure=true  # 失败时截图
```

### 修改配置
1. 编辑 `src/test/resources/config.properties`
2. 修改相应的配置值
3. 重新运行测试

## 测试报告

### 控制台输出
测试运行时会显示详细的执行信息：
```
✓ TC-001: 首页加载测试通过
✓ TC-002: 语言切换测试通过
✓ TC-003: 主要功能链接测试通过
...
```

### 截图
测试失败时会在 `screenshots/` 目录下生成截图：
```
screenshots/
├── TC-001_验证首页正常加载.png
├── TC-002_验证语言切换功能.png
└── ...
```

### Maven报告
运行 `mvn surefire-report:report` 后，在 `target/site/surefire-report.html` 查看详细报告。

## 开发指南

### 添加新的测试用例
1. 在 `DeepSeekFunctionalTests.java` 中添加新的测试方法
2. 使用 `@Test`、`@DisplayName` 和 `@Tag` 注解
3. 遵循Given-When-Then模式编写测试
4. 使用AssertJ进行断言

### 添加新的页面对象
1. 在 `pages/` 目录下创建新的页面类
2. 封装页面元素和操作方法
3. 在测试类中实例化使用

### 最佳实践
1. **使用稳定的选择器**: 优先使用 `data-testid`、`role`、`text` 选择器
2. **添加适当的等待**: 使用 `waitForLoadState` 而不是硬性等待
3. **编写清晰的断言**: 使用AssertJ的流式断言
4. **保持测试独立**: 每个测试应该可以独立运行
5. **添加详细的日志**: 在关键步骤添加日志输出

## 故障排除

### 常见问题

#### 1. 浏览器无法启动
```bash
# 重新安装Playwright浏览器
mvn exec:java -e -Dexec.mainClass=com.microsoft.playwright.CLI -Dexec.args="install"
```

#### 2. 测试运行缓慢
- 检查网络连接
- 减少 `slow.mo` 配置值
- 启用无头模式 (`headless=true`)

#### 3. 元素定位失败
- 检查选择器是否仍然有效
- 添加适当的等待时间
- 使用更稳定的选择器策略

#### 4. 测试间歇性失败
- 增加超时时间
- 添加重试机制
- 检查网络稳定性

### 调试技巧
1. **启用详细日志**: 在配置中设置 `DEBUG` 级别日志
2. **手动运行测试**: 在IDE中单独运行失败的测试
3. **检查截图**: 查看失败时生成的截图
4. **查看控制台输出**: 检查测试执行过程中的日志

## 持续集成

### GitHub Actions示例
```yaml
name: DeepSeek Automation Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up JDK 11
      uses: actions/setup-java@v3
      with:
        java-version: '11'
    - name: Run tests
      run: mvn test
```

## 贡献指南
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证
MIT License

## 联系方式
如有问题或建议，请通过GitHub Issues提交。