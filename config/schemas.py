"""
统一响应格式Schema定义
遵循Django-Ninja推荐的Schema设计模式
"""
from ninja import Schema
from typing import Any, Optional, List, Generic, TypeVar
from pydantic import Field


# 泛型类型变量
T = TypeVar('T')


class BaseResponse(Schema):
    """基础响应格式"""
    code: int = Field(default=200, description="状态码")
    message: str = Field(description="响应消息")
    data: Optional[Any] = Field(default=None, description="业务数据")


class SuccessResponse(BaseResponse):
    """成功响应"""
    code: int = 200
    message: str = "操作成功"


class ErrorResponse(Schema):
    """错误响应格式"""
    code: int = Field(description="错误码")
    message: str = Field(description="错误描述")
    errors: Optional[dict] = Field(default=None, description="详细错误信息")


class PaginationMeta(Schema):
    """分页元数据"""
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")


class PaginatedResponse(Schema):
    """分页响应格式"""
    code: int = 200
    message: str = "查询成功"
    data: dict = Field(description="分页数据")


def create_success_response(data: Any = None, message: str = "操作成功") -> dict:
    """
    创建成功响应
    
    Args:
        data: 业务数据
        message: 响应消息
        
    Returns:
        统一格式的成功响应字典
    """
    return {
        "code": 200,
        "message": message,
        "data": data
    }


def create_error_response(code: int, message: str, errors: Optional[dict] = None) -> dict:
    """
    创建错误响应
    
    Args:
        code: 错误码
        message: 错误描述
        errors: 详细错误信息
        
    Returns:
        统一格式的错误响应字典
    """
    response = {
        "code": code,
        "message": message
    }
    if errors:
        response["errors"] = errors
    return response


def create_paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "查询成功"
) -> dict:
    """
    创建分页响应
    
    Args:
        items: 数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页数量
        message: 响应消息
        
    Returns:
        统一格式的分页响应字典
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return {
        "code": 200,
        "message": message,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    }


# HTTP状态码常量
class StatusCode:
    """HTTP状态码常量"""
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
