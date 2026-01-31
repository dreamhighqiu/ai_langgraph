"""
LLM 配置测试脚本

演示如何通过 .env 文件配置 LLM
"""

import os
import sys
from pathlib import Path

# 确保在正确的目录
project_root = Path(__file__).parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

print("=" * 70)
print("🧪 LLM 配置测试")
print("=" * 70)

# ============================================================================
# 步骤 1: 检查 .env 文件
# ============================================================================
print("\n📁 步骤 1: 检查 .env 文件")
print("-" * 70)

env_file = project_root / ".env"
if env_file.exists():
    print(f"✅ .env 文件存在: {env_file}")
    
    # 读取并显示关键配置（隐藏敏感信息）
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if 'API_KEY' in line:
                    key, value = line.split('=', 1)
                    print(f"  {key}={'*' * 20}... (已隐藏)")
                elif any(k in line for k in ['MODEL', 'PROVIDER', 'BASE_URL']):
                    print(f"  {line}")
else:
    print(f"❌ .env 文件不存在: {env_file}")
    print("   请先创建 .env 文件：")
    print("   cp env.example .env")
    sys.exit(1)

# ============================================================================
# 步骤 2: 导入 Settings 并查看配置
# ============================================================================
print("\n⚙️  步骤 2: 加载 Settings 配置")
print("-" * 70)

try:
    from config.settings import settings
    
    print(f"✅ Settings 加载成功")
    print(f"\n配置详情:")
    print(f"  default_llm_provider: {settings.default_llm_provider}")
    print(f"  openai_model:         {settings.openai_model}")
    print(f"  openai_base_url:      {settings.openai_base_url or '(默认)'}")
    
    # 检查 API Key（隐藏完整值）
    if settings.openai_api_key:
        masked_key = settings.openai_api_key[:10] + '...' + settings.openai_api_key[-10:]
        print(f"  openai_api_key:       {masked_key}")
    else:
        print(f"  openai_api_key:       ❌ 未配置")
    
    print(f"\n其他配置:")
    print(f"  deepseek_model:       {settings.deepseek_model}")
    print(f"  anthropic_model:      {settings.anthropic_model}")
    
except Exception as e:
    print(f"❌ Settings 加载失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# 步骤 3: 测试 LLM 配置信息
# ============================================================================
print("\n🔍 步骤 3: 获取 LLM 配置信息")
print("-" * 70)

try:
    from config.llm_config import get_llm_info
    
    info = get_llm_info()
    
    print(f"✅ LLM 配置信息:")
    print(f"  Provider:        {info['provider']}")
    print(f"  Model:           {info['model']}")
    print(f"  API Key 已配置:  {'✅' if info['api_key_configured'] else '❌'}")
    
    if 'base_url' in info:
        print(f"  Base URL:        {info['base_url']}")
    
except Exception as e:
    print(f"❌ 获取 LLM 配置信息失败: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# 步骤 4: 测试 LLM 初始化
# ============================================================================
print("\n🚀 步骤 4: 测试 LLM 初始化")
print("-" * 70)

try:
    from config.llm_config import get_llm_model
    
    print("正在初始化 LLM...")
    model = get_llm_model()
    
    print(f"✅ LLM 初始化成功!")
    print(f"  类型: {type(model).__name__}")
    print(f"  模型: {model}")
    
    # 检查模型属性
    if hasattr(model, 'model_name'):
        print(f"  模型名称: {model.model_name}")
    
except Exception as e:
    print(f"❌ LLM 初始化失败: {e}")
    print("\n可能的原因:")
    print("  1. API Key 未配置或无效")
    print("  2. 网络连接问题")
    print("  3. API 端点不可达")
    import traceback
    traceback.print_exc()

# ============================================================================
# 步骤 5: 测试不同提供商
# ============================================================================
print("\n🔄 步骤 5: 测试其他 LLM 提供商")
print("-" * 70)

from config.llm_config import get_llm

providers_to_test = []

if settings.openai_api_key:
    providers_to_test.append(("openai", settings.openai_model))

if settings.deepseek_api_key:
    providers_to_test.append(("deepseek", settings.deepseek_model))

if settings.anthropic_api_key:
    providers_to_test.append(("anthropic", settings.anthropic_model))

if not providers_to_test:
    print("⚠️  没有配置任何 LLM 提供商的 API Key")
else:
    for provider, model_name in providers_to_test:
        try:
            print(f"\n测试 {provider.upper()}...")
            model = get_llm(provider=provider, model_name=model_name)
            print(f"  ✅ {provider.upper()} 初始化成功 (模型: {model_name})")
        except Exception as e:
            print(f"  ❌ {provider.upper()} 初始化失败: {e}")

# ============================================================================
# 步骤 6: 环境变量验证
# ============================================================================
print("\n🌍 步骤 6: 环境变量验证")
print("-" * 70)

important_vars = [
    "OPENAI_API_KEY",
    "OPENAI_MODEL", 
    "OPENAI_BASE_URL",
    "DEFAULT_LLM_PROVIDER",
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_MODEL",
]

print("当前环境变量:")
for var in important_vars:
    value = os.getenv(var)
    if value:
        if 'API_KEY' in var:
            display_value = value[:10] + '...' + value[-10:] if len(value) > 20 else value
        else:
            display_value = value
        print(f"  {var:30} = {display_value}")
    else:
        print(f"  {var:30} = (未设置)")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 70)
print("📊 测试总结")
print("=" * 70)

checks = [
    (".env 文件存在", env_file.exists()),
    ("Settings 加载成功", 'settings' in locals()),
    ("LLM 配置信息可获取", 'info' in locals()),
    ("LLM 初始化成功", 'model' in locals() and model is not None),
]

all_passed = all(result for _, result in checks)

for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"  {status} {check_name}")

print("\n" + "=" * 70)
if all_passed:
    print("🎉 所有测试通过！LLM 配置正常工作！")
else:
    print("⚠️  部分测试失败，请检查上面的错误信息")
print("=" * 70)

# ============================================================================
# 配置建议
# ============================================================================
if not all_passed:
    print("\n💡 配置建议:")
    print("-" * 70)
    
    if not env_file.exists():
        print("1. 创建 .env 文件:")
        print("   cd testing-agents-service")
        print("   cp env.example .env")
        print("   vim .env  # 编辑填入实际的 API Key")
    
    if not settings.openai_api_key:
        print("\n2. 配置 OpenAI API Key:")
        print("   在 .env 文件中添加:")
        print("   OPENAI_API_KEY=sk-proj-your-actual-key...")
    
    print("\n3. 验证配置:")
    print("   python test_llm_config.py")
    
    print("\n4. 查看详细文档:")
    print("   docs/LLM_CONFIG_ENV_GUIDE.md")

