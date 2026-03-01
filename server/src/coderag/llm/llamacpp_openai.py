import requests
from typing import List, Dict, Any, Optional
from coderag.settings import settings
from coderag.llm.provider import LLMProvider


class LlamaCppOpenAI(LLMProvider):
    """llama.cpp OpenAI兼容接口"""

    def __init__(self, host: str = None, port: int = None, model_path: str = None):
        self.host = host or settings.llamacpp_host
        self.port = port or settings.llamacpp_port
        self.model_path = model_path or settings.llamacpp_model_path
        self.base_url = f"http://{self.host}:{self.port}/v1"
        self.headers = {
            "Content-Type": "application/json",
        }

    def generate(self, prompt: str, **kwargs) -> str:
        """生成回答"""
        endpoint = f"{self.base_url}/chat/completions"
        data = {
            "model": self.model_path,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": kwargs.get("temperature", settings.temperature),
            "top_p": kwargs.get("top_p", settings.top_p),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "stream": False,
        }

        try:
            response = requests.post(endpoint, json=data, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, I couldn't generate a response."

    def stream_generate(self, prompt: str, **kwargs) -> str:
        """流式生成回答"""
        endpoint = f"{self.base_url}/chat/completions"
        data = {
            "model": self.model_path,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": kwargs.get("temperature", settings.temperature),
            "top_p": kwargs.get("top_p", settings.top_p),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "stream": True,
        }

        try:
            response = requests.post(
                endpoint, json=data, headers=self.headers, stream=True
            )
            response.raise_for_status()

            full_response = ""
            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    chunk_str = chunk.decode('utf-8')
                    # 处理SSE格式
                    lines = chunk_str.split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            data_str = line[6:]
                            if data_str == '[DONE]':
                                break
                            import json
                            try:
                                chunk_data = json.loads(data_str)
                                if "choices" in chunk_data:
                                    delta = chunk_data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        content = delta["content"]
                                        full_response += content
                                        yield content
                            except json.JSONDecodeError:
                                pass
            return full_response
        except Exception as e:
            print(f"Error streaming response: {e}")
            yield "Sorry, I couldn't generate a response."

    def embed(self, text: str) -> List[float]:
        """生成文本嵌入"""
        endpoint = f"{self.base_url}/embeddings"
        data = {
            "model": self.model_path,
            "input": text,
        }

        try:
            response = requests.post(endpoint, json=data, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            return result["data"][0]["embedding"]
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # 返回零向量作为 fallback
            return [0.0] * settings.embedding_dim