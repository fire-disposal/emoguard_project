#!/usr/bin/env python3
"""
创建测试科普文章
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.articles.models import Article
from django.utils import timezone

def create_test_articles():
    """创建测试科普文章"""
    print("=== 创建测试科普文章 ===")
    
    # 测试文章内容
    test_articles = [
        {
            "title": "如何识别和应对抑郁症？",
            "content": """<p>抑郁症是一种常见的心理健康问题，影响着全球数百万人的生活。了解抑郁症的症状和应对方法对于维护心理健康至关重要。</p>

<h3>抑郁症的常见症状：</h3>
<ul>
<li>持续的悲伤、焦虑或"空虚"情绪</li>
<li>对曾经感兴趣的活动失去兴趣或愉悦感</li>
<li>感到绝望、悲观或无助</li>
<li>精力减少、疲劳感增加</li>
<li>难以集中注意力、记忆力下降</li>
</ul>

<h3>应对策略：</h3>
<p><strong>1. 寻求专业帮助</strong><br>
心理咨询和治疗是应对抑郁症的有效方法。认知行为疗法（CBT）和药物治疗都可能有所帮助。</p>

<p><strong>2. 建立支持网络</strong><br>
与家人朋友保持联系，分享你的感受。社会支持对康复过程非常重要。</p>

<p><strong>3. 保持健康生活方式</strong><br>
规律运动、均衡饮食、充足睡眠都有助于改善情绪状态。</p>

<p><strong>4. 练习正念冥想</strong><br>
正念练习可以帮助你更好地觉察和管理情绪。</p>

<p>记住，寻求帮助是勇敢的行为。如果你或你认识的人正在经历抑郁症状，请不要犹豫，立即寻求专业帮助。</p>""",
            "cover_image": "https://example.com/images/depression-help.jpg",
            "status": "published"
        },
        {
            "title": "焦虑管理：日常生活中的放松技巧",
            "content": """<p>在快节奏的现代生活中，焦虑感变得越来越普遍。学会管理焦虑不仅能够改善生活质量，还能增强心理韧性。</p>

<h3>理解焦虑</h3>
<p>焦虑是身体对压力的自然反应，适度的焦虑可以帮助我们保持警觉和动力。但当焦虑变得过度或持续时，就可能影响日常生活。</p>

<h3>即时放松技巧</h3>
<p><strong>深呼吸练习</strong></p>
<p>4-7-8呼吸法：吸气4秒，屏息7秒，呼气8秒。重复3-4次。</p>

<p><strong>渐进性肌肉放松</strong></p>
<p>从脚趾开始，逐步紧张和放松身体各部位的肌肉。</p>

<p><strong>5-4-3-2-1接地技巧</strong></p>
<ul>
<li>说出5个你能看到的东西</li>
<li>说出4个你能触摸到的东西</li>
<li>说出3个你能听到的声音</li>
<li>说出2个你能闻到的气味</li>
<li>说出1个你能尝到的味道</li>
</ul>

<h3>长期管理策略</h3>
<p><strong>建立规律作息</strong><br>
保持规律的睡眠和饮食时间，有助于稳定情绪。</p>

<p><strong>限制咖啡因和酒精</strong><br>
这些物质可能加重焦虑症状。</p>

<p><strong>定期运动</strong><br>
运动是天然的抗焦虑药物，每周至少150分钟中等强度运动。</p>

<p>通过这些技巧的练习，你可以更好地管理日常生活中的焦虑感。</p>""",
            "cover_image": "https://example.com/images/anxiety-relief.jpg",
            "status": "published"
        },
        {
            "title": "认知训练：保持大脑活力的方法",
            "content": """<p>随着年龄的增长，保持大脑活力和认知功能变得越来越重要。好消息是，通过适当的训练和生活方式调整，我们可以有效地维护和提升认知能力。</p>

<h3>认知训练的重要性</h3>
<p>认知训练就像给大脑做运动，可以帮助：</p>
<ul>
<li>提高记忆力和注意力</li>
<li>增强学习能力</li>
<li>延缓认知衰退</li>
<li>改善日常生活功能</li>
</ul>

<h3>实用的认知训练方法</h3>
<p><strong>1. 记忆练习</strong></p>
<p>尝试记住购物清单、电话号码或诗歌。使用联想记忆法，将新信息与已知事物联系起来。</p>

<p><strong>2. 注意力训练</strong></p>
<p>练习专注做一件事，避免多任务处理。可以尝试冥想或正念练习。</p>

<p><strong>3. 学习新技能</strong></p>
<p>学习新语言、乐器或手工艺。新技能的学习能够激活大脑的不同区域。</p>

<p><strong>4. 逻辑推理游戏</strong></p>
<p>数独、象棋、拼图等游戏能够锻炼逻辑思维和问题解决能力。</p>

