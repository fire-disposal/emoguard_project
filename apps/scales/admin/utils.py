"""
管理员工具函数 - 提供常用的管理功能
"""
from django.utils.html import format_html
from apps.users.models import User


def get_user_info(user_id):
    """获取用户信息（工具函数）"""
    # 性别映射
    GENDER_MAP = {
        'male': '男',
        'female': '女',
        'other': '其他',
        '': '未知'
    }
    
    try:
        user = User.objects.get(id=user_id)
        return {
            'real_name': user.real_name or '匿名用户',
            'age': user.age or '未知',
            'gender': GENDER_MAP.get(user.gender, '未知'),
            'education': user.education or '未知',
            'province': user.province or '未知',
            'city': user.city or '未知',
            'district': user.district or '未知',
            'phone': user.phone or '无'
        }
    except User.DoesNotExist:
        return {
            'real_name': '用户不存在',
            'age': '未知',
            'gender': '未知',
            'education': '未知',
            'province': '未知',
            'city': '未知',
            'district': '未知',
            'phone': '用户不存在'
        }


def format_user_info_html(user_info, show_full=True):
    """格式化用户信息为HTML（主题友好）"""
    if show_full:
        return format_html(
            '<div class="user-info">'
            '<div class="user-name">{}</div>'
            '<div class="user-details">{}岁 · {}</div>'
            '<div class="user-location">{} · {}</div>'
            '</div>',
            user_info['real_name'],
            user_info['age'],
            user_info['gender'],
            user_info['education'],
            f"{user_info['province']} {user_info['city']}"
        )
    else:
        return format_html(
            '<div class="user-info-compact">'
            '<div class="user-name">{}</div>'
            '<div class="user-details">{}岁 · {}</div>'
            '</div>',
            user_info['real_name'],
            user_info['age'],
            user_info['gender']
        )


def format_status_badge(status, status_type='assessment'):
    """格式化状态标签（主题友好）"""
    if status_type == 'assessment':
        css_classes = {
            'in_progress': 'status-in-progress',
            'completed': 'status-completed',
            'abandoned': 'status-abandoned'
        }
    else:  # scale_config
        css_classes = {
            'draft': 'status-draft',
            'active': 'status-active'
        }
    
    css_class = css_classes.get(status, 'status-default')
    text = {
        'in_progress': '进行中',
        'completed': '已完成',
        'abandoned': '已放弃',
        'draft': '草稿',
        'active': '启用'
    }.get(status, status)
    
    return format_html(
        '<span class="status-badge {}">{}</span>',
        css_class, text
    )


def format_progress_bar(current, total, width=100):
    """格式化进度条（主题友好）"""
    if total == 0:
        progress_percent = 0
    else:
        progress_percent = min(int((current / total) * 100), 100)
    
    return format_html(
        '<div class="progress-container" style="width: {}px;">'
        '<div class="progress-bar-bg">'
        '<div class="progress-bar-fill" style="width: {}%;"></div>'
        '</div>'
        '<div class="progress-text">{}%</div>'
        '</div>',
        width, progress_percent, progress_percent
    )


def format_duration(duration_ms):
    """格式化时长显示"""
    if not duration_ms:
        return "0秒"
    
    seconds = duration_ms // 1000
    if seconds < 60:
        return f"{seconds}秒"
    else:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}分{remaining_seconds}秒"


def format_phone_privacy(phone):
    """手机号隐私处理"""
    if not phone:
        return '无'
    
    if len(phone) >= 11:
        return phone[:3] + '****' + phone[-4:]
    return phone


def get_risk_color(risk_level):
    """获取风险等级对应的颜色"""
    risk_colors = {
        '高风险': '#e74c3c',
        '中风险': '#f39c12',
        '低风险': '#27ae60'
    }
    return risk_colors.get(risk_level, '#95a5a6')


def format_risk_assessment(final_result):
    """格式化风险评估显示"""
    if not final_result or not isinstance(final_result, dict):
        return '无评估数据'
    
    conclusion = final_result.get('conclusion', '未知结论')
    risk_level = final_result.get('risk_level', '未知风险')
    abnormal_count = final_result.get('abnormal_count', 0)
    total_score = final_result.get('total_score', 0)
    
    risk_color = get_risk_color(risk_level)
    
    return {
        'conclusion': conclusion,
        'risk_level': risk_level,
        'abnormal_count': abnormal_count,
        'total_score': total_score,
        'risk_color': risk_color
    }