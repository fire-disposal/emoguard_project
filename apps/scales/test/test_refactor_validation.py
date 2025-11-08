"""
重构验证测试 - 确保重构后的功能完整性
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.scales.models import ScaleConfig, ScaleResult
from apps.scales.services import (
    UserService, ScaleResultService, AssessmentFlowService, ResponseService
)
from apps.scales.calculators import get_calculator, FlowStepCalculator, ConclusionCalculator

User = get_user_model()


class RefactorValidationTest(TestCase):
    """重构验证测试类"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建测试用户
        self.test_user = User.objects.create_user(
            id="11111111-1111-1111-1111-111111111111",
            username="testuser",
            password="testpass123"
        )
        
        # 创建SCD量表配置
        self.scd_config = ScaleConfig.objects.create(
            name="主观认知下降量表",
            code="scd_q9",
            version="1.0",
            type="SCD",
            questions=[
                {
                    "id": 1,
                    "question": "您是否有记忆问题？",
                    "options": [
                        {"text": "没有", "value": "0"},
                        {"text": "偶尔", "value": "1"},
                        {"text": "经常", "value": "2"}
                    ]
                }
            ],
            status="active"
        )
        
        # 创建MMSE量表配置
        self.mmse_config = ScaleConfig.objects.create(
            name="简易智能状态检查",
            code="mmse",
            version="1.0",
            type="MMSE",
            questions=[
                {
                    "id": 1,
                    "question": "现在是哪一年？",
                    "options": [
                        {"text": "正确", "value": "1"},
                        {"text": "错误", "value": "0"}
                    ]
                }
            ],
            status="active"
        )
    
    def test_user_service_get_profile(self):
        """测试用户服务获取用户资料"""
        profile = UserService.get_user_profile(str(self.test_user.id))
        
        self.assertIsNotNone(profile)
        self.assertIn('education', profile)
        self.assertIn('age', profile)
        self.assertIn('gender', profile)
    
    def test_scale_result_service_create_result(self):
        """测试量表结果服务创建结果"""
        result = ScaleResultService.create_scale_result(
            user_id=str(self.test_user.id),
            scale_config_id=self.scd_config.id,
            selected_options=[0],
            duration_ms=30000,
            started_at="2024-01-01T10:00:00",
            completed_at="2024-01-01T10:00:30"
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.user_id, str(self.test_user.id))
        self.assertEqual(result.scale_config, self.scd_config)
        self.assertEqual(result.selected_options, [0])
        self.assertIn('score', result.analysis)
        self.assertIn('level', result.analysis)
    
    def test_assessment_flow_service_create_group(self):
        """测试评估流程服务创建分组"""
        group = AssessmentFlowService.create_assessment_group(
            user_id=str(self.test_user.id)
        )
        
        self.assertIsNotNone(group)
        self.assertEqual(group.user_id, str(self.test_user.id))
        self.assertEqual(group.flow_type, 'cognitive_assessment')
        self.assertEqual(group.status, 'in_progress')
    
    def test_flow_step_calculator(self):
        """测试流程步骤计算器"""
        calculator = FlowStepCalculator()
        
        # 测试空完成情况
        result = calculator.calculate_next_step([], {})
        self.assertFalse(result['completed'])
        self.assertIn('scd_q9', result['next_scales'])
        
        # 测试SCD正常情况
        scale_results = {
            'scd_q9': {'is_abnormal': False, 'score': 3}
        }
        result = calculator.calculate_next_step(['scd_q9'], scale_results)
        self.assertTrue(result['completed'])
        self.assertEqual(result['next_scales'], [])
    
    def test_conclusion_calculator(self):
        """测试结论计算器"""
        calculator = ConclusionCalculator()
        
        # 测试正常情况
        analysis_data = {
            'scd_q9': {'is_abnormal': False, 'score': 3}
        }
        result = calculator.calculate(analysis_data)
        
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['conclusion'], '正常人群')
        self.assertEqual(result['risk_level'], '低风险')
    
    def test_response_service_build_scale_result_response(self):
        """测试响应服务构建量表结果响应"""
        # 创建量表结果
        from django.utils import timezone
        result = ScaleResult.objects.create(
            user_id=str(self.test_user.id),
            scale_config=self.scd_config,
            selected_options=[0],
            conclusion="测试结论",
            duration_ms=30000,
            started_at=timezone.now(),
            completed_at=timezone.now(),
            status='completed',
            analysis={'score': 3, 'level': '正常'}
        )
        
        response_data = ResponseService.build_scale_result_response(result)
        
        self.assertIn('id', response_data)
        self.assertIn('user_id', response_data)
        self.assertIn('scale_config', response_data)
        self.assertIn('analysis', response_data)
        self.assertEqual(response_data['conclusion'], "测试结论")
    
    def test_get_calculator_factory(self):
        """测试计算器工厂方法"""
        calculator = get_calculator(self.scd_config)
        
        self.assertIsNotNone(calculator)
        self.assertEqual(calculator.scale_config, self.scd_config)
    
    def test_assessment_flow_integration(self):
        """测试评估流程集成"""
        # 创建评估分组
        group = AssessmentFlowService.create_assessment_group(
            user_id=str(self.test_user.id)
        )
        
        # 获取下一步步骤
        next_step = AssessmentFlowService.get_next_step(group)
        self.assertFalse(next_step['completed'])
        self.assertIn('scd_q9', next_step['next_scales'])
        
        # 提交SCD结果
        result, is_completed = AssessmentFlowService.submit_scale_result(
            group=group,
            scale_config_id=self.scd_config.id,
            selected_options=[0],  # 正常分数
            duration_ms=30000,
            started_at="2024-01-01T10:00:00",
            completed_at="2024-01-01T10:00:30"
        )
        
        self.assertIsNotNone(result)
        self.assertTrue(is_completed)  # SCD正常，流程应该完成
        
        # 验证分组状态
        group.refresh_from_db()
        self.assertEqual(group.status, 'completed')
        self.assertIsNotNone(group.completed_at)
        self.assertIn('conclusion', group.comprehensive_analysis)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试不存在的用户
        profile = UserService.get_user_profile("non-existent-user")
        self.assertIsNone(profile)
        
        # 测试不存在的量表配置
        result = ScaleResultService.create_scale_result(
            user_id=str(self.test_user.id),
            scale_config_id=99999,  # 不存在的ID
            selected_options=[0],
            duration_ms=30000,
            started_at="2024-01-01T10:00:00",
            completed_at="2024-01-01T10:00:30"
        )
        self.assertIsNone(result)
        
        # 测试不存在的评估分组
        group = AssessmentFlowService.get_assessment_group(99999)
        self.assertIsNone(group)