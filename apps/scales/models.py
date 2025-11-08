from django.db import models
from django.core.exceptions import ValidationError
import yaml

class ScaleConfig(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('active', '启用'),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, verbose_name="量表名称")
    code = models.CharField(max_length=64, unique=True, verbose_name="量表代码")
    version = models.CharField(max_length=32, verbose_name="版本号")
    description = models.TextField(blank=True, verbose_name="描述")
    type = models.CharField(max_length=64, verbose_name="类型")
    questions = models.JSONField(default=list, verbose_name="问题列表")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft', verbose_name="状态")
    yaml_config = models.TextField(blank=True, verbose_name="YAML 配置")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 用于跟踪字段变化
    _original_yaml = None
    _fields_modified = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 保存原始 YAML 值用于检测变化
        self._original_yaml = self.yaml_config

    def _parse_yaml_to_fields(self):
        """从 YAML 配置解析到基础字段"""
        if not self.yaml_config or not self.yaml_config.strip():
            return
        
        try:
            data = yaml.safe_load(self.yaml_config)
            if not data:
                raise ValidationError("YAML 配置不能为空")
            
            # 验证必填字段
            required_fields = ['code', 'questions']
            for field in required_fields:
                if field not in data:
                    raise ValidationError(f"YAML 配置必须包含 '{field}' 字段")
            
            if not data['questions'] or not isinstance(data['questions'], list):
                raise ValidationError("YAML 配置必须包含非空的 'questions' 字段")
            
            # 验证问题结构
            for i, question in enumerate(data['questions']):
                if not isinstance(question, dict):
                    raise ValidationError(f"问题 {i+1} 必须是字典格式")
                if 'id' not in question:
                    raise ValidationError(f"问题 {i+1} 必须包含 'id' 字段")
                if 'question' not in question:
                    raise ValidationError(f"问题 {i+1} 必须包含 'question' 字段")
                if 'options' not in question or not isinstance(question['options'], list):
                    raise ValidationError(f"问题 {i+1} 必须包含 'options' 列表")
                
                # 验证选项结构
                for j, option in enumerate(question['options']):
                    if not isinstance(option, dict):
                        raise ValidationError(f"问题 {i+1} 的选项 {j+1} 必须是字典格式")
                    if 'text' not in option:
                        raise ValidationError(f"问题 {i+1} 的选项 {j+1} 必须包含 'text' 字段")
                    if 'value' not in option:
                        raise ValidationError(f"问题 {i+1} 的选项 {j+1} 必须包含 'value' 字段")
            
            # 将 value 字段转换为字符串
            for question in data['questions']:
                if 'options' in question:
                    for option in question['options']:
                        if 'value' in option:
                            option['value'] = str(option['value'])
            
            # 更新字段
            self.name = data.get('name', '')
            self.code = data.get('code', '')
            self.version = data.get('version', '1.0')
            self.description = data.get('description', '')
            self.type = data.get('type', '')
            self.questions = data['questions']
            self.status = data.get('status', 'draft')
            
        except yaml.YAMLError as e:
            raise ValidationError(f"YAML 格式错误: {str(e)}")
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"解析 YAML 配置失败: {str(e)}")

    def _sync_fields_to_yaml(self):
        """从基础字段同步到 YAML 配置"""
        yaml_data = {
            'name': self.name,
            'code': self.code,
            'version': self.version,
            'description': self.description,
            'type': self.type,
            'status': self.status,
            'questions': self.questions
        }
        
        # 转换为 YAML 格式
        self.yaml_config = yaml.dump(
            yaml_data,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False
        )

    def clean(self):
        """验证模型数据"""
        try:
            super().clean()
            
            # 检测 YAML 是否被修改
            yaml_modified = self.yaml_config != self._original_yaml
            
            # 检测基础字段是否被修改（排除新建情况）
            if self.pk:
                try:
                    old_instance = ScaleConfig.objects.get(pk=self.pk)
                    self._fields_modified = (
                        old_instance.name != self.name or
                        old_instance.code != self.code or
                        old_instance.version != self.version or
                        old_instance.description != self.description or
                        old_instance.type != self.type or
                        old_instance.status != self.status or
                        old_instance.questions != self.questions
                    )
                except ScaleConfig.DoesNotExist:
                    self._fields_modified = False
            
            # 优先级：YAML 修改 > 基础字段修改
            if yaml_modified:
                # YAML 被修改，解析并更新基础字段
                self._parse_yaml_to_fields()
            elif self._fields_modified:
                # 基础字段被修改，反向同步到 YAML
                self._sync_fields_to_yaml()
            elif not self.yaml_config and self.questions:
                # 初次创建或 YAML 为空但有 questions，生成 YAML
                self._sync_fields_to_yaml()
                
        except Exception as e:
            # 增强错误处理，避免静默失败
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"ScaleConfig 验证失败: {str(e)}")
            raise

    def save(self, *args, **kwargs):
        """保存前执行验证和同步"""
        try:
            self.full_clean()  # 触发 clean 方法
            super().save(*args, **kwargs)
            # 保存后更新原始 YAML 值
            self._original_yaml = self.yaml_config
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"ScaleConfig 保存失败: {str(e)}")
            raise

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "量表配置"
        verbose_name_plural = "量表配置"


