# pytest_yaml_api 接口自动化测试框架 - 面试要点整理

---

## 📊 项目概述

这是一套基于 **Pytest + YAML + Jinja2** 的企业级 API 接口自动化测试框架，实现了**数据驱动**和**关键字驱动**相结合的测试方案，支持多环境切换、数据库校验、Allure报告、WebSocket测试、Mock数据、CI/CD集成等功能。

### 业务场景
- 支持 Backend（后台管理系统）、Playturbo（创意平台）、OpenAPI（开放接口）等多个业务线
- 覆盖用户登录、资产管理、需求管理、创意审核、报表、财务账单等核心业务模块
- 测试用例总计 **1000+** 条（Backend 381条、Playturbo 612条、OpenAPI 48条）

---

## 🏗️ 技术架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           pytest_yaml_api 框架架构                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   CI/CD     │    │   Docker    │    │   Allure    │    │  钉钉/飞书   │  │
│  │  Jenkins    │───▶│   容器化     │───▶│   报告      │───▶│  通知推送   │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                              测试执行层                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         pytest 测试引擎                              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │   │
│  │  │ conftest │  │  pytest  │  │  插件    │  │  Fixture │             │   │
│  │  │  配置    │  │   .ini   │  │  系统    │  │   管理   │             │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                              核心引擎层                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  YAML    │  │ Jinja2   │  │  参数    │  │  断言    │  │  数据    │     │
│  │  解析器  │  │ 模板渲染  │  │  提取    │  │  校验    │  │  提取    │     │
│  │ runner   │  │ render   │  │ extract  │  │ validate │  │ extract  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                              数据驱动层                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │  │
│  │   │ YAML    │    │ config  │    │ extract │    │ api_    │          │  │
│  │   │ 用例    │    │ .yaml   │    │ .yaml   │    │ mysql   │          │  │
│  │   └─────────┘    └─────────┘    └─────────┘    └─────────┘          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                              基础支撑层                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ HTTP     │  │  MySQL   │  │  Redis   │  │ WebSocket│  │  Mock    │     │
│  │ Session  │  │  连接池  │  │  连接    │  │  客户端  │  │ mitmproxy│     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 技术栈

| 技术领域 | 技术选型 | 版本 |
|---------|---------|------|
| 测试框架 | Pytest | 8.1.1 |
| 数据驱动 | pytest_yaml_yoyo (自研插件) | 1.6.8 |
| 模板引擎 | Jinja2 | 3.1.3 |
| HTTP客户端 | Requests | 2.31.0 |
| 数据提取 | JMESPath + JSONPath | - |
| 数据库 | PyMySQL + Redis | - |
| 报告 | Allure | 2.13.5 |
| 数据生成 | Faker | 24.9.0 |
| 容器化 | Docker | - |
| CI/CD | Jenkins | - |
| Mock | mitmproxy | - |

---

## 🔄 核心流程图

### 测试用例执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        测试执行流程                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   pytest 收集用例      │
                    │   (YAML文件识别)       │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   解析 config 配置     │
                    │   - variables 变量     │
                    │   - fixtures          │
                    │   - hooks             │
                    │   - export            │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Jinja2 模板渲染      │
                    │   ${var} → 实际值      │
                    └───────────────────────┘
                                │
                                ▼
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   request 请求   │  │   ws WebSocket  │  │   api 分层调用  │
│   HTTP/HTTPS    │  │   长连接        │  │   复用公共接口   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   hooks 钩子执行       │
                    │   - request 预处理     │
                    │   - response 后处理    │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   extract 参数提取     │
                    │   - JMESPath          │
                    │   - JSONPath          │
                    │   - 正则表达式         │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   validate 断言校验    │
                    │   - eq/ne/contains    │
                    │   - 数据库断言         │
                    │   - 长度/类型断言      │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   export 变量导出      │
                    │   用于后续用例         │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Allure 报告生成      │
                    │   通知推送            │
                    └───────────────────────┘
