"""
评估核心模块 - 极简设计，后端主导
"""

from typing import Dict, Any, Optional, List
from apps.scales.models import ScaleResult
import logging

logger = logging.getLogger(__name__)


class ScaleResultService:
    """单量表服务 - 独立的单问卷功能"""

    @staticmethod
    def create_single_scale_result(
        user_id: str,
        scale_config_id: int,
        selected_options: List[int],
        duration_ms: int,
        started_at: str,
        completed_at: str,
    ) -> Optional[ScaleResult]:
        """创建单量表结果（不关联智能测评）"""
        try:
            return ScaleResult.objects.create(
                user_id=user_id,
                scale_config_id=scale_config_id,
                selected_options=selected_options,
                duration_ms=duration_ms,
                started_at=started_at,
                completed_at=completed_at,
            )
        except Exception as e:
            logger.error(f"创建单量表结果失败: {str(e)}")
            return None

    @staticmethod
    def get_single_scale_result(result_id: int) -> Optional[Dict[str, Any]]:
        """获取单量表结果详情"""
        try:
            result = ScaleResult.objects.select_related("scale_config").get(
                id=result_id
            )

            return {
                "id": result.id,
                "user_id": result.user_id,
                "scale_config": {
                    "id": result.scale_config.id,
                    "name": result.scale_config.name,
                    "code": result.scale_config.code,
                    "type": result.scale_config.type,
                },
                "selected_options": result.selected_options,
                "analysis": result.analysis,
                "conclusion": result.conclusion,
                "duration_ms": result.duration_ms,
                "started_at": result.started_at.isoformat(),
                "completed_at": result.completed_at.isoformat(),
                "created_at": result.created_at.isoformat(),
            }

        except ScaleResult.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"获取单量表结果失败: {str(e)}")
            return None
