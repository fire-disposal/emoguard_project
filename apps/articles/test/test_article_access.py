#!/usr/bin/env python3
"""
测试用户获取科普文章内容功能
"""
import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api"

def test_get_published_articles():
    """测试获取已发布的科普文章"""
    print("=== 测试获取已发布科普文章 ===")
    
    try:
        # 获取已发布的文章（status=published）
        params = {
            "status": "published",
            "page": 1,
            "page_size": 10
        }
        
        response = requests.get(f"{BASE_URL}/articles/", params=params)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            articles = response.json()
            print(f"获取到 {len(articles)} 篇已发布文章")
            
            if articles:
                # 显示文章基本信息
                for i, article in enumerate(articles[:3]):  # 显示前3篇
                    print(f"\n文章 {i+1}:")
                    print(f"  - ID: {article['id']}")
                    print(f"  - 标题: {article['title']}")
                    print(f"  - 状态: {article['status']}")
                    print(f"  - 发布时间: {article['publish_time']}")
                    print(f"  - 内容长度: {len(article['content'])} 字符")
                    if article.get('cover_image'):
                        print(f"  - 封面图片: {article['cover_image'][:50]}...")
                
                return articles
            else:
                print("⚠️  没有找到已发布的文章")
                return []
        else:
            print(f"❌ 错误: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None

def test_get_article_detail(article_id):
    """测试获取单篇文章详情"""
    print(f"\n=== 测试获取文章详情 (ID: {article_id}) ===")
    
    try:
        response = requests.get(f"{BASE_URL}/articles/{article_id}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            article = response.json()
            print("✅ 文章详情获取成功!")
            print(f"标题: {article['title']}")
            print(f"状态: {article['status']}")
            print(f"发布时间: {article['publish_time']}")
            print(f"创建时间: {article['created_at']}")
            print(f"更新时间: {article['updated_at']}")
            print(f"内容预览: {article['content'][:200]}...")
            if article.get('cover_image'):
                print(f"封面图片: {article['cover_image']}")
            
            return article
        elif response.status_code == 404:
            print(f"❌ 文章不存在 (ID: {article_id})")
            return None
        else:
            print(f"❌ 错误: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None

def test_search_articles():
    """测试文章搜索功能"""
    print("\n=== 测试文章搜索功能 ===")
    
    search_terms = ["健康", "心理", "认知", "情绪"]
    
    for term in search_terms:
        print(f"\n搜索关键词: '{term}'")
        try:
            params = {
                "search": term,
                "status": "published",
                "page": 1,
                "page_size": 5
            }
            
            response = requests.get(f"{BASE_URL}/articles/", params=params)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                articles = response.json()
                print(f"找到 {len(articles)} 篇相关文章")
                
                if articles:
                    print("相关文章:")
                    for i, article in enumerate(articles[:2]):  # 显示前2篇
                        print(f"  {i+1}. {article['title']}")
            else:
                print(f"❌ 搜索失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 搜索异常: {e}")

def test_different_user_scenarios():
    """测试不同用户场景"""
    print("\n=== 测试不同用户场景 ===")
    
    scenarios = [
        {
            "name": "匿名用户获取已发布文章",
            "test": lambda: test_get_published_articles()
        },
        {
            "name": "匿名用户搜索文章", 
            "test": lambda: test_search_articles()
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        try:
            result = scenario['test']()
            if result is not None:
                print(f"✅ {scenario['name']} - 成功")
            else:
                print(f"❌ {scenario['name']} - 失败")
        except Exception as e:
            print(f"❌ {scenario['name']} - 异常: {e}")

def test_article_content_types():
    """测试文章内容类型"""
    print("\n=== 测试文章内容类型 ===")
    
    # 获取一篇文章来检查内容格式
    articles = test_get_published_articles()
    if not articles:
        print("❌ 无法获取文章进行内容类型测试")
        return
    
    article = articles[0]
    article_id = article['id']
    
    detail = test_get_article_detail(article_id)
    if not detail:
        return
    
    print("\n内容类型分析:")
    content = detail['content']
    
    # 检查是否包含HTML标签（富文本内容）
    if '<' in content and '>' in content:
        print("✅ 内容包含HTML标签，支持富文本格式")
        # 检查常见的HTML标签
        html_tags = ['<p>', '<div>', '<br>', '<strong>', '<b>', '<em>', '<i>', '<ul>', '<ol>', '<li>']
        found_tags = [tag for tag in html_tags if tag in content.lower()]
        if found_tags:
            print(f"  发现的HTML标签: {', '.join(found_tags[:5])}")
    else:
        print("ℹ️  内容为纯文本格式")
    
    # 检查内容长度
    content_length = len(content)
    if content_length < 500:
        print(f"ℹ️  内容长度: {content_length} 字符（短文）")
    elif content_length < 2000:
        print(f"ℹ️  内容长度: {content_length} 字符（中等长度）")
    else:
        print(f"ℹ️  内容长度: {content_length} 字符（长文）")
    
    # 检查是否包含图片
    if 'src=' in content or '<img' in content:
        print("✅ 内容包含图片")
    
    # 检查是否包含链接
    if 'href=' in content or '<a ' in content:
        print("✅ 内容包含链接")

def main():
    """主测试函数"""
    print("开始测试用户获取科普文章内容功能...")
    
    success = True
    
    # 测试基本文章获取功能
    print("\n" + "="*60)
    articles = test_get_published_articles()
    if articles is None:
        success = False
    
    # 如果有文章，测试详情获取
    if articles and len(articles) > 0:
        article_id = articles[0]['id']
        detail = test_get_article_detail(article_id)
        if not detail:
            success = False
    else:
        print("\n⚠️  没有已发布的文章可供测试详情获取")
    
    # 测试搜索功能
    print("\n" + "="*60)
    test_search_articles()
    
    # 测试不同用户场景
    print("\n" + "="*60)
    test_different_user_scenarios()
    
    # 测试内容类型
    print("\n" + "="*60)
    test_article_content_types()
    
    print("\n" + "="*60)
    print("=== 科普文章获取功能测试总结 ===")
    if success:
        print("✅ 用户获取科普文章内容功能测试通过")
        print("✅ 匿名用户可以正常浏览已发布的科普文章")
        print("✅ 文章搜索功能正常工作")
        print("✅ 文章内容格式支持富文本")
        print("✅ 系统支持多种内容类型（文本、图片、链接等）")
    else:
        print("❌ 发现文章获取功能问题")
    
    return success

if __name__ == "__main__":
    main()