# MTG 移动广告归因自动化测试框架 - 面试详解

---

## 📌 一、项目概述

### 1.1 项目背景与业务价值

**业务背景**：在移动广告投放场景中，广告主投放广告后需要验证归因系统是否能正确追踪用户从**点击广告 → 跳转应用商店 → 下载安装应用 → 打开应用**的完整链路。这个归因链路的准确性直接关系到广告收益结算。

**项目定位**：这是一个**端到端的移动应用广告归因自动化测试平台**，通过自动化手段替代人工测试，实现高效、稳定的归因验证。

**支持平台**：
- ✅ Android 平台 (Google Play Store)
- ✅ iOS 平台 (Apple App Store)
- ✅ Amazon 平台 (Amazon App Store)

### 1.2 项目价值与效率提升

| 对比项 | 手动测试 | 自动化测试 | 提升幅度 |
|--------|---------|-----------|---------|
| 单个 Offer 测试时间 | ~30分钟 | ~5分钟 | **83% ↑** |
| 每日测试数量 | ~15个 | ~100个 | **567% ↑** |
| 人力成本 | 1人/天 | 0.2人/天 | **80% ↓** |
| 测试稳定性 | 85% | 95%+ | **10% ↑** |
| 问题响应时间 | ~2小时 | ~10分钟 | **92% ↓** |

---

## 📐 二、技术架构设计

### 2.1 项目整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MTG Attribution Test Automation                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │   main.py   │───▶│  conftest   │───▶│  runner.py  │───▶│   Report    │   │
│  │   (入口)    │    │  (Fixture)  │    │  (测试用例)  │    │  (钉钉通知) │   │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘   │
│         │                  │                  │                              │
│         ▼                  ▼                  ▼                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                          Driver Layer (驱动层)                        │    │
│  ├─────────────┬─────────────┬─────────────┬─────────────────────────┤    │
│  │ AndroidDriver│  IOSDriver  │AmazonDriver │      FlyVpn Handler     │    │
│  │  (安卓操作)  │  (iOS操作)  │ (亚马逊操作) │       (VPN切换)         │    │
│  └─────────────┴─────────────┴─────────────┴─────────────────────────┘    │
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                          Utils Layer (工具层)                         │    │
│  ├────────────┬────────────┬────────────┬────────────┬────────────────┤    │
│  │ AdbUtils   │ OfferUtils │ OfferMysql │NoticeUtils │  HttpRequest   │    │
│  │(ADB命令)   │(单子拉取)  │(数据库操作) │(钉钉通知)  │  (HTTP请求)    │    │
│  └────────────┴────────────┴────────────┴────────────┴────────────────┘    │
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                          Data Layer (数据层)                          │    │
│  ├─────────────────────────────┬───────────────────────────────────────┤    │
│  │   Model (SQLAlchemy ORM)    │         Element (页面元素)              │    │
│  │   MtgTestTrackingAuto       │     playstore/appstore/flyvpn         │    │
│  └─────────────────────────────┴───────────────────────────────────────┘    │
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                          Infrastructure (基础设施)                    │    │
│  ├─────────────────────────────┬───────────────────────────────────────┤    │
│  │      Appium Server          │           MySQL Database              │    │
│  │    (移动端自动化引擎)         │         (测试数据存储)                 │    │
│  └─────────────────────────────┴───────────────────────────────────────┘    │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心技术栈

| 技术领域 | 技术选型 | 版本 | 用途说明 |
|----------|---------|------|---------|
| 测试框架 | **Pytest** | 7.4.4 | 测试用例管理、Fixture依赖注入、参数化 |
| 自动化引擎 | **Appium** | 4.0.1 | 移动端UI自动化,跨平台支持 |
| 编程语言 | **Python** | 3.x | 主开发语言 |
| 数据库ORM | **SQLAlchemy** | 2.0.30 | 对象关系映射,数据库操作 |
| 数据库驱动 | **PyMySQL** | 1.0.2 | MySQL数据库连接 |
| Web驱动 | **Selenium** | 4.23.1 | Appium底层依赖 |
| 日志系统 | **Loguru** | 0.5.3 | 结构化日志记录 |
| 设备控制 | **ADB** | - | Android设备调试桥 |

