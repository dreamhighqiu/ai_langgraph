# Playwright + Pytest UI自动化测试框架 - 面试详解

## 一、项目概述

### 1.1 项目背景
这是一个基于 **Playwright + Pytest** 的 Web UI 自动化测试框架，主要用于 **PlayTurbo** 和 **MindWorks Creative** 平台的自动化测试。该平台是一个可玩广告（Playable Ads）创意制作和管理系统。

### 1.2 核心价值
- **提升测试效率**：将手工测试转换为自动化，节省80%+的回归测试时间
- **保障产品质量**：每次发版前自动执行回归测试，及时发现问题
- **支持CI/CD**：集成到Jenkins流水线，实现持续集成测试
- **实时通知**：测试完成后自动发送钉钉通知，快速反馈结果

---

## 二、技术架构

### 2.1 技术栈

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 核心框架 | Playwright | 1.50.0 | Web自动化测试引擎 |
| 测试框架 | Pytest | 7.2.2 | 单元测试框架 |
| 报告工具 | Allure | 2.13.1 | 生成美观的测试报告 |
| 数据驱动 | PyYAML/CSV/Excel | - | 测试数据管理 |
| 数据库 | PyMySQL | 1.0.2 | MySQL数据库操作 |
| HTTP请求 | Requests | 2.31.0 | API接口测试 |
| 图像识别 | OpenCV | 4.7.0.72 | AI图像相似度对比 |
| 数据生成 | Faker | 19.3.0 | 生成测试数据 |
| 容器化 | Docker | - | 测试环境容器化 |
| 通知 | DingTalkChatbot | 1.5.7 | 测试结果通知 |

### 2.2 架构设计图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         测试执行层 (run.py)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │   Pytest 引擎   │──│  自定义插件层   │──│  Fixture配置层  │      │
│  │  (pytest.ini)   │  │   (plugins/)    │  │  (conftest.py)  │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                         测试用例层 (cases/)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ playable_fe │  │  backend    │  │   monkey    │  │    job      │ │
│  │  前台测试   │  │  后台测试   │  │  压力测试   │  │  Job测试    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                         页面对象层 (pages/)                          │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │  Page Object Model (POM) - 封装页面元素定位和操作方法           ││
│  │  • login_fe_page.py    • demand_submit_page.py                  ││
│  │  • monkey_fe_page.py   • parameter_dict_page.py                 ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                         工具层 (utils/)                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ db.py    │ │ http_    │ │ validata │ │ yaml_    │ │ handle_  │  │
│  │ 数据库   │ │ session  │ │ .py断言  │ │ util.py  │ │ util.py  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                         基础设施层                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Docker容器   │  │ Allure报告   │  │ 钉钉通知     │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 三、项目结构详解

```
playwright_pytest_ui-main/
├── cases/                      # 测试用例目录
│   ├── playable_fe/            # 前台UI测试用例
│   │   ├── 000_vrecord/        # 录屏功能测试
│   │   ├── dm/                 # 模板资源测试
│   │   ├── gm/                 # 游戏素材测试
│   │   ├── veditor/            # 视频编辑器测试
│   │   ├── payment/            # 支付功能测试
│   │   └── insights/           # 数据分析测试
│   ├── playable_backend/       # 后台管理测试用例
│   │   └── demand/             # 需求管理测试
│   ├── monkey/                 # Monkey压力测试
│   └── job/                    # 定时任务测试
│
├── pages/                      # Page Object 页面对象
│   ├── playable_fe/            # 前台页面对象
│   │   ├── login_fe_page.py    # 前台登录页
│   │   └── parameter_dict_page.py
│   ├── playable_backend/       # 后台页面对象
│   │   ├── login_backend_page.py
│   │   └── demand_submit_page.py
│   └── monkey/                 # Monkey测试页面
│       └── monkey_fe_page.py
│
├── plugins/                    # 自定义pytest插件
│   ├── __init__.py             # 全局g对象定义
│   ├── pytest_playwright.py    # Playwright集成插件
│   └── pytest_base_url_plugin.py
│
├── utils/                      # 工具类
│   ├── db.py                   # MySQL数据库操作
│   ├── http_session.py         # HTTP请求封装
│   ├── log.py                  # 日志管理
│   ├── validata.py             # 断言工具类
│   ├── yaml_util.py            # YAML文件操作
│   ├── rand.py                 # 随机数据生成
│   ├── handle_util.py          # 通用操作封装
│   ├── handle_excel.py         # Excel文件处理
│   ├── handle_console_log.py   # 控制台日志处理
│   ├── create_funtion.py       # 动态函数创建
│   └── report_notify.py        # 测试报告通知
│
├── AI_images/                  # AI图像对比
│   ├── image_similarity.py     # 图像相似度计算
│   ├── cal_confidence.py       # 置信度计算
│   ├── imgs_actual/            # 实际截图
│   └── imgs_expect/            # 期望截图
│
├── routes/                     # 路由配置
│   └── playturbo.py            # 前台路由定义
│
├── data/                       # 测试数据
│   ├── params.csv              # 参数化数据
│   └── download/               # 下载文件存储
│
├── auth/                       # 登录认证缓存
│   ├── outer_login.json        # 外部账号登录态
│   ├── inner_login.json        # 内部账号登录态
│   └── backend_login.json      # 后台登录态
│
├── docker_handle/              # Docker配置
│   ├── Dockerfile              # Docker构建文件
│   └── nginx.conf              # Nginx配置
│
├── config.py                   # 多环境配置
├── conftest.py                 # Pytest全局fixture
├── pytest.ini                  # Pytest配置
├── run.py                      # 测试执行入口
├── requirements.txt            # 依赖管理
└── gremlins.min.js             # Monkey测试JS库
```