```

### 数据流转图

```
┌─────────────────────────────────────────────────────────────────┐
│                         数据流转                                 │
└─────────────────────────────────────────────────────────────────┘

  config.yaml          YAML用例文件              extract.yaml
       │                    │                        │
       │   ┌────────────────┼────────────────┐       │
       │   │                │                │       │
       ▼   ▼                ▼                ▼       ▼
  ┌─────────────────────────────────────────────────────────┐
  │                     变量上下文 Context                   │
  │  ┌─────────────────────────────────────────────────────┐│
  │  │  - __builtins__  (Python内置函数)                   ││
  │  │  - my_builtins   (自定义函数: rand_str, ftime...)   ││
  │  │  - env           (环境配置: BASE_URL, MYSQL_HOST)   ││
  │  │  - rcy()         (读取config.yaml)                  ││
  │  │  - ry()          (读取extract.yaml)                 ││
  │  │  - query_sql()   (数据库查询)                       ││
  │  │  - execute_sql() (数据库执行)                       ││
  │  │  - fixture变量   (pytest fixture注入)              ││
  │  │  - extract提取   (接口响应提取)                     ││
  │  └─────────────────────────────────────────────────────┘│
  └─────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  Jinja2 模板渲染   │
                    │  ${变量名}        │
                    │  ${函数()}        │
                    │  ${变量|过滤器}   │
                    └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   渲染后的请求数据  │
                    │   实际发送的HTTP   │
                    └───────────────────┘
```

---

## ✨ 核心功能点

### 1. YAML用例驱动 (数据驱动测试)

**YAML用例结构设计：**
```yaml
config:
    allure:
        feature: 模块名称
    variables:                    # 模块级变量
        name: test_${rand_str(3)}
    hooks:                        # 全局钩子
        request: ['sign_request']
    export:                       # 变量导出
        - project_id

test_case_name:                   # 用例名称
-
    name: 接口描述
    allure:
        title: 用例标题
    variables:                    # 步骤级变量
        local_var: value
    request:
        method: post
        url: /api/endpoint
        json:
            name: ${name}
    extract:                      # 参数提取
        id: body.data.id
        token: $..token
    validate:                     # 断言校验
        - eq: [status_code, 200]
        - eq: [body.code, 0]
        - contains: [body.message, success]
```

**技术亮点：**
- 用例与代码分离，降低维护成本
- 支持多种变量引用方式：`${var}`、`${func()}`、`${var|filter}`
- 支持同一层级变量互相引用

### 2. 多环境配置管理

```python
# config.py 多环境配置
class TestConfig(Config):
    """测试环境"""
    BASE_URL = 'http://creative-api-test.mintegral.com'
    MYSQL_HOST = "xxx.rds.amazonaws.com"
    ...

class DevConfig(Config):
    """开发环境"""
    BASE_URL = 'http://creative-api-dev.mintegral.com'
    ...

env = {
    "test": TestConfig,
    "dev": DevConfig,
    "online": OnlineConfig
}
```

**执行方式：**
```bash
pytest --env test  # 切换测试环境
pytest --env dev   # 切换开发环境
```

### 3. 灵活的参数提取

支持 **3种提取语法**：
| 语法类型 | 示例 | 说明 |
|---------|------|------|
| JMESPath | `body.data.id` | 路径式取值 |
| JSONPath | `$..token` | 递归搜索 |
| 正则表达式 | `"token":"(.+?)"` | 正则匹配 |

```yaml
extract:
    # JMESPath 语法
    user_id: body.data.user.id
    # JSONPath 语法
    all_ids: $..list[*].id
    # 正则语法
    session: 'session_id="(.+?)"'
```

### 4. 丰富的断言方式

```yaml
validate:
    # 相等断言
    - eq: [status_code, 200]
    - eq: [body.code, 0]
    
    # 包含断言
    - contains: [body.message, success]
    - contained_by: [body.status, [1, 2, 3]]
    
    # 比较断言
    - gt: [body.data.total, 0]
    - le: [body.data.count, 100]
    
    # 长度断言
    - len_eq: [body.data.list, 10]
    - len_gt: [body.data.list, 0]
    
    # 字符串断言
    - startswith: [body.data.url, "https://"]
    - endswith: [body.data.file, ".zip"]
    
    # 数据库断言
    - eq: ['${query_sql(sql).id}', '${project_id}']
