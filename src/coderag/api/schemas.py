from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class HealthCheck(BaseModel):
    status: str = "healthy"
    timestamp: datetime
    version: str


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户问题")
    top_k: int = Field(5, description="检索结果数量")
    stream: bool = Field(True, description="是否流式输出")


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


# 解决循环引用
Reference.model_rebuild()
RetrievalResult.model_rebuild()
ChatResponse.model_rebuild()