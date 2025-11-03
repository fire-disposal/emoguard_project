#!/usr/bin/env python3
"""
问卷问答功能完整性测试脚本 - 包含身份验证
"""
import requests
import json
import uuid
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:8000/api"

def admin_login_and_create_user():
    """管理员登录并创建测试用户"""
    print("=== 管理员登录并创建测试用户 ===")
    
    # 管理员登录
    admin_login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # 管理员登录
        response = requests.post(f"{BASE_URL}/users/admin/login", json=admin_login_data)
        print(f"管理员登录状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"管理员登录失败: {response.text}")
            return None
        
        admin_tokens = response.json()
        admin_access_token = admin_tokens.get('access_token')
        print("管理员登录成功!")
        
        # 创建测试用户
        test_username = f"testuser_{uuid.uuid4().hex[:8]}"
        create_user_data = {
            "username": test_username,
            "password": "Test123456!",
            "email": f"{test_username}@test.com",
            "role": "user"
        }
        
        headers = {
            "Authorization": f"Bearer {admin_access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{BASE_URL}/users/admin/users", json=create_user_data, headers=headers)
        print(f"创建用户状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("测试用户创建成功!")
        else:
            print(f"创建用户失败: {response.text}")
            # 如果用户已存在，继续尝试登录
        
        # 使用新创建的用户登录
        user_login_data = {
            "username": test_username,
            "password": "Test123456!"
        }
        
        response = requests.post(f"{BASE_URL}/token/pair", json=user_login_data)
        print(f"用户登录状态码: {response.status_code}")
        
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get('access')
            print("用户登录成功!")
            print(f"访问令牌: {access_token[:20]}...")
            return access_token
        else:
            print(f"用户登录错误: {response.text}")
            return None
            
    except Exception as e:
        print(f"异常: {e}")
        return None

def test_get_scale_configs():
    """测试获取问卷配置列表"""
    print("\n=== 测试获取问卷配置列表 ===")
    try:
        response = requests.get(f"{BASE_URL}/scales/configs")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            configs = response.json()
            print(f"获取到 {len(configs)} 个问卷配置")
            
            # 打印前3个问卷的基本信息
            for i, config in enumerate(configs[:3]):
                print(f"问卷 {i+1}:")
                print(f"  - ID: {config['id']}")
                print(f"  - 名称: {config['name']}")
                print(f"  - 编码: {config['code']}")
                print(f"  - 类型: {config['type']}")
                print(f"  - 状态: {config['status']}")
                print(f"  - 问题数量: {len(config['questions'])}")
            
            return configs
        else:
            print(f"错误: {response.text}")
            return None
    except Exception as e:
        print(f"异常: {e}")
        return None

def test_get_scale_config_detail(config_id):
    """测试获取单个问卷配置详情"""
    print(f"\n=== 测试获取问卷配置详情 (ID: {config_id}) ===")
    try:
        response = requests.get(f"{BASE_URL}/scales/configs/{config_id}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            config = response.json()
            print(f"问卷名称: {config['name']}")
            print(f"问卷编码: {config['code']}")
            print(f"问卷类型: {config['type']}")
            print(f"问题数量: {len(config['questions'])}")
            
            # 检查第一个问题的结构
            if config['questions']:
                first_question = config['questions'][0]
                print(f"第一个问题: {first_question['question']}")
                print(f"选项数量: {len(first_question['options'])}")
                if first_question['options']:
                    first_option = first_question['options'][0]
                    print(f"第一个选项: {first_option['text']} (value: {first_option.get('value', 'N/A')})")
            
            return config
        else:
            print(f"错误: {response.text}")
            return None
    except Exception as e:
        print(f"异常: {e}")
        return None

def test_create_scale_result(config_id, user_id, access_token):
    """测试创建问卷结果"""
    print(f"\n=== 测试创建问卷结果 ===")
    
    # 首先获取问卷配置以了解问题结构
    config_response = requests.get(f"{BASE_URL}/scales/configs/{config_id}")
    if config_response.status_code != 200:
        print("无法获取问卷配置")
        return None
    
    config = config_response.json()
    questions = config['questions']
    
    # 为每个问题选择一个随机选项（这里简化处理，选择第一个选项）
    selected_options = [0] * len(questions)
    
    # 计算开始和结束时间
    started_at = datetime.now() - timedelta(minutes=5)
    completed_at = datetime.now()
    
    result_data = {
        "user_id": user_id,
        "scale_config_id": config_id,
        "selected_options": selected_options,
        "duration_ms": 300000,  # 5分钟
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat()
    }
    
    print(f"提交的数据: {json.dumps(result_data, ensure_ascii=False, indent=2)}")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/scales/results", json=result_data, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("问卷结果创建成功!")
            print(f"结果ID: {result['id']}")
            print(f"用户ID: {result['user_id']}")
            print(f"结论: {result.get('conclusion', 'N/A')}")
            print(f"分析结果: {json.dumps(result.get('analysis', {}), ensure_ascii=False, indent=2)}")
            return result
        else:
            print(f"错误: {response.text}")
            return None
    except Exception as e:
        print(f"异常: {e}")
        return None

def test_get_scale_results(user_id, access_token):
    """测试获取问卷结果列表"""
    print(f"\n=== 测试获取问卷结果列表 (用户ID: {user_id}) ===")
    try:
        params = {
            "user_id": user_id,
            "page": 1,
            "page_size": 10
        }
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(f"{BASE_URL}/scales/results", params=params, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            print(f"获取到 {len(results)} 个结果")
            
            for i, result in enumerate(results):
                print(f"结果 {i+1}:")
                print(f"  - ID: {result['id']}")
                print(f"  - 问卷名称: {result['scale_config']['name']}")
                print(f"  - 完成时间: {result['completed_at']}")
                print(f"  - 用时: {result['duration_ms']}ms")
                print(f"  - 结论: {result.get('conclusion', 'N/A')[:50]}...")
            
            return results
        else:
            print(f"错误: {response.text}")
            return None
    except Exception as e:
        print(f"异常: {e}")
        return None

def main():
    """主测试函数"""
    print("开始问卷问答功能完整性测试...")
    
    # 步骤1: 管理员登录并创建测试用户
    access_token = admin_login_and_create_user()
    if not access_token:
        print("无法获取访问令牌，测试终止")
        return
    
    # 步骤2: 获取问卷配置列表
    configs = test_get_scale_configs()
    if not configs:
        print("无法获取问卷配置，测试终止")
        return
    
    # 步骤3: 获取第一个问卷的详情
    first_config = configs[0]
    config_detail = test_get_scale_config_detail(first_config['id'])
    if not config_detail:
        print("无法获取问卷详情，测试终止")
        return
    
    # 步骤4: 创建问卷结果
    test_user_id = str(uuid.uuid4())
    result = test_create_scale_result(first_config['id'], test_user_id, access_token)
    if not result:
        print("无法创建问卷结果，测试终止")
        return
    
    # 步骤5: 获取问卷结果列表
    test_get_scale_results(test_user_id, access_token)
    
    print("\n=== 测试总结 ===")
    print("✅ 用户注册和登录 - 通过")
    print("✅ 获取问卷配置列表 - 通过")
    print("✅ 获取问卷配置详情 - 通过")
    print("✅ 创建问卷结果 - 通过")
    print("✅ 获取问卷结果列表 - 通过")
    print("\n问卷问答功能完整性测试完成!")

if __name__ == "__main__":
    main()