```

### 5. 数据库集成

```yaml
config:
    variables:
        sql: SELECT id FROM user WHERE name='${username}'

test_db_validate:
    name: 数据库校验
    request:
        method: post
        url: /user/create
        json:
            name: ${username}
    validate:
        # 接口响应与数据库结果对比
        - eq: [body.data.id, '${query_sql(sql).id}']
```

### 6. Hooks钩子机制

```python
# conftest.py 定义钩子函数
def request_sign(req):
    """请求签名"""
    json_data = req.get("json", {})
    sign = generate_md5(json_data)
    json_data['sign'] = sign

my_builtins.request_sign = request_sign
```

```yaml
# YAML中使用钩子
config:
    hooks:
        request: ['request_sign']    # 请求前处理
        response: ['log_response']   # 响应后处理
```

### 7. WebSocket支持

```yaml
test_websocket:
    name: WebSocket测试
    ws:
        url: ws://localhost:8080/ws
    send:
        type: subscribe
        channel: user_updates
    extract:
        msg: body.data
    validate:
        - eq: [status, 101]
```

### 8. 文件上传

```yaml
test_upload:
    name: 文件上传
    request:
        method: post
        url: /upload/file
        files:
            file: data/test.zip
            image: data/test.png
    validate:
        - eq: [status_code, 200]
```

### 9. 参数化测试

**方式一：列表参数化**
```yaml
config:
    fixtures: username, password
    parameters:
        - [user1, '123456']
        - [user2, '654321']
```

**方式二：字典参数化**
```yaml
config:
    parameters:
        - {"username": "user1", "password": "123456"}
        - {"username": "user2", "password": "654321"}
```

### 10. 全局变量导出 (export)

```yaml
# 用例1：登录获取token
test_login:
    request:
        method: post
        url: /login
    extract:
        token: body.data.token
    export:
        - token  # 导出为全局变量

# 用例2：使用全局token
test_get_user:
    request:
        method: get
        url: /user/info
        headers:
            Authorization: ${token}  # 引用全局变量
```

---

## 🔧 疑难点及解决方案

### 疑难点1：同一层级变量互相引用

**问题描述：** 
```yaml
variables:
    base_name: test
    full_name: ${base_name}_123  # 无法引用同层级的base_name
```

**解决方案：**
在 `runner.py` 中实现逐个变量渲染：

```python
# 解决同一层级变量引用变量问题
for key, value in config_variables.items():
    m_variables = {key: value}
    m_variables_render = render_template_obj.rend_template_any(m_variables, **self.context)
    # 更新到 self.context 后再渲染下一个
    self.context.update(m_variables_render)
    self.module_variable.update(m_variables_render)
```

### 疑难点2：函数内嵌套变量引用

**问题描述：**
```yaml
variables:
    project_id: 12345
    sql: SELECT * FROM task WHERE project_id=${project_id}
    
# 需要支持：${query_sql("${sql}")}
```

**解决方案：**
在模板渲染时递归处理嵌套变量：

```python
def re_replace_template_str(match) -> str:
    res_result = match.group()
    res_result_ = str(res_result).lstrip('${').rstrip('}')
    # 检测内部是否还有 ${} 嵌套
    if '${' in res_result_ and '}' in res_result_:
        instance_temp = env_filter.from_string(res_result_)
        temp_render_res = instance_temp.render(*args, **kwargs)
        return '${' + temp_render_res + '}'
    return res_result

