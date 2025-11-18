"""
导出资源类 - 用于管理后台数据导出
"""
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from apps.scales.models import ScaleResult, ScaleConfig
from apps.users.models import User


class ScaleResultResource(resources.ModelResource):
    """量表结果导出资源 - 增强版，支持多种导出格式和题目展平"""

    # 基础信息
    id = fields.Field(column_name='记录ID', attribute='id')
    user_id_display = fields.Field(column_name='用户ID', attribute='user_id')
    user_real_name = fields.Field(
        column_name='用户姓名',
        attribute='user_id',
        widget=ForeignKeyWidget(User, 'real_name')
    )
    user_gender = fields.Field(
        column_name='性别',
        attribute='user_id',
        widget=ForeignKeyWidget(User, 'gender')
    )
    user_age = fields.Field(
        column_name='年龄',
        attribute='user_id',
        widget=ForeignKeyWidget(User, 'age')
    )
    user_education = fields.Field(
        column_name='学历',
        attribute='user_id',
        widget=ForeignKeyWidget(User, 'education')
    )
    user_province = fields.Field(
        column_name='省份',
        attribute='user_id',
        widget=ForeignKeyWidget(User, 'province')
    )
    user_city = fields.Field(
        column_name='城市',
        attribute='user_id',
        widget=ForeignKeyWidget(User, 'city')
    )
    user_district = fields.Field(
        column_name='区县',
        attribute='user_id',
        widget=ForeignKeyWidget(User, 'district')
    )
    user_phone = fields.Field(
        column_name='手机号',
        attribute='user_id',
        widget=ForeignKeyWidget(User, 'phone')
    )
    scale_name = fields.Field(
        column_name='量表名称',
        attribute='scale_config__name',
        widget=ForeignKeyWidget(ScaleConfig, 'name')
    )
    scale_code = fields.Field(
        column_name='量表代码',
        attribute='scale_config__code',
        widget=ForeignKeyWidget(ScaleConfig, 'code')
    )
    scale_type = fields.Field(
        column_name='量表类型',
        attribute='scale_config__type',
        widget=ForeignKeyWidget(ScaleConfig, 'type')
    )
    scale_version = fields.Field(
        column_name='量表版本',
        attribute='scale_config__version',
        widget=ForeignKeyWidget(ScaleConfig, 'version')
    )
    score = fields.Field(column_name='得分', attribute='analysis')
    max_score = fields.Field(column_name='满分', attribute='analysis')
    level = fields.Field(column_name='等级', attribute='analysis')
    is_abnormal = fields.Field(column_name='是否异常', attribute='analysis')
    abnormal_details = fields.Field(column_name='异常详情', attribute='analysis')
    recommendations = fields.Field(column_name='建议', attribute='analysis')
    risk_assessment = fields.Field(column_name='风险评估', attribute='analysis')
    duration_seconds = fields.Field(column_name='答题时长(秒)', attribute='duration_ms')
    duration_minutes = fields.Field(column_name='答题时长(分)', attribute='duration_ms')
    started_at = fields.Field(column_name='开始时间', attribute='started_at')
    completed_at = fields.Field(column_name='完成时间', attribute='completed_at')
    created_at = fields.Field(column_name='创建时间', attribute='created_at')

    # 精简且科研友好的动态题目展平导出
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 仅导出当前筛选结果中所有量表的题目（避免无关冗余）
        self._question_fields = []
        try:
            # 只收集当前数据库所有ScaleConfig的题目（可按需过滤）
            configs = ScaleConfig.objects.all()
            seen = set()
            for config in configs:
                for idx, q in enumerate(config.questions):
                    # 列名：Q序号_题干前10字
                    col = f"Q{idx+1}_{q['question'][:10]}"
                    if col not in seen:
                        seen.add(col)
                        self.fields[col] = fields.Field(column_name=col)
                        self._question_fields.append((config.id, idx, col, q['question']))
        except Exception:
            pass

    def dehydrate(self, obj):
        data = super().dehydrate(obj)
        # 只展平本条记录对应量表的题目
        questions = getattr(obj.scale_config, 'questions', [])
        answers = obj.selected_options or []
        config_id = obj.scale_config.id if obj.scale_config else None
        for q_cfg_id, q_idx, col, qtext in self._question_fields:
            val = ''
            if config_id == q_cfg_id and q_idx < len(questions) and q_idx < len(answers):
                q = questions[q_idx]
                opt_idx = answers[q_idx]
                try:
                    val = q['options'][opt_idx]['text']
                except Exception:
                    val = str(opt_idx)
            data[col] = val
        return data
    
    class Meta:
        model = ScaleResult
        fields = [
            'id', 'user_id_display', 'user_real_name', 'user_gender', 'user_age', 'user_education',
            'user_province', 'user_city', 'user_district', 'user_phone',
            'scale_name', 'scale_code', 'scale_type', 'scale_version',
            'score', 'max_score', 'level', 'is_abnormal', 'abnormal_details', 'recommendations', 'risk_assessment',
            'duration_seconds', 'duration_minutes', 'started_at', 'completed_at', 'created_at',
            'assessment_id'
        ]
        export_order = fields
        skip_unchanged = True
        report_skipped = True
    
    def dehydrate_user_id_display(self, result):
        """用户ID显示（截断）"""
        return str(result.user_id)[:8]
    
    def dehydrate_user_gender(self, result):
        """性别显示"""
        GENDER_MAP = {
            'male': '男',
            'female': '女',
            'other': '其他',
            '': '未知'
        }
        try:
            user = User.objects.get(id=result.user_id)
            return GENDER_MAP.get(user.gender, '未知')
        except User.DoesNotExist:
            return '用户不存在'
    
    def dehydrate_user_age(self, result):
        """年龄显示"""
        try:
            user = User.objects.get(id=result.user_id)
            return str(user.age) if user.age else '未知'
        except User.DoesNotExist:
            return '未知'
    
    def dehydrate_user_education(self, result):
        """学历显示"""
        try:
            user = User.objects.get(id=result.user_id)
            return user.education or '未知'
        except User.DoesNotExist:
            return '未知'
    
    def dehydrate_user_province(self, result):
        """省份显示"""
        try:
            user = User.objects.get(id=result.user_id)
            return user.province or '未知'
        except User.DoesNotExist:
            return '未知'
    
    def dehydrate_user_city(self, result):
        """城市显示"""
        try:
            user = User.objects.get(id=result.user_id)
            return user.city or '未知'
        except User.DoesNotExist:
            return '未知'
    
    def dehydrate_user_district(self, result):
        """区县显示"""
        try:
            user = User.objects.get(id=result.user_id)
            return user.district or '未知'
        except User.DoesNotExist:
            return '未知'
    
    def dehydrate_user_phone(self, result):
        """手机号显示（隐私处理）"""
        try:
            user = User.objects.get(id=result.user_id)
            phone = user.phone or ''
            if len(phone) >= 11:
                return phone[:3] + '****' + phone[-4:]
            return phone or '无'
        except User.DoesNotExist:
            return '用户不存在'
    
    def dehydrate_score(self, result):
        """提取得分"""
        return result.analysis.get('score', 'N/A') if result.analysis else 'N/A'
    
    def dehydrate_max_score(self, result):
        """提取满分"""
        return result.analysis.get('max_score', 'N/A') if result.analysis else 'N/A'
    
    def dehydrate_level(self, result):
        """提取等级"""
        return result.analysis.get('level', 'N/A') if result.analysis else 'N/A'
    
    def dehydrate_is_abnormal(self, result):
        """提取是否异常"""
        abnormal = result.analysis.get('is_abnormal', False) if result.analysis else False
        return '异常' if abnormal else '正常'
    
    def dehydrate_abnormal_details(self, result):
        """提取异常详情"""
        if not result.analysis:
            return '无'
        
        abnormal_details = result.analysis.get('abnormal_details', [])
        if isinstance(abnormal_details, list):
            return '; '.join(abnormal_details) if abnormal_details else '无异常'
        return str(abnormal_details) if abnormal_details else '无异常'
    
    def dehydrate_recommendations(self, result):
        """提取建议"""
        recommendations = result.analysis.get('recommendations', []) if result.analysis else []
        if isinstance(recommendations, list):
            return '; '.join(recommendations) if recommendations else '无建议'
        return str(recommendations) if recommendations else '无建议'
    
    def dehydrate_risk_assessment(self, result):
        """提取风险评估"""
        if not result.analysis:
            return '无评估'
        
        risk_level = result.analysis.get('risk_level', '未知')
        risk_factors = result.analysis.get('risk_factors', [])
        
        if isinstance(risk_factors, list) and risk_factors:
            return f"{risk_level} ({'; '.join(risk_factors)})"
        return risk_level
    
    def dehydrate_duration_seconds(self, result):
        """转换时长为秒"""
        return result.duration_ms // 1000 if result.duration_ms else 0
    
    def dehydrate_duration_minutes(self, result):
        """转换时长为分钟"""
        return round(result.duration_ms / 60000, 1) if result.duration_ms else 0.0
    
    def dehydrate_assessment_id(self, result):
        """智能测评ID"""
        return result.smart_assessment.id if result.smart_assessment else '无'


