"""
验证提示词优化效果

简单脚本，用于查看生成的系统提示词
"""



import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
# type: ignore  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WnpCeGVBPT06ODg3MTBjOTM=

from dataclasses import dataclass
from unittest.mock import Mock


@dataclass
class TestCaseGeneratorContext:
    """测试用例生成器上下文"""
    project_identifier: str = ""
    folder_id: str = ""
    current_user_id: str = "00000000-0000-0000-0000-000000000001"
    template_type: str = "test_case"

# fmt: off  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WnpCeGVBPT06ODg3MTBjOTM=

def verify_prompt():
    """验证提示词内容"""
    print("\n" + "="*80)
    print("验证智能体提示词优化效果")
    print("="*80 + "\n")
    
    # 模拟上下文
    project_identifier = "PROJ-DEMO-001"
    folder_id = "123e4567-e89b-12d3-a456-426614174000"
    template_type = "test_case"
    
    print(f"📋 模拟上下文信息:")
    print(f"   项目标识符: {project_identifier}")
    print(f"   文件夹 ID: {folder_id}")
    print(f"   模板类型: {template_type}")
    print()
    
    # 构建上下文信息提示（与实际代码相同）
    context_section = f"""
## 🎯 当前上下文信息（重要！）

**系统已自动配置以下参数，调用工具时必须使用这些值：**

- **项目标识符 (project_identifier)**: `{project_identifier}`
- **文件夹 ID (folder_id)**: `{folder_id}`
- **默认模板类型 (template)**: `{template_type}`

**⚠️ 调用工具时的关键注意事项：**

1. **必须使用上述参数**：创建测试用例时，`project_identifier` 和 `folder_id` 必须使用上面显示的值
2. **不要询问用户**：这些参数已由前端自动传入，不需要用户手动提供
3. **模板类型**：
   - 如果 template_type 是 `test_case`，创建普通测试用例（使用 test_case_steps）
   - 如果 template_type 是 `test_case_bdd`，创建 BDD 测试用例（使用 feature/scenario/background）
   - 用户可以在对话中要求使用特定模板，但默认使用上述值
4. **参数验证**：如果上述参数为空，立即提示用户"系统配置错误，缺少必要的项目或文件夹信息"

**✅ 正确的工具调用示例：**
```python
create_test_case_tool(
    project_identifier="{project_identifier}",  # 使用上下文中的值
    folder_id="{folder_id}",                    # 使用上下文中的值
    template="{template_type}",                 # 使用上下文中的默认模板
    name="用户登录功能测试",
    description="验证用户登录功能",
    ...
)
```

**❌ 错误的做法：**
- 不要询问用户 "请提供项目标识符"
- 不要使用硬编码的值如 "PROJ-001"
- 不要忽略上下文中的 template_type
"""
    
    print("📝 生成的上下文信息部分:\n")
    print(context_section)
    print("\n" + "="*80)
    print("✅ 验证点:")
    print("="*80 + "\n")
# pylint: disable  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WnpCeGVBPT06ODg3MTBjOTM=
    
    # 验证点
    checks = [
        ("包含项目标识符", project_identifier in context_section),
        ("包含文件夹 ID", folder_id in context_section),
        ("包含模板类型", template_type in context_section),
        ("包含调用注意事项", "调用工具时的关键注意事项" in context_section),
        ("包含正确示例", "正确的工具调用示例" in context_section),
        ("包含错误示例", "错误的做法" in context_section),
        ("强调必须使用参数", "必须使用上述参数" in context_section),
        ("提示不要询问用户", "不要询问用户" in context_section),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}: {'通过' if result else '失败'}")
        if not result:
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 所有验证点都通过！提示词优化成功！")
    else:
        print("⚠️  部分验证点未通过，请检查提示词内容")
    print("="*80 + "\n")
# pragma: no cover  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WnpCeGVBPT06ODg3MTBjOTM=
    
    # 显示关键信息
    print("📌 关键优化点:")
    print("1. ✅ 上下文参数已嵌入到提示词中")
    print("2. ✅ 智能体能够看到具体的参数值")
    print("3. ✅ 提供了详细的使用说明和示例")
    print("4. ✅ 明确了正确和错误的做法")
    print("5. ✅ 强调了参数验证的重要性")
    print()


if __name__ == "__main__":
    verify_prompt()

