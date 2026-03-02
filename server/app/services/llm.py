from typing import List, Dict, Any, Optional
from app.config import settings
from app.utils.logging import get_logger
from coderag.llm.provider import LLMProviderFactory as CoreLLMProviderFactory

logger = get_logger(__name__)


class LLMProviderFactory:
    """LLM 提供者工厂 - 包装核心 LLM 实现"""

    @staticmethod
    def get_provider(provider_name: str) -> Any:
        """获取 LLM 提供者实例"""
        try:
            provider = CoreLLMProviderFactory.get_provider(provider_name)
            logger.info(f"Initialized LLM provider: {provider_name}")
            return provider
        except Exception as e:
            logger.error(f"Error initializing LLM provider: {e}", exc_info=e)
            raise