from sentence_transformers import SentenceTransformer
from typing import List
from coderag.settings import settings


class EmbeddingProvider:
    """嵌入向量提供者"""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self.model = None

    def _get_model(self):
        """延迟加载模型"""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
        return self.model

    def embed(self, text: str) -> List[float]:
        """生成文本嵌入"""
        model = self._get_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本嵌入"""
        model = self._get_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()


def get_embedding_provider() -> EmbeddingProvider:
    """获取嵌入提供者实例"""
    return EmbeddingProvider()