---

## 四、核心功能实现

### 4.1 多环境配置管理

**技术实现**：基于类继承实现多环境配置切换

```python
# config.py - 环境配置类
class TestConfig(Config):
    """测试环境"""
    FE_URL = 'http://mindworks-creative-test.mintegral.com'
    BACKEND_URL = 'http://playable-portal-test.mintegral.com'
    MYSQL_HOST = "192.168.1.103"
    # ...其他配置

class DevConfig(Config):
    """开发环境"""
    FE_URL = 'http://playturbo-dev.mintegral.com'
    # ...

# 环境映射
env = {
    "test": TestConfig,
    "dev": DevConfig,
    "uat": UatConfig,
}
```

**使用方式**：
```bash
pytest --env test    # 运行测试环境
pytest --env dev     # 运行开发环境
```

### 4.2 自定义Playwright插件

**核心实现**：重写了 `pytest-playwright` 插件，增加了以下功能：

```python
# plugins/pytest_playwright.py

@pytest.fixture
def page(context: BrowserContext, pytestconfig, request):
    """增强的page fixture"""
    pages: List[Page] = []
    context.on("page", lambda page: pages.append(page))
    page = context.new_page()
    
    # 启用追踪
    tracing_option = pytestconfig.getoption("--tracing")
    if tracing_option in ["on", "retain-on-failure"]:
        context.tracing.start_chunk()
    
    yield page
    
    # 用例失败时自动截图并附加到Allure报告
    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else True
    if capture_screenshot and failed:
        screenshot_path = f"test-failed-{index+1}.png"
        page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, attachment_type=allure.attachment_type.PNG)
    
    # 录制视频
    if preserve_video:
        video.save_as(path=file_path)
        allure.attach.file(file_path, attachment_type=allure.attachment_type.WEBM)
```

**功能特性**：
- 失败自动截图
- 失败自动录制Trace
- 视频录制支持
- 自动附加到Allure报告

### 4.3 Page Object Model (POM) 设计模式

**实现示例**：

```python
# pages/playable_fe/login_fe_page.py
class LoginFePage:
    def __init__(self, page: Page):
        self.page = page
        # 元素定位封装
        self.locator_username = page.get_by_placeholder("请输入用户名称")
        self.locator_password = page.get_by_role("textbox", name="请输入密码")
        self.locator_login_btn = page.locator('//span[text()="登录"]')
    
    def navigate(self, url):
        self.page.goto(url)
    
    def login(self, username, password) -> None:
        """完整登录操作"""
        self.locator_username.fill(username)
        self.locator_password.fill(password)
        self.locator_login_btn.click()
```

**设计优势**：
- 页面元素与测试逻辑分离
- 提高代码复用性
- 便于维护，元素变化只需修改一处

### 4.4 登录态Cookie复用

**实现原理**：利用Playwright的 `storage_state` 功能保存和复用登录态

