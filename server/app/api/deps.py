from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.services.llm import LLMProviderFactory
from app.services.retriever import Retriever

# 安全依赖
security = HTTPBearer()

def get_retriever() -> Retriever:
    """获取检索器实例"""
    return Retriever()

def get_llm_provider(provider_name: Optional[str] = None):
    """获取 LLM 提供商实例"""
    provider = provider_name or settings.llm_provider
    return LLMProviderFactory.get_provider(provider)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户（预留）"""
    # 这里可以添加 JWT 验证逻辑
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"token": token}
