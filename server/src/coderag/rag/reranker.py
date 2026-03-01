from typing import List, Dict, Any, Optional
import torch
from sentence_transformers import CrossEncoder


class LLMReranker:
    """基于 LLM/Cross-Encoder 的文档重排序器
    
    使用 Cross-Encoder 模型对检索结果进行更精确的重排序，
    相比 Bi-Encoder + BM25 的方式，可以获得更准确的语义相关性分数。
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3",
        device: Optional[str] = None,
        max_length: int = 512,
        use_fp16: bool = True
    ):
        """初始化 LLM 重排序器
        
        Args:
            model_name: Cross-Encoder 模型名称，支持以下模型:
                - BAAI/bge-reranker-v2-m3 (推荐，效果好)
                - BAAI/bge-reranker-base
                - BAAI/bge-reranker-large
                - cross-encoder/ms-marco-MiniLM-L-6-v2
                - cross-encoder/ms-marco-MiniLM-L-12-v2
            device: 设备类型，'cuda', 'cpu' 或 None (自动选择)
            max_length: 最大序列长度
            use_fp16: 是否使用 FP16 推理（节省显存）
        """
        self.model_name = model_name
        self.max_length = max_length
        
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        self.use_fp16 = use_fp16 and self.device == "cuda"
        
        self.model: Optional[CrossEncoder] = None
        self._load_model()
    
    def _load_model(self):
        """加载 Cross-Encoder 模型"""
        try:
            self.model = CrossEncoder(
                self.model_name,
                max_length=self.max_length,
                device=self.device
            )
            if self.use_fp16:
                self.model.modelhalf()
        except Exception as e:
            raise RuntimeError(f"Failed to load reranker model {self.model_name}: {e}")
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None,
        return_scores: bool = True
    ) -> List[Dict[str, Any]]:
        """对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 待重排的文档列表，每项需包含 'content' 字段
            top_k: 返回 top-k 结果，None 表示返回全部
            return_scores: 是否在结果中包含相关性分数
            
        Returns:
            重排后的文档列表，包含 'rerank_score' 字段
        """
        if not documents or not self.model:
            return documents
        
        if not all('content' in doc for doc in documents):
            raise ValueError("All documents must contain 'content' field")
        
        doc_contents = [doc['content'] for doc in documents]
        pairs = [(query, doc) for doc in doc_contents]
        
        try:
            scores = self.model.predict(pairs, convert_to_numpy=True)
        except Exception as e:
            raise RuntimeError(f"Reranking failed: {e}")
        
        for doc, score in zip(documents, scores):
            doc['rerank_score'] = float(score)
        
        sorted_docs = sorted(
            documents, 
            key=lambda x: x.get('rerank_score', 0), 
            reverse=True
        )
        
        for i, doc in enumerate(sorted_docs):
            doc['rank'] = i + 1
        
        if top_k is not None:
            sorted_docs = sorted_docs[:top_k]
        
        if not return_scores:
            for doc in sorted_docs:
                doc.pop('rerank_score', None)
        
        return sorted_docs
    
    def compute_scores(self, query: str, documents: List[str]) -> List[float]:
        """计算查询与文档的相关性分数
        
        Args:
            query: 查询文本
            documents: 文档内容列表
            
        Returns:
            相关性分数列表
        """
        if not self.model:
            return [0.0] * len(documents)
        
        pairs = [(query, doc) for doc in documents]
        scores = self.model.predict(pairs, convert_to_numpy=True)
        return scores.tolist()
    
    def warmup(self):
        """预热模型，运行一次推理以加快后续调用"""
        dummy_query = "warmup query"
        dummy_doc = ["warmup document"]
        self.model.predict([(dummy_query, dummy_doc)])
    
    @property
    def is_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self.model is not None
    
    def __repr__(self) -> str:
        return f"LLMReranker(model_name='{self.model_name}', device='{self.device}')"


class RerankConfig:
    """重排序配置类"""
    
    RERANK_MODELS = {
        "bge-reranker-v2-m3": "BAAI/bge-reranker-v2-m3",
        "bge-reranker-large": "BAAI/bge-reranker-large",
        "bge-reranker-base": "BAAI/bge-reranker-base",
        "ms-marco-MiniLM-L-6-v2": "cross-encoder/ms-marco-MiniLM-L-6-v2",
        "ms-marco-MiniLM-L-12-v2": "cross-encoder/ms-marco-MiniLM-L-12-v2",
    }
    
    @classmethod
    def get_model_name(cls, model_key: str) -> str:
        """获取模型名称"""
        return cls.RERANK_MODELS.get(model_key, cls.RERANK_MODELS["bge-reranker-v2-m3"])


def get_llm_reranker(
    model_name: str = "BAAI/bge-reranker-v2-m3",
    device: Optional[str] = None,
    **kwargs
) -> LLMReranker:
    """获取 LLM 重排序器实例的便捷函数
    
    Args:
        model_name: 模型名称或预定义 key
        device: 设备类型
        **kwargs: 其他参数
        
    Returns:
        LLMReranker 实例
    """
    if model_name in RerankConfig.RERANK_MODELS:
        model_name = RerankConfig.RERANK_MODELS[model_name]
    
    return LLMReranker(model_name=model_name, device=device, **kwargs)
