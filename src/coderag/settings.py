from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any


class EmbeddingModelConfig(BaseSettings):
    """嵌入模型配置"""
    model_name: str = "BAAI/bge-small-en-v1.5"
    model_type: str = "local"
    dimension: int = 384
    device: str = "cpu"
    normalize_embeddings: bool = True
    batch_size: int = 32
    max_seq_length: int = 512
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_path: Optional[str] = None


class Settings(BaseSettings):
    # 基础配置
    project_name: str = "CodeRAG Lab"
    environment: str = "development"
    debug: bool = True

    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # 向量库配置
    vector_store: str = "qdrant"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "coderag"
    
    # FAISS配置
    faiss_index_path: str = "data/faiss_index"
    faiss_metadata_path: str = "data/faiss_metadata.pkl"

    # PostgreSQL + pgvector 配置
    pgvector_enabled: bool = False
    pgvector_connection_string: str = "postgresql://user:password@localhost:5432/coderag"

    # 嵌入模型配置
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384
    embedding_device: str = "cpu"

    embedding_models: Dict[str, Dict[str, Any]] = {
        "bge-small": {
            "type": "local",
            "model": "BAAI/bge-small-en-v1.5",
            "dimension": 384,
            "device": "cpu",
            "description": "BAAI bge-small-en-v1.5 本地模型",
        },
        "bge-base": {
            "type": "local",
            "model": "BAAI/bge-base-en-v1.5",
            "dimension": 768,
            "device": "cpu",
            "description": "BAAI bge-base-en-v1.5 本地模型",
        },
        "bge-large": {
            "type": "local",
            "model": "BAAI/bge-large-en-v1.5",
            "dimension": 1024,
            "device": "cpu",
            "description": "BAAI bge-large-en-v1.5 本地模型",
        },
        "zhipu": {
            "type": "api",
            "model": "embedding-3",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "api_key": "",
            "dimension": 1024,
            "description": "智谱AI embedding-3 API",
        },
        "openai": {
            "type": "api",
            "model": "text-embedding-ada-002",
            "base_url": "https://api.openai.com/v1",
            "api_key": "",
            "dimension": 1536,
            "description": "OpenAI Ada embedding API",
        },
        "ollama": {
            "type": "ollama",
            "model": "nomic-embed-text",
            "base_url": "http://localhost:11434",
            "dimension": 768,
            "description": "Ollama 本地 embedding 模型",
        },
        "minimax": {
            "type": "minimax",
            "model": "embedding-3-256",  # TODO: 确认实际模型名称
            "base_url": "https://api.minimax.chat/v1",
            "api_key": "",  # TODO: 填入你的 MiniMax API Key
            "dimension": 1024,
            "description": "MiniMax embedding API",
        },
    }

    # LLM配置
    llm_provider: str = "minimax"

    # llama.cpp配置
    llamacpp_host: str = "localhost"
    llamacpp_port: int = 8080
    llamacpp_model_path: str = "/path/to/model.gguf"

    # MiniMax 配置 (请填入你的API Key)
    minimax_api_key: str = ""  # TODO: 填入你的 MiniMax API Key
    minimax_base_url: str = "https://api.minimax.chat/v1"
    minimax_model: str = "MiniMax-M2.5"  # TODO: 根据实际模型名称调整

    # HF Transformers配置
    hf_model_name: str = "mistralai/Mistral-7B-v0.1"
    hf_device: str = "cpu"

    # 检索配置
    top_k: int = 5
    top_p: float = 0.95
    temperature: float = 0.7

    # 检索增强配置
    enable_llm_rerank: bool = False
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    enable_fulltext: bool = False
    fulltext_index_dir: str = "data/whoosh_index"
    min_similarity: float = 0.0
    vector_weight: float = 0.5
    fulltext_weight: float = 0.5

    # 分块配置
    chunk_size: int = 2000
    chunk_overlap: int = 200

    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/coderag.log"

    # 评测配置
    eval_dataset_path: str = "data/eval/coderag_eval_v1.json"
    eval_output_path: str = "data/runs/"

    # 数据目录
    data_dir: str = "data"

    def get_embedding_config(self, model_name: str = None) -> EmbeddingModelConfig:
        """获取指定嵌入模型的配置"""
        model_name = model_name or self.embedding_model
        
        if model_name in self.embedding_models:
            config = self.embedding_models[model_name]
            return EmbeddingModelConfig(
                model_name=config.get("model", model_name),
                model_type=config.get("type", "local"),
                dimension=config.get("dimension", self.embedding_dim),
                device=config.get("device", self.embedding_device),
                base_url=config.get("base_url"),
                api_key=config.get("api_key"),
                model_path=config.get("model_path"),
            )
        
        return EmbeddingModelConfig(
            model_name=model_name,
            model_type="local",
            dimension=self.embedding_dim,
            device=self.embedding_device,
        )

    class Config:
        env_file = (".env.local", ".env")
        case_sensitive = False
        extra = "ignore"


settings = Settings()
