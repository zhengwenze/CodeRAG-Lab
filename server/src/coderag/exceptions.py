from fastapi import HTTPException, status
from typing import Dict, Any, Optional


class ErrorCode:
    """错误码定义"""
    # 系统错误
    SYSTEM_ERROR = "SYSTEM_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"

    # 业务错误
    INVALID_INPUT = "INVALID_INPUT"
    NOT_FOUND = "NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # 评测错误
    EVALUATION_ERROR = "EVALUATION_ERROR"
    DATASET_ERROR = "DATASET_ERROR"

    # 推理错误
    LLM_ERROR = "LLM_ERROR"
    INFERENCE_ERROR = "INFERENCE_ERROR"


class CodeRAGException(Exception):
    """CodeRAG 基础异常"""

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class SystemException(CodeRAGException):
    """系统异常"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            ErrorCode.SYSTEM_ERROR,
            message,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            details,
        )


class InvalidInputException(CodeRAGException):
    """输入无效异常"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            ErrorCode.INVALID_INPUT,
            message,
            status.HTTP_400_BAD_REQUEST,
            details,
        )


class NotFoundException(CodeRAGException):
    """资源未找到异常"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            ErrorCode.NOT_FOUND,
            message,
            status.HTTP_404_NOT_FOUND,
            details,
        )


class LLMRuntimeException(CodeRAGException):
    """LLM运行时异常"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            ErrorCode.LLM_ERROR,
            message,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            details,
        )


class EvaluationException(CodeRAGException):
    """评测异常"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            ErrorCode.EVALUATION_ERROR,
            message,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            details,
        )


def handle_exception(e: Exception) -> HTTPException:
    """异常处理函数"""
    if isinstance(e, CodeRAGException):
        return HTTPException(
            status_code=e.status_code,
            detail={
                "error_code": e.error_code,
                "message": e.message,
                "details": e.details,
            },
        )
    else:
        # 处理其他异常
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": ErrorCode.SYSTEM_ERROR,
                "message": "Internal server error",
                "details": str(e),
            },
        )