from typing import List, Dict, Any, Optional
from coderag.rag.qdrant_store import QdrantStore
from coderag.rag.faiss_store import FaissStore
from coderag.rag.bm25_rerank import HybridRetriever
from coderag.rag.reranker import LLMReranker, get_llm_reranker
from coderag.rag.fulltext_search import FullTextSearcher
from coderag.rag.hybrid_search import HybridSearcher
from coderag.settings import settings


class Retriever:
    """检索器，支持多种检索模式和重排序
    
    功能特性：
    - 向量检索 (Qdrant / Faiss)
    - 全文检索 (Whoosh)
    - 混合检索 (向量 + 全文)
    - BM25 重排序
    - LLM Cross-Encoder 重排序
    """

    def __init__(
        self,
        enable_llm_rerank: bool = False,
        enable_fulltext: bool = False,
        reranker_model: str = "BAAI/bge-reranker-v2-m3"
    ):
        """初始化检索器
        
        Args:
            enable_llm_rerank: 是否启用 LLM 重排序
            enable_fulltext: 是否启用全文检索
            reranker_model: LLM 重排序模型名称
        """
        if settings.vector_store == "faiss":
            self.store = FaissStore()
        else:
            self.store = QdrantStore()
        
        self.top_k = settings.top_k
        self.enable_fulltext = enable_fulltext
        self.enable_llm_rerank = enable_llm_rerank
        
        self.hybrid_retriever = HybridRetriever(vector_weight=0.5, bm25_weight=0.5)
        
        self.llm_reranker: Optional[LLMReranker] = None
        if enable_llm_rerank:
            self.llm_reranker = get_llm_reranker(reranker_model)
        
        self.fulltext_searcher: Optional[FullTextSearcher] = None
        if enable_fulltext:
            self.fulltext_searcher = FullTextSearcher()
        
        self.hybrid_searcher: Optional[HybridSearcher] = None
        if enable_fulltext:
            self.hybrid_searcher = HybridSearcher(
                fulltext_searcher=self.fulltext_searcher,
                vector_weight=0.5,
                fulltext_weight=0.5
            )
            self.hybrid_searcher.set_vector_searcher(self._vector_search_wrapper)

    def _vector_search_wrapper(self, query: str, embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """向量检索的包装函数，用于混合搜索"""
        return self.store.search(query_vector=embedding, top_k=top_k)

    def retrieve(self, query: str, embedding: List[float], top_k: int = None) -> List[Dict[str, Any]]:
        """基础向量检索"""
        top_k = top_k or self.top_k
        results = self.store.search(
            query_vector=embedding,
            top_k=top_k,
        )
        return results

    def fulltext_search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """全文检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        if not self.fulltext_searcher:
            raise RuntimeError("Fulltext search is not enabled. Set enable_fulltext=True when initializing Retriever.")
        
        top_k = top_k or self.top_k
        return self.fulltext_searcher.search(query, limit=top_k)

    def hybrid_retrieve(
        self,
        query: str,
        embedding: List[float],
        top_k: int = None,
        use_rerank: bool = True,
        rerank_method: str = "bm25"
    ) -> List[Dict[str, Any]]:
        """混合检索（向量检索 + 多种重排策略）
        
        支持的重排方法：
        - bm25: BM25 重排序
        - llm: LLM Cross-Encoder 重排序
        - hybrid: 混合检索 (向量 + 全文)

        Args:
            query: 查询文本
            embedding: 查询向量
            top_k: 返回结果数量
            use_rerank: 是否使用重排序
            rerank_method: 重排序方法 ('bm25', 'llm', 'hybrid')
        """
        top_k = top_k or self.top_k
        
        if rerank_method == "hybrid":
            return self._hybrid_search(query, embedding, top_k)
        
        vector_results = self.store.search(
            query_vector=embedding,
            top_k=top_k * 2,
        )

        if not vector_results:
            return []

        if not use_rerank:
            for i, doc in enumerate(vector_results):
                doc['rank'] = i + 1
            return vector_results[:top_k]

        if rerank_method == "llm" and self.llm_reranker:
            return self.llm_reranker.rerank(query, vector_results, top_k=top_k)
        
        return self.hybrid_retriever.rerank(query, vector_results, use_hybrid=True, top_k=top_k)

    def _hybrid_search(
        self,
        query: str,
        embedding: List[float],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """执行混合搜索 (向量 + 全文)"""
        if not self.hybrid_searcher:
            raise RuntimeError("Hybrid search is not enabled. Set enable_fulltext=True when initializing Retriever.")
        
        return self.hybrid_searcher.search(
            query=query,
            embedding=embedding,
            top_k=top_k,
            use_fulltext=True,
            use_vector=True
        )

    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = None,
        method: str = "bm25"
    ) -> List[Dict[str, Any]]:
        """使用指定方法重排检索结果
        
        Args:
            query: 查询文本
            results: 待重排的检索结果
            top_k: 返回结果数量
            method: 重排方法 ('bm25', 'llm')
            
        Returns:
            重排后的结果列表
        """
        top_k = top_k or self.top_k
        
        if method == "llm" and self.llm_reranker:
            return self.llm_reranker.rerank(query, results, top_k=top_k)
        
        return self.hybrid_retriever.rerank(query, results, use_hybrid=True, top_k=top_k)

    def add_points(self, points: List[Dict[str, Any]]):
        """添加向量点到索引
        
        Args:
            points: 向量点列表
        """
        if hasattr(self.store, 'add_points'):
            self.store.add_points(points)
        else:
            print("Error: Store does not have add_points method")
        
        if self.fulltext_searcher and self.enable_fulltext:
            ft_documents = []
            for point in points:
                if 'content' in point:
                    ft_documents.append({
                        "id": point.get("id", point.get("file_path", "")),
                        "content": point.get("content", ""),
                        "file_path": point.get("file_path", ""),
                        "start_line": point.get("start_line", 0),
                        "end_line": point.get("end_line", 0),
                    })
            if ft_documents:
                self.fulltext_searcher.add_documents(ft_documents)

    def add_documents_to_fulltext(self, documents: List[Dict[str, Any]]) -> int:
        """添加文档到全文索引
        
        Args:
            documents: 文档列表
            
        Returns:
            添加的文档数量
        """
        if not self.fulltext_searcher:
            raise RuntimeError("Fulltext search is not enabled.")
        
        return self.fulltext_searcher.add_documents(documents)

    def clear_index(self):
        """清空向量索引"""
        if hasattr(self.store, 'clear_index'):
            self.store.clear_index()
        elif hasattr(self.store, 'delete_collection'):
            self.store.delete_collection()
        else:
            print("Error: Store does not have clear method")

    def clear_fulltext_index(self):
        """清空全文索引"""
        if self.fulltext_searcher:
            self.fulltext_searcher.clear_index()

    def clear_all_indexes(self):
        """清空所有索引"""
        self.clear_index()
        self.clear_fulltext_index()

    def warmup(self):
        """预热 LLM 重排序模型"""
        if self.llm_reranker:
            self.llm_reranker.warmup()

    def __repr__(self) -> str:
        return (
            f"Retriever("
            f"vector_store={settings.vector_store}, "
            f"enable_llm_rerank={self.enable_llm_rerank}, "
            f"enable_fulltext={self.enable_fulltext})"
        )
