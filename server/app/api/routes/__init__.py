"""API 路由模块"""

from fastapi import APIRouter

# 创建主路由
api_router = APIRouter()

# 导入并注册子路由
# 例如：from app.api.routes.chat import router as chat_router
# api_router.include_router(chat_router, prefix="/chat", tags=["chat"])

__all__ = ["api_router"]
