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


@app.get("/config")
async def get_config():
    """获取配置"""
    return {
        "embedding_model": settings.embedding_model,
        "embedding_dim": settings.embedding_dim,
        "llm_provider": settings.llm_provider,
        "vector_store": settings.vector_store,
    }


@app.post("/chat")
async def chat(request: Request, chat_request: ChatRequest):
    """聊天端点，实现RAG问答"""
    request_id = getattr(request.state, "request_id", "")
    logger.info(f"Chat request received: {chat_request.messages[-1].content[:50]}...", extra={"request_id": request_id})
    
    try:
        from coderag.security import get_input_validator, get_output_sanitizer
        validator = get_input_validator()
        sanitizer = get_output_sanitizer()
        
        # 获取最后一条用户消息
        user_message = None
        for msg in reversed(chat_request.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message or not user_message.strip():
            raise HTTPException(status_code=400, detail="User message cannot be empty")
        
        # 验证用户输入
        user_message = validator.validate_message(user_message)
        
        from coderag.rag.retriever import Retriever
        from coderag.rag.prompt import PromptTemplate
        from coderag.llm.provider import LLMProviderFactory
        from coderag.settings import settings
        
        # 生成查询嵌入
        llm = LLMProviderFactory.get_provider(settings.llm_provider)
        embedding = llm.embed(user_message)
        
        # 检索相关片段
        retriever = Retriever()
        results = retriever.retrieve(
            query=user_message,
            embedding=embedding,
            top_k=chat_request.top_k
        )
        
        # 构建上下文
        contexts = [
            {
                'file_path': result['file_path'],
                'content': result['content'],
                'start_line': result.get('start_line'),
                'end_line': result.get('end_line'),
            }
            for result in results
        ]
        
        # 构建Prompt并调用LLM
        prompt = PromptTemplate.rag_prompt(user_message, contexts)
        answer = llm.generate(prompt)
        
        # 构建引用
        references = [
            Reference(
                file_path=result['file_path'],
                start_line=result.get('start_line'),
                end_line=result.get('end_line'),
                content=result['content'],
                score=result['score'],
            )
            for result in results
        ]
        
        # 构建检索结果
        retrieval_results = [
            RetrievalResult(
                file_path=result['file_path'],
                content=result['content'],
                score=result['score'],
                rank=result['rank'],
            )
            for result in results
        ]
        
        # 构建响应并清理输出
        response_data = {
            "id": request_id,
            "message": answer,
            "references": references if chat_request.include_hits else [],
            "retrieval_results": retrieval_results if chat_request.include_hits else [],
            "timestamp": datetime.utcnow(),
        }
        
        response = ChatResponse(**sanitizer.sanitize_response(response_data))
        
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


@app.post("/eval/run")
async def run_evaluation(request: Request):
    """运行评测"""
    from coderag.eval.runner import EvaluationRunner
    from coderag.settings import settings
    
    try:
        runner = EvaluationRunner(
            dataset_path=settings.eval_dataset_path,
            top_k=settings.top_k,
            skip_llm=True
        )
        results = runner.run_evaluation()
        
        return {
            "status": "completed",
            "dataset_name": results.get("dataset_name"),
            "total_questions": results.get("total_questions"),
            "metrics": results.get("metrics"),
            "timestamp": results.get("timestamp"),
        }
    except Exception as e:
        logger.error(f"Error running evaluation: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/eval/results")
async def get_evaluation_results():
    """获取最新的评测结果"""
    import os
    from pathlib import Path
    
    eval_output_path = Path(settings.eval_output_path)
    if not eval_output_path.exists():
        return {"results": [], "message": "No evaluation results found"}
    
    result_files = sorted(eval_output_path.glob("coderag_eval_v1_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not result_files:
        return {"results": [], "message": "No evaluation results found"}
    
    results = []
    for f in result_files[:10]:
        results.append({
            "filename": f.name,
            "path": str(f),
        })
    
    return {"results": results}


@app.get("/eval/results/{filename}")
async def get_evaluation_result(filename: str):
    """获取指定评测结果文件"""
    import json
    from pathlib import Path
    
    file_path = Path(settings.eval_output_path) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


@app.get("/datasets")
async def list_datasets():
    """获取知识库列表"""
    from pathlib import Path
    data_dir = Path(settings.data_dir)
    datasets_dir = data_dir / "datasets"
    
    if not datasets_dir.exists():
        return {"data": []}
    
    datasets = []
    for ds in datasets_dir.iterdir():
        if ds.is_dir():
            doc_count = len(list(ds.glob("*.txt"))) + len(list(ds.glob("*.md")))
            datasets.append({
                "id": ds.name,
                "name": ds.name,
                "description": f"知识库 {ds.name}",
                "document_count": doc_count,
                "chunk_count": doc_count * 10,
                "created_at": datetime.utcnow().isoformat(),
            })
    
    return {"data": datasets}


@app.post("/datasets")
async def create_dataset(request: Request):
    """创建知识库"""
    from pathlib import Path
    import json
    
    data_dir = Path(settings.data_dir)
    datasets_dir = data_dir / "datasets"
    datasets_dir.mkdir(parents=True, exist_ok=True)
    
    body = await request.json()
    name = body.get("name", "unnamed")
    
    ds_path = datasets_dir / name
    ds_path.mkdir(parents=True, exist_ok=True)
    
    return {
        "id": name,
        "name": name,
        "description": body.get("description", ""),
        "created_at": datetime.utcnow().isoformat(),
    }


@app.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    """获取知识库详情"""
    from pathlib import Path
    
    data_dir = Path(settings.data_dir)
    ds_path = data_dir / "datasets" / dataset_id
    
    if not ds_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return {
        "id": dataset_id,
        "name": dataset_id,
        "description": f"知识库 {dataset_id}",
    }


@app.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """删除知识库"""
    from pathlib import Path
    import shutil
    
    data_dir = Path(settings.data_dir)
    ds_path = data_dir / "datasets" / dataset_id
    
    if ds_path.exists():
        shutil.rmtree(ds_path)
    
    return {"message": "Dataset deleted"}


@app.post("/datasets/{dataset_id}/documents")
async def upload_document(dataset_id: str, request: Request):
    """上传文档"""
    from pathlib import Path
    import shutil
    
    data_dir = Path(settings.data_dir)
    ds_path = data_dir / "datasets" / dataset_id
    ds_path.mkdir(parents=True, exist_ok=True)
    
    form = await request.form()
    file = form.get("file")
    
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_path = ds_path / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    return {
        "id": file.filename,
        "filename": file.filename,
        "status": "completed",
        "size": file_path.stat().st_size,
        "created_at": datetime.utcnow().isoformat(),
    }


@app.get("/datasets/{dataset_id}/documents")
async def list_documents(dataset_id: str):
    """获取文档列表"""
    from pathlib import Path
    
    data_dir = Path(settings.data_dir)
    ds_path = data_dir / "datasets" / dataset_id
    
    if not ds_path.exists():
        return {"data": []}
    
    documents = []
    for f in ds_path.iterdir():
        if f.is_file():
            documents.append({
                "id": f.name,
                "filename": f.name,
                "status": "completed",
                "size": f.stat().st_size,
                "created_at": datetime.fromtimestamp(f.stat().st_ctime).isoformat(),
            })
    
    return {"data": documents}


@app.delete("/datasets/{dataset_id}/documents/{document_id}")
async def delete_document(dataset_id: str, document_id: str):
    """删除文档"""
    from pathlib import Path
    
    data_dir = Path(settings.data_dir)
    file_path = data_dir / "datasets" / dataset_id / document_id
    
    if file_path.exists():
        file_path.unlink()
    
    return {"message": "Document deleted"}


@app.get("/datasets/{dataset_id}/documents/{document_id}/chunks")
async def get_chunks(dataset_id: str, document_id: str):
    """获取文档切片"""
    return {"data": []}


if __name__ == "__main__":
    logger.info(f"Starting CodeRAG Lab service on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "coderag.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )