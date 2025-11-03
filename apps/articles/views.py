from ninja import Router, Query
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Article
from .serializers import (
    ArticleCreateSchema, ArticleUpdateSchema, ArticleResponseSchema, ArticleListQuerySchema
)

articles_router = Router()

@articles_router.get("/", response=list[ArticleResponseSchema])
def list_articles(request, filters: ArticleListQuerySchema = Query(...)):
    """
    获取文章列表，支持状态过滤、搜索和分页
    """
    queryset = Article.objects.all()
    
    # 状态过滤
    if filters.status:
        queryset = queryset.filter(status=filters.status)
    
    # 搜索功能
    if filters.search:
        queryset = queryset.filter(
            Q(title__icontains=filters.search) | Q(content__icontains=filters.search)
        )
    
    # 分页
    start = (filters.page - 1) * filters.page_size
    end = start + filters.page_size
    articles = queryset[start:end]
    
    return [
        ArticleResponseSchema(
            id=a.id,
            title=a.title,
            content=a.content,
            cover_image=a.cover_image,
            publish_time=a.publish_time.isoformat() if a.publish_time else None,
            status=a.status,
            created_at=a.created_at.isoformat(),
            updated_at=a.updated_at.isoformat()
        )
        for a in articles
    ]

@articles_router.get("/{article_id}", response=ArticleResponseSchema)
def get_article(request, article_id: int):
    """
    获取单篇文章详情
    """
    article = get_object_or_404(Article, id=article_id)
    return ArticleResponseSchema(
        id=article.id,
        title=article.title,
        content=article.content,
        cover_image=article.cover_image,
        publish_time=article.publish_time.isoformat() if article.publish_time else None,
        status=article.status,
        created_at=article.created_at.isoformat(),
        updated_at=article.updated_at.isoformat()
    )

@articles_router.post("/", response=ArticleResponseSchema)
def create_article(request, data: ArticleCreateSchema):
    """
    创建新文章
    """
    article = Article.objects.create(
        title=data.title,
        content=data.content,
        cover_image=data.cover_image,
        publish_time=data.publish_time,
        status=data.status
    )
    
    return ArticleResponseSchema(
        id=article.id,
        title=article.title,
        content=article.content,
        cover_image=article.cover_image,
        publish_time=article.publish_time.isoformat() if article.publish_time else None,
        status=article.status,
        created_at=article.created_at.isoformat(),
        updated_at=article.updated_at.isoformat()
    )

@articles_router.put("/{article_id}", response=ArticleResponseSchema)
def update_article(request, article_id: int, data: ArticleUpdateSchema):
    """
    更新文章
    """
    article = get_object_or_404(Article, id=article_id)
    
    # 更新字段
    if data.title is not None:
        article.title = data.title
    if data.content is not None:
        article.content = data.content
    if data.cover_image is not None:
        article.cover_image = data.cover_image
    if data.publish_time is not None:
        article.publish_time = data.publish_time
    if data.status is not None:
        article.status = data.status
    
    article.save()
    
    return ArticleResponseSchema(
        id=article.id,
        title=article.title,
        content=article.content,
        cover_image=article.cover_image,
        publish_time=article.publish_time.isoformat() if article.publish_time else None,
        status=article.status,
        created_at=article.created_at.isoformat(),
        updated_at=article.updated_at.isoformat()
    )

@articles_router.delete("/{article_id}")
def delete_article(request, article_id: int):
    """
    删除文章
    """
    article = get_object_or_404(Article, id=article_id)
    article.delete()
    return {"success": True}

@articles_router.post("/{article_id}/publish")
def publish_article(request, article_id: int):
    """
    发布文章
    """
    article = get_object_or_404(Article, id=article_id)
    article.status = 'published'
    if not article.publish_time:
        from django.utils import timezone
        article.publish_time = timezone.now()
    article.save()
    return {"success": True}

@articles_router.post("/{article_id}/draft")
def draft_article(request, article_id: int):
    """
    将文章设为草稿
    """
    article = get_object_or_404(Article, id=article_id)
    article.status = 'draft'
    article.save()
    return {"success": True}