### 2.3 目录结构设计

```
mtg-attribution-test-automation/
├── main.py                 # 主入口文件 - Pytest启动
├── runner.py               # 测试用例主流程 - 核心业务逻辑
├── conftest.py             # Pytest配置 - Fixture定义、Driver初始化
├── settings.py             # 全局配置 - 日志路径、截图路径
├── utils.py                # 工具函数 - Click URL生成
│
├── config/                 # 📁 配置文件目录
│   ├── devices.json        # 多设备配置(Appium连接参数)
│   └── sys_config.py       # 系统配置(数据库/钉钉Token)
│
├── driver/                 # 📁 Driver封装层 (核心)
│   ├── android_driver.py   # Android操作封装(下载/安装/清缓存)
│   ├── ios_driver.py       # iOS操作封装(App Store操作)
│   ├── amazon_driver.py    # Amazon操作(继承Android)
│   ├── fly_vpn.py          # VPN连接封装(国家切换)
│   └── common_func.py      # 通用等待函数
│
├── element/                # 📁 页面元素定义 (Page Object雏形)
│   ├── elements.py         # 应用包名/元素定位符
│   └── flyvpn_element.py   # FlyVPN页面元素+国家映射
│
├── utils/                  # 📁 工具类目录
│   ├── adb_utils.py        # ADB命令封装(设备操作)
│   ├── offer_utils.py      # Offer数据拉取与筛选逻辑
│   ├── offer_mysql.py      # 测试记录数据库操作
│   ├── notice_utils.py     # 钉钉通知工具
│   ├── http_request.py     # HTTP请求封装(重试机制)
│   ├── sql_template.py     # SQLAlchemy通用操作模板
│   ├── time_utils.py       # 时间工具
│   ├── sub_process.py      # 子进程执行封装
│   └── exception_utils.py  # 自定义异常类
│
├── model/                  # 📁 数据库模型
│   └── mtg_test_tracking_auto.py  # 测试记录表ORM模型
│
├── log/                    # 📁 日志输出目录 (按平台/日期分类)
└── jpg/                    # 📁 截图输出目录 (失败截图)
```

---

## 🔄 三、核心流程详解

### 3.1 Android测试完整流程图

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        Android 自动化测试流程图                                │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │    1. 获取测试数据       │
                        │  MtgNewOffer.get_offer  │
                        └────────────┬────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ 从线上数据库拉取  │      │  多维度筛选过滤   │      │  随机选择Offer   │
│ 符合条件的Offer  │─────▶│ (平台/国家/设备)  │─────▶│  避免集中测试    │
└─────────────────┘      └─────────────────┘      └────────┬────────┘
                                                           │
                                                           ▼
                        ┌─────────────────────────┐
                        │    2. 运行前检查         │
                        └────────────┬────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  实例化AdbUtils  │      │ 检查应用是否已装  │      │  检查屏幕锁屏    │
│   获取设备UDID   │      │  已装则跳过执行   │      │  锁屏则解锁     │
└─────────────────┘      └─────────────────┘      └────────┬────────┘
                                                           │
                                                           ▼
                        ┌─────────────────────────┐
                        │    3. 网络环境配置       │
                        └────────────┬────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  检查WiFi状态    │      │ 清除Play Store  │      │  连接FlyVPN     │
│  关闭则开启     │─────▶│    缓存数据      │─────▶│ 切换目标国家    │
└─────────────────┘      └─────────────────┘      └────────┬────────┘
                                                           │
                                                           ▼
                        ┌─────────────────────────┐
                        │  Ping Google验证网络    │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │    4. 模拟广告点击       │
                        └────────────┬────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ 生成Click URL   │      │  打开测单工具    │      │ 自动跳转到      │
│ (token+gaid+id) │─────▶│  传入Click URL  │─────▶│ Google Play    │
└─────────────────┘      └─────────────────┘      └────────┬────────┘
                                                           │
                                                           ▼
                        ┌─────────────────────────┐
                        │    5. 应用下载安装       │
                        └────────────┬────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ 判断进入PlayStore│      │点击Install按钮  │      │ 监控下载进度    │
