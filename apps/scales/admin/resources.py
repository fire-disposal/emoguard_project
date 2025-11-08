"""
导出资源类 - 用于管理后台数据导出
"""
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from apps.scales.models import ScaleResult, ScaleConfig, SmartAssessmentRecord
from apps.users.models import User


class ScaleResultResource(resources.ModelResource):
    """量表结果导出资源 - 增强版，支持多种导出格式"""
    
    # 基础信息
    id = fields.Field(column_name='记录ID', attribute='id')
    user_id_display = fields.Field(column_name='用户ID', attribute='user_id')
    
    # 用户基本信息（带缓存优化）
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
    
    # 量表基本信息
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
    
    # 结果信息（增强版）
    score = fields.Field(column_name='得分', attribute='analysis')
    max_score = fields.Field(column_name='满分', attribute='analysis')
    level = fields.Field(column_name='等级', attribute='analysis')
    is_abnormal = fields.Field(column_name='是否异常', attribute='analysis')
    abnormal_details = fields.Field(column_name='异常详情', attribute='analysis')
    recommendations = fields.Field(column_name='建议', attribute='analysis')
    risk_assessment = fields.Field(column_name='风险评估', attribute='analysis')
    
    # 时间信息（增强版）
    duration_seconds = fields.Field(column_name='答题时长(秒)', attribute='duration_ms')
    duration_minutes = fields.Field(column_name='答题时长(分)', attribute='duration_ms')
    started_at = fields.Field(column_name='开始时间', attribute='started_at')
    completed_at = fields.Field(column_name='完成时间', attribute='completed_at')
    created_at = fields.Field(column_name='创建时间', attribute='created_at')
    
    # 智能测评关联
    assessment_id = fields.Field(
        column_name='智能测评ID',
        attribute='smart_assessment__id',
        widget=ForeignKeyWidget(SmartAssessmentRecord, 'id')
    )
    
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


class SmartAssessmentResource(resources.ModelResource):
    """智能测评导出资源"""
    
    id = fields.Field(column_name='测评ID', attribute='id')
    user_id_display = fields.Field(column_name='用户ID', attribute='user_id')
    user_real_name = fields.Field(
        column_name='用户姓名',
        attribute='user_id',
        widget=ForeignKeyWidget(User, 'real_name')
    )
    status = fields.Field(column_name='状态', attribute='status')
    current_scale_index = fields.Field(column_name='当前进度', attribute='current_scale_index')
    scale_count = fields.Field(column_name='量表数量', attribute='scale_scores')
    
    # 结果信息
    final_conclusion = fields.Field(column_name='最终结论', attribute='final_result')
    risk_level = fields.Field(column_name='风险等级', attribute='final_result')
    abnormal_count = fields.Field(column_name='异常项目数', attribute='final_result')
    total_score = fields.Field(column_name='总分', attribute='final_result')
    
    # 时间信息
    started_at = fields.Field(column_name='开始时间', attribute='started_at')
    completed_at = fields.Field(column_name='完成时间', attribute='completed_at')
    created_at = fields.Field(column_name='创建时间', attribute='created_at')
    total_duration_minutes = fields.Field(column_name='总时长(分钟)', attribute='started_at')
    
    class Meta:
        model = SmartAssessmentRecord
        fields = [
            'id', 'user_id_display', 'user_real_name', 'status', 'current_scale_index', 'scale_count',
            'final_conclusion', 'risk_level', 'abnormal_count', 'total_score',
            'started_at', 'completed_at', 'created_at', 'total_duration_minutes'
        ]
        export_order = fields
    
    def dehydrate_user_id_display(self, assessment):
        """用户ID显示（截断）"""
        return str(assessment.user_id)[:8]
    
    def dehydrate_user_real_name(self, assessment):
        """用户姓名"""
        try:
            user = User.objects.get(id=assessment.user_id)
            return user.real_name or '匿名用户'
        except User.DoesNotExist:
            return '用户不存在'
    
    def dehydrate_scale_count(self, assessment):
        """量表数量"""
        return len(assessment.scale_scores) if assessment.scale_scores else 0
    
    def dehydrate_final_conclusion(self, assessment):
        """最终结论"""
        return assessment.final_result.get('conclusion', '未知结论') if assessment.final_result else '无结论'
    
    def dehydrate_risk_level(self, assessment):
        """风险等级"""
        return assessment.final_result.get('risk_level', '未知风险') if assessment.final_result else '无评估'
    
    def dehydrate_abnormal_count(self, assessment):
        """异常项目数"""
        return assessment.final_result.get('abnormal_count', 0) if assessment.final_result else 0
    
    def dehydrate_total_score(self, assessment):
        """总分"""
        return assessment.final_result.get('total_score', 0) if assessment.final_result else 0
    
    def dehydrate_total_duration_minutes(self, assessment):
        """总时长（分钟）"""
        if assessment.completed_at and assessment.started_at:
            duration = assessment.get_total_duration()
            return round(duration / 60000, 1)
        return 0.0