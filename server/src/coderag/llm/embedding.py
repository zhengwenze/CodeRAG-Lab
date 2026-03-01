from typing import List, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
from coderag.settings import settings, EmbeddingModelConfig
import logging

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    """嵌入向量提供者，支持多种模型"""

    def __init__(self, model_name: str = None, config: EmbeddingModelConfig = None):
        self.model_name = model_name or settings.embedding_model
        self.config = config or settings.get_embedding_config(self.model_name)
        self.model = None

    def _get_local_model(self):
        """加载本地 Sentence Transformers 模型"""
        import os
        if self.model is None:
            cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
            model_cache = os.path.join(cache_dir, f"models--{self.model_name.replace('/', '--')}")
            
            # 检查模型缓存是否完整
            if os.path.exists(model_cache):
                snapshot_dir = os.path.join(model_cache, "snapshots")
                if os.path.exists(snapshot_dir):
                    for snapshot in os.listdir(snapshot_dir):
                        config_file = os.path.join(snapshot_dir, snapshot, "config.json")
                        if not os.path.exists(config_file):
                            logger.warning(f"Model cache incomplete, will re-download: {self.model_name}")
                            # 删除不完整的缓存
                            import shutil
                            shutil.rmtree(model_cache, ignore_errors=True)
                            break
            
            try:
                self.model = SentenceTransformer(self.model_name, device=self.config.device)
            except Exception as e:
                logger.error(f"Failed to load model {self.model_name}: {e}")
                raise
        return self.model

    def _get_api_model(self):
        """获取 API 嵌入模型"""
        if self.config.model_type == "zhipu":
            return self._get_zhipu_model()
        elif self.config.model_type == "openai":
            return self._get_openai_model()
        elif self.config.model_type == "ollama":
            return self._get_ollama_model()
        elif self.config.model_type == "minimax":
            return self._get_minimax_model()
        else:
            raise ValueError(f"不支持的 API 模型类型: {self.config.model_type}")

    def _get_minimax_model(self):
        """MiniMax 嵌入模型"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
            return MiniMaxEmbeddingClient(client, self.config.model_name)
        except ImportError:
            raise ImportError("请安装 OpenAI SDK: pip install openai")

    def _get_zhipu_model(self):
        """智谱AI嵌入模型"""
        try:
            from zhipuai import ZhipuAI
            client = ZhipuAI(api_key=self.config.api_key)
            return ZhipuEmbeddingClient(client, self.config.model_name)
        except ImportError:
            raise ImportError("请安装智谱AI SDK: pip install zhipuai")

    def _get_openai_model(self):
        """OpenAI 兼容嵌入模型"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
            return OpenAIEmbeddingClient(client, self.config.model_name)
        except ImportError:
            raise ImportError("请安装 OpenAI SDK: pip install openai")

    def _get_ollama_model(self):
        """Ollama 嵌入模型"""
        return OllamaEmbeddingClient(self.config.base_url, self.config.model_name)

    def embed(self, text: str) -> List[float]:
        """生成文本嵌入"""
        if self.config.model_type == "local":
            try:
                model = self._get_local_model()
                embedding = model.encode(text, normalize_embeddings=self.config.normalize_embeddings)
                return embedding.tolist()
            except Exception as e:
                logger.warning(f"Failed to load local model, using simple embedding: {e}")
                from coderag.llm.simple_embedding import get_simple_embedding_provider
                simple_provider = get_simple_embedding_provider(self.config.dimension)
                return simple_provider.embed(text)
        else:
            try:
                client = self._get_api_model()
                return client.embed(text)
            except Exception as e:
                logger.warning(f"Failed to use API embedding, using simple embedding: {e}")
                from coderag.llm.simple_embedding import get_simple_embedding_provider
                simple_provider = get_simple_embedding_provider(self.config.dimension)
                return simple_provider.embed(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本嵌入"""
        if self.config.model_type == "local":
            try:
                model = self._get_local_model()
                embeddings = model.encode(
                    texts, 
                    normalize_embeddings=self.config.normalize_embeddings,
                    batch_size=self.config.batch_size
                )
                return embeddings.tolist()
            except Exception as e:
                logger.warning(f"Failed to load local model, using simple embedding: {e}")
                from coderag.llm.simple_embedding import get_simple_embedding_provider
                simple_provider = get_simple_embedding_provider(self.config.dimension)
                return simple_provider.embed_batch(texts)
        else:
            try:
                client = self._get_api_model()
                return client.embed_batch(texts)
            except Exception as e:
                logger.warning(f"Failed to use API embedding, using simple embedding: {e}")
                from coderag.llm.simple_embedding import get_simple_embedding_provider
                simple_provider = get_simple_embedding_provider(self.config.dimension)
                return simple_provider.embed_batch(texts)

    def get_dimension(self) -> int:
        """获取向量维度"""
        return self.config.dimension


class ZhipuEmbeddingClient:
    """智谱AI嵌入客户端"""

    def __init__(self, client, model_name: str):
        self.client = client
        self.model_name = model_name

    def embed(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        return [item.embedding for item in response.data]


class OpenAIEmbeddingClient:
    """OpenAI 兼容嵌入客户端"""

    def __init__(self, client, model_name: str):
        self.client = client
        self.model_name = model_name

    def embed(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        return [item.embedding for item in response.data]


class OllamaEmbeddingClient:
    """Ollama 嵌入客户端"""

    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name

    def _request(self, texts: List[str]) -> List[List[float]]:
        import requests
        url = f"{self.base_url}/api/embeddings"
        response = requests.post(
            url,
            json={"model": self.model_name, "prompt": texts[0]}
        )
        if response.status_code == 200:
            return [response.json()["embedding"]]
        raise Exception(f"Ollama embedding failed: {response.text}")

    def embed(self, text: str) -> List[float]:
        return self._request([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(text) for text in texts]


class MiniMaxEmbeddingClient:
    """MiniMax 嵌入客户端 (OpenAI 兼容格式)"""

    def __init__(self, client, model_name: str):
        self.client = client
        self.model_name = model_name

    def embed(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        return [item.embedding for item in response.data]


def get_embedding_provider(model_name: str = None) -> EmbeddingProvider:
    """获取嵌入提供者实例"""
    return EmbeddingProvider(model_name)


def list_available_embedding_models() -> Dict[str, Dict[str, Any]]:
    """列出所有可用的嵌入模型配置"""
    return settings.embedding_models