│  (状态检测)      │─────▶│  开始下载       │─────▶│ (Cancel按钮)   │
└─────────────────┘      └─────────────────┘      └────────┬────────┘
                                                           │
                                                           ▼
                        ┌─────────────────────────┐
                        │  等待安装完成(Uninstall) │
                        │    最长等待30分钟        │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │    6. 安装验证与回调     │
                        └────────────┬────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  回调测试服务器  │      │  发送钉钉通知    │      │  打开应用验证   │
│  记录安装成功   │─────▶│  成功消息推送    │─────▶│  启动正常      │
└─────────────────┘      └─────────────────┘      └────────┬────────┘
                                                           │
                                                           ▼
                        ┌─────────────────────────┐
                        │    7. 稳定性测试         │
                        │    Monkey随机事件       │
                        └────────────┬────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ Monkey测试      │      │  关闭应用       │      │  二次启动测试   │
│ 50次随机操作    │─────▶│ force-stop     │─────▶│  再次Monkey    │
└─────────────────┘      └─────────────────┘      └────────┬────────┘
                                                           │
                                                           ▼
                        ┌─────────────────────────┐
                        │    8. 清理与状态更新     │
                        └────────────┬────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  关闭相关应用    │      │   卸载测试应用   │      │ 更新数据库状态  │
│ (VPN/测单工具)   │─────▶│  (remove_app)   │─────▶│  status=2成功  │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

### 3.2 异常处理流程

```
                        ┌─────────────────────────┐
                        │      测试执行过程        │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │      发生异常?          │
                        └────────────┬────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │ Yes                             │ No
                    ▼                                 ▼
          ┌─────────────────┐              ┌─────────────────┐
          │  AssertionError │              │    正常完成      │
          │   (预期失败)     │              │    流程结束      │
          └────────┬────────┘              └─────────────────┘
                   │
                   ▼
          ┌─────────────────────────────────────┐
          │          解析失败类型               │
          │   error_message.split(":")[1]      │
          └────────────────┬────────────────────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     │                     │                     │
     ▼                     ▼                     ▼
┌─────────┐         ┌─────────┐         ┌─────────────┐
│ 类型12   │         │ 类型16   │         │  其他类型    │
│应用已安装│         │ 网络异常  │         │ 下载失败等   │
└────┬────┘         └────┬────┘         └──────┬──────┘
     │                   │                      │
     ▼                   ▼                      ▼
┌──────────────────────────────────────────────────────┐
│              统一处理流程                             │
├──────────────────────────────────────────────────────┤
│  1. 更新数据库状态 (status=3/4, fail_type)            │
│  2. 记录失败原因 (fail_reason)                        │
│  3. 发送钉钉失败通知 (包含截图URL)                     │
│  4. 记录错误日志 (logger.error)                       │
└──────────────────────────────────────────────────────┘
```

### 3.3 失败类型码定义

| 失败码 | 含义 | 处理策略 |
|--------|-----|---------|
| 12 | 应用已安装 | 标记status=4，跳过本次 |
| 16 | 网络异常 | 检查VPN/WiFi连接 |
| 17 | 屏幕解锁失败 | 需人工介入 |
| 18 | 没有待测单子 | 正常结束,无需处理 |
| 其他 | 下载安装失败 | 记录详细原因,重试 |

---

## 🧩 四、核心功能模块详解

### 4.1 Driver层设计 - AndroidDriver

**设计理念**：继承 `appium.webdriver.Remote`，封装业务操作方法

**核心方法**：

```python
class AndroidDriver(webdriver.Remote):
    
    def clear_cache(self, app_id: str) -> None:
        """清除应用缓存 - 避免商店缓存影响测试"""
        self.execute_script('mobile: clearApp', {'appId': app_id})
    
    def get_click_url(self, gaid: str, token: str) -> str:
        """生成广告点击URL - 核心归因追踪入口"""
        click_id = base64.b64encode(str(time.time()).encode('utf-8'))
        return f"https://ss-api.mintegral.com/api/v1/tracking/click?token={token}&gaid={gaid}&click_id={click_id}"
    
    def open_app_with_url(self, url: str) -> None:
        """通过Intent打开测单工具并传递URL"""
        self.execute_script('mobile: startActivity', {
            'action': 'android.intent.action.VIEW',
            'uri': url,
            'component': 'com.mintegral.mtgautotest/.activity.WebActivity'
        })
    
    def download_app(self) -> bool:
        """应用下载安装核心逻辑 - 状态机模式"""
        # 1. 点击Install按钮
        # 2. 监控Cancel按钮判断下载中
        # 3. 检测Uninstall按钮确认安装完成
        # 4. 超时控制(30分钟)
```

