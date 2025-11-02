from ninja import Schema
from typing import Optional

class ArticleCreateSchema(Schema):
    title: str
    content: str
    cover_image: Optional[str] = None
    publish_time: Optional[str] = None
    status: str = "draft"

class ArticleUpdateSchema(Schema):
    title: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    publish_time: Optional[str] = None
    status: Optional[str] = None

class ArticleResponseSchema(Schema):
    id: int
    title: str
    content: str
    cover_image: Optional[str]
    publish_time: str
    status: str
    created_at: str
    updated_at: str

class ArticleListQuerySchema(Schema):
    status: Optional[str] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 10