```python
# conftest.py
@pytest.fixture(scope="session")
def login_backend(browser, pytestconfig):
    """全局先登录，保存Cookie"""
    context = browser.new_context(base_url="https://test-accounts.mobvista.com")
    page = context.new_page()
    
    # 执行登录
    login = LoginBackendPage(page)
    login.navigate()
    login.login(username="xxx", password="xxx")
    
    # 等待登录完成
    page.wait_for_url(url='**/#/system/profile', timeout=120000)
    
    # 保存登录态到JSON文件
    storage_path = pytestconfig.rootpath.joinpath('auth/backend_login.json')
    context.storage_state(path=storage_path)
    
    yield context
```

**使用方式**：
```python
# 在测试用例中复用登录态
@pytest.fixture
def logged_in_context(browser, browser_context_args):
    context = browser.new_context(
        storage_state="auth/backend_login.json",
        **browser_context_args
    )
    yield context
```

### 4.5 AI图像对比断言

**技术实现**：融合多种图像相似度算法

```python
# AI_images/image_similarity.py

def calc_image_similarity(actual_path, expect_path):
    """融合三种算法计算图片相似度"""
    # ORB特征点匹配
    similary_ORB = float(ORB_img_similarity(expect_path, actual_path))
    # 感知哈希算法
    similary_phash = float(phash_img_similarity(expect_path, actual_path))
    # 直方图对比
    similary_hist = float(calc_similar_by_path(expect_path, actual_path))
    
    # 融合策略：如果最大值>0.95取最大，否则取最小
    max_sim = max(similary_ORB, similary_phash, similary_hist)
    min_sim = min(similary_ORB, similary_phash, similary_hist)
    
    return max_sim if max_sim > 0.95 else min_sim

def similarity_page(page: Page, png_name, expect_sim=0):
    """页面截图相似度断言"""
    png = page.screenshot(path=f'AI_images/imgs_actual/{png_name}')
    # 附加到Allure报告
    allure.attach(png, f'actual截图_{png_name}', allure.attachment_type.PNG)
    
    # 计算相似度
    sim = cal_ccoeff_confidence(actual_img, expect_img)
    
    assert expect_sim <= sim, f'相似度断言失败: {sim} < {expect_sim}'
```

**应用场景**：
- UI布局回归测试
- 图表渲染验证
- 复杂界面对比

### 4.6 Monkey压力测试

**技术实现**：集成 gremlins.js 实现随机操作

```python
# pages/monkey/monkey_fe_page.py
class MonkeyPage:
    def __init__(self, page: Page):
        self.page = page
        # 配置日志记录
        self.log = logging.Logger("monkey")
        
    def navigate(self, url):
        # 注入gremlins.js
        self.page.add_init_script(path='./gremlins.min.js')
        
        # 监听控制台消息、页面错误、请求
        self.page.on("console", self.console_handle)
        self.page.on("pageerror", self.pageerror_handle)
        self.page.on("request", self.request_handle)
        
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
        
        # 执行Monkey测试
        self.page.evaluate("gremlins.createHorde().unleash()")
```

**测试效果**：
- 随机点击、滚动、输入
- 自动捕获JavaScript错误
- 记录埋点请求验证

### 4.7 数据驱动测试

**支持多种数据源**：

```python
# CSV数据驱动
@pytest.mark.parametrize('data', readCsv('data/params.csv'))
def test_params(self, data):
    self.page.goto(data[1])

# Excel数据驱动
@pytest.mark.parametrize('data', dict_date('data/1.xlsx', 'Sheet1'))
def test_excel_data(self, data):
    self.page.fill('#username', data['用户名'])

# YAML数据驱动
from utils.yaml_util import read_yaml
test_data = read_yaml('data/test_data.yml')
```

### 4.8 钉钉/飞书/企业微信通知

**实现代码**：

```python
# utils/report_notify.py

def ding_ding_notify(access_token, title, text, at_mobiles=None):
    """钉钉机器人通知"""
    webhook = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}'
    ding = DingtalkChatbot(webhook=webhook)
    ding.send_markdown(title=title, text=text, at_mobiles=at_mobiles)

def fei_shu_notify(token, title, text, color="green"):
    """飞书机器人通知"""
    url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{token}"
    data = {"msg_type": "interactive", "card": {...}}
    requests.post(url, json=data)

def wecom_notify(token, text, msgtype="markdown"):
    """企业微信机器人通知"""
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={token}"
    requests.post(url, json={"msgtype": msgtype, "markdown": {"content": text}})
```

**通知内容**：

```markdown
### UI自动化执行结果:
- 运行仓库后台域名: http://playable-portal-test.mintegral.com
- 运行playturbo域名: http://mindworks-creative-test.mintegral.com
- 持续时间: 15 min

### 本次运行结果:
- 总用例数: 50
- 通过用例：45
- 失败用例： 3
- 异常用例： 2
- 通过率： 90.00 %
```

