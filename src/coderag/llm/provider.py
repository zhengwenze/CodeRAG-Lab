from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMProvider(ABC):
    """LLM提供者接口"""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """生成回答"""
        pass

    @abstractmethod
    def stream_generate(self, prompt: str, **kwargs) -> str:
        """流式生成回答"""
        pass

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """生成文本嵌入"""
        pass


class LLMProviderFactory:
    """LLM提供者工厂"""

    @staticmethod
    def get_provider(provider_name: str, **kwargs) -> LLMProvider:
        """获取LLM提供者"""
        if provider_name == "llamacpp":
            from coderag.llm.llamacpp_openai import LlamaCppOpenAI
            return LlamaCppOpenAI(**kwargs)
        elif provider_name == "hf":
            # 后续实现HF Transformers提供者
            raise NotImplementedError("HF provider not implemented yet")
        else:
            raise ValueError(f"Unknown provider: {provider_name}")