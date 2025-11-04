"""
测试 YAML 配置与基础字段的双向同步功能
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scales.models import ScaleConfig


def test_yaml_to_fields():
    """测试：编辑 YAML 自动更新基础字段"""
    print("\n" + "="*60)
    print("测试 1: YAML 编辑 -> 自动更新基础字段")
    print("="*60)
    
    yaml_content = """
name: 测试量表-YAML源
code: TEST_YAML_001
version: "2.0"
description: 这是通过 YAML 创建的量表
type: 测试类型
status: active
questions:
  - id: 1
    question: 测试问题1
    options:
      - text: 选项A
        value: 0
      - text: 选项B
        value: 1
"""
    
    # 创建量表并设置 YAML
    scale = ScaleConfig(yaml_config=yaml_content)
    scale.save()
    
    print("✓ YAML 配置已设置")
    print(f"✓ 自动解析的 name: {scale.name}")
    print(f"✓ 自动解析的 code: {scale.code}")
    print(f"✓ 自动解析的 version: {scale.version}")
    print(f"✓ 自动解析的 type: {scale.type}")
    print(f"✓ 自动解析的 status: {scale.status}")
    print(f"✓ 自动解析的 questions 数量: {len(scale.questions)}")
    
    assert scale.name == "测试量表-YAML源"
    assert scale.code == "TEST_YAML_001"
    assert scale.version == "2.0"
    assert scale.type == "测试类型"
    assert scale.status == "active"
    assert len(scale.questions) == 1
    
    print("✅ 测试通过！YAML -> 字段同步正常")
    
    # 清理
    scale.delete()
    return True


def test_fields_to_yaml():
    """测试：编辑基础字段自动反向同步到 YAML"""
    print("\n" + "="*60)
    print("测试 2: 基础字段编辑 -> 自动同步到 YAML")
    print("="*60)
    
    # 先通过 YAML 创建一个量表
    initial_yaml = """
name: 初始量表
code: TEST_FIELDS_001
version: "1.0"
description: 初始描述
type: 初始类型
status: draft
questions:
  - id: 1
    question: 初始问题
    options:
      - text: 选项1
        value: 0
"""
    
    scale = ScaleConfig(yaml_config=initial_yaml)
    scale.save()
    
    print(f"✓ 初始量表已创建: {scale.name}")
    
    # 修改基础字段
    scale.name = "修改后的量表名"
    scale.version = "2.5"
    scale.description = "修改后的描述"
    scale.type = "修改后的类型"
    scale.status = "active"
    scale.save()
    
    print("✓ 基础字段已修改")
    print(f"✓ 新的 name: {scale.name}")
    print(f"✓ 新的 version: {scale.version}")
    
    # 检查 YAML 是否同步更新
    import yaml
    yaml_data = yaml.safe_load(scale.yaml_config)
    
    print(f"✓ YAML 中的 name: {yaml_data['name']}")
    print(f"✓ YAML 中的 version: {yaml_data['version']}")
    print(f"✓ YAML 中的 description: {yaml_data['description']}")
    print(f"✓ YAML 中的 type: {yaml_data['type']}")
    print(f"✓ YAML 中的 status: {yaml_data['status']}")
    
    assert yaml_data['name'] == "修改后的量表名"
    assert yaml_data['version'] == "2.5"
    assert yaml_data['description'] == "修改后的描述"
    assert yaml_data['type'] == "修改后的类型"
    assert yaml_data['status'] == "active"
    
    print("✅ 测试通过！字段 -> YAML 反向同步正常")
    
    # 清理
    scale.delete()
    return True


def test_yaml_priority():
    """测试：同时修改 YAML 和字段时，YAML 优先"""
    print("\n" + "="*60)
    print("测试 3: YAML 优先级测试")
    print("="*60)
    
    # 创建初始量表
    initial_yaml = """
name: 原始名称
code: TEST_PRIORITY_001
version: "1.0"
description: 原始描述
type: 原始类型
status: draft
questions:
  - id: 1
    question: 原始问题
    options:
      - text: 选项1
        value: 0
"""
    
    scale = ScaleConfig(yaml_config=initial_yaml)
    scale.save()
    
    print("✓ 初始量表已创建")
    
    # 同时修改 YAML 和基础字段
    new_yaml = """
name: YAML优先名称
code: TEST_PRIORITY_001
version: "3.0"
description: YAML优先描述
type: YAML优先类型
status: active
questions:
  - id: 1
    question: YAML优先问题
    options:
      - text: YAML选项
        value: 0
"""
    
    scale.yaml_config = new_yaml
    scale.name = "字段修改名称（应该被YAML覆盖）"
    scale.version = "9.9"
    scale.save()
    
    print("✓ 同时修改了 YAML 和基础字段")
    print(f"✓ 最终 name: {scale.name}")
    print(f"✓ 最终 version: {scale.version}")
    
    # YAML 应该优先
    assert scale.name == "YAML优先名称", f"期望 'YAML优先名称'，实际 '{scale.name}'"
    assert scale.version == "3.0", f"期望 '3.0'，实际 '{scale.version}'"
    
    print("✅ 测试通过！YAML 优先级正确")
    
    # 清理
    scale.delete()
    return True


def test_validation():
    """测试：YAML 验证功能"""
    print("\n" + "="*60)
    print("测试 4: YAML 验证功能")
    print("="*60)
    
    # 测试缺少 code 字段
    print("\n测试 4.1: 缺少 code 字段")
    invalid_yaml_no_code = """
name: 无效量表
version: "1.0"
questions:
  - id: 1
    question: 测试
    options:
      - text: 选项
        value: 0
"""
    
    try:
        scale = ScaleConfig(yaml_config=invalid_yaml_no_code)
        scale.save()
        print("❌ 应该抛出验证错误")
        return False
    except Exception as e:
        print(f"✓ 正确捕获错误: {str(e)}")
    
    # 测试缺少 questions 字段
    print("\n测试 4.2: 缺少 questions 字段")
    invalid_yaml_no_questions = """
name: 无效量表2
code: INVALID_002
version: "1.0"
"""
    
    try:
        scale = ScaleConfig(yaml_config=invalid_yaml_no_questions)
        scale.save()
        print("❌ 应该抛出验证错误")
        return False
    except Exception as e:
        print(f"✓ 正确捕获错误: {str(e)}")
    
    # 测试 YAML 格式错误
    print("\n测试 4.3: YAML 格式错误")
    invalid_yaml_syntax = """
name: 错误格式
code: INVALID_003
  questions:
    - invalid yaml syntax here
"""
    
    try:
        scale = ScaleConfig(yaml_config=invalid_yaml_syntax)
        scale.save()
        print("❌ 应该抛出格式错误")
        return False
    except Exception as e:
        print(f"✓ 正确捕获错误: {str(e)}")
    
    print("✅ 测试通过！YAML 验证功能正常")
    return True


def main():
    print("\n" + "🧪"*30)
    print("开始测试 ScaleConfig YAML 双向同步功能")
    print("🧪"*30)
    
    try:
        test_yaml_to_fields()
        test_fields_to_yaml()
        test_yaml_priority()
        test_validation()
        
        print("\n" + "🎉"*30)
        print("所有测试通过！功能完全正常！")
        print("🎉"*30)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
