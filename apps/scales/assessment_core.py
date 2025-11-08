"""
评估核心模块 - 极简设计，后端主导
"""
from typing import Dict, Any, Optional, List
from django.utils import timezone
from apps.scales.models import ScaleResult, ScaleConfig, SmartAssessmentRecord
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)


class SmartAssessmentService:
    """智能测评服务"""
    
    @staticmethod
    def start_assessment(user_id: str) -> Dict[str, Any]:
        """开始智能测评"""
        try:
            # 获取用户信息
            user = User.objects.get(id=user_id)
            
            # 决定测评策略 - 根据用户信息智能选择量表
            scale_configs = SmartAssessmentService._select_scales_for_user(user)
            
            if not scale_configs:
                raise ValueError("没有可用的量表配置")
            
            # 创建测评记录
            assessment = SmartAssessmentRecord.objects.create(
                user_id=user_id,
                status='in_progress',
                current_scale_index=0,
                scale_responses=[],
                scale_scores=[]
            )
            
            # 获取第一个量表
            next_scale = SmartAssessmentService._get_next_scale(assessment, scale_configs)
            
            return {
                'id': assessment.id,
                'next_scale': next_scale,
                'total_scales': len(scale_configs)
            }
            
        except User.DoesNotExist:
            logger.error(f"用户不存在: {user_id}")
            raise ValueError("用户不存在")
        except Exception as e:
            logger.error(f"开始智能测评失败: {str(e)}")
            raise
    
    @staticmethod
    def submit_answer(assessment_id: int, scale_config_id: int, user_id: str,
                     selected_options: List[int], duration_ms: int,
                     started_at: str, completed_at: str) -> Dict[str, Any]:
        """提交智能测评答案"""
        try:
            assessment = SmartAssessmentRecord.objects.get(id=assessment_id)
            
            # 验证测评归属
            if str(assessment.user_id) != user_id:
                return {
                    'success': False,
                    'completed': False,
                    'next_scale': None,
                    'final_result': None,
                    'message': '无权操作此测评',
                    'error': '无权操作此测评'
                }
            
            if assessment.status != 'in_progress':
                return {
                    'success': False,
                    'completed': False,
                    'next_scale': None,
                    'final_result': None,
                    'message': '测评已结束',
                    'error': '测评已结束'
                }
            
            # 验证量表配置是否存在且有效
            scale_config = ScaleConfig.objects.get(id=scale_config_id)
            if scale_config.status != 'active':
                return {
                    'success': False,
                    'completed': False,
                    'next_scale': None,
                    'final_result': None,
                    'message': '量表配置不可用',
                    'error': '量表配置不可用'
                }
            
            # 检查是否已经回答过这个量表
            existing_response = assessment.get_scale_response(scale_config_id)
            if existing_response:
                return {
                    'success': False,
                    'completed': False,
                    'next_scale': None,
                    'final_result': None,
                    'message': '该量表已经回答过',
                    'error': '该量表已经回答过'
                }
            
            # 创建量表结果并计算得分
            from apps.scales.services.scale_result_service import ScaleResultService
            from apps.scales.services.user_service import UserService
            
            # 获取用户资料用于计算
            user_profile = UserService.get_user_profile(user_id)
            
            # 创建量表结果（关联到智能测评）
            scale_result = ScaleResultService.create_scale_result(
                user_id=user_id,
                scale_config_id=scale_config_id,
                selected_options=selected_options,
                duration_ms=duration_ms,
                started_at=started_at,
                completed_at=completed_at,
                user_profile=user_profile
            )
            
            if not scale_result:
                return {
                    'success': False,
                    'completed': False,
                    'next_scale': None,
                    'final_result': None,
                    'message': '量表结果创建失败',
                    'error': '量表结果创建失败'
                }
            
            # 关联到智能测评记录
            scale_result.smart_assessment = assessment
            scale_result.save()
            
            # 将子量表数据添加到智能测评记录中（添加错误处理）
            try:
                assessment.add_scale_response(scale_config_id, selected_options, scale_result.analysis)
            except Exception as e:
                logger.warning(f"添加子量表数据到智能测评记录失败: {str(e)}，但量表结果已创建")
                # 继续流程，不影响主要功能
            
            # 更新测评进度
            assessment.current_scale_index += 1
            assessment.save()
            
            # 获取用户的量表配置列表
            user = User.objects.get(id=assessment.user_id)
            scale_configs = SmartAssessmentService._select_scales_for_user(user, assessment)
            
            # 检查是否完成
            if assessment.current_scale_index >= len(scale_configs):
                # 完成测评
                assessment.status = 'completed'
                assessment.completed_at = timezone.now()
                assessment.final_result = SmartAssessmentService._generate_final_result(assessment)
                assessment.save()
                
                return {
                    'success': True,
                    'completed': True,
                    'next_scale': None,
                    'final_result': assessment.final_result,
                    'message': '测评已完成'
                }
            else:
                # 获取下一个量表
                next_scale = SmartAssessmentService._get_next_scale(assessment, scale_configs)
                # 若无下一个量表，直接完成测评
                if not next_scale:
                    assessment.status = 'completed'
                    assessment.completed_at = timezone.now()
                    assessment.final_result = SmartAssessmentService._generate_final_result(assessment)
                    assessment.save()
                    return {
                        'success': True,
                        'completed': True,
                        'next_scale': None,
                        'final_result': assessment.final_result,
                        'message': '测评已完成'
                    }
                return {
                    'success': True,
                    'completed': False,
                    'next_scale': next_scale,
                    'final_result': None,
                    'message': '继续下一个量表'
                }
                
        except SmartAssessmentRecord.DoesNotExist:
            return {
                'success': False,
                'completed': False,
                'next_scale': None,
                'final_result': None,
                'message': '测评不存在',
                'error': '测评不存在'
            }
        except ScaleConfig.DoesNotExist:
            return {
                'success': False,
                'completed': False,
                'next_scale': None,
                'final_result': None,
                'message': '量表配置不存在',
                'error': '量表配置不存在'
            }
        except Exception as e:
            logger.error(f"提交智能测评答案失败: {str(e)}")
            return {
                'success': False,
                'completed': False,
                'next_scale': None,
                'final_result': None,
                'message': str(e),
                'error': str(e)
            }
    
    @staticmethod
    def get_assessment_result(assessment_id: int) -> Optional[Dict[str, Any]]:
        """获取智能测评结果"""
        try:
            assessment = SmartAssessmentRecord.objects.get(id=assessment_id)
            
            # 获取所有量表结果
            scale_results = ScaleResult.objects.filter(
                smart_assessment=assessment
            ).select_related('scale_config').order_by('created_at')
            
            results_data = []
            for result in scale_results:
                analysis = result.analysis or {}
                results_data.append({
                    'id': result.id,
                    'scale_name': result.scale_config.name,
                    'score': analysis.get('score'),
                    'level': analysis.get('level'),
                    'is_abnormal': analysis.get('is_abnormal', False),
                    'created_at': result.created_at.isoformat()
                })
            
            return {
                'id': assessment.id,
                'user_id': str(assessment.user_id),  # 将UUID转换为字符串
                'status': assessment.status,
                'started_at': assessment.started_at.isoformat(),
                'completed_at': assessment.completed_at.isoformat() if assessment.completed_at else None,
                'scale_responses': assessment.scale_responses,
                'scale_scores': assessment.scale_scores,
                'results': results_data,
                'final_result': assessment.final_result or {},
                'total_duration': assessment.get_total_duration()
            }
            
        except SmartAssessmentRecord.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"获取智能测评结果失败: {str(e)}")
            return None
    
    @staticmethod
    def _select_scales_for_user(user: User, assessment=None) -> List[ScaleConfig]:
        """
        为用户智能选择量表配置（支持分数动态判断）
        - 第一步只推送 SCD
        - SCD 完成后，根据分数决定是否推送 MMSE/MoCA
        """
        all_configs = ScaleConfig.objects.filter(
            status='active'
        ).order_by('type', '-version', '-created_at')

        # 按type分组，每个type只取最新版本
        selected_configs = []
        seen_types = set()
        for config in all_configs:
            if config.type not in seen_types:
                selected_configs.append(config)
                seen_types.add(config.type)

        # 动态流程
        if assessment is None or not assessment.scale_responses:
            # 初始：只推送 SCD
            return [c for c in selected_configs if c.type == 'SCD']

        # 已有 SCD 响应，判断分数
        scd_response = None
        for resp in assessment.scale_responses:
            sc_id = resp.get('scale_config_id')
            sc_cfg = next((c for c in selected_configs if c.id == sc_id), None)
            if sc_cfg and sc_cfg.type == 'SCD':
                scd_response = resp
                break

        if scd_response and 'analysis' in scd_response:
            scd_score = scd_response['analysis'].get('score', 0)
            if scd_score > 5:
                # SCD 异常，推送 MMSE、MoCA
                return [c for c in selected_configs if c.type in ('MMSE', 'MoCA')]
            else:
                # SCD 正常，不再推送
                return []

        # 默认只推送 SCD
        return [c for c in selected_configs if c.type == 'SCD']
    
    @staticmethod
    def _get_next_scale(assessment, scale_configs: List[ScaleConfig]) -> Optional[Dict[str, Any]]:
        """获取下一个量表"""
        if assessment.current_scale_index >= len(scale_configs):
            return None
        
        config = scale_configs[assessment.current_scale_index]
        
        return {
            'id': config.id,  # 新增，确保前端 scaleConfig.id 可用
            'config_id': config.id,
            'name': config.name,
            'description': config.description,
            'questions': config.questions,
            'type': config.type
        }
    
    @staticmethod
    def _generate_final_result(assessment) -> Dict[str, Any]:
        """生成最终结果"""
        scale_results = ScaleResult.objects.filter(
            smart_assessment=assessment
        ).select_related('scale_config')
        
        # 简化的结果分析
        abnormal_count = 0
        total_score = 0
        recommendations = []
        scale_summaries = []
        
        for result in scale_results:
            analysis = result.analysis or {}
            scale_name = result.scale_config.name
            
            # 单个量表摘要
            score = analysis.get('score', 0)
            level = analysis.get('level', '未知')
            is_abnormal = analysis.get('is_abnormal', False)
            
            scale_summaries.append({
                'scale_name': scale_name,
                'score': score,
                'level': level,
                'is_abnormal': is_abnormal
            })
            
            if is_abnormal:
                abnormal_count += 1
            
            total_score += score
            
            # 收集建议
            recs = analysis.get('recommendations', [])
            if recs and isinstance(recs, list):
                recommendations.extend(recs)
        
        # 风险评估
        if abnormal_count > 0:
            risk_level = "高风险"
            conclusion = "建议进一步专业评估"
        else:
            risk_level = "低风险" 
            conclusion = "认知功能正常"
        
        return {
            'conclusion': conclusion,
            'risk_level': risk_level,
            'total_score': total_score,
            'abnormal_count': abnormal_count,
            'scale_summaries': scale_summaries,
            'recommendations': list(set(recommendations))  # 去重
        }


