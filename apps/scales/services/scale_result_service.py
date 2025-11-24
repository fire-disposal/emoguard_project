"""
量表结果服务 - 处理量表结果相关业务逻辑
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from django.shortcuts import get_object_or_404
from apps.scales.models import ScaleResult, ScaleConfig
from apps.scales.calculators import get_calculator
import logging

logger = logging.getLogger(__name__)

class ScaleResultService:
    """量表结果服务类 - 处理量表结果的创建和计算"""
    
    @staticmethod
    def _copy_user_info(user) -> Dict[str, Any]:
        """
        从用户对象拷贝信息到字典
        
        Args:
            user: 用户对象
            
        Returns:
            用户信息字典
        """
        return {
            'real_name': getattr(user, "real_name", ""),
            'gender': getattr(user, "gender", ""),
            'age': getattr(user, "age", None),
            'education': getattr(user, "education", ""),
            'province': getattr(user, "province", ""),
            'city': getattr(user, "city", ""),
            'district': getattr(user, "district", ""),
            'phone': getattr(user, "phone", ""),
        }

    @staticmethod
    def _validate_assessment(questions: List[Dict], selected_options: List[int], started_at, completed_at) -> Dict[str, Any]:
        """
        验证评估有效性
        Args:
            questions: 题目列表
            selected_options: 用户选择
            started_at: 开始时间
            completed_at: 完成时间
        Returns:
            验证结果
        """
        warnings = []
        is_valid = True

        # 检查答题完整性
        if len(selected_options) != len(questions):
            warnings.append(f"答题不完整：应答{len(questions)}题，实际答{len(selected_options)}题")
            is_valid = False

        # 检查答题时长
        duration = (completed_at - started_at).total_seconds()
        min_duration = len(questions) * 2  # 每题至少2秒

        if duration < min_duration:
            warnings.append(f"答题时间过短：{duration:.0f}秒，可能影响结果准确性")

        # 检查选项有效性
        for idx, selected_idx in enumerate(selected_options):
            if idx < len(questions):
                options_count = len(questions[idx].get("options", []))
                if selected_idx >= options_count or selected_idx < 0:
                    warnings.append(f"题目{idx+1}的选项索引{selected_idx}无效")
                    is_valid = False

        return {
            "is_valid": is_valid,
            "warnings": warnings
        }

    @staticmethod
    def _calculate_score_by_instance(scale_config, scale_result, user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """
        根据量表配置和结果计算分数（模块化版本）
        Args:
            scale_config: ScaleConfig实例
            scale_result: ScaleResult实例
            user_profile: 用户资料字典（可选）
        Returns:
            分析结果JSON
        """
        selected_options = scale_result.selected_options

        # 验证有效性
        validation = ScaleResultService._validate_assessment(
            scale_config.questions,
            selected_options,
            scale_result.started_at,
            scale_result.completed_at
        )

        # 使用模块化计分器
        calculator = get_calculator(scale_config, user_profile)
        analysis = calculator.calculate(selected_options)

        # 添加验证结果和元数据
        analysis["validation"] = validation
        analysis["scale_code"] = scale_config.code
        analysis["scale_name"] = scale_config.name

        logger.info(f"量表{scale_config.code}评分完成: 总分{analysis['score']}/{analysis.get('max_score', 'N/A')}, 等级{analysis['level']}")

        return analysis
    
    @staticmethod
    def create_scale_result(
        user_id: str,
        scale_config_id: int,
        selected_options: list,
        duration_ms: int,
        started_at: str,
        completed_at: str,
        user_profile: Optional[Dict] = None
    ) -> Optional[ScaleResult]:
        """
        创建量表结果
        
        Args:
            user_id: 用户ID
            scale_config_id: 量表配置ID
            selected_options: 选择的选项
            duration_ms: 用时（毫秒）
            started_at: 开始时间
            completed_at: 完成时间
            user_profile: 用户资料
            
        Returns:
            量表结果实例或None
        """
        try:
            # 获取量表配置
            scale_config = get_object_or_404(ScaleConfig, id=scale_config_id)
            
            # 如果未提供用户资料，尝试获取
            if user_profile is None:
                from apps.users.models import User
                user_obj = User.objects.filter(id=user_id).first()
                user_profile = ScaleResultService._copy_user_info(user_obj) if user_obj else {}
            
            # 标准化时间格式
            started_dt = datetime.fromisoformat(started_at)
            completed_dt = datetime.fromisoformat(completed_at)
            
            # 验证和修正时长
            calculated_duration = int((completed_dt - started_dt).total_seconds() * 1000)
            if calculated_duration != duration_ms:
                logger.info(f"修正答题时长: {duration_ms}ms -> {calculated_duration}ms")
                duration_ms = calculated_duration
            
            # 创建临时对象用于计算
            temp_result = ScaleResult(
                user_id=user_id,
                scale_config=scale_config,
                selected_options=selected_options,
                duration_ms=duration_ms,
                started_at=started_dt,
                completed_at=completed_dt,
                status='completed'
            )
            
            # 计算分数和分析
            analysis = ScaleResultService._calculate_score_by_instance(
                scale_config,
                temp_result,
                user_profile
            )
            
            # 构建结论摘要
            conclusion = ScaleResultService._build_conclusion(analysis)
            
            # 创建量表结果
            # 自动拷贝用户信息
            from apps.users.models import User
            user_obj = User.objects.filter(id=user_id).first()
            user_info = ScaleResultService._copy_user_info(user_obj) if user_obj else {}
            
            result = ScaleResult.objects.create(
                user_id=user_id,
                real_name=user_info.get("real_name", ""),
                gender=user_info.get("gender", ""),
                age=user_info.get("age", None),
                education=user_info.get("education", ""),
                province=user_info.get("province", ""),
                city=user_info.get("city", ""),
                district=user_info.get("district", ""),
                phone=user_info.get("phone", ""),
                scale_config=scale_config,
                selected_options=selected_options,
                conclusion=conclusion,
                duration_ms=duration_ms,
                started_at=started_dt,
                completed_at=completed_dt,
                status='completed',
                analysis=analysis
            )
            
            logger.info(f"量表结果创建成功: 用户{user_id}, 量表{scale_config.code}, 分数{analysis.get('score', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"创建量表结果失败: {str(e)}")
            return None
    
    @staticmethod
    def _build_conclusion(analysis: Dict[str, Any]) -> str:
        """
        构建结论摘要
        
        Args:
            analysis: 分析结果
            
        Returns:
            结论摘要字符串
        """
        try:
            score = analysis.get('score', 'N/A')
            level = analysis.get('level', 'N/A')
            
            # 根据不同量表类型构建不同的结论格式
            if 'is_abnormal' in analysis:
                abnormal_status = "异常" if analysis['is_abnormal'] else "正常"
                return f"分值:{score} 分级:{level} 状态:{abnormal_status}"
            else:
                return f"分值:{score} 分级:{level}"
                
        except Exception as e:
            logger.error(f"构建结论摘要失败: {str(e)}")
            return f"分值:{analysis.get('score', 'N/A')} 分级:{analysis.get('level', 'N/A')}"
    
    @staticmethod
    def get_user_scale_results(user_id: str, limit: int = 10) -> list:
        """
        获取用户的量表结果列表
        
        Args:
            user_id: 用户ID
            limit: 限制数量
            
        Returns:
            量表结果列表
        """
        try:
            return list(ScaleResult.objects.filter(
                user_id=user_id
            ).select_related('scale_config').order_by('-created_at')[:limit])
        except Exception as e:
            logger.error(f"获取用户量表结果失败: {str(e)}")
            return []
    
    @staticmethod
    def get_scale_result_by_id(result_id: int) -> Optional[ScaleResult]:
        """
        根据ID获取量表结果
        
        Args:
            result_id: 结果ID
            
        Returns:
            量表结果实例或None
        """
        try:
            return ScaleResult.objects.select_related('scale_config').get(id=result_id)
        except ScaleResult.DoesNotExist:
            logger.warning(f"量表结果 {result_id} 不存在")
            return None
        except Exception as e:
            logger.error(f"获取量表结果失败: {str(e)}")
            return None
    
    @staticmethod
    def create_single_scale_result(user_id: str, scale_config_id: int,
                                 selected_options: List[int], duration_ms: int,
                                 started_at: str, completed_at: str) -> Optional[ScaleResult]:
        """
        创建单量表结果
        
        Args:
            user_id: 用户ID
            scale_config_id: 量表配置ID
            selected_options: 选择的选项
            duration_ms: 用时（毫秒）
            started_at: 开始时间
            completed_at: 完成时间
            
        Returns:
            量表结果实例或None
        """
        try:
            # 标准化时间格式
            started_dt = datetime.fromisoformat(started_at)
            completed_dt = datetime.fromisoformat(completed_at)
            
            # 验证和修正时长
            calculated_duration = int((completed_dt - started_dt).total_seconds() * 1000)
            if calculated_duration != duration_ms:
                logger.info(f"修正答题时长: {duration_ms}ms -> {calculated_duration}ms")
                duration_ms = calculated_duration
            
            # 获取量表配置
            scale_config = get_object_or_404(ScaleConfig, id=scale_config_id)
            
            # 创建临时对象用于计算
            temp_result = ScaleResult(
                user_id=user_id,
                scale_config=scale_config,
                selected_options=selected_options,
                duration_ms=duration_ms,
                started_at=started_dt,
                completed_at=completed_dt,
                status='completed'
            )
            
            # 计算分数和分析
            analysis = ScaleResultService._calculate_score_by_instance(
                scale_config,
                temp_result,
                None  # 单量表不使用用户资料
            )
            
            # 构建结论摘要
            conclusion = ScaleResultService._build_conclusion(analysis)
            
            # 自动拷贝用户信息
            from apps.users.models import User
            user_obj = User.objects.filter(id=user_id).first()
            user_info = ScaleResultService._copy_user_info(user_obj) if user_obj else {}
            
            # 创建量表结果
            result = ScaleResult.objects.create(
                user_id=user_id,
                real_name=user_info.get("real_name", ""),
                gender=user_info.get("gender", ""),
                age=user_info.get("age", None),
                education=user_info.get("education", ""),
                province=user_info.get("province", ""),
                city=user_info.get("city", ""),
                district=user_info.get("district", ""),
                phone=user_info.get("phone", ""),
                scale_config=scale_config,
                selected_options=selected_options,
                conclusion=conclusion,
                duration_ms=duration_ms,
                started_at=started_dt,
                completed_at=completed_dt,
                status='completed',
                analysis=analysis
            )
            
            logger.info(f"量表结果创建成功: 用户{user_id}, 量表{scale_config.code}, 分数{analysis.get('score', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"创建量表结果失败: {str(e)}")
            return None
    
    @staticmethod
    def get_scale_result_detail(result_id: int) -> Optional[Dict[str, Any]]:
        """
        获取量表结果详情
        
        Args:
            result_id: 结果ID
            
        Returns:
            量表结果详情字典或None
        """
        try:
            result = ScaleResult.objects.select_related('scale_config').get(id=result_id)
            
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
            logger.error(f"获取量表结果失败: {str(e)}")
            return None
    @staticmethod
    def flatten_scale_result(record, with_question_info=True):
        """
        展平量表结果为题目分数列，支持带题目信息或仅分数
        返回 (titles, values)
        """
        config = ScaleConfig.objects.get(id=record.scale_config_id)
        questions = config.questions
        selected_options = getattr(record, "selected_options", [])
        titles, values = [], []
        for idx, question in enumerate(questions):
            q_title = f"Q{idx+1}"
            if with_question_info:
                q_title += f": {question.get('question', '')}"
            titles.append(q_title)
            value = selected_options[idx] if idx < len(selected_options) else ""
            values.append(value)
        return titles, values