---

## 五、技术亮点

### 5.1 自定义Playwright插件
- **亮点**：重写官方 `pytest-playwright` 插件，实现更灵活的控制
- **价值**：支持失败自动截图/录屏、Trace追踪、Allure集成

### 5.2 Session级别登录态复用
- **亮点**：使用 `storage_state` 保存Cookie，避免重复登录
- **价值**：节省测试时间，提高执行效率

### 5.3 AI图像相似度断言
- **亮点**：融合ORB、pHash、直方图三种算法
- **价值**：解决UI自动化中复杂界面验证难题

### 5.4 全链路Trace追踪
- **亮点**：失败用例自动生成Trace.zip，可在Playwright Trace Viewer中回放
- **价值**：快速定位问题，调试更高效

### 5.5 Monkey测试集成
- **亮点**：集成gremlins.js实现Web页面压力测试
- **价值**：发现边界异常、内存泄漏等问题

### 5.6 多环境配置切换
- **亮点**：支持 test/dev/uat 多环境一键切换
- **价值**：同一套用例支持多环境验证

### 5.7 Docker容器化
- **亮点**：基于微软官方Playwright镜像构建
- **价值**：保证CI/CD环境一致性

---

## 六、疑难点及解决方案

### 6.1 问题：Playwright的 `is_visible()` 返回错误结果
**现象**：元素明明可见，但 `locator.is_visible()` 返回False

**解决方案**：
```python
# 使用expect断言替代
from playwright.sync_api import expect
expect(locator).to_be_visible()

# 或使用等待机制
page.wait_for_selector(selector, state="visible")
```

### 6.2 问题：登录态失效导致用例大面积失败
**现象**：Session过期后，依赖登录态的用例全部失败

**解决方案**：
```python
# 在fixture中增加登录态刷新机制
@pytest.fixture(scope="session", autouse=True)
def refresh_login_state(browser, pytestconfig):
    # 检查登录态是否过期
    if is_token_expired('auth/login.json'):
        # 重新登录并保存
        perform_login_and_save()
```

### 6.3 问题：元素定位不稳定
**现象**：动态ID、异步加载导致定位失败

**解决方案**：
```python
# 1. 优先使用语义化定位器
page.get_by_role("button", name="提交")
page.get_by_placeholder("请输入用户名")
page.get_by_text("登录成功")

# 2. 使用等待机制
page.wait_for_selector('[data-testid="submit"]', state="visible")
page.wait_for_load_state("networkidle")

# 3. 使用XPath兜底
page.locator('//span[contains(text(),"确定")]')
```

### 6.4 问题：并发执行时资源竞争
**现象**：多进程执行时，共享数据冲突

**解决方案**：
```python
# 使用xdist的loadscope模式，按模块分发
pytest -n auto --dist=loadscope

# 数据库操作使用单例模式
class ConnectMysql(object):
    instance = None
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance
```

### 6.5 问题：CI环境无头模式字体渲染差异
**现象**：Linux环境截图与本地Mac/Windows不一致

**解决方案**：
```python
# 按环境区分期望图片
if is_run_env() == "linux":
    expect_path = 'AI_images/imgs_expect_linux/'
elif is_run_env() == "mac":
    expect_path = 'AI_images/imgs_expect_mac/'

# Dockerfile中安装字体
RUN apt-get install -y fonts-noto-cjk
```

### 6.6 问题：文件上传在Docker中失败
**现象**：本地上传成功，Docker环境失败

**解决方案**：
```python
# 使用绝对路径
import os
file_path = os.path.join(os.getcwd(), 'data', 'test.png')

# 确保文件存在
if not os.path.exists(file_path):
    raise FileNotFoundError(f"上传文件不存在: {file_path}")

# 使用file_chooser处理上传
with page.expect_file_chooser() as fc_info:
    page.click('#upload-btn')
file_chooser = fc_info.value
file_chooser.set_files(file_path)
```

---

## 七、面试常见问题

### Q1: 为什么选择Playwright而不是Selenium？

**答案要点**：
1. **自动等待**：Playwright内置智能等待，无需显式WebDriverWait
2. **速度更快**：直接通过CDP协议控制浏览器，比Selenium快2-3倍
3. **更好的稳定性**：自动处理元素状态检查，减少Flaky测试
4. **多浏览器支持**：一套API支持Chromium、Firefox、WebKit
5. **原生Trace功能**：可录制回放，调试更方便
6. **网络拦截**：原生支持Mock和拦截请求