class SmartAssessmentRecord(models.Model):
    """智能测评记录 - 后端主导的测评流程"""
    STATUS_CHOICES = (
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('abandoned', '已放弃'),
    )
    
    id = models.AutoField(primary_key=True)
    user_id = models.UUIDField(verbose_name='用户ID', db_index=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='in_progress', verbose_name='状态')
    current_scale_index = models.IntegerField(default=0, verbose_name='当前量表索引')
    
    # 子量表回答选项数组 - 存储每个子量表的用户回答选项
    scale_responses = models.JSONField(default=list, blank=True, verbose_name='子量表回答选项')
    
    # 子量表得分与评估数组 - 存储每个子量表的计算后得分与评估
    scale_scores = models.JSONField(default=list, blank=True, verbose_name='子量表得分与评估')
    
    # 最终结果
    final_result = models.JSONField(default=dict, blank=True, verbose_name='最终结果')
    
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_total_duration(self):
        """获取总耗时（毫秒）"""
        if self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() * 1000)
        return 0
    
    def add_scale_response(self, scale_config_id: int, selected_options: list, analysis: dict):
        """添加子量表回答和得分评估"""
        # 验证数据完整性
        if not isinstance(selected_options, list):
            raise ValueError("selected_options 必须是列表")
        
        if not isinstance(analysis, dict):
            raise ValueError("analysis 必须是字典")
        
        # 使用当前时间而不是依赖updated_at
        from django.utils import timezone
        current_time = timezone.now().isoformat()
        
        # 添加回答选项（修正：带上 analysis 字段，便于流程判断）
        self.scale_responses.append({
            'scale_config_id': scale_config_id,
            'selected_options': selected_options,
            'created_at': current_time,
            'analysis': analysis  # 新增，确保流程判断可用
        })
        
        # 添加得分评估
        self.scale_scores.append({
            'scale_config_id': scale_config_id,
            'score': analysis.get('score'),
            'level': analysis.get('level'),
            'is_abnormal': analysis.get('is_abnormal', False),
            'recommendations': analysis.get('recommendations', []),
            'scale_name': analysis.get('scale_name', ''),
            'scale_code': analysis.get('scale_code', ''),
            'created_at': current_time
        })
    
    def get_scale_response(self, scale_config_id: int) -> dict:
        """获取指定子量表的回答选项"""
        for response in self.scale_responses:
            if response.get('scale_config_id') == scale_config_id:
                return response
        return {}
    
    def get_scale_score(self, scale_config_id: int) -> dict:
        """获取指定子量表的得分评估"""
        for score in self.scale_scores:
            if score.get('scale_config_id') == scale_config_id:
                return score
        return {}
    
    def validate_data_consistency(self):
        """验证数据一致性（容错版本）"""
        errors = []
        
        try:
            # 确保数据是列表类型
            if not isinstance(self.scale_responses, list):
                self.scale_responses = []
            if not isinstance(self.scale_scores, list):
                self.scale_scores = []
            
            # 验证scale_responses和scale_scores数量一致性
            if len(self.scale_responses) != len(self.scale_scores):
                errors.append(f"回答选项数量({len(self.scale_responses)})与得分评估数量({len(self.scale_scores)})不一致")
            
            # 验证scale_config_id一致性
            response_ids = set()
            score_ids = set()
            
            try:
                for resp in self.scale_responses:
                    if isinstance(resp, dict) and 'scale_config_id' in resp:
                        response_ids.add(resp.get('scale_config_id'))
            except Exception:
                pass  # 忽略格式错误
            
            try:
                for score in self.scale_scores:
                    if isinstance(score, dict) and 'scale_config_id' in score:
                        score_ids.add(score.get('scale_config_id'))
            except Exception:
                pass  # 忽略格式错误
            
            if response_ids != score_ids:
                missing_in_scores = response_ids - score_ids
                missing_in_responses = score_ids - response_ids
                if missing_in_scores:
                    errors.append(f"以下量表ID有回答选项但无得分评估: {missing_in_scores}")
                if missing_in_responses:
                    errors.append(f"以下量表ID有得分评估但无回答选项: {missing_in_responses}")
            
            # 验证状态一致性
            if self.status == 'completed':
                if not self.completed_at:
                    errors.append("已完成状态的测评缺少完成时间")
                if not self.final_result:
                    errors.append("已完成状态的测评缺少最终结果")
                if len(self.scale_scores) == 0:
                    errors.append("已完成状态的测评缺少量表得分数据")
            
            # 验证进度一致性
            expected_progress = len(self.scale_responses)
            if self.current_scale_index != expected_progress:
                errors.append(f"当前进度索引({self.current_scale_index})与实际回答数量({expected_progress})不一致")
                
        except Exception as e:
            errors.append(f"数据一致性验证过程中发生错误: {str(e)}")
        
        return errors
    
    def clean(self):
        """模型验证（简化版本，避免阻塞正常流程）"""
        super().clean()
        
        # 只在admin操作或特定情况下进行严格的数据一致性验证
        # 正常保存时不进行严格检查，避免阻塞流程
        if self.status == 'completed':
            # 只检查关键字段是否存在
            if not self.completed_at:
                from django.core.exceptions import ValidationError
                raise ValidationError("已完成状态的测评必须设置完成时间")
            
            if not self.final_result:
                from django.core.exceptions import ValidationError
                raise ValidationError("已完成状态的测评必须设置最终结果")
    
    def __str__(self):
        return f"智能测评-{self.id} 用户:{self.user_id} ({self.get_status_display()})"
    
    class Meta:
        verbose_name = "智能测评记录"
        verbose_name_plural = "智能测评记录"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]


class ScaleResult(models.Model):
    STATUS_CHOICES = (
        ('completed', '已完成'),
    )
    id = models.AutoField(primary_key=True)
    user_id = models.UUIDField()
    scale_config = models.ForeignKey(ScaleConfig, on_delete=models.CASCADE, related_name='results')
    selected_options = models.JSONField(default=list)
    conclusion = models.TextField(blank=True, verbose_name='结论摘要')
    duration_ms = models.IntegerField()
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='completed')
    analysis = models.JSONField(default=dict, blank=True)
    
    # 关联到智能测评（可选，兼容单量表模式）
    smart_assessment = models.ForeignKey(
        SmartAssessmentRecord, 
        on_delete=models.CASCADE, 
        related_name='scale_results',
        null=True, 
        blank=True,
        verbose_name='所属智能测评'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Result-{self.id} 用户:{self.user_id}"

    class Meta:
        verbose_name = "量表结果"
        verbose_name_plural = "量表结果"
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['smart_assessment', 'scale_config']),
        ]