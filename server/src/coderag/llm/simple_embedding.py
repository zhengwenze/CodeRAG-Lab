"""
Simple embedding provider - fallback when real models unavailable
"""
import numpy as np
from typing import List
import hashlib


class SimpleEmbeddingProvider:
    """简单的基于 hash 的嵌入向量提供者 (备用方案)"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def embed(self, text: str) -> List[float]:
        """生成文本嵌入 (简单 hash 方法)"""
        vec = np.zeros(self.dimension, dtype=np.float32)
        
        # 使用多个 hash 函数生成不同的维度值
        for i in range(min(len(text), self.dimension)):
            # 字符级别的 hash
            hash_val = hashlib.md5(f"{text}_{i}".encode()).hexdigest()
            vec[i] = int(hash_val[:8], 16) % 1000 / 1000.0
        
        # 添加位置编码
        for i in range(self.dimension):
            vec[i] += np.sin(i / self.dimension * np.pi) * 0.1
        
        # 归一化
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
            
        return vec.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成嵌入"""
        return [self.embed(text) for text in texts]
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        return self.dimension


def get_simple_embedding_provider(dimension: int = 384) -> SimpleEmbeddingProvider:
    """获取简单的嵌入提供者"""
    return SimpleEmbeddingProvider(dimension)
