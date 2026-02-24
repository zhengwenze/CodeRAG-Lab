from typing import List, Dict, Any
from coderag.rag.qdrant_store import QdrantStore
from coderag.rag.faiss_store import FaissStore
from coderag.rag.bm25_rerank import HybridRetriever
from coderag.settings import settings


class Retriever:
    """检索器，支持向量检索 + BM25 重排"""

    def __init__(self):
        if settings.vector_store == "faiss":
            self.store = FaissStore()
        else:
            self.store = QdrantStore()
        self.top_k = settings.top_k
        self.hybrid_retriever = HybridRetriever(vector_weight=0.5, bm25_weight=0.5)

    def retrieve(self, query: str, embedding: List[float], top_k: int = None) -> List[Dict[str, Any]]:
        """检索相关文档"""
        top_k = top_k or self.top_k
        results = self.store.search(
            query_vector=embedding,
            top_k=top_k,
        )
        return results

    def hybrid_retrieve(self, query: str, embedding: List[float], top_k: int = None, use_rerank: bool = True) -> List[Dict[str, Any]]:
        """混合检索（向量检索 + BM25 重排）

        Args:
            query: 查询文本
            embedding: 查询向量
            top_k: 返回结果数量
            use_rerank: 是否使用 BM25 重排
        """
        top_k = top_k or self.top_k

        vector_results = self.store.search(
            query_vector=embedding,
            top_k=top_k * 2,
        )

        if not vector_results:
            return []

        if use_rerank:
            return self.hybrid_retriever.rerank(query, vector_results, use_hybrid=True, top_k=top_k)

        for i, doc in enumerate(vector_results):
            doc['rank'] = i + 1

        return vector_results[:top_k]

    def rerank(self, query: str, results: List[Dict[str, Any]], top_k: int = None) -> List[Dict[str, Any]]:
        """使用 BM25 重排检索结果"""
        top_k = top_k or self.top_k
        return self.hybrid_retriever.rerank(query, results, use_hybrid=True, top_k=top_k)

    def add_points(self, points: List[Dict[str, Any]]):
        """添加向量点"""
        if hasattr(self.store, 'add_points'):
            self.store.add_points(points)
        else:
            print("Error: Store does not have add_points method")

    def clear_index(self):
        """清空索引"""
        if hasattr(self.store, 'clear_index'):
            self.store.clear_index()
        elif hasattr(self.store, 'delete_collection'):
            self.store.delete_collection()
        else:
            print("Error: Store does not have clear method")