**亮点**：
- 使用 Appium Mobile Script 而非传统XPath定位，更稳定
- 下载过程采用状态机模式，避免硬编码等待时间
- 30分钟超时机制防止无限等待

### 4.2 VPN自动化 - FlyVpn

**设计难点**：需要自动切换20+国家的VPN连接

**实现方案**：

```python
class FlyVpn:
    top_geo_map = {
        "US": {"name": "United States", "city": "Portland"},
        "JP": {"name": "Japan", "city": "Osaka"},
        # ... 20+ 国家映射
    }
    
    def connect_server(self, geo: str) -> None:
        """连接指定国家VPN"""
        # 1. 检查当前连接状态
        if self._is_connected(geo):
            return  # 已连接正确国家
        
        # 2. 断开错误连接
        # 3. 进入收藏列表
        # 4. 滚动查找目标国家
        # 5. 点击连接
```

**技术要点**：
- 国家代码到全称的映射配置
- 滚动查找元素（最多5次滚动）
- 连接状态检测与自动重连

### 4.3 数据驱动 - OfferUtils

**业务逻辑**：从线上数据库拉取待测单子，进行多维度筛选

```python
class MtgNewOffer:
    def get_offer_info(self, is_amazon):
        # 1. 从数据库拉取符合条件的offer列表
        temp_offer_list = self.get_offer_list_via_db(is_amazon)
        
        # 2. 过滤当天已手动测试的单子
        remove_offer_id_list = self.check_offer_status(tokens_offer)
        
        # 3. 过滤已成功(status=2)或失败超过5次的单子
        for result in mysql_result:
            if status in [2, 4] or run_counts >= 5:
                continue
        
        # 4. 随机选择一个(避免集中测试)
        random_offer_id = random.choice(result_offer_list)
        
        return offer_info
```

**SQL查询关键点**：
```sql
-- 核心筛选条件
WHERE cp.is_testing != 1           -- 非测试中状态
  AND cp.user_activation = 2       -- 已激活
  AND cp.campaign_type != 9        -- 排除特定类型
  AND cp.received_billing_type IN (1, 11)  -- CPI/CPA计费
  AND cp.ctime > {上周时间戳}       -- 近一周创建
```

### 4.4 通知系统 - NoticeUtils

**钉钉通知实现**：

```python
class PostDingTalk:
    def success_notice(self, offer, device_info, third_url):
        """发送成功通知"""
        text = f"""
        ## 【{platform}】自动化安装完成
        - AdvOfferId: {adv_offer_id}
        - AppName: {app_name}
        - DeviceInfo: {device_info}
        - InstallTime: {now_time}
        - Country: {country}
        """
        self.post_action(title, text)
    
    def fail_notice(self, offer, device_info, third_url, fail_reason, screen_url):
        """发送失败通知(包含截图)"""
        text += f"![screenshot]({screen_url})"
```

### 4.5 ADB工具封装 - AdbUtils

```python
class AdbUtils:
    def is_installed_package(self, platform, app_id) -> bool:
        """检查应用是否已安装"""
        cmd = f'adb -s {self.udid} shell pm list packages -3 | findstr "^package:{app_id}$"'
        
    def network_is_success(self) -> bool:
        """Ping Google验证网络"""
        cmd = f"adb -s {self.udid} shell ping -c 3 www.google.com"
        # 解析丢包率
        
    def monkey_app(self, package_name):
        """Monkey压力测试"""
        cmd = f'adb -s {self.udid} shell monkey -p {package_name} --throttle 500 --pct-touch 100 -v 50'
        # 50次随机点击事件，间隔500ms
```