### Q2: 如何处理动态元素和异步加载？

**答案要点**：
```python
# 1. 等待网络空闲
page.wait_for_load_state("networkidle")

# 2. 等待元素状态
page.wait_for_selector('.loading', state="hidden")
locator.wait_for(state="visible")

# 3. 等待特定请求完成
with page.expect_response("**/api/data") as resp:
    page.click('#load-btn')
response = resp.value
```

### Q3: 如何设计可维护的自动化测试框架？

**答案要点**：
1. **分层设计**：用例层、页面对象层、工具层分离
2. **POM模式**：页面元素和操作封装在Page类中
3. **数据驱动**：测试数据与代码分离
4. **配置外部化**：环境配置独立管理
5. **统一断言**：封装AssertUtils工具类
6. **日志规范**：统一日志格式和级别

### Q4: 如何保证测试用例的稳定性？

**答案要点**：
1. **合理等待**：使用显式等待，避免硬编码sleep
2. **重试机制**：使用pytest-rerunfailures失败重跑
3. **数据隔离**：每个用例使用独立数据，避免数据污染
4. **环境检查**：执行前验证环境可用性
5. **用例独立**：用例之间不能有依赖关系
6. **清理机制**：测试后清理创建的数据

### Q5: 这个项目中你最满意的技术实现是什么？

**参考答案**：

**自定义Playwright插件的实现**

我重写了官方的pytest-playwright插件，实现了以下增强功能：

1. **失败自动截图**：用例失败时自动截取当前页面
2. **Trace追踪**：生成可回放的Trace文件
3. **视频录制**：支持失败用例录制回放
4. **Allure集成**：自动将截图、视频、Trace附加到报告

这个设计让问题定位效率提升了80%以上。之前失败用例需要手动复现，现在直接看Trace回放就能定位问题。

### Q6: 如何实现测试报告的实时通知？

**答案要点**：
```python
# 在pytest_terminal_summary钩子中实现
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    total = terminalreporter._numcollected
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    
    # 构建通知内容
    text = f"总用例: {total}, 通过: {passed}, 失败: {failed}"
    
    # 发送钉钉通知
    ding_ding_notify(access_token="xxx", text=text)
```

### Q7: 如何处理跨域iframe中的元素？

**答案要点**：
```python
# 使用frame_locator定位iframe中的元素
frame = page.frame_locator("#preview-device-iframe")
element = frame.locator("#gameDiv")
element.click()

# 多层嵌套iframe
page.frame_locator("#outer").frame_locator("#inner").locator("button")
```

### Q8: 项目中如何实现数据库验证？

**答案要点**：
```python
# 使用fixture注入数据库连接
@pytest.fixture(scope="session")
def execute_mysql():
    db = ConnectMysql(host=..., user=..., password=...)
    yield db
    db.close()

# 在用例中使用
def test_create_order(self, execute_mysql):
    # 执行UI操作创建订单
    self.page.click('#create-btn')
    
    # 数据库验证
    result = execute_mysql.query_sql(
        "SELECT * FROM orders WHERE name='test_order'"
    )
    assert result is not None
    assert result['status'] == 'created'
```

---

## 八、项目运行指南

### 8.1 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 安装浏览器
playwright install
```

### 8.2 运行测试
```bash
# 运行全部用例
pytest

# 指定环境
pytest --env test

# 指定用例
pytest -k "test_login"

# 生成报告
pytest --alluredir ./temps
allure serve ./temps
```

### 8.3 Docker运行
```bash
# 构建镜像
docker build -t playwright-test .

# 运行测试
docker run -it playwright-test pytest
```

---

## 九、总结

这个项目是一个**企业级UI自动化测试框架**，具有以下特点：

1. **技术先进**：基于Playwright这一新一代自动化工具
2. **架构清晰**：采用分层设计，遵循POM模式
3. **功能完善**：支持多环境、数据驱动、AI图像对比
4. **工程化程度高**：Docker容器化、CI/CD集成、实时通知
5. **可扩展性强**：插件化设计，易于扩展新功能

通过这个项目，我深入掌握了：
- Playwright自动化测试技术
- Pytest测试框架高级用法
- POM设计模式
- Docker容器化部署
- CI/CD流水线集成
- 图像识别在测试中的应用
