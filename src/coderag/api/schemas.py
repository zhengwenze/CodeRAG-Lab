from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
import re


class HealthCheck(BaseModel):
    status: str = "healthy"
    timestamp: datetime
    version: str


class ChatMessage(BaseModel):
    role: str = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        if len(v) > 10000:
            raise ValueError("Message content exceeds maximum length of 10000")
        return v.strip()

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed_roles = ['user', 'assistant', 'system']
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")
        return v


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="对话消息列表")
    top_k: int = Field(5, description="检索结果数量")
    stream: bool = Field(True, description="是否流式输出")
    include_hits: bool = Field(True, description="是否包含检索结果")

    @field_validator('top_k')
    @classmethod
    def validate_top_k(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError("top_k must be between 1 and 100")
        return v


class ChatResponse(BaseModel):
    id: str
    message: str
    references: List["Reference"]
    retrieval_results: List["RetrievalResult"]
    timestamp: datetime


class Reference(BaseModel):
    file_path: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    content: str
    score: float


class RetrievalResult(BaseModel):
    file_path: str
    content: str
    score: float
    rank: int


class EvaluationRequest(BaseModel):
    dataset_path: str = Field(..., description="评测数据集路径")
    top_k: int = Field(5, description="检索结果数量")


class EvaluationResult(BaseModel):
    recall_at_k: float
    mrr: float
    accuracy: float
    no_reference_rate: float
    timestamp: datetime


class AskRequest(BaseModel):
    query: str = Field(..., description="用户查询")
    top_k: int = Field(5, description="检索结果数量")


class AskResponse(BaseModel):
    query: str
    results: List[RetrievalResult]
    timestamp: datetime


# 解决循环引用
Reference.model_rebuild()
RetrievalResult.model_rebuild()
ChatResponse.model_rebuild()
AskResponse.model_rebuild()