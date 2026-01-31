@echo off
REM DeepSeek自动化测试运行脚本（Windows）

echo =========================================
echo DeepSeek网站自动化测试
echo =========================================

REM 检查Java环境
echo 检查Java环境...
java -version >nul 2>&1
if errorlevel 1 (
    echo 错误: Java未安装或未配置
    exit /b 1
)

REM 检查Maven环境
echo 检查Maven环境...
mvn -version >nul 2>&1
if errorlevel 1 (
    echo 错误: Maven未安装或未配置
    exit /b 1
)

REM 创建必要的目录
echo 创建测试目录...
if not exist screenshots mkdir screenshots
if not exist target mkdir target

REM 清理并安装依赖
echo 清理并安装依赖...
call mvn clean compile

if errorlevel 1 (
    echo 错误: 依赖安装失败
    exit /b 1
)

REM 运行测试
echo 开始运行测试...
echo =========================================

REM 根据参数运行不同的测试
if "%1"=="smoke" (
    echo 运行冒烟测试...
    call mvn test -Dgroups=smoke
) else if "%1"=="regression" (
    echo 运行回归测试...
    call mvn test -Dgroups=regression
) else if "%1"=="all" (
    echo 运行所有测试...
    call mvn test
) else if "%1"=="single" (
    if not "%2"=="" (
        echo 运行单个测试: %2
        call mvn test -Dtest="%2"
    ) else (
        echo 错误: 请指定测试类名
        exit /b 1
    )
) else (
    echo 运行默认测试套件...
    call mvn test -Dtest=DeepSeekFunctionalTests
)

REM 检查测试结果
if errorlevel 1 (
    echo =========================================
    echo ❌ 测试失败!
    
    REM 检查是否有截图
    if exist screenshots\* (
        echo 失败的截图已保存到 screenshots\ 目录
    )
) else (
    echo =========================================
    echo ✅ 所有测试通过!
)

echo =========================================
echo 测试完成
exit /b %errorlevel%