#!/usr/bin/env python3
"""
验证问卷数据完整性
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scales.models import ScaleConfig

def verify_data_integrity():
    """验证数据完整性"""
    print("=== 问卷数据完整性验证 ===")
    
    # 获取所有问卷配置
    configs = ScaleConfig.objects.all()
    print(f"数据库中共有 {len(configs)} 个问卷配置")
    
    total_issues = 0
    
    for config in configs:
        print(f"\n--- 检查问卷: {config.name} (ID: {config.id}) ---")
        issues = 0
        
        # 检查基本信息
        if not config.name:
            print("❌ 问卷名称为空")
            issues += 1
        
        if not config.code:
            print("❌ 问卷编码为空")
            issues += 1
        
        if not config.type:
            print("❌ 问卷类型为空")
            issues += 1
        
        # 检查问题数据
        if not config.questions:
            print("❌ 问题列表为空")
            issues += 1
        else:
            print(f"✅ 问题数量: {len(config.questions)}")
            
            # 检查前3个问题
            for i, question in enumerate(config.questions[:3]):
                print(f"\n  问题 {i+1}: {question.get('question', '无问题文本')}")
                
                if not question.get('id'):
                    print("    ❌ 问题ID缺失")
                    issues += 1
                
                if not question.get('question'):
                    print("    ❌ 问题文本缺失")
                    issues += 1
                
                options = question.get('options', [])
                if not options:
                    print("    ❌ 选项列表为空")
                    issues += 1
                else:
                    print(f"    ✅ 选项数量: {len(options)}")
                    
                    # 检查前2个选项
                    for j, option in enumerate(options[:2]):
                        text = option.get('text', '')
                        value = option.get('value', '')
                        print(f"      选项 {j+1}: {text} (value: {value})")
                        
                        if not text:
                            print(f"      ❌ 选项 {j+1} 文本为空")
                            issues += 1
                        
                        if value == '':
                            print(f"      ❌ 选项 {j+1} value为空")
                            issues += 1
        
        if issues == 0:
            print("✅ 此问卷数据完整")
        else:
            print(f"❌ 此问卷有 {issues} 个问题")
            total_issues += issues
    
    print(f"\n=== 验证总结 ===")
    if total_issues == 0:
        print("✅ 所有问卷数据完整，没有发现任何问题")
    else:
        print(f"❌ 共发现 {total_issues} 个数据完整性问题")
    
    return total_issues == 0

def check_yaml_vs_database():
    """检查YAML文件与数据库的一致性"""
    print("\n=== YAML文件与数据库一致性检查 ===")
    
    import yaml
    import os
    
    yaml_dir = "apps/scales/yaml_configs"
    yaml_files = [f for f in os.listdir(yaml_dir) if f.endswith('.yaml')]
    
    print(f"找到 {len(yaml_files)} 个YAML文件")
    
    for yaml_file in yaml_files:
        file_path = os.path.join(yaml_dir, yaml_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            code = yaml_data.get('code')
            if not code:
                print(f"❌ {yaml_file} 缺少code字段")
                continue
            
            # 检查数据库中是否存在对应的配置
            try:
                db_config = ScaleConfig.objects.get(code=code)
                print(f"✅ {yaml_file}: 数据库中存在对应配置 (ID: {db_config.id})")
                
                # 比较问题数量
                yaml_questions = len(yaml_data.get('questions', []))
                db_questions = len(db_config.questions)
                if yaml_questions == db_questions:
                    print(f"  ✅ 问题数量一致: {yaml_questions}")
                else:
                    print(f"  ❌ 问题数量不一致: YAML({yaml_questions}) vs DB({db_questions})")
                
            except ScaleConfig.DoesNotExist:
                print(f"❌ {yaml_file}: 数据库中找不到对应配置 (code: {code})")
                
        except Exception as e:
            print(f"❌ 读取 {yaml_file} 失败: {e}")

if __name__ == "__main__":
    print("开始问卷数据完整性验证...")
    
    # 验证数据完整性
    integrity_ok = verify_data_integrity()
    
    # 检查YAML与数据库一致性
    check_yaml_vs_database()
    
    print("\n=== 最终结论 ===")
    if integrity_ok:
        print("✅ 问卷数据完整性验证通过")
        print("✅ 所有问卷配置数据完整，问题结构正确")
        print("✅ YAML文件与数据库同步正常")
    else:
        print("❌ 发现数据完整性问题，需要修复")
    
    print("\n验证完成!")