---

## 🎯 五、技术亮点与创新点

### 5.1 数据驱动架构

**传统方案问题**：测试数据硬编码在代码中，维护困难

**本项目方案**：
- 测试数据完全来源于线上数据库
- 支持多维度智能筛选（平台/国家/设备类型/计费类型）
- 自动记录执行状态，避免重复测试
- 智能过滤策略（跳过已成功/失败超限的单子）

### 5.2 智能环境管理

```
┌─────────────────────────────────────────────────────────┐
│                    环境自动化管理                        │
├─────────────────────────────────────────────────────────┤
│  WiFi检测 ──▶ 关闭则自动开启 ──▶ 等待连接              │
│      │                                                  │
│      ▼                                                  │
│  VPN管理 ──▶ 检测当前国家 ──▶ 不匹配则切换             │
│      │                                                  │
│      ▼                                                  │
│  网络验证 ──▶ Ping Google ──▶ 失败则报错               │
│      │                                                  │
│      ▼                                                  │
│  屏幕状态 ──▶ 锁屏检测 ──▶ 自动解锁                    │
└─────────────────────────────────────────────────────────┘
```

### 5.3 稳定性保障机制

| 机制 | 实现方式 | 效果 |
|------|---------|------|
| 元素等待 | WebDriverWait + 自定义wait_for_condition | 避免元素未加载 |
| 超时控制 | 30分钟下载超时 | 防止无限等待 |
| 重试机制 | HTTP请求3次重试 | 网络波动容错 |
| 失败截图 | get_screenshot_as_file | 问题定位 |
| 分级日志 | INFO/ERROR分文件存储 | 日志分析 |

### 5.4 Pytest Fixture依赖注入

```python
@pytest.fixture(scope="session")
def device_config():
    """会话级别 - 读取设备配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'config/devices.json')
    with open(config_path, 'r') as file:
        return json.load(file)

@pytest.fixture(scope="session", autouse=True)
def handle_setup(request, device_config):
    """会话级别 - 初始化日志、存储设备信息"""
    # 解析命令行参数
    device_key = request.config.getoption("--device")
    # 初始化日志
    logger.add(info_log_path, level="INFO", ...)
    # 存储到session供后续使用
    request.session.device_info = device_info

@pytest.fixture(scope="function")
def android_driver(request):
    """函数级别 - 每个测试用例独立Driver实例"""
    driver = AndroidDriver(command_executor=appium_server_url, options=options)
    yield driver
    driver.quit()  # 测试完成后清理
```

**设计优势**：
- 会话级别Fixture避免重复读取配置
- 函数级别Driver保证测试隔离
- yield语法实现自动资源清理

### 5.5 模块化扩展设计

**新增平台只需**：
1. 创建新的Driver类（继承基类或Remote）
2. 定义页面元素（elements.py）
3. 在conftest.py添加Fixture
4. 在runner.py添加测试函数

**示例 - Amazon继承Android**：
```python
class AmazonDriver(AndroidDriver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    # 复用父类方法，按需覆写
```

---

## 🔧 六、疑难点与解决方案

### 6.1 Google Play Store元素定位问题

**问题描述**：
- Play Store频繁更新，元素ID带有混淆（`0_resource_name_obfuscated`）
- 不同版本按钮文字可能不同（Install/Get）

**解决方案**：
```python
# 使用XPath + text属性定位，更稳定
playstore = {
    "Install": '//android.widget.Button[@resource-id="com.android.vending:id/0_resource_name_obfuscated" and @text="Install"]',
    "Cancel": '//android.widget.Button[...and @text="Cancel"]',
    "Uninstall": '//android.widget.Button[...and @text="Uninstall"]'
}
```

**进阶方案**：
- 定期使用Appium Inspector更新元素定位
- 建立元素变更监控机制

### 6.2 下载状态判断难题

**问题描述**：
- 下载进度无法直接获取
- 下载完成后Install按钮消失时机不确定