class SingleScaleService:
    """单量表服务 - 独立的单问卷功能"""
    
    @staticmethod
    def create_single_scale_result(user_id: str, scale_config_id: int,
                                 selected_options: List[int], duration_ms: int,
                                 started_at: str, completed_at: str) -> Optional[ScaleResult]:
        """创建单量表结果（不关联智能测评）"""
        try:
            return ScaleResult.objects.create(
                user_id=user_id,
                scale_config_id=scale_config_id,
                selected_options=selected_options,
                duration_ms=duration_ms,
                started_at=started_at,
                completed_at=completed_at,
                smart_assessment=None
            )
        except Exception as e:
            logger.error(f"创建单量表结果失败: {str(e)}")
            return None
    
    @staticmethod
    def get_single_scale_result(result_id: int) -> Optional[Dict[str, Any]]:
        """获取单量表结果详情"""
        try:
            result = ScaleResult.objects.select_related('scale_config').get(
                id=result_id,
                smart_assessment__isnull=True
            )
            
            return {
                'id': result.id,
                'user_id': result.user_id,
                'scale_config': {
                    'id': result.scale_config.id,
                    'name': result.scale_config.name,
                    'code': result.scale_config.code,
                    'type': result.scale_config.type
                },
                'selected_options': result.selected_options,
                'analysis': result.analysis,
                'conclusion': result.conclusion,
                'duration_ms': result.duration_ms,
                'started_at': result.started_at.isoformat(),
                'completed_at': result.completed_at.isoformat(),
                'created_at': result.created_at.isoformat()
            }
            
        except ScaleResult.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"获取单量表结果失败: {str(e)}")
            return None