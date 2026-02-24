from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn
import uuid

from coderag.settings import settings
from coderag.api.schemas import HealthCheck, ChatRequest, ChatResponse, Reference, RetrievalResult, AskRequest, AskResponse
from coderag.logging import get_logger
from coderag.exceptions import CodeRAGException, handle_exception

logger = get_logger(__name__)

app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    description="可溯源代码库助手",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(CodeRAGException)
async def coderag_exception_handler(request: Request, exc: CodeRAGException):
    """CodeRAG异常处理"""
    logger.error(f"CodeRAGException: {exc.error_code} - {exc.message}", exc_info=exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"General Exception: {exc}", exc_info=exc)
    http_exc = handle_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
    )


# 请求ID中间件
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """添加请求ID"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    # 更新日志上下文
    import logging
    logging.currentframe().f_locals['request_id'] = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
async def health_check(request: Request):
    """健康检查端点"""
    logger.info("Health check request received", extra={"request_id": getattr(request.state, "request_id", "")})
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="0.1.0",
    )


@app.post("/chat")
async def chat(request: Request, chat_request: ChatRequest):
    """聊天端点"""
    request_id = getattr(request.state, "request_id", "")
    logger.info(f"Chat request received: {chat_request.message[:50]}...", extra={"request_id": request_id})
    
    try:
        # 暂时返回mock数据
        references = [
            Reference(
                file_path="src/coderag/api/main.py",
                start_line=1,
                end_line=10,
                content="from fastapi import FastAPI, HTTPException\nfrom fastapi.middleware.cors import CORSMiddleware",
                score=0.95,
            )
        ]
        retrieval_results = [
            RetrievalResult(
                file_path="src/coderag/api/main.py",
                content="from fastapi import FastAPI, HTTPException",
                score=0.95,
                rank=1,
            )
        ]
        
        response = ChatResponse(
            id=request_id,
            message="这是一个mock回答",
            references=references,
            retrieval_results=retrieval_results,
            timestamp=datetime.utcnow(),
        )
        
        logger.info("Chat request processed successfully", extra={"request_id": request_id})
        return response
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", extra={"request_id": request_id}, exc_info=e)
        raise


@app.post("/ask")
async def ask(request: Request, ask_request: AskRequest):
    """检索端点，返回top-k片段"""
    request_id = getattr(request.state, "request_id", "")
    logger.info(f"Ask request received: {ask_request.query[:50]}...", extra={"request_id": request_id})
    
    try:
        from coderag.rag.retriever import Retriever
        from coderag.llm.provider import LLMProviderFactory
        from coderag.settings import settings
        
        # 生成查询嵌入
        llm = LLMProviderFactory.get_provider(settings.llm_provider)
        embedding = llm.embed(ask_request.query)
        
        # 检索相关片段
        retriever = Retriever()
        results = retriever.retrieve(
            query=ask_request.query,
            embedding=embedding,
            top_k=ask_request.top_k
        )
        
        # 转换为RetrievalResult格式
        retrieval_results = [
            RetrievalResult(
                file_path=result['file_path'],
                content=result['content'],
                score=result['score'],
                rank=result['rank'],
            )
            for result in results
        ]
        
        response = AskResponse(
            query=ask_request.query,
            results=retrieval_results,
            timestamp=datetime.utcnow(),
        )
        
        logger.info(f"Ask request processed successfully, retrieved {len(results)} results", extra={"request_id": request_id})
        return response
    except Exception as e:
        logger.error(f"Error processing ask request: {e}", extra={"request_id": request_id}, exc_info=e)
        raise


if __name__ == "__main__":
    logger.info(f"Starting CodeRAG Lab service on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "coderag.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )