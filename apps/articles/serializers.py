from ninja import Schema
from typing import Optional, Literal

class ArticleCreateSchema(Schema):
    title: str
    content: str
    status: Literal["draft", "published"] = "draft"

class ArticleUpdateSchema(Schema):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[Literal["draft", "published"]] = None

class ArticleResponseSchema(Schema):
    id: int
    title: str
    content: str
    status: str
    created_at: str
    updated_at: str

class ArticleListQuerySchema(Schema):
    status: Optional[str] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 10