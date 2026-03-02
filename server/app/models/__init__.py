"""数据模型模块"""

from typing import Optional, Dict, Any
from datetime import datetime

class Document:
    """文档模型"""
    def __init__(
        self,
        file_path: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.file_path = file_path
        self.content = content
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()

class Chunk:
    """文档分块模型"""
    def __init__(
        self,
        chunk_id: str,
        content: str,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.chunk_id = chunk_id
        self.content = content
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.metadata = metadata or {}

class RetrievalHit:
    """检索结果模型"""
    def __init__(
        self,
        chunk_id: str,
        content: str,
        file_path: str,
        score: float,
        rank: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.chunk_id = chunk_id
        self.content = content
        self.file_path = file_path
        self.score = score
        self.rank = rank
        self.metadata = metadata or {}

__all__ = ["Document", "Chunk", "RetrievalHit"]
