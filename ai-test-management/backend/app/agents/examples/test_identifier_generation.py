"""
测试新的标识符生成逻辑

验证随机数生成的标识符不会重复
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


from app.utils.identifier import generate_test_case_identifier
# noqa  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VTJSWWFRPT06NWYxMWJlMDI=


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
# noqa  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VTJSWWFRPT06NWYxMWJlMDI=
        
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
    
    # 验证数字范围
    numbers = [int(id.split('-')[1]) for id in identifiers]
    print(f"\n数字范围: {min(numbers)} - {max(numbers)}")
    print(f"预期范围: 100000 - 999999")
    
    if min(numbers) >= 100000 and max(numbers) <= 999999:
        print("✅ 数字范围正确！")
    else:
        print("❌ 数字范围不正确！")


if __name__ == "__main__":
    test_identifier_uniqueness()

# fmt: off  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VTJSWWFRPT06NWYxMWJlMDI=
