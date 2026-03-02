from typing import List, Dict, Any
from app.config import settings
from app.utils.logging import get_logger
from coderag.rag.retriever import Retriever as CoreRetriever

logger = get_logger(__name__)


class Retriever:
    """检索器 - 包装核心检索逻辑"""

    def __init__(self):
        """初始化检索器"""
        self.core_retriever = CoreRetriever(
            enable_llm_rerank=settings.enable_llm_rerank,
            enable_fulltext=settings.enable_fulltext
        )
        logger.info(f"Initialized Retriever with core implementation")

    def retrieve(self, query: str, embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """检索相关文档

        Args:
            query: 查询文本
            embedding: 查询嵌入向量
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        try:
            results = self.core_retriever.retrieve(
                query=query,
                embedding=embedding,
                top_k=top_k
            )
            logger.info(f"Retrieved {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error in retrieve: {e}", exc_info=e)
            return []

    def hybrid_retrieve(self, query: str, embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """混合检索

        Args:
            query: 查询文本
            embedding: 查询嵌入向量
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        try:
            results = self.core_retriever.hybrid_retrieve(
                query=query,
                embedding=embedding,
                top_k=top_k
            )
            logger.info(f"Retrieved {len(results)} results from hybrid search")
            return results
        except Exception as e:
            logger.error(f"Error in hybrid_retrieve: {e}", exc_info=e)
            return []