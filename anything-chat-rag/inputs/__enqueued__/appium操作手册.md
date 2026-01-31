# Appium 自动化测试完全手册

> 本手册基于 Appium 2.x + Python 客户端，涵盖 Android 和 iOS 平台的常用功能、难点解析和面试问答

---

## 📚 目录

1. [Appium 基础概念](#一appium-基础概念)
2. [环境配置与Driver初始化](#二环境配置与driver初始化)
3. [元素定位策略](#三元素定位策略)
4. [元素操作方法](#四元素操作方法)
5. [应用管理操作](#五应用管理操作)
6. [设备控制操作](#六设备控制操作)
7. [等待机制](#七等待机制)
8. [手势操作](#八手势操作)
9. [屏幕截图与录制](#九屏幕截图与录制)
10. [特殊场景处理](#十特殊场景处理)
11. [Android vs iOS 差异对比](#十一android-vs-ios-差异对比)
12. [常见问题与解决方案](#十二常见问题与解决方案)
13. [面试高频问题](#十三面试高频问题)

---

## 一、Appium 基础概念

### 1.1 什么是 Appium？

Appium 是一个开源的移动端自动化测试框架，基于 **WebDriver 协议**，支持：
- **原生应用** (Native App)
- **混合应用** (Hybrid App)  
- **移动网页** (Mobile Web)

### 1.2 Appium 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Test Script (Python/Java/JS)              │
│                              ↓                                   │
│                     Appium Python Client                         │
│                    (appium-python-client)                        │
│                              ↓                                   │
│                  HTTP Request (JSON Wire Protocol)               │
│                              ↓                                   │
├─────────────────────────────────────────────────────────────────┤
│                        Appium Server                             │
│                              ↓                                   │
├────────────────────────┬────────────────────────────────────────┤
│      Android           │              iOS                        │
│         ↓              │               ↓                         │
│   UiAutomator2         │          XCUITest                       │
│   (Google官方)         │        (Apple官方)                      │
│         ↓              │               ↓                         │
│   Android Device       │          iOS Device                     │
└────────────────────────┴────────────────────────────────────────┘
```

### 1.3 核心组件

| 组件 | Android | iOS | 说明 |
|------|---------|-----|------|
| **自动化引擎** | UiAutomator2 | XCUITest | 官方自动化框架 |
| **驱动** | appium-uiautomator2-driver | appium-xcuitest-driver | Appium驱动 |
| **设备连接** | ADB | libimobiledevice | 设备通信工具 |
| **元素查看器** | Appium Inspector / uiautomatorviewer | Appium Inspector | 元素定位工具 |

### 1.4 Appium 2.x vs 1.x 主要变化

| 特性 | Appium 1.x | Appium 2.x |
|------|-----------|-----------|
| 驱动管理 | 内置所有驱动 | 需手动安装 `appium driver install` |
| 插件系统 | 无 | 支持插件扩展 |
| Capabilities | `desiredCapabilities` | `capabilities` + `appium:` 前缀 |
| 安装方式 | `npm install -g appium` | `npm install -g appium@next` |

---

## 二、环境配置与Driver初始化

### 2.1 Appium 2.x 安装

```bash
# 安装 Appium Server
npm install -g appium

# 安装驱动
appium driver install uiautomator2    # Android
appium driver install xcuitest        # iOS

# 启动服务
appium --port 4723 --log-level info
```

### 2.2 Python 客户端安装

```bash
pip install appium-python-client~=4.0.1
pip install selenium~=4.23.1
```

### 2.3 Desired Capabilities 配置

#### Android 配置

```python
from appium.options.android import UiAutomator2Options

# 方式1：直接设置属性
options = UiAutomator2Options()
options.platform_name = "Android"
options.platform_version = "10.0"
options.device_name = "Pixel 4"
options.udid = "9889db454149334c46"
options.automation_name = "UiAutomator2"
options.app = "/path/to/app.apk"  # 可选
options.no_reset = True
options.new_command_timeout = 1800

# 方式2：字典方式加载
desired_caps = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:udid": "9889db454149334c46",
    "platformVersion": "10.0",
    "appium:noReset": True,
    "locale": "US",
    "language": "en",
    "newCommandTimeout": 1800
}
options = UiAutomator2Options().load_capabilities(desired_caps)
```

#### iOS 配置

```python
from appium.options.ios import XCUITestOptions

options = XCUITestOptions()
options.platform_name = "iOS"
options.platform_version = "16.7"
options.device_name = "iPhone 14"
options.udid = "66100823447740ba1a2593e7092f8ab18d583483"
options.automation_name = "XCUITest"
options.bundle_id = "com.apple.Preferences"  # 启动的应用
options.wda_local_port = 8100
options.web_driver_agent_url = "http://localhost:18100"
options.auto_accept_alerts = True  # 自动接受系统弹窗

# iOS 特有配置
desired_caps = {
    "platformName": "iOS",
    "appium:automationName": "XCUITest",
    "platformVersion": "16.7",
    "appium:udid": "真机UDID",
    "appium:app": "com.apple.Preferences",
    "appium:webDriverAgentUrl": "http://localhost:18100",
    "appium:autoAcceptAlerts": True,
    # 自定义弹窗处理选择器
    "appium:settings[acceptAlertButtonSelector]": "**/XCUIElementTypeAny[`label=='Allow' OR label=='Open'`]"
}
```

### 2.4 Driver 初始化

```python
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

# Android Driver
android_options = UiAutomator2Options().load_capabilities(android_caps)
android_driver = webdriver.Remote(
    command_executor="http://127.0.0.1:4723",
    options=android_options
)

# iOS Driver
ios_options = XCUITestOptions().load_capabilities(ios_caps)
ios_driver = webdriver.Remote(
    command_executor="http://127.0.0.1:4729",
    options=ios_options
)

# 使用完毕后关闭
driver.quit()
```

### 2.5 常用 Capabilities 参数详解

| 参数 | 类型 | 平台 | 说明 |
|------|------|------|------|
| `platformName` | string | 通用 | Android / iOS |
| `platformVersion` | string | 通用 | 系统版本号 |
| `deviceName` | string | 通用 | 设备名称 |
| `udid` | string | 通用 | 设备唯一标识符 |
| `automationName` | string | 通用 | UiAutomator2 / XCUITest |
| `app` | string | 通用 | APK/IPA路径或URL |
| `appPackage` | string | Android | 应用包名 |
| `appActivity` | string | Android | 启动Activity |
| `bundleId` | string | iOS | Bundle ID |
| `noReset` | boolean | 通用 | 不重置应用状态 |
| `fullReset` | boolean | 通用 | 完全重置(卸载重装) |
| `newCommandTimeout` | int | 通用 | 命令超时时间(秒) |
| `autoAcceptAlerts` | boolean | iOS | 自动接受系统弹窗 |
| `autoGrantPermissions` | boolean | Android | 自动授权权限 |
| `skipDeviceInitialization` | boolean | 通用 | 跳过设备初始化 |

---

## 三、元素定位策略

### 3.1 通用定位方式

```python
from appium.webdriver.common.appiumby import AppiumBy

# 1. ID 定位 (resource-id / name)
element = driver.find_element(AppiumBy.ID, "com.example:id/button")

# 2. XPATH 定位
element = driver.find_element(AppiumBy.XPATH, "//android.widget.Button[@text='Login']")

# 3. CLASS_NAME 定位
element = driver.find_element(AppiumBy.CLASS_NAME, "android.widget.Button")

# 4. ACCESSIBILITY_ID 定位 (content-desc / accessibilityIdentifier)
element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "login_button")

# 5. NAME 定位 (iOS特有)
element = driver.find_element(AppiumBy.NAME, "Login")
```

### 3.2 Android 特有定位方式

```python
# 1. UiAutomator 定位 (功能强大)
element = driver.find_element(
    AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().text("Login")'
)

# UiAutomator 常用方法
'new UiSelector().text("精确文本")'
'new UiSelector().textContains("包含文本")'
'new UiSelector().textStartsWith("开头文本")'
'new UiSelector().textMatches("正则.*")'
'new UiSelector().resourceId("com.example:id/btn")'
'new UiSelector().className("android.widget.Button")'
'new UiSelector().description("content-desc值")'
'new UiSelector().clickable(true)'
'new UiSelector().enabled(true)'
'new UiSelector().scrollable(true)'
'new UiSelector().instance(0)'  # 第N个匹配元素

# 链式调用
'new UiSelector().className("android.widget.Button").text("Login")'

# 父子关系
'new UiSelector().className("android.widget.LinearLayout").childSelector(new UiSelector().text("Login"))'

# 2. UiScrollable 滚动定位
element = driver.find_element(
    AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().text("目标文本"))'
)
```

### 3.3 iOS 特有定位方式

```python
# 1. iOS Predicate String (推荐)
element = driver.find_element(
    AppiumBy.IOS_PREDICATE,
    "type == 'XCUIElementTypeButton' AND label == 'Login'"
)

# Predicate 常用表达式
"label == '精确文本'"
"label CONTAINS '包含'"
"label BEGINSWITH '开头'"
"label ENDSWITH '结尾'"
"label MATCHES '正则.*'"
"name == 'accessibility identifier'"
"type == 'XCUIElementTypeButton'"
"enabled == true"
"visible == true"
"value CONTAINS '值'"

# 组合条件
"type == 'XCUIElementTypeButton' AND label CONTAINS 'Login'"
"label == 'A' OR label == 'B'"
"NOT (label == 'Cancel')"

# 2. iOS Class Chain (XPath替代品,性能更好)
element = driver.find_element(
    AppiumBy.IOS_CLASS_CHAIN,
    "**/XCUIElementTypeButton[`label == 'Login'`]"
)

# Class Chain 语法
"**/XCUIElementTypeCell"  # 所有Cell
"**/XCUIElementTypeCell[3]"  # 第3个Cell (1-based)
"**/XCUIElementTypeCell[`name == 'test'`]"  # 带条件
"**/XCUIElementTypeCell/XCUIElementTypeButton"  # 直接子元素
"**/XCUIElementTypeCell/**/XCUIElementTypeButton"  # 任意后代
"**/XCUIElementTypeCell[-1]"  # 最后一个
"**/XCUIElementTypeCell[`visible == 1`][1]"  # 可见的第一个
```

### 3.4 定位策略对比

| 定位方式 | Android | iOS | 性能 | 推荐度 |
|----------|---------|-----|------|--------|
| ID | ✅ resource-id | ✅ name | ⭐⭐⭐⭐⭐ | 首选 |
| ACCESSIBILITY_ID | ✅ content-desc | ✅ accessibilityIdentifier | ⭐⭐⭐⭐⭐ | 首选 |
| XPATH | ✅ | ✅ | ⭐⭐ | 备选 |
| CLASS_NAME | ✅ | ✅ | ⭐⭐⭐ | 简单场景 |
| ANDROID_UIAUTOMATOR | ✅ | ❌ | ⭐⭐⭐⭐ | Android推荐 |
| IOS_PREDICATE | ❌ | ✅ | ⭐⭐⭐⭐ | iOS推荐 |
| IOS_CLASS_CHAIN | ❌ | ✅ | ⭐⭐⭐⭐ | iOS推荐 |

### 3.5 元素定位最佳实践

```python
# ✅ 推荐：使用 accessibility_id (跨平台一致)
element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "login_button")

# ✅ 推荐：Android 使用 UiAutomator
element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 
    'new UiSelector().resourceId("com.app:id/btn").text("Login")')

# ✅ 推荐：iOS 使用 Predicate
element = driver.find_element(AppiumBy.IOS_PREDICATE, 
    "type == 'XCUIElementTypeButton' AND label == 'Login'")

# ❌ 避免：过长的 XPath
element = driver.find_element(AppiumBy.XPATH, 
    "//android.widget.LinearLayout/android.widget.FrameLayout[2]/android.widget.Button")

# ✅ 替代：使用相对定位或组合条件
element = driver.find_element(AppiumBy.XPATH, 
    "//android.widget.Button[@text='Login']")
```

### 3.6 查找多个元素

```python
# 返回元素列表
elements = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.Button")

for el in elements:
    print(el.text)
    
# 获取第N个元素
first_button = elements[0]
last_button = elements[-1]
```

---

## 四、元素操作方法

### 4.1 基本操作

```python
# 点击
element.click()

# 输入文本
element.send_keys("Hello World")

# 清除文本
element.clear()

# 获取文本内容
text = element.text

# 获取属性值
value = element.get_attribute("text")          # Android
value = element.get_attribute("value")         # iOS
value = element.get_attribute("name")          # accessibility id
value = element.get_attribute("enabled")       # 是否可用
value = element.get_attribute("displayed")     # 是否显示
value = element.get_attribute("selected")      # 是否选中
value = element.get_attribute("checked")       # Android 复选框
value = element.get_attribute("visible")       # iOS 可见性

# 获取元素位置和大小
location = element.location      # {'x': 100, 'y': 200}
size = element.size              # {'width': 50, 'height': 30}
rect = element.rect              # {'x': 100, 'y': 200, 'width': 50, 'height': 30}

# 判断元素状态
element.is_displayed()   # 是否可见
element.is_enabled()     # 是否可用
element.is_selected()    # 是否被选中
```

### 4.2 Android 特有属性

```python
# Android 元素属性
element.get_attribute("resource-id")      # 资源ID
element.get_attribute("content-desc")     # 内容描述
element.get_attribute("class")            # 类名
element.get_attribute("package")          # 包名
element.get_attribute("checkable")        # 是否可勾选
element.get_attribute("clickable")        # 是否可点击
element.get_attribute("focusable")        # 是否可获取焦点
element.get_attribute("scrollable")       # 是否可滚动
element.get_attribute("long-clickable")   # 是否可长按
element.get_attribute("bounds")           # 边界坐标 [0,0][1080,1920]
```

### 4.3 iOS 特有属性

```python
# iOS 元素属性
element.get_attribute("label")            # 标签文本
element.get_attribute("value")            # 值
element.get_attribute("name")             # accessibility identifier
element.get_attribute("type")             # 元素类型
element.get_attribute("visible")          # 是否可见
element.get_attribute("accessible")       # 是否可访问
element.get_attribute("enabled")          # 是否可用
element.get_attribute("rect")             # 位置和大小
```

### 4.4 隐藏键盘

```python
# Android
driver.hide_keyboard()

# iOS (多种方式)
driver.hide_keyboard()
driver.hide_keyboard(strategy="pressKey", key="Done")
driver.hide_keyboard(strategy="tapOutside")

# 通过点击空白区域隐藏
driver.tap([(100, 100)])
```

---

## 五、应用管理操作

### 5.1 应用生命周期管理

```python
# ==================== 通用方法 ====================

# 安装应用
driver.install_app("/path/to/app.apk")               # Android
driver.install_app("/path/to/app.ipa")               # iOS

# 卸载应用
driver.remove_app("com.example.app")                 # Android 包名
driver.remove_app("com.example.app.bundleid")        # iOS Bundle ID

# 检查应用是否已安装
is_installed = driver.is_app_installed("com.example.app")

# 启动应用 (应用必须已安装)
driver.activate_app("com.example.app")

# 关闭应用 (后台结束)
driver.terminate_app("com.example.app")

# 将应用置于后台
driver.background_app(5)  # 后台5秒后恢复前台
driver.background_app(-1) # 永久后台

# 重置应用 (清除数据)
driver.reset()
```

### 5.2 查询应用状态

```python
# 查询应用状态
state = driver.query_app_state("com.example.app")

# 状态码含义
# 0: 未安装
# 1: 未运行
# 2: 后台运行(挂起)
# 3: 后台运行
# 4: 前台运行

# 使用 Mobile Script 方式
state = driver.execute_script("mobile: queryAppState", {"appId": "com.example.app"})
```

### 5.3 Android 应用管理

```python
# 清除应用数据和缓存 (不卸载)
driver.execute_script("mobile: clearApp", {"appId": "com.example.app"})

# 启动指定 Activity
driver.execute_script("mobile: startActivity", {
    "component": "com.example.app/.MainActivity",
    "action": "android.intent.action.VIEW",
    "uri": "https://example.com"
})

# 获取当前 Activity
current_activity = driver.current_activity

# 获取当前包名
current_package = driver.current_package

# 等待 Activity
driver.wait_activity(".MainActivity", timeout=10)

# 启动 Activity (传统方式)
driver.start_activity("com.example.app", ".MainActivity")
```

### 5.4 iOS 应用管理

```python
# 启动应用 (带参数)
driver.execute_script("mobile: launchApp", {
    "bundleId": "com.example.app",
    "arguments": ["--arg1", "--arg2"],
    "environment": {"KEY": "VALUE"}
})

# 关闭应用
result = driver.execute_script("mobile: terminateApp", {"bundleId": "com.example.app"})

# 激活应用
driver.execute_script("mobile: activateApp", {"bundleId": "com.example.app"})

# 获取当前活动应用信息
app_info = driver.execute_script("mobile: activeAppInfo")
# 返回: {'bundleId': 'com.example.app', 'name': 'App Name', 'pid': 1234}
```

### 5.5 应用操作实战代码

```python
# 项目实例：打开测单工具并传入URL (Android)
def open_app_with_url(driver, url):
    encoded_url = url.replace('&', '\&')
    driver.execute_script(
        'mobile: startActivity',
        {
            'action': 'android.intent.action.VIEW',
            'uri': encoded_url,
            'component': 'com.mintegral.mtgautotest/.activity.WebActivity',
        },
    )

# 项目实例：打开应用 (iOS)
def open_app(driver, bundle_id, arguments=""):
    driver.execute_script("mobile: launchApp", {
        "bundleId": bundle_id, 
        "arguments": arguments
    })
```

---

## 六、设备控制操作

### 6.1 按键操作

```python
# ==================== Android 按键 ====================
from appium.webdriver.extensions.android.nativekey import AndroidKey

# 方式1：使用 press_keycode
driver.press_keycode(AndroidKey.HOME)        # Home键
driver.press_keycode(AndroidKey.BACK)        # 返回键
driver.press_keycode(AndroidKey.MENU)        # 菜单键
driver.press_keycode(AndroidKey.POWER)       # 电源键
driver.press_keycode(AndroidKey.ENTER)       # 回车键
driver.press_keycode(AndroidKey.DEL)         # 删除键
driver.press_keycode(AndroidKey.VOLUME_UP)   # 音量+
driver.press_keycode(AndroidKey.VOLUME_DOWN) # 音量-

# 常用键码值
# 3 = HOME
# 4 = BACK
# 24 = VOLUME_UP
# 25 = VOLUME_DOWN
# 26 = POWER
# 66 = ENTER
# 67 = DEL
# 82 = MENU

driver.press_keycode(3)   # Home键
driver.press_keycode(4)   # 返回键
driver.press_keycode(82)  # 解锁屏幕

# 长按键
driver.long_press_keycode(AndroidKey.POWER)

# ==================== iOS 没有直接的按键操作 ====================
# iOS 需要通过其他方式实现

# Home 键 (iOS 真机需要硬件操作)
# 可以通过 XCTest 的私有方法实现，但不稳定
```

### 6.2 网络控制

```python
# ==================== Android 网络控制 ====================
from appium.webdriver.connectiontype import ConnectionType

# 获取当前网络状态
network_status = driver.network_connection
# 返回值: 0=无网络, 1=飞行模式, 2=WiFi, 4=数据网络, 6=全部开启

# 设置网络状态
driver.set_network_connection(ConnectionType.WIFI_ONLY)      # 仅WiFi
driver.set_network_connection(ConnectionType.DATA_ONLY)      # 仅数据
driver.set_network_connection(ConnectionType.ALL_NETWORK_ON) # 全部开启
driver.set_network_connection(ConnectionType.AIRPLANE_MODE)  # 飞行模式
driver.set_network_connection(ConnectionType.NO_CONNECTION)  # 关闭所有

# ==================== iOS 网络控制 ====================
# iOS 不支持直接控制网络，需要通过系统设置应用操作
# 或使用 ADB 类似的工具 (如 libimobiledevice)
```

### 6.3 剪贴板操作

```python
# ==================== Android 剪贴板 ====================
# 设置剪贴板内容
driver.set_clipboard_text("Hello World")

# 获取剪贴板内容
text = driver.get_clipboard_text()

# ==================== iOS 剪贴板 (有限制) ====================
import base64

# 设置剪贴板
driver.execute_script("mobile: setClipboard", {
    "content": base64.b64encode(b"Hello World").decode("utf-8"),
    "contentType": "plaintext"
})

# 获取剪贴板 (iOS真机限制：WDA必须在前台)
def get_clipboard_ios(driver):
    # 先切换到WDA应用前台
    driver.activate_app('com.facebook.WebDriverAgentRunner.xctrunner')
    # 再读取剪贴板
    base64_content = driver.execute_script("mobile: getClipboard")
    return base64.b64decode(base64_content).decode("utf-8")
```

### 6.4 屏幕方向

```python
# 获取当前屏幕方向
orientation = driver.orientation  # 'PORTRAIT' 或 'LANDSCAPE'

# 设置屏幕方向
driver.orientation = 'LANDSCAPE'  # 横屏
driver.orientation = 'PORTRAIT'   # 竖屏
```

### 6.5 屏幕锁定/解锁

```python
# ==================== Android ====================
# 检查是否锁屏
is_locked = driver.is_locked()

# 解锁屏幕
driver.unlock()

# 锁定屏幕
driver.lock()
driver.lock(5)  # 锁定5秒后自动解锁

# ==================== iOS ====================
# 检查是否锁屏
is_locked = driver.is_locked()

# 解锁屏幕 (iOS 真机可能需要输入密码)
driver.unlock()

# 锁定屏幕
driver.lock()
```

### 6.6 设备信息获取

```python
# 获取设备时间
device_time = driver.device_time

# 获取屏幕尺寸
window_size = driver.get_window_size()
# 返回: {'width': 1080, 'height': 1920}

# Android 专属
# 通过 ADB 获取更多信息
# adb shell getprop ro.product.model  # 设备型号
# adb shell getprop ro.build.version.release  # 系统版本
```

### 6.7 文件操作

```python
# ==================== Android 文件操作 ====================
import base64

# 推送文件到设备
with open("local_file.txt", "rb") as f:
    data = base64.b64encode(f.read()).decode("utf-8")
driver.push_file("/sdcard/Download/remote_file.txt", data)

# 从设备拉取文件
file_data = driver.pull_file("/sdcard/Download/remote_file.txt")
with open("local_copy.txt", "wb") as f:
    f.write(base64.b64decode(file_data))

# 拉取整个文件夹
folder_data = driver.pull_folder("/sdcard/Download/")

# ==================== iOS 文件操作 ====================
# iOS 文件操作受沙盒限制，只能访问应用内部文件

# 推送文件到应用沙盒
driver.push_file("@com.example.app/Documents/file.txt", data)

# 从应用沙盒拉取文件
file_data = driver.pull_file("@com.example.app/Documents/file.txt")
```

---

## 七、等待机制

### 7.1 隐式等待

```python
# 全局等待，对所有元素查找生效
driver.implicitly_wait(10)  # 最多等待10秒
```

### 7.2 显式等待

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy

# 基本用法
wait = WebDriverWait(driver, 10)  # 最多等待10秒

# 等待元素出现
element = wait.until(
    EC.presence_of_element_located((AppiumBy.ID, "com.example:id/button"))
)

# 等待元素可见
element = wait.until(
    EC.visibility_of_element_located((AppiumBy.ID, "com.example:id/button"))
)

# 等待元素可点击
element = wait.until(
    EC.element_to_be_clickable((AppiumBy.ID, "com.example:id/button"))
)

# 等待文本出现
wait.until(
    EC.text_to_be_present_in_element((AppiumBy.ID, "com.example:id/text"), "Expected Text")
)

# 等待元素消失
wait.until(
    EC.invisibility_of_element_located((AppiumBy.ID, "com.example:id/loading"))
)

# 等待多个元素
elements = wait.until(
    EC.presence_of_all_elements_located((AppiumBy.CLASS_NAME, "android.widget.Button"))
)
```

### 7.3 自定义等待函数

```python
# 项目实战：通用等待函数
def wait_for_element(driver, locator, value, timeout_sec=10):
    """等待元素出现"""
    return WebDriverWait(driver, timeout_sec).until(
        EC.presence_of_element_located((locator, value))
    )

# 项目实战：条件等待函数
def wait_for_condition(method, timeout_sec=5, interval_sec=1):
    """
    等待条件成立
    method: 返回 True/False 的函数
    """
    import time
    started = time.time()
    while time.time() - started <= timeout_sec:
        result = method()
        if result:
            return result
        time.sleep(interval_sec)
    return result

# 使用示例：等待应用进入前台
wait_for_condition(
    lambda: driver.query_app_state("com.example.app") == 4,
    timeout_sec=20,
    interval_sec=2
)
```

### 7.4 等待机制最佳实践

```python
# ✅ 推荐：显式等待 + 自定义超时
def find_element_with_wait(driver, locator, value, wait_time=10):
    try:
        return WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((locator, value))
        )
    except TimeoutException:
        # 超时处理：截图 + 日志
        driver.get_screenshot_as_file(f"timeout_{value}.png")
        logger.error(f"Element not found: {value}")
        return None

# ✅ 推荐：结合业务状态判断
def wait_for_app_state(driver, package, expected_state, timeout=20):
    """等待应用达到指定状态"""
    def check_state():
        return driver.query_app_state(package) == expected_state
    
    return wait_for_condition(check_state, timeout_sec=timeout, interval_sec=2)

# ❌ 避免：硬编码 sleep
time.sleep(10)  # 不推荐

# ✅ 替代：条件等待
wait.until(EC.visibility_of_element_located((AppiumBy.ID, "element_id")))
```

---

## 八、手势操作

### 8.1 基础手势

```python
# ==================== 点击操作 ====================
# 点击元素
element.click()

# 点击坐标
driver.tap([(100, 200)])  # 单点点击
driver.tap([(100, 200), (300, 400)])  # 多点点击

# 长按
from appium.webdriver.common.touch_action import TouchAction
action = TouchAction(driver)
action.long_press(element).release().perform()
action.long_press(x=100, y=200, duration=2000).release().perform()  # 长按2秒
```

### 8.2 滑动操作

```python
# ==================== 方法1：swipe 方法 ====================
# swipe(start_x, start_y, end_x, end_y, duration)
driver.swipe(500, 1500, 500, 500, 800)  # 上滑

# 封装滑动方法
def swipe_up(driver, duration=800):
    """上滑"""
    size = driver.get_window_size()
    start_x = size['width'] // 2
    start_y = int(size['height'] * 0.8)
    end_y = int(size['height'] * 0.2)
    driver.swipe(start_x, start_y, start_x, end_y, duration)

def swipe_down(driver, duration=800):
    """下滑"""
    size = driver.get_window_size()
    start_x = size['width'] // 2
    start_y = int(size['height'] * 0.2)
    end_y = int(size['height'] * 0.8)
    driver.swipe(start_x, start_y, start_x, end_y, duration)

def swipe_left(driver, duration=800):
    """左滑"""
    size = driver.get_window_size()
    start_x = int(size['width'] * 0.8)
    end_x = int(size['width'] * 0.2)
    y = size['height'] // 2
    driver.swipe(start_x, y, end_x, y, duration)

def swipe_right(driver, duration=800):
    """右滑"""
    size = driver.get_window_size()
    start_x = int(size['width'] * 0.2)
    end_x = int(size['width'] * 0.8)
    y = size['height'] // 2
    driver.swipe(start_x, y, end_x, y, duration)

# ==================== 方法2：flick 快速滑动 ====================
# flick(start_x, start_y, end_x, end_y)
driver.flick(500, 1500, 500, 500)  # 快速上滑
```

### 8.3 滚动操作

```python
# ==================== Android 滚动 ====================
# 使用 UiScrollable
driver.find_element(
    AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
    '.scrollIntoView(new UiSelector().text("目标文本"))'
)

# Mobile Script 方式
driver.execute_script("mobile: scroll", {
    "direction": "down",  # up, down, left, right
    "strategy": "accessibility id",
    "selector": "element_id"
})

# ==================== iOS 滚动 ====================
# 滚动到可见
driver.execute_script("mobile: scroll", {
    "direction": "down"
})

# 滚动到元素
driver.execute_script("mobile: scrollToElement", {
    "element": element.id
})

# 使用 Predicate 滚动查找
driver.execute_script("mobile: scroll", {
    "direction": "down",
    "predicateString": "label == '目标文本'"
})
```

### 8.4 拖拽操作

```python
# ==================== 拖拽元素 ====================
from_element = driver.find_element(AppiumBy.ID, "source")
to_element = driver.find_element(AppiumBy.ID, "target")

# 方法1：drag_and_drop
driver.drag_and_drop(from_element, to_element)

# 方法2：TouchAction
action = TouchAction(driver)
action.long_press(from_element).move_to(to_element).release().perform()

# 方法3：坐标拖拽
action.long_press(x=100, y=100).move_to(x=300, y=300).release().perform()
```

### 8.5 缩放操作

```python
# ==================== 双指缩放 ====================
from appium.webdriver.common.multi_action import MultiAction
from appium.webdriver.common.touch_action import TouchAction

# 放大
def zoom_in(driver, element):
    action1 = TouchAction(driver)
    action2 = TouchAction(driver)
    
    center = element.location
    width = element.size['width']
    height = element.size['height']
    
    action1.press(x=center['x'], y=center['y']).wait(200)\
           .move_to(x=center['x']-width//2, y=center['y']).release()
    action2.press(x=center['x'], y=center['y']).wait(200)\
           .move_to(x=center['x']+width//2, y=center['y']).release()
    
    multi = MultiAction(driver)
    multi.add(action1, action2)
    multi.perform()

# 缩小 (反向移动)
def zoom_out(driver, element):
    # 从边缘向中心移动
    pass
```

### 8.6 W3C Actions (Appium 2.x 推荐)

```python
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

# 创建触摸输入
finger = PointerInput(interaction.POINTER_TOUCH, "finger")

# 点击操作
actions = ActionChains(driver)
actions.w3c_actions = ActionBuilder(driver, mouse=finger)
actions.w3c_actions.pointer_action.move_to_location(100, 200)
actions.w3c_actions.pointer_action.click()
actions.perform()

# 滑动操作
actions = ActionChains(driver)
actions.w3c_actions = ActionBuilder(driver, mouse=finger)
actions.w3c_actions.pointer_action.move_to_location(500, 1500)
actions.w3c_actions.pointer_action.pointer_down()
actions.w3c_actions.pointer_action.move_to_location(500, 500)
actions.w3c_actions.pointer_action.pointer_up()
actions.perform()

# 长按操作
actions = ActionChains(driver)
actions.w3c_actions = ActionBuilder(driver, mouse=finger)
actions.w3c_actions.pointer_action.move_to_location(100, 200)
actions.w3c_actions.pointer_action.pointer_down()
actions.w3c_actions.pointer_action.pause(2)  # 按住2秒
actions.w3c_actions.pointer_action.pointer_up()
actions.perform()
```

---

## 九、屏幕截图与录制

### 9.1 截图

```python
import os
import time

# ==================== 基本截图 ====================
# 保存到文件
driver.get_screenshot_as_file("/path/to/screenshot.png")
driver.save_screenshot("/path/to/screenshot.png")

# 获取 Base64 编码
screenshot_base64 = driver.get_screenshot_as_base64()

# 获取二进制数据
screenshot_bytes = driver.get_screenshot_as_png()

# ==================== 封装截图方法 ====================
def take_screenshot(driver, name, save_dir="./screenshots"):
    """截图并保存"""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    file_path = os.path.join(save_dir, f"{timestamp}_{name}.png")
    driver.get_screenshot_as_file(file_path)
    return file_path

# ==================== 元素截图 ====================
element = driver.find_element(AppiumBy.ID, "element_id")
element.screenshot("/path/to/element.png")
```

### 9.2 屏幕录制

```python
# ==================== Android 录屏 ====================
# 开始录制
driver.start_recording_screen(
    videoType="mp4",           # 视频格式
    videoQuality="medium",      # 质量: low, medium, high
    timeLimit=180,             # 最长180秒
    bitRate=4000000,           # 比特率
    videoSize="1280x720"       # 分辨率
)

# 执行测试操作...

# 停止录制并获取视频
video_base64 = driver.stop_recording_screen()

# 保存视频文件
import base64
with open("recording.mp4", "wb") as f:
    f.write(base64.b64decode(video_base64))

# ==================== iOS 录屏 ====================
# 开始录制
driver.start_recording_screen(
    videoType="mpeg4",         # iOS 使用 mpeg4
    videoQuality="medium",
    timeLimit=180,
    videoFps=30                # 帧率
)

# 停止录制
video_base64 = driver.stop_recording_screen()
```

### 9.3 页面源码获取

```python
# 获取当前页面的 XML/JSON 源码
page_source = driver.page_source

# 保存页面源码
with open("page_source.xml", "w", encoding="utf-8") as f:
    f.write(page_source)

# 用于调试元素定位问题
print(page_source)
```

---

## 十、特殊场景处理

### 10.1 系统弹窗处理

```python
# ==================== Android 权限弹窗 ====================
# 方法1：自动授权 (Capabilities 配置)
desired_caps["autoGrantPermissions"] = True

# 方法2：手动点击
try:
    allow_button = driver.find_element(AppiumBy.ID, "com.android.permissioncontroller:id/permission_allow_button")
    allow_button.click()
except:
    pass

# 方法3：UiAutomator 定位
driver.find_element(
    AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().text("Allow")'
).click()

# ==================== iOS 系统弹窗 ====================
# 方法1：自动接受 (Capabilities 配置)
desired_caps["autoAcceptAlerts"] = True

# 方法2：自定义弹窗选择器
desired_caps["settings[acceptAlertButtonSelector]"] = \
    "**/XCUIElementTypeAny[`label=='Allow' OR label=='Open' OR label=='Continue'`]"

# 方法3：手动处理
try:
    driver.switch_to.alert.accept()  # 接受弹窗
except:
    pass

try:
    driver.switch_to.alert.dismiss()  # 拒绝弹窗
except:
    pass

# 方法4：直接查找弹窗按钮
try:
    allow_btn = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Allow")
    allow_btn.click()
except:
    pass
```

### 10.2 WebView 处理

```python
# ==================== 切换上下文 ====================
# 获取所有上下文
contexts = driver.contexts
# 返回: ['NATIVE_APP', 'WEBVIEW_com.example.app']

# 切换到 WebView
driver.switch_to.context('WEBVIEW_com.example.app')

# 在 WebView 中操作 (使用 Web 元素定位)
element = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
element.send_keys("test")

# 切换回原生视图
driver.switch_to.context('NATIVE_APP')

# ==================== Chrome DevTools ====================
# Android 需要开启 Chrome 调试
desired_caps["chromeOptions"] = {"w3c": False}

# 获取 window handles
handles = driver.window_handles
driver.switch_to.window(handles[1])
```

### 10.3 Toast 消息获取 (Android)

```python
# Toast 是临时显示的消息，需要快速捕获
# 使用 UiAutomator 定位
try:
    toast = driver.find_element(
        AppiumBy.XPATH,
        "//android.widget.Toast"
    )
    toast_text = toast.text
except:
    toast_text = None

# 或者使用 PageSource 搜索
page_source = driver.page_source
if "Toast消息内容" in page_source:
    print("Toast appeared!")
```

### 10.4 Picker/日期选择器

```python
# ==================== Android ====================
# 日期选择器通常需要滑动操作
# 使用 UiScrollable 滚动到目标值

# ==================== iOS Picker ====================
# iOS 使用 wheel 定位
wheels = driver.find_elements(AppiumBy.CLASS_NAME, "XCUIElementTypePickerWheel")

# 设置值
wheels[0].send_keys("2024")   # 年
wheels[1].send_keys("12")     # 月
wheels[2].send_keys("25")     # 日

# 或使用滑动
driver.execute_script("mobile: selectPickerWheelValue", {
    "element": wheels[0].id,
    "order": "next",  # next 或 previous
    "offset": 0.15    # 偏移量
})
```

### 10.5 下拉刷新

```python
def pull_to_refresh(driver):
    """下拉刷新"""
    size = driver.get_window_size()
    start_x = size['width'] // 2
    start_y = int(size['height'] * 0.3)
    end_y = int(size['height'] * 0.8)
    driver.swipe(start_x, start_y, start_x, end_y, 500)
```

### 10.6 验证码处理

```python
# 验证码自动化处理策略

# 1. 万能验证码 (开发环境)
# 与开发约定测试环境使用固定验证码

# 2. 绕过验证码
# 通过接口或Cookie绕过

# 3. OCR 识别
# 使用 Tesseract 或第三方服务

# 4. 白名单机制
# 测试手机号加入白名单

# 5. 手动输入
# 等待用户手动输入后继续
input("请手动输入验证码后按回车继续...")
```

---

## 十一、Android vs iOS 差异对比

### 11.1 环境配置差异

| 配置项 | Android | iOS |
|--------|---------|-----|
| **驱动** | UiAutomator2 | XCUITest |
| **设备连接** | ADB (USB调试) | libimobiledevice + WebDriverAgent |
| **应用格式** | APK | IPA |
| **应用标识** | Package Name | Bundle ID |
| **设备标识** | UDID (adb devices) | UDID (idevice_id -l) |
| **签名要求** | 开发者选项开启即可 | 需要开发者证书签名 |

### 11.2 元素定位差异

| 定位方式 | Android | iOS | 说明 |
|----------|---------|-----|------|
| ID | `resource-id` | `name` | 属性名不同 |
| ACCESSIBILITY_ID | `content-desc` | `accessibilityIdentifier` | 跨平台首选 |
| XPATH | 支持 | 支持但性能差 | iOS慎用 |
| ANDROID_UIAUTOMATOR | ✅ | ❌ | Android专用 |
| IOS_PREDICATE | ❌ | ✅ | iOS专用 |
| IOS_CLASS_CHAIN | ❌ | ✅ | iOS专用 |
| NAME | ❌ | ✅ | iOS专用 |

### 11.3 元素属性差异

| 属性 | Android | iOS |
|------|---------|-----|
| 文本 | `text` | `label` / `value` |
| ID | `resource-id` | `name` |
| 描述 | `content-desc` | `accessibilityIdentifier` |
| 类名 | `android.widget.Button` | `XCUIElementTypeButton` |
| 可见性 | `displayed` | `visible` |

### 11.4 操作差异

| 操作 | Android | iOS |
|------|---------|-----|
| **Home键** | `press_keycode(3)` | 无直接API,需硬件操作 |
| **返回键** | `press_keycode(4)` | 无返回键,滑动返回 |
| **网络控制** | `set_network_connection` | 不支持,需系统设置 |
| **剪贴板** | 直接读写 | WDA需在前台 |
| **权限弹窗** | `autoGrantPermissions` | `autoAcceptAlerts` |
| **应用启动** | `activate_app(package)` | `activate_app(bundleId)` |
| **清除数据** | `mobile: clearApp` | 需卸载重装 |

### 11.5 应用管理差异

```python
# ==================== Android ====================
# 清除应用数据(不卸载)
driver.execute_script("mobile: clearApp", {"appId": "com.example.app"})

# 启动 Activity
driver.start_activity("com.example.app", ".MainActivity")

# 获取当前 Activity
activity = driver.current_activity

# ==================== iOS ====================
# 无法单独清除数据，需要卸载重装
driver.remove_app("com.example.bundleid")
driver.install_app("/path/to/app.ipa")

# 启动应用
driver.execute_script("mobile: launchApp", {"bundleId": "com.example.bundleid"})

# 获取当前应用信息
app_info = driver.execute_script("mobile: activeAppInfo")
```

### 11.6 滑动/滚动差异

```python
# ==================== Android 滚动 ====================
driver.find_element(
    AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiScrollable(new UiSelector().scrollable(true))'
    '.scrollIntoView(new UiSelector().text("目标"))'
)

# ==================== iOS 滚动 ====================
driver.execute_script("mobile: scroll", {
    "direction": "down",
    "predicateString": "label == '目标'"
})
```

---

## 十二、常见问题与解决方案

### 12.1 连接问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 无法连接设备 | USB调试未开启 | 开启开发者选项 → USB调试 |
| ADB 找不到设备 | 驱动问题 | 安装设备驱动,`adb kill-server && adb start-server` |
| WDA 启动失败 | 证书问题 | 重新签名 WebDriverAgent |
| Session 创建失败 | Appium Server未启动 | 确认服务启动并监听正确端口 |
| 设备断连 | USB连接不稳定 | 换数据线,使用 WiFi 连接 |

### 12.2 元素定位问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 元素找不到 | 页面未加载完成 | 添加显式等待 |
| 元素ID频繁变化 | 动态ID | 使用相对定位/多属性组合 |
| XPath 定位慢 | iOS XPath性能差 | 改用 Predicate/ClassChain |
| 多个匹配元素 | 定位不唯一 | 使用更精确的定位符 |
| 元素在 WebView 中 | 上下文问题 | 切换到 WEBVIEW 上下文 |

### 12.3 操作问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 点击无效 | 元素被遮挡 | 滚动元素到可见区域 |
| 输入失败 | 键盘未弹出 | 先点击输入框 |
| 滑动不生效 | 坐标计算错误 | 使用相对坐标 |
| Toast 捕获不到 | 显示时间短 | 循环检测或截图分析 |

### 12.4 稳定性问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 测试不稳定 | 等待时间不够 | 增加显式等待 |
| 随机失败 | 网络/设备状态 | 添加重试机制 |
| 内存溢出 | Driver 未关闭 | 确保 driver.quit() 执行 |
| 命令超时 | 操作时间过长 | 增加 newCommandTimeout |

### 12.5 iOS 特有问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| WDA 编译失败 | Xcode 版本不匹配 | 更新 Xcode 和 Appium |
| 真机需要信任 | 开发者未信任 | 设置 → 通用 → 设备管理 → 信任 |
| 剪贴板读取失败 | 安全限制 | WDA 应用需在前台 |
| 应用无法安装 | 签名问题 | 重新签名 IPA |

---

## 十三、面试高频问题

### Q1: Appium 的工作原理是什么？

**回答要点：**
> Appium 基于 C/S 架构，工作原理如下：
> 1. **客户端**发送 HTTP 请求（基于 WebDriver 协议）到 Appium Server
> 2. **Appium Server** 接收请求，转发给对应平台的驱动
> 3. **Android** 使用 UiAutomator2 驱动，将命令转为 UiAutomator2 框架可执行的操作
> 4. **iOS** 使用 XCUITest 驱动，通过 WebDriverAgent 将命令转为 XCTest 框架操作
> 5. 驱动与设备/模拟器交互，执行实际操作
> 6. 结果沿相反路径返回给测试脚本

---

### Q2: 如何选择元素定位策略？

**回答要点：**
> 定位策略选择优先级：
> 1. **ACCESSIBILITY_ID** - 首选，跨平台一致
> 2. **ID** - Android 的 resource-id，iOS 的 name
> 3. **Android: UiAutomator** - 功能强大，支持滚动查找
> 4. **iOS: Predicate/ClassChain** - 性能比 XPath 好
> 5. **XPATH** - 最后选择，iOS上性能较差
> 
> 原则：
> - 唯一性：确保定位到唯一元素
> - 稳定性：避免使用动态变化的属性
> - 可读性：便于维护

---

### Q3: 隐式等待和显式等待的区别？

**回答要点：**
> **隐式等待 (implicitly_wait)**：
> - 全局生效，设置一次对所有元素查找有效
> - 等待元素出现，超时抛出 NoSuchElementException
> - 缺点：无法针对特定元素设置不同等待时间
> 
> **显式等待 (WebDriverWait)**：
> - 针对特定元素设置
> - 可自定义等待条件（出现/可见/可点击等）
> - 更灵活，推荐使用
> 
> **最佳实践**：
> - 隐式等待设置较小值（3-5秒）作为兜底
> - 关键元素使用显式等待

---

### Q4: 如何处理系统弹窗？

**回答要点：**
> **Android**：
> - Capabilities 设置 `autoGrantPermissions: true` 自动授权
> - 手动定位并点击 Allow/Deny 按钮
> 
> **iOS**：
> - Capabilities 设置 `autoAcceptAlerts: true` 自动接受
> - 自定义 `acceptAlertButtonSelector` 匹配多种弹窗
> - 使用 `driver.switch_to.alert.accept()`
> 
> **通用处理**：
> - 封装弹窗处理函数，try-catch 包裹
> - 测试用例开始前预先处理可能的弹窗

---

### Q5: Appium 测试不稳定怎么办？

**回答要点：**
> 1. **等待机制**：使用显式等待替代 sleep
> 2. **元素定位**：使用稳定的定位策略，避免动态属性
> 3. **失败重试**：封装重试机制，处理偶发失败
> 4. **环境检查**：测试前检查网络、设备状态
> 5. **错误处理**：完善的异常捕获和日志记录
> 6. **截图保存**：失败时自动截图，便于问题定位
> 7. **页面刷新**：某些场景增加刷新或返回重试
> 8. **设备重启**：长时间运行后定期重启设备

---

### Q6: Android 和 iOS 自动化有什么区别？

**回答要点：**
> | 方面 | Android | iOS |
> |------|---------|-----|
> | 驱动 | UiAutomator2 | XCUITest |
> | 设备连接 | ADB | WebDriverAgent |
> | 定位推荐 | UiAutomator | Predicate |
> | XPath性能 | 一般 | 较差 |
> | 网络控制 | 支持 | 不支持 |
> | 剪贴板 | 直接访问 | 需WDA前台 |
> | 权限处理 | autoGrantPermissions | autoAcceptAlerts |
> | 应用数据 | 可单独清除 | 需卸载重装 |

---

### Q7: 如何处理 WebView？

**回答要点：**
> 1. 获取所有上下文：`driver.contexts`
> 2. 切换到 WebView：`driver.switch_to.context('WEBVIEW_xxx')`
> 3. 使用 Web 定位方式操作元素（CSS/XPATH）
> 4. 操作完成后切回原生：`driver.switch_to.context('NATIVE_APP')`
> 
> **注意事项**：
> - Android 需要应用开启 WebView 调试
> - 可能需要配置 ChromeDriver 版本

---

### Q8: 如何进行性能优化？

**回答要点：**
> 1. **减少元素查找**：缓存已定位元素
> 2. **优化定位策略**：ID > ACCESSIBILITY_ID > UiAutomator > XPATH
> 3. **合理使用等待**：避免过长的隐式等待
> 4. **减少截图**：仅在失败时截图
> 5. **复用 Session**：减少 Driver 创建销毁
> 6. **跳过设备初始化**：`skipDeviceInitialization: true`
> 7. **使用 noReset**：避免每次重装应用
> 8. **并行执行**：多设备并行运行

---

### Q9: 你在项目中遇到过什么难点？

**回答示例：**
> 1. **Play Store 元素定位**：Google 频繁更新导致元素变化，使用 XPath+text 组合定位，建立定期维护机制
> 
> 2. **下载进度判断**：无法直接获取进度值，采用状态机模式——通过 Cancel 按钮判断下载中，Uninstall 按钮判断完成
> 
> 3. **VPN 切换稳定性**：连接后增加网络验证（Ping Google），失败则重试
> 
> 4. **iOS 剪贴板限制**：发现 WDA 需在前台才能读取，通过先激活 WDA 应用再读取解决

---

### Q10: Appium 有什么局限性？

**回答要点：**
> 1. **执行效率**：相比原生框架(Espresso/XCTest)较慢
> 2. **稳定性**：依赖链长，任一环节问题都可能导致失败
> 3. **iOS限制多**：剪贴板、网络控制等受系统限制
> 4. **游戏应用**：Unity/Cocos 等游戏引擎支持有限
> 5. **高级手势**：复杂手势实现困难
> 6. **版本兼容**：需要维护与系统版本的兼容性
> 
> **应对策略**：
> - 关键业务使用原生框架补充
> - 建立稳定性保障机制
> - 定期更新 Appium 和驱动版本

---

## 📚 附录

### A. 常用 ADB 命令

```bash
# 设备管理
adb devices                          # 查看连接设备
adb -s <udid> shell                  # 进入设备shell
adb connect <ip>:5555                # WiFi连接设备

# 应用管理
adb install app.apk                  # 安装应用
adb uninstall com.example.app        # 卸载应用
adb shell pm list packages           # 列出所有包名
adb shell pm clear com.example.app   # 清除应用数据
adb shell am start -n com.example.app/.MainActivity  # 启动Activity
adb shell am force-stop com.example.app              # 强制停止应用

# 设备信息
adb shell getprop ro.product.model   # 设备型号
adb shell wm size                    # 屏幕分辨率
adb shell dumpsys battery            # 电池信息

# 文件操作
adb push local.txt /sdcard/          # 推送文件
adb pull /sdcard/remote.txt ./       # 拉取文件

# 截图录屏
adb shell screencap /sdcard/screen.png  # 截图
adb shell screenrecord /sdcard/demo.mp4 # 录屏

# 输入操作
adb shell input text "Hello"         # 输入文本
adb shell input keyevent 3           # 模拟按键
adb shell input tap 100 200          # 点击坐标
adb shell input swipe 100 200 100 500 500  # 滑动

# 日志
adb logcat                           # 查看日志
adb logcat -c                        # 清除日志
```

### B. iOS 常用命令 (libimobiledevice)

```bash
# 设备管理
idevice_id -l                        # 列出设备UDID
ideviceinfo -u <udid>                # 设备信息
idevicename -u <udid>                # 设备名称

# 应用管理
ideviceinstaller -l                  # 列出已安装应用
ideviceinstaller -i app.ipa          # 安装应用
ideviceinstaller -U com.example.app  # 卸载应用

# 日志
idevicesyslog                        # 系统日志

# 截图
idevicescreenshot screenshot.png     # 截图
```

### C. Appium Inspector 使用

1. 下载安装 Appium Inspector
2. 配置 Remote Host: `127.0.0.1`
3. 配置 Remote Port: `4723`
4. 填写 Desired Capabilities
5. Start Session
6. 点击元素查看属性和定位符
7. 复制定位符到代码中使用

---

**最后更新**：2024年12月
**适用版本**：Appium 2.x + appium-python-client 4.x
