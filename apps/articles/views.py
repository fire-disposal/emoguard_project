from ninja import Router, Query
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings
from .models import Article
from .serializers import (
    ArticleCreateSchema, ArticleUpdateSchema, ArticleResponseSchema, ArticleListQuerySchema
)
from config.jwt_auth_adapter import jwt_auth

articles_router = Router(tags=["articles"])


def _require_admin(request):
    if getattr(request.auth, "role", None) != "admin":
        raise HttpError(403, "需要管理员权限")


def _is_admin(request):
    return getattr(request.auth, "role", None) == "admin"


@articles_router.get("/", response=list[ArticleResponseSchema], auth=jwt_auth)
def list_articles(request, filters: ArticleListQuerySchema = Query(...)):
    """获取文章列表；非管理员仅可见已发布文章"""
    queryset = Article.objects.all()

    if _is_admin(request):
        if filters.status:
            queryset = queryset.filter(status=filters.status)
    else:
        queryset = queryset.filter(status='published')

    # 搜索功能
    if filters.search:
        queryset = queryset.filter(
            Q(title__icontains=filters.search) | Q(content__icontains=filters.search)
        )

    # 分页
    page_size = min(filters.page_size, settings.MAX_PAGE_SIZE)
    start = (filters.page - 1) * page_size
    end = start + page_size
    articles = queryset[start:end]

    return [
        ArticleResponseSchema(
            id=a.id,
            title=a.title,
            content=a.content,
            status=a.status,
            created_at=a.created_at.isoformat(),
            updated_at=a.updated_at.isoformat()
        )
        for a in articles
    ]

@articles_router.get("/{article_id}", response=ArticleResponseSchema, auth=jwt_auth)
def get_article(request, article_id: int):
    """获取单篇文章详情；非管理员不可见草稿"""
    if _is_admin(request):
        article = get_object_or_404(Article, id=article_id)
    else:
        article = get_object_or_404(Article, id=article_id, status='published')
    return ArticleResponseSchema(
        id=article.id,
        title=article.title,
        content=article.content,
        status=article.status,
        created_at=article.created_at.isoformat(),
        updated_at=article.updated_at.isoformat()
    )

@articles_router.post("/", response=ArticleResponseSchema, auth=jwt_auth)
def create_article(request, data: ArticleCreateSchema):
    """创建新文章（管理员）"""
    _require_admin(request)
    article = Article.objects.create(
        title=data.title,
        content=data.content,
        status=data.status
    )

    return ArticleResponseSchema(
        id=article.id,
        title=article.title,
        content=article.content,
        status=article.status,
        created_at=article.created_at.isoformat(),
        updated_at=article.updated_at.isoformat()
    )

@articles_router.put("/{article_id}", response=ArticleResponseSchema, auth=jwt_auth)
def update_article(request, article_id: int, data: ArticleUpdateSchema):
    """更新文章（管理员）"""
    _require_admin(request)
    article = get_object_or_404(Article, id=article_id)

    # 更新字段
    if data.title is not None:
        article.title = data.title
    if data.content is not None:
        article.content = data.content
    if data.status is not None:
        article.status = data.status

    article.save()

    return ArticleResponseSchema(
        id=article.id,
        title=article.title,
        content=article.content,
        status=article.status,
        created_at=article.created_at.isoformat(),
        updated_at=article.updated_at.isoformat()
    )

@articles_router.delete("/{article_id}", auth=jwt_auth)
def delete_article(request, article_id: int):
    """删除文章（管理员）"""
    _require_admin(request)
    article = get_object_or_404(Article, id=article_id)
    article.delete()
    return {"success": True}

@articles_router.post("/{article_id}/publish", auth=jwt_auth)
def publish_article(request, article_id: int):
    """发布文章（管理员）"""
    _require_admin(request)
    article = get_object_or_404(Article, id=article_id)
    article.status = 'published'
    article.save()
    return {"success": True}

@articles_router.post("/{article_id}/draft", auth=jwt_auth)
def draft_article(request, article_id: int):
    """将文章设为草稿（管理员）"""
    _require_admin(request)
    article = get_object_or_404(Article, id=article_id)
    article.status = 'draft'
    article.save()
    return {"success": True}