template_str = re.sub('\$\{(.+)\}', re_replace_template_str, template_str)
```

### 疑难点3：接口关联与数据传递

**问题描述：** 接口A的响应需要传给接口B，且可能跨文件传递

**解决方案：**
1. **同文件内：** 使用 `extract` 提取 + `${变量}` 引用
2. **跨文件：** 使用 `export` 导出全局变量
3. **配置文件：** 使用 `config.yaml` 持久化关键数据

### 疑难点4：动态数据生成

**问题描述：** 测试数据需要唯一性（避免重复数据导致失败）

**解决方案：**
集成 Faker 库 + 自定义函数：

```python
# conftest.py
from faker import Faker
fake = Faker(["zh_CN"])

def rand_str(length=6):
    return fake.bothify(text='?' * length)

def current_time(format='%Y-%m-%d %H:%M:%S'):
    return time.strftime(format)

my_builtins.rand_str = rand_str
my_builtins.current_time = current_time
```

```yaml
# YAML中使用
variables:
    unique_name: test_${rand_str(8)}_${current_time('%Y%m%d%H%M%S')}
```

### 疑难点5：异步接口测试

**问题描述：** 某些接口是异步的，提交后需要轮询查询结果

**解决方案：**
使用 `sleep` 关键字 + 循环断言：

```yaml
# 提交异步任务
test_submit:
    request:
        method: post
        url: /async/submit
    extract:
        task_id: body.data.task_id

# 等待并查询结果
test_query:
    sleep: 10  # 等待10秒
    request:
        method: get
        url: /async/query
        params:
            id: ${task_id}
    validate:
        - eq: [body.data.status, success]
```

### 疑难点6：数据库单例连接

**问题描述：** 频繁创建数据库连接导致性能问题

**解决方案：**
使用单例模式：

```python
class ConnectMysql(object):
    instance = None
    init_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, host, user, password, port, database):
        if self.init_flag:
            return  # 已初始化，直接返回
        # ... 初始化连接
        self.init_flag = True
```

---

## 🌟 项目亮点

### 亮点1：自研 pytest_yaml_yoyo 插件

- 将 YAML 文件自动解析为 pytest 测试用例
- 支持动态创建测试函数和测试类
- 无需编写 Python 代码即可完成测试

### 亮点2：Jinja2 模板引擎集成

- 自定义语法 `${var}` 替代默认 `{{var}}`
- 支持过滤器：`${list|list_to_str}`
- 支持切片：`${url[:4]}` 提取前4个字符

### 亮点3：三层数据提取

```
response.json() ─┬─► JMESPath: body.data.list[0].id
                 ├─► JSONPath: $..list[*].id  
                 └─► 正则:     "id":"(\d+)"
```

### 亮点4：多维度断言

- 响应断言（状态码、响应体、响应头）
- 数据库断言（与数据库数据对比）
- 长度断言、类型断言、正则断言

### 亮点5：完整的CI/CD集成

```
Jenkins触发 ─► Docker容器 ─► 执行测试 ─► 生成Allure报告 ─► 钉钉/飞书通知
                   │
                   └─► 支持代码覆盖率统计（goc工具）
```

### 亮点6：Swagger 自动生成用例

```python
# 自动解析 swagger.json 生成 YAML 用例
s = SwaggerToYaml(swagger='http://api.example.com/swagger.json')
s.parse_json()  # 自动生成测试用例
```

### 亮点7：Mock数据支持

使用 mitmproxy 实现接口 Mock：

```python
class MockAPI:
    def request(self, flow: http.HTTPFlow):
        if flow.request.pretty_url == "http://api.example.com/data":
            flow.response = http.Response.make(
                200,
                '{"code": 0, "data": "mock_data"}',
                {"Content-Type": "application/json"}
            )
