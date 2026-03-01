from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    """文档索引状态"""
    PENDING = "pending"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"


class QuestionStatus(str, Enum):
    """问题生成状态"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentState(str, Enum):
    """文档可用状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class DocumentMetadata(BaseModel):
    """文档元数据模型"""
    document_id: str = Field(..., description="文档唯一标识")
    name: str = Field(..., description="文档名称")
    file_size: int = Field(default=0, description="文件大小（字节）")
    file_type: str = Field(default="", description="文件类型")
    status: DocumentStatus = Field(default=DocumentStatus.PENDING, description="索引状态")
    question_status: QuestionStatus = Field(default=QuestionStatus.PENDING, description="问题生成状态")
    state: DocumentState = Field(default=DocumentState.ACTIVE, description="可用状态")
    dataset_id: str = Field(default="", description="所属知识库ID")
    paragraph_num: int = Field(default=0, description="段落数量")
    chunk_num: int = Field(default=0, description="分块数量")
    embedding_time: Optional[datetime] = Field(default=None, description="向量化完成时间")
    question_time: Optional[datetime] = Field(default=None, description="问题生成完成时间")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    update_time: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class DatasetMetadata(BaseModel):
    """知识库元数据模型"""
    dataset_id: str = Field(..., description="知识库唯一标识")
    title: str = Field(default="", description="知识库标题")
    description: str = Field(default="", description="知识库描述")
    document_num: int = Field(default=0, description="文档数量")
    paragraph_num: int = Field(default=0, description="段落总数")
    embedding_model: str = Field(default="", description="嵌入模型名称")
    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    update_time: datetime = Field(default_factory=datetime.now, description="更新时间")


class DocumentStateManager:
    """文档状态管理器"""
    
    def __init__(self):
        self._states: Dict[str, DocumentMetadata] = {}
    
    def register_document(
        self,
        document_id: str,
        name: str,
        dataset_id: str = "",
        file_size: int = 0,
        file_type: str = "",
        metadata: Dict[str, Any] = None,
    ) -> DocumentMetadata:
        """注册新文档"""
        doc = DocumentMetadata(
            document_id=document_id,
            name=name,
            dataset_id=dataset_id,
            file_size=file_size,
            file_type=file_type,
            status=DocumentStatus.PENDING,
            metadata=metadata or {},
        )
        self._states[document_id] = doc
        return doc
    
    def start_indexing(self, document_id: str) -> None:
        """开始索引"""
        if document_id in self._states:
            self._states[document_id].status = DocumentStatus.INDEXING
            self._states[document_id].update_time = datetime.now()
    
    def complete_indexing(
        self,
        document_id: str,
        paragraph_num: int = 0,
        chunk_num: int = 0,
    ) -> None:
        """完成索引"""
        if document_id in self._states:
            self._states[document_id].status = DocumentStatus.COMPLETED
            self._states[document_id].paragraph_num = paragraph_num
            self._states[document_id].chunk_num = chunk_num
            self._states[document_id].embedding_time = datetime.now()
            self._states[document_id].update_time = datetime.now()
    
    def fail_indexing(self, document_id: str, error_message: str) -> None:
        """索引失败"""
        if document_id in self._states:
            self._states[document_id].status = DocumentStatus.FAILED
            self._states[document_id].error_message = error_message
            self._states[document_id].update_time = datetime.now()
    
    def start_question_generation(self, document_id: str) -> None:
        """开始生成问题"""
        if document_id in self._states:
            self._states[document_id].question_status = QuestionStatus.GENERATING
            self._states[document_id].update_time = datetime.now()
    
    def complete_question_generation(self, document_id: str) -> None:
        """完成问题生成"""
        if document_id in self._states:
            self._states[document_id].question_status = QuestionStatus.COMPLETED
            self._states[document_id].question_time = datetime.now()
            self._states[document_id].update_time = datetime.now()
    
    def fail_question_generation(self, document_id: str, error_message: str) -> None:
        """问题生成失败"""
        if document_id in self._states:
            self._states[document_id].question_status = QuestionStatus.FAILED
            self._states[document_id].error_message = error_message
            self._states[document_id].update_time = datetime.now()
    
    def deactivate(self, document_id: str) -> None:
        """停用文档"""
        if document_id in self._states:
            self._states[document_id].state = DocumentState.INACTIVE
            self._states[document_id].update_time = datetime.now()
    
    def activate(self, document_id: str) -> None:
        """激活文档"""
        if document_id in self._states:
            self._states[document_id].state = DocumentState.ACTIVE
            self._states[document_id].update_time = datetime.now()
    
    def get_status(self, document_id: str) -> Optional[DocumentMetadata]:
        """获取文档状态"""
        return self._states.get(document_id)
    
    def get_all_documents(self, dataset_id: str = None) -> list:
        """获取所有文档"""
        if dataset_id:
            return [doc for doc in self._states.values() if doc.dataset_id == dataset_id]
        return list(self._states.values())
    
    def get_documents_by_status(
        self,
        status: DocumentStatus,
        dataset_id: str = None,
    ) -> list:
        """按状态获取文档"""
        docs = [doc for doc in self._states.values() if doc.status == status]
        if dataset_id:
            docs = [doc for doc in docs if doc.dataset_id == dataset_id]
        return docs
    
    def remove(self, document_id: str) -> None:
        """移除文档"""
        if document_id in self._states:
            del self._states[document_id]
    
    def clear(self, dataset_id: str = None) -> None:
        """清空文档"""
        if dataset_id:
            self._states = {
                k: v for k, v in self._states.items() 
                if v.dataset_id != dataset_id
            }
        else:
            self._states.clear()


_global_state_manager = DocumentStateManager()


def get_document_state_manager() -> DocumentStateManager:
    """获取全局文档状态管理器"""
    return _global_state_manager
