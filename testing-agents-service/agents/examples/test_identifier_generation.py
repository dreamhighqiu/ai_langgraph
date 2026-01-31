"""
测试新的标识符生成逻辑

验证随机数生成的标识符不会重复
"""


# pylint: disable  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y0hFd1ZBPT06NzMxNDg0MDE=

from app.utils.identifier import generate_test_case_identifier


def test_identifier_uniqueness():
    """测试标识符唯一性"""
    print("测试标识符生成...")
    print("=" * 60)
    
    # 生成 100 个标识符
    identifiers = set()
    duplicates = []
    
    for i in range(100):
        identifier = generate_test_case_identifier()
        if identifier in identifiers:
            duplicates.append(identifier)
        identifiers.add(identifier)
        
        if i < 10:  # 只打印前 10 个
            print(f"{i+1}. {identifier}")
    
    print("...")
    print(f"\n生成了 {len(identifiers)} 个唯一标识符")
    
    if duplicates:
        print(f"⚠️  发现 {len(duplicates)} 个重复标识符: {duplicates}")
    else:
        print("✅ 所有标识符都是唯一的！")
    
    # 验证格式
    print("\n验证格式:")
    sample = list(identifiers)[0]
    print(f"示例: {sample}")
    print(f"格式: TC-{sample.split('-')[1]}")
    print(f"长度: {len(sample)} 字符")
# noqa  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y0hFd1ZBPT06NzMxNDg0MDE=
    
    # 验证数字范围
    numbers = [int(id.split('-')[1]) for id in identifiers]
    print(f"\n数字范围: {min(numbers)} - {max(numbers)}")
    print(f"预期范围: 100000 - 999999")
# fmt: off  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y0hFd1ZBPT06NzMxNDg0MDE=
    
    if min(numbers) >= 100000 and max(numbers) <= 999999:
        print("✅ 数字范围正确！")
    else:
        print("❌ 数字范围不正确！")


if __name__ == "__main__":
    test_identifier_uniqueness()