```

---

## 📈 项目成果

| 指标 | 数据 |
|------|------|
| 测试用例总数 | 1000+ |
| 覆盖业务模块 | 30+ |
| 支持测试环境 | 5个 (dev/test/test2/auto/online) |
| 日均执行次数 | 50+ |
| 缺陷发现率 | 提升 40% |
| 回归测试效率 | 提升 70% |

---

## 🎯 面试常见问题

### Q1: 为什么选择 YAML 而不是 Excel 或 JSON？

**回答要点：**
- YAML 可读性更好，支持注释
- 层级结构清晰，适合表达复杂数据
- 与 Python 生态兼容性好
- 支持多行字符串，适合写 SQL

### Q2: 如何保证测试用例的独立性？

**回答要点：**
- 使用 Faker 生成唯一测试数据
- 使用 pytest fixture scope 控制
- 通过 setup/teardown 清理测试数据
- 使用 export 机制传递必要数据

### Q3: 如何处理接口依赖？

**回答要点：**
- 同文件：extract 提取 + ${变量} 引用
- 跨文件：export 导出全局变量
- 跨模块：config.yaml 持久化
- 数据库：直接查询获取

### Q4: 框架如何扩展新功能？

**回答要点：**
- 新增断言：在 `validate.py` 添加断言方法
- 新增函数：在 `conftest.py` 添加 `my_builtins.xxx = func`
- 新增过滤器：在 `env_filter.filters["name"] = func`
- 新增 Hooks：定义函数并注册到 my_builtins

### Q5: 如何保证框架的稳定性？

**回答要点：**
- 异常处理：完善的 try-catch 机制
- 日志系统：详细的执行日志
- 重试机制：支持 pytest-rerunfailures
- 超时控制：HTTP 请求超时设置

---

## 📚 技术深度问题

### Q1: Jinja2 模板渲染原理？

Jinja2 通过 AST（抽象语法树）解析模板字符串，将 `${var}` 转换为 Python 表达式执行。本框架通过自定义 `variable_start_string='${'` 和 `variable_end_string='}'` 修改默认语法。

### Q2: pytest 插件机制原理？

pytest 通过 hook 函数实现插件，本框架使用：
- `pytest_collect_file`: 收集 YAML 文件作为测试模块
- `pytest_runtest_call`: 动态添加 allure 报告信息
- fixture 系统：管理测试资源生命周期

### Q3: 如何实现 YAML 转 pytest 用例？

1. 使用 `pytest_collect_file` hook 识别 `.yml` 文件
2. 解析 YAML 内容，提取 config 和 test case
3. 使用 `types.FunctionType` 动态创建测试函数
4. 将函数添加到动态创建的 Module 对象

---

## 🔍 项目目录结构

```
pytest_yaml_api/
├── allRun.py              # 主运行入口
├── config.py              # 多环境配置
├── config.yaml            # 运行时配置数据
├── conftest.py            # pytest 全局配置
├── pytest.ini             # pytest 配置文件
├── requirements.txt       # 依赖包
├── Dockerfile             # Docker 容器配置
├── jenkins.sh             # Jenkins CI 脚本
│
├── utils/                 # 工具模块
│   ├── runner.py          # YAML 执行引擎
│   ├── validate.py        # 断言校验
│   ├── extract.py         # 参数提取
│   ├── db.py              # 数据库操作
│   ├── render_template_obj.py  # Jinja2 渲染
│   ├── request_session.py # HTTP 会话
│   ├── log.py             # 日志处理
│   ├── report_notify.py   # 报告通知
│   └── swagger_parser.py  # Swagger 解析
│
├── testcases/             # 测试用例
│   ├── backend/           # 后台管理系统 (381 用例)
│   ├── playturbo/         # 创意平台 (612 用例)
│   └── openapi/           # 开放接口 (48 用例)
│
├── api_mysql/             # 数据库操作模板
├── mitmproxy_tool/        # Mock 工具
├── data/                  # 测试数据文件
└── reports/               # 测试报告
```

---

## 💡 总结

这套框架的核心价值在于：

1. **低门槛**：测试人员只需编写 YAML，无需深入 Python
2. **高效率**：数据驱动 + 关键字驱动，快速编写用例
3. **可维护**：用例与代码分离，修改配置无需改代码
4. **可扩展**：插件化设计，易于添加新功能
5. **可集成**：完善的 CI/CD 支持，自动化程度高

通过这套框架，将接口自动化测试的效率提升了 **70%**，测试覆盖率提升了 **40%**，是一套真正投入生产使用的企业级测试框架。