**解决方案 - 状态机判断**：
```python
def download_app(self):
    # 状态1: 点击Install
    click_install_result = _click_install_button()
    
    # 状态2: 下载中 (Cancel按钮存在)
    if _is_installing():
        while True:
            if _is_installing():
                # 仍在下载，继续等待
                sleep(3)
            else:
                # 状态3: 下载完成 (Uninstall按钮出现)
                if _is_installed():
                    return True
```

### 6.3 VPN连接稳定性问题

**问题描述**：
- VPN连接不稳定，可能自动断开
- 不同国家服务器响应速度差异大

**解决方案**：
```python
def connect_server(self, geo: str):
    # 1. 先检查当前连接状态
    if self._is_connected(geo):
        return  # 已连接正确国家，无需操作
    
    # 2. 连接后验证
    # ... 连接操作 ...
    
    # 3. 在runner.py中进行网络验证
    assert adb_utils.network_is_success(), "网络异常，需检查设备网络连接情况:16"
```

### 6.4 iOS剪贴板安全限制

**问题描述**：
- iOS真机获取剪贴板需要WDA应用在前台
- Apple安全策略限制后台读取剪贴板

**解决方案**：
```python
def get_clipboard_string(self) -> str:
    # 先切换到WDA应用前台
    self.open_app('com.mtg.qa.WebDriverAgentRunner.xctrunner')
    # 再读取剪贴板
    base64_content = self.execute_script("mobile: getClipboard")
    return base64.b64decode(base64_content).decode("utf-8")
```

### 6.5 多设备并发执行

**问题描述**：
- 如何在多台设备上并行执行测试？

**解决方案**：
```json
// devices.json 配置多设备
{
  "android-us": {
    "appium_server_url": "http://localhost:4731",
    "desired_caps": {"appium:udid": "设备1UDID"}
  },
  "android-uk": {
    "appium_server_url": "http://localhost:4732",
    "desired_caps": {"appium:udid": "设备2UDID"}
  }
}
```

```bash
# 并行启动多个Appium Server
appium -p 4731 &
appium -p 4732 &

# 并行执行测试
python main.py --device=android-us &
python main.py --device=android-uk &
```

---

## 💡 七、面试常见问题与回答

### Q1: 请介绍一下这个项目的业务背景？

**回答要点**：
> 这是一个移动广告归因测试自动化项目。在移动广告投放中，广告主需要追踪用户从点击广告到安装应用的完整链路，这个过程叫做"归因"。我们的项目就是自动化验证这个归因链路是否正确工作——从生成点击URL、跳转应用商店、下载安装应用、到验证安装成功并回调数据。项目支持Android、iOS和Amazon三大平台，每天可以自动测试100+个广告Offer，相比人工测试效率提升了5倍以上。

### Q2: 为什么选择Appium而不是其他自动化框架？

**回答要点**：
> 选择Appium主要基于以下考虑：
> 1. **跨平台支持**：Appium同时支持Android和iOS，我们只需要一套技术栈
> 2. **无需修改应用**：Appium不需要在被测应用中嵌入SDK
> 3. **协议标准化**：基于WebDriver协议，社区生态完善
> 4. **语言灵活**：支持Python等多种语言客户端
> 5. **真机支持**：我们的测试需要在真机上执行，涉及应用商店操作

### Q3: 项目中遇到过哪些技术难点？如何解决的？

**回答要点**：
> 1. **Play Store元素定位不稳定**：Google经常更新Play Store，元素ID会变化。我们采用XPath+text属性组合定位，同时建立定期更新机制。
> 2. **下载进度无法获取**：采用状态机模式，通过Cancel按钮判断下载中，Uninstall按钮判断下载完成，而非依赖进度值。
> 3. **VPN连接稳定性**：增加连接状态检测和网络验证环节，连接后Ping Google确保网络可用。
> 4. **iOS剪贴板限制**：发现需要WDA应用在前台才能读取剪贴板，通过先切换应用再读取解决。

### Q4: 如何保证测试的稳定性？

**回答要点**：
> 我们从多个层面保障稳定性：
> 1. **元素等待机制**：使用WebDriverWait显式等待，避免元素未加载
> 2. **超时控制**：下载设置30分钟超时，HTTP请求3次重试
> 3. **环境自检**：测试前检查WiFi、VPN、屏幕状态，自动修复
> 4. **失败截图**：关键步骤失败时自动截图，便于问题定位
> 5. **智能过滤**：跳过已测试成功或失败超过5次的单子
> 6. **分级日志**：INFO和ERROR分开记录，便于分析

