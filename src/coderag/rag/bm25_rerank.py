from typing import List, Dict, Any, Optional
import numpy as np
from rank_bm25 import BM25Okapi
import re


class BM25Reranker:
    """BM25 检索重排器"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.bm25_model: Optional[BM25Okapi] = None
        self.documents: List[Dict[str, Any]] = []

    def index(self, documents: List[Dict[str, Any]]):
        """构建 BM25 索引

        Args:
            documents: 文档列表，每项包含 'content' 和 'file_path' 等字段
        """
        self.documents = documents
        if not documents:
            self.bm25_model = None
            return

        tokenized_docs = [self._tokenize(doc.get('content', '')) for doc in documents]
        self.bm25_model = BM25Okapi(tokenized_docs)

    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        if not text:
            return []
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return tokens

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        """对文档进行 BM25 重排

        Args:
            query: 查询文本
            documents: 待重排的文档列表
            top_k: 返回 top-k 结果

        Returns:
            重排后的文档列表，包含 'bm25_score' 字段
        """
        if not documents or not self.bm25_model:
            for i, doc in enumerate(documents):
                doc['bm25_score'] = 0.0
                doc['rank'] = i + 1
            return documents[:top_k]

        tokenized_query = self._tokenize(query)
        scores = self.bm25_model.get_scores(tokenized_query)

        for i, (doc, score) in enumerate(zip(documents, scores)):
            doc['bm25_score'] = float(score)

        sorted_docs = sorted(documents, key=lambda x: x.get('bm25_score', 0), reverse=True)

        for i, doc in enumerate(sorted_docs):
            doc['rank'] = i + 1

        return sorted_docs[:top_k]

    def get_scores(self, query: str) -> List[float]:
        """获取查询对所有文档的 BM25 分数"""
        if not self.bm25_model:
            return [0.0] * len(self.documents)

        tokenized_query = self._tokenize(query)
        return self.bm25_model.get_scores(tokenized_query).tolist()


class HybridRetriever:
    """混合检索器：向量检索 + BM25 重排"""

    def __init__(self, vector_weight: float = 0.5, bm25_weight: float = 0.5):
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.bm25_reranker = BM25Reranker()

    def rerank(
        self,
        query: str,
        vector_results: List[Dict[str, Any]],
        use_hybrid: bool = False,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """混合检索 + 重排

        Args:
            query: 查询文本
            vector_results: 向量检索返回的结果
            use_hybrid: 是否使用混合检索
            top_k: 返回 top-k 结果

        Returns:
            重排后的文档列表
        """
        if not vector_results:
            return []

        if not use_hybrid:
            for i, doc in enumerate(vector_results):
                doc['combined_score'] = doc.get('score', 0)
                doc['rank'] = i + 1
            return vector_results[:top_k]

        self.bm25_reranker.index(vector_results)
        bm25_results = self.bm25_reranker.rerank(query, vector_results, top_k=len(vector_results))

        vector_scores = [doc.get('score', 0) for doc in bm25_results]
        bm25_scores = [doc.get('bm25_score', 0) for doc in bm25_results]

        vector_max = max(vector_scores) if vector_scores else 1
        bm25_max = max(bm25_scores) if bm25_scores else 1

        for doc in bm25_results:
            normalized_vector = doc.get('score', 0) / vector_max if vector_max > 0 else 0
            normalized_bm25 = doc.get('bm25_score', 0) / bm25_max if bm25_max > 0 else 0

            doc['combined_score'] = (
                self.vector_weight * normalized_vector +
                self.bm25_weight * normalized_bm25
            )

        sorted_docs = sorted(bm25_results, key=lambda x: x.get('combined_score', 0), reverse=True)

        for i, doc in enumerate(sorted_docs):
            doc['rank'] = i + 1

        return sorted_docs[:top_k]


def get_bm25_reranker() -> BM25Reranker:
    """获取 BM25 reranker 实例"""
    return BM25Reranker()


def get_hybrid_retriever(vector_weight: float = 0.5, bm25_weight: float = 0.5) -> HybridRetriever:
    """获取混合检索器实例"""
    return HybridRetriever(vector_weight=vector_weight, bm25_weight=bm25_weight)
