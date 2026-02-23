from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 基础配置
    project_name: str = "CodeRAG Lab"
    environment: str = "development"
    debug: bool = True

    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # 向量库配置
    vector_store: str = "qdrant"  # faiss 或 qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "coderag"

    # 嵌入模型配置
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384

    # LLM配置
    llm_provider: str = "llamacpp"  # llamacpp 或 hf

    # llama.cpp配置
    llamacpp_host: str = "localhost"
    llamacpp_port: int = 8080
    llamacpp_model_path: str = "/path/to/model.gguf"

    # HF Transformers配置
    hf_model_name: str = "mistralai/Mistral-7B-v0.1"
    hf_device: str = "cpu"

    # 检索配置
    top_k: int = 5
    top_p: float = 0.95
    temperature: float = 0.7

    # 分块配置
    chunk_size: int = 1000
    chunk_overlap: int = 100

    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/coderag.log"

    # 评测配置
    eval_dataset_path: str = "data/eval/coderag_eval_v1.json"
    eval_output_path: str = "data/runs/"

    # 数据目录
    data_dir: str = "data"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()