### Q5: 项目的架构设计有什么特点？

**回答要点**：
> 1. **分层设计**：Driver层封装设备操作，Utils层提供工具函数，Model层定义数据模型，Element层管理页面元素
> 2. **数据驱动**：测试数据从数据库动态获取，无需硬编码
> 3. **依赖注入**：使用Pytest Fixture管理Driver生命周期
> 4. **配置化**：设备信息、数据库配置等通过配置文件管理
> 5. **可扩展**：新增平台只需继承Driver基类，添加Element定义

### Q6: 如何实现多国家VPN切换？

**回答要点**：
> VPN切换是项目的一个特色功能。我们集成了FlyVPN应用，维护了一个国家代码到VPN服务器的映射表（如US->Portland, JP->Osaka）。测试前根据Offer的目标国家自动切换VPN：先检查当前连接状态，如果连接的是错误国家则断开，然后进入收藏列表选择目标国家连接。连接后通过Ping Google验证网络是否可用。

### Q7: 你在这个项目中的角色和贡献？

**回答示例**（根据实际情况调整）：
> 我是这个项目的核心开发者，主要负责：
> 1. 整体架构设计和技术选型
> 2. Android Driver层的开发和优化
> 3. 数据驱动机制的实现
> 4. 钉钉通知系统的开发
> 5. 测试稳定性优化
> 
> 项目上线后，将测试效率从每天15个提升到100+个，人力成本降低80%。

---

## 📚 八、技术延伸学习

### 8.1 Appium相关

- Appium Desktop / Appium Inspector 元素定位工具
- UiAutomator2 vs XCUITest 驱动差异
- Appium 2.0 Plugin机制

### 8.2 Pytest相关

- Fixture作用域（function/class/module/session）
- conftest.py的作用和加载顺序
- pytest-html / Allure 报告生成

### 8.3 移动测试相关

- ADB命令大全
- Android Monkey/UIAutomator
- iOS libimobiledevice工具链

### 8.4 可能的优化方向

1. **Allure报告集成**：可视化测试报告
2. **Jenkins CI/CD**：定时任务自动触发
3. **Docker容器化**：Appium Server容器化部署
4. **多线程并发**：使用pytest-xdist并行执行
5. **智能失败分析**：基于失败原因自动分类

---

## 📝 九、项目代码核心片段速记

### 9.1 测试入口（main.py）

```python
if __name__ == '__main__':
    pytest.main(['runner.py', '-s', '--device=android-us'])
```

### 9.2 Fixture定义（conftest.py）

```python
@pytest.fixture(scope="function")
def android_driver(request):
    options = UiAutomator2Options()
    driver = AndroidDriver(command_executor=appium_server_url, 
                          options=options.load_capabilities(desired_caps))
    yield driver
    driver.quit()
```

### 9.3 测试用例（runner.py）

```python
def test_android(android_driver):
    # 1. 获取单子
    offer_info = MtgNewOffer(platform='android', country='US').data
    
    # 2. 环境检查
    adb_utils = AdbUtils()
    assert adb_utils.is_lock_screen()
    
    # 3. 网络配置
    flyvpn.connect_server("US")
    
    # 4. 模拟点击
    click_url = android_driver.get_click_url(gaid, token)
    android_driver.open_app_with_url(url=click_url)
    
    # 5. 下载安装
    android_driver.download_app()
    
    # 6. 通知回调
    notice_utils.back_test_msg("success", offer_info)
```

### 9.4 下载状态判断

```python
def download_app(self):
    _click_install_button()  # 点击Install
    
    while _is_installing():  # Cancel按钮存在=下载中
        if time.time() - start_time > 30 * 60:
            raise Exception("超时")
        sleep(3)
    
    if _is_installed():  # Uninstall按钮存在=安装完成
        return True
```

---

**最后更新**：2024年12月  
**文档用途**：求职面试准备  
**建议**：结合实际项目经验，灵活调整回答内容