<h3>生活方式建议</h3>
<p><strong>健康饮食</strong><br>
地中海饮食模式被认为有益于大脑健康，包括大量蔬菜、水果、全谷物和健康脂肪。</p>

<p><strong>社交活动</strong><br>
保持活跃的社交生活，参与社区活动，与他人交流互动。</p>

<p><strong>充足睡眠</strong><br>
每晚7-9小时的优质睡眠对认知功能至关重要。</p>

<p>记住，认知训练是一个持续的过程。保持耐心和一致性，你会看到积极的改变。</p>""",
            "cover_image": "https://example.com/images/brain-training.jpg",
            "status": "published"
        },
        {
            "title": "情绪调节：如何成为情绪的主人",
            "content": """<p>情绪是人类体验的重要组成部分，学会调节情绪是心理健康的关键技能。当我们能够有效地管理情绪时，我们就能更好地应对生活中的挑战。</p>

<h3>情绪调节的基础</h3>
<p>情绪调节不是压抑情绪，而是理解、接受并适当地表达情绪。这包括：</p>
<ul>
<li>识别和命名情绪</li>
<li>理解情绪的触发因素</li>
<li>选择适当的应对策略</li>
<li>在需要时寻求支持</li>
</ul>

<h3>实用的情绪调节技巧</h3>
<p><strong>1. 情绪标记</strong></p>
<p>当情绪出现时，尝试准确地标记它。不是简单地说"我感觉不好"，而是具体地说"我感到失望"或"我感到沮丧"。</p>

<p><strong>2. 情绪日记</strong></p>
<p>记录每天的情绪变化，包括触发因素、强度和处理方式。这有助于识别情绪模式。</p>

<p><strong>3. 认知重构</strong></p>
<p>挑战消极的思维模式，寻找更平衡、现实的观点。问自己："这个想法有证据支持吗？"</p>

<p><strong>4. 情绪释放技巧</strong></p>
<ul>
<li>深呼吸和放松练习</li>
<li>身体运动或锻炼</li>
<li>创造性表达（绘画、写作、音乐）</li>
<li>与信任的人交谈</li>
</ul>

<h3>建立情绪韧性</h3>
<p><strong>自我关怀</strong><br>
对自己保持友善和理解，特别是在困难时期。</p>

<p><strong>设定边界</strong><br>
学会说"不"，保护自己的情绪能量。</p>

<p><strong>培养积极情绪</strong><br>
有意识地培养感恩、希望和喜悦等积极情绪。</p>

<p>记住，情绪调节是一个学习过程。对自己保持耐心，庆祝每一个小的进步。</p>""",
            "cover_image": "https://example.com/images/emotion-regulation.jpg",
            "status": "published"
        }
    ]
    
    created_count = 0
    
    for article_data in test_articles:
        try:
            # 检查是否已存在相同标题的文章
            if Article.objects.filter(title=article_data["title"]).exists():
                print(f"⚠️  文章已存在: {article_data['title']}")
                continue
            
            article = Article.objects.create(
                title=article_data["title"],
                content=article_data["content"],
                cover_image=article_data["cover_image"],
                publish_time=timezone.now(),
                status=article_data["status"]
            )
            created_count += 1
            print(f"✅ 创建文章: {article.title} (ID: {article.id})")
            
        except Exception as e:
            print(f"❌ 创建文章失败: {article_data['title']} - {e}")
    
    print(f"\n=== 创建完成 ===")
    print(f"成功创建 {created_count} 篇测试文章")
    
    # 显示最终统计
    total_published = Article.objects.filter(status='published').count()
    total_draft = Article.objects.filter(status='draft').count()
    print(f"当前文章统计:")
    print(f"  已发布: {total_published} 篇")
    print(f"  草稿: {total_draft} 篇")
    print(f"  总计: {total_published + total_draft} 篇")

def check_existing_articles():
    """检查现有文章"""
    print("=== 检查现有文章 ===")
    
    articles = Article.objects.all()
    print(f"数据库中共有 {len(articles)} 篇文章")
    
    if articles:
        print("\n文章列表:")
        for article in articles:
            print(f"  ID: {article.id}")
            print(f"  标题: {article.title}")
            print(f"  状态: {article.status}")
            print(f"  发布时间: {article.publish_time}")
            print(f"  内容长度: {len(article.content)} 字符")
            print("-" * 40)
    
    return articles

if __name__ == "__main__":
    print("开始创建测试科普文章...")
    
    # 先检查现有文章
    existing = check_existing_articles()
    
    # 如果没有已发布的文章，创建测试文章
    published_count = Article.objects.filter(status='published').count()
    if published_count == 0:
        print("\n没有已发布的文章，创建测试文章...")
        create_test_articles()
    else:
        print(f"\n已有 {published_count} 篇已发布文章，无需创建")
    
    print("\n完成!")