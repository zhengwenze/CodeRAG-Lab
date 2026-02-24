from typing import List, Dict, Any
from coderag.rag.qdrant_store import QdrantStore
from coderag.rag.faiss_store import FaissStore
from coderag.settings import settings


class Retriever:
    """检索器"""

    def __init__(self):
        if settings.vector_store == "faiss":
            self.store = FaissStore()
        else:
            self.store = QdrantStore()
        self.top_k = settings.top_k

    def retrieve(self, query: str, embedding: List[float], top_k: int = None) -> List[Dict[str, Any]]:
        """检索相关文档"""
        top_k = top_k or self.top_k
        results = self.store.search(
            query_vector=embedding,
            top_k=top_k,
        )
        return results

    def hybrid_retrieve(self, query: str, embedding: List[float], top_k: int = None) -> List[Dict[str, Any]]:
        """混合检索（向量+BM25）"""
        # 暂时只实现向量检索
        return self.retrieve(query, embedding, top_k)

    def rerank(self, query: str, results: List[Dict[str, Any]], top_k: int = None) -> List[Dict[str, Any]]:
        """重排检索结果"""
        top_k = top_k or self.top_k
        # 暂时只按分数排序
        reranked = sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
        # 更新排名
        for i, item in enumerate(reranked):
            item['rank'] = i + 1
        return reranked

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
