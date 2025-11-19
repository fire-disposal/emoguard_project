"""用户反馈API视图 - 原生基础版本"""
from ninja import Router
from apps.feedback.models import Feedback
from apps.feedback.serializers import FeedbackCreateSchema
from config.jwt_auth_adapter import jwt_auth

feedback_router = Router(tags=["feedback"])


@feedback_router.post("/feedback", auth=jwt_auth)
def create_feedback(request, data: FeedbackCreateSchema):
    """创建用户反馈 - 最简版本"""
    user = request.user if request.user.is_authenticated else None
    
    feedback = Feedback.objects.create(
        user=user,
        rating=data.rating,
        content=data.content or ''
    )
    
    return {
        'id': feedback.id,
        'message': '反馈提交成功'
    }


@feedback_router.get("/feedback", auth=jwt_auth)
def list_user_feedback(request):
    """获取用户自己的反馈列表"""
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
    
    return [{
        'id': f.id,
        'rating': f.rating,
        'content': f.content,
        'created_at': f.created_at.isoformat(),
        'is_processed': f.is_processed
    } for f in feedbacks]