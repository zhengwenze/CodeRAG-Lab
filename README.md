
---

# CodeRAG Lab（Win10）— 可溯源代码库助手（RAG + 评测 + llama.cpp 部署）

> 把任意开源/本地代码仓库（repo）变成一个 **"能检索、能引用、能评测、可服务化"** 的 RAG 问答系统。  
> **简历定位**：可溯源 RAG（Citations） + 评测体系（Eval/Regression） + 工程化服务（API/Deploy/CI）。

---

## Quickstart（快速跑通）

### 0) 前置依赖
- Python 3.10+
- Poetry
- Docker Desktop（用于 Qdrant）
- llama.cpp 的 `llama-server.exe`（OpenAI Compatible API）
- （可选）Git Bash（方便运行 make；没有 make 也可手动执行命令）

### 1) 启动 Qdrant
```docker compose up -d
docker compose up -d
```

### 2) 启动 llama.cpp（OpenAI 兼容）

**建议先用小模型跑通链路：**

```bash
llama-server -hf ggml-org/gemma-3-1b-it-GGUF --port 8080
```

（后续换你本地 GGUF 模型）

```bash
llama-server -m D:\models\your-model-q4_k_m.gguf --port 8080
```

验证：

```bash
curl http://127.0.0.1:8080/v1/models
```

### 3) 安装依赖 + 启动 API

```bash
copy .env.example .env
poetry install
poetry run uvicorn coderag.api.main:app --host 127.0.0.1 --port 8000 --reload
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

### 4) 入库一个 repo

```bash
poetry run python -m coderag.cli ingest-repo --repo "D:\path\to\repo"
```

### 5) 发起问答

PowerShell（注意引号转义）：

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/chat" `
  -ContentType "application/json" `
  -Body '{"messages":[{"role":"user","content":"Where is the FastAPI app created?"}],"top_k":6,"include_hits":true}'
```

---

## 1. 你将得到什么（功能与卖点）

* ✅ **可溯源问答（Citations）**：回答必须引用检索到的代码/文档片段（文件路径 + chunk）
* ✅ **检索可解释（Explainable Retrieval）**：返回 top-k 命中片段及相似度分数（调参依据）
* ✅ **离线评测（Eval）**：输出 `hit_rate@k`、`citation_rate`、`contains_rate`，并保存评测结果文件
* ✅ **推理层可插拔（Provider Pattern）**：默认 llama.cpp（OpenAI 兼容），后续可替换其他推理引擎
* ✅ **工程化骨架（Production-ready Skeleton）**：FastAPI + Docker(Qdrant) + Poetry + 测试/CI

---

## 2. 架构概览

```
      +------------------+
      |  Web/Client/curl |
      +--------+---------
               |
               v
        +------+-------+             +----------------------+
        |   FastAPI    |   HTTP      |   llama.cpp server   |
        | /chat /ingest+-----------> | OpenAI-compatible API|
        +------+-------+             | /v1/chat/completions |
               |
        retrieve v
        +------+-------+
        |    Qdrant    |
        | Vector Search|
        +--------------+
```

* **Qdrant**：向量检索（top-k）
* **FastAPI**：RAG 编排（检索→拼 prompt→调用 LLM→返回引用）
* **llama.cpp**：离线推理（Win10 资源友好，demo 稳）

---

## 3. 项目目录结构

```
coderag-lab/
  README.md
  Makefile
  pyproject.toml
  .env.example
  docker-compose.yml

  data/
    eval/
      coderag_eval_v1.json
    runs/                # 评测输出（自动生成）
    qdrant_storage/      # qdrant 数据卷（自动生成）

  src/
    coderag/
      settings.py

      api/
        main.py
        schemas.py

      ingest/
        repo_loader.py
        chunker.py

      rag/
        qdrant_store.py
        retriever.py
        prompt.py

      llm/
        provider.py
        llamacpp_openai.py

      eval/
        runner.py

      cli.py
```

---

## 4. 配置（.env）

> ✅ 建议只保留 **一套命名**，避免后期混乱。
> 本项目推荐使用"OpenAI 兼容服务"的配置方式：`LLM_BASE_URL` + `LLM_MODEL`。

复制 `.env.example` 为 `.env`，并按需修改：

```env
# ---- LLM Provider ----
LLM_PROVIDER=llamacpp_openai
LLM_BASE_URL=http://127.0.0.1:8080/v1
LLM_API_KEY=none
LLM_MODEL=local-gguf

# ---- Vector DB ----
VECTOR_STORE=faiss  # faiss 或 qdrant
QDRANT_URL=http://127.0.0.1:6333
QDRANT_COLLECTION=coderag_chunks

# ---- FAISS Config ----
FAISS_INDEX_PATH=data/faiss_index
FAISS_METADATA_PATH=data/faiss_metadata.pkl

# ---- Embedding / Chunking ----
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=900
CHUNK_OVERLAP=120

# ---- Retrieval ----
TOP_K=6

# ---- Server ----
APP_HOST=127.0.0.1
APP_PORT=8000
```

### 4.1 Week 2 新增配置

- `VECTOR_STORE`：向量存储选择，支持 `faiss`（本地）或 `qdrant`
- `FAISS_INDEX_PATH`：FAISS 索引文件路径
- `FAISS_METADATA_PATH`：FAISS 元数据文件路径

> ⚠️ 如果你改 embedding 模型，向量维度可能变化，需要同步调整 Qdrant collection 的向量维度（初期建议先别换 embedding）。

---

## 5. API 接口说明

### 5.1 `GET /health`

返回：

```json
{ "status": "ok" }
```

### 5.2 `POST /ingest/repo`

请求：

```json
{
  "repo_path": "D:\\path\\to\\repo",
  "glob": "**/*"
}
```

响应：

```json
{
  "files": 123,
  "chunks": 456,
  "collection": "coderag_chunks"
}
```

### 5.3 `POST /chat`

请求：

```json
{
  "messages": [{"role":"user","content":"Where is the FastAPI app created?"}],
  "top_k": 6,
  "include_hits": true
}
```

响应（简化示例）：

```json
{
  "answer": "The FastAPI app is created in ... [SOURCE 1]",
  "citations": [
    { "score": 0.78, "source": "src/coderag/api/main.py", "chunk_id": "xxx", "text": "..." }
  ],
  "debug": { "top_k": 6 }
}
```

### 5.4 `POST /ask` (Week 2 新增)

**功能**：返回检索到的 top-k 片段（不进行 LLM 生成）

请求：

```json
{
  "query": "Where is the FastAPI app created?",
  "top_k": 5
}
```

响应：

```json
{
  "query": "Where is the FastAPI app created?",
  "results": [
    {
      "file_path": "src/coderag/api/main.py",
      "content": "from fastapi import FastAPI, HTTPException\nfrom fastapi.middleware.cors import CORSMiddleware",
      "score": 0.95,
      "rank": 1
    },
    {
      "file_path": "src/coderag/api/main.py",
      "content": "app = FastAPI(\n    title=settings.project_name,\n    version=\"0.1.0\",\n    description=\"可溯源代码库助手\",\n)",
      "score": 0.92,
      "rank": 2
    }
  ],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 6. 入库（Ingest Repo）

```bash
poetry run python -m coderag.cli ingest-repo --repo "D:\path\to\repo"
```

默认只读取常见文本文件（py/md/java/ts/json/yaml 等）。可在：

* `src/coderag/ingest/repo_loader.py` 修改允许的后缀集合。

---

## 7. 评测（Eval）

> **评测是"玩具 vs 生产"的分水岭**：你最终要能回答——"效果好不好？改动后变好了还是变差了？"

### 7.1 评测数据格式

文件：`data/eval/coderag_eval_v1.json`

```json
{
  "dataset_name": "coderag_eval_v1",
  "repo_name": "your_repo_name",
  "items": [
    {
      "id": "q1",
      "question": "Where is the FastAPI app created and how is it started?",
      "gold": {
        "must_cite_sources": ["src/coderag/api/main.py"],
        "answer_must_contain": ["FastAPI", "uvicorn"]
      },
      "tags": ["architecture", "api"]
    }
  ]
}
```

字段说明：

* `must_cite_sources`：期望检索命中的"黄金来源路径"（用于命中率）
* `answer_must_contain`：回答必须包含的关键词（规则评测）
* `tags`：便于分组统计（后续可做 per-tag 指标）

### 7.2 运行评测

```bash
poetry run python -m coderag.cli eval --dataset "data/eval/coderag_eval_v1.json"
```

输出：

* 控制台 summary
* 写入：`data/runs/<dataset>_<timestamp>.json`

核心指标：

* `hit_rate@k`：top-k 是否包含 gold source（检索能力）
* `citation_rate`：回答是否包含 `[SOURCE n]`（引用约束是否生效）
* `contains_rate`：是否覆盖关键词（粗略正确性）

---

## 8. Makefile（可选）

> Win10 没有 make 的话可忽略，直接手动执行命令即可。

常用：

* `make qdrant-up`
* `make run`
* `make ingest REPO=...`
* `make eval DATA=...`
* `make test`

---

## 9. 工程化亮点（写简历时怎么量化）

你可以把这些写成"可验证成果"：

* **可溯源回答**：回答引用 `[SOURCE n]`，并返回引用片段与来源路径
* **离线评测**：自建评测集 N 条；`hit_rate@k` / `citation_rate` 等指标可复现
* **回归能力**：每次改 chunking / prompt / 检索参数都能对比指标（建议 Week 6 起做）
* **一键启动**：Docker 启动 Qdrant；API 一条命令启动；llama.cpp 服务对接
* **测试与 CI**：pytest + GitHub Actions（确保改动不破坏关键路径）

---

## 10. 常见问题（Win10）

### Q1：Qdrant 启动失败

* 确认 Docker Desktop 正在运行
* 检查端口 `6333` 是否被占用
* 查看容器日志：

```bash
docker compose logs -f
```

### Q2：llama-server 启动失败

* 检查模型路径是否正确（必须是 GGUF）
* 检查端口 `8080` 是否占用
* 建议先用 `gemma-3-1b` 跑通，再换大模型

### Q3：FastAPI 启动失败

* 先确认依赖安装完成：`poetry install`
* `.env` 是否存在且字段正确
* 端口 `8000` 是否占用

### Q4：embedding 维度不匹配

* 初期建议先用 `all-MiniLM-L6-v2`（维度常见为 384）
* 换 embedding 后，需要同步调整 Qdrant collection 的向量维度，并重建 collection

---

## 11. Roadmap（后续迭代建议：做法 + 验收标准）

1. **引用升级到行号**

   * 做法：chunk 时记录 `start_line/end_line`，payload 带上行号
   * 验收：citations 里能显示 `path:line_start-line_end`

2. **检索增强：rerank 或混合检索（BM25+向量）**

   * 验收：评测集 `hit_rate@k` 或正确率有可量化提升（例如 +5%）

3. **前端 Demo（Streamlit/React）**

   * 验收：左侧对话、右侧引用与 top-k 命中可视化

4. **反馈闭环**

   * 做法：记录用户对回答的"有用/没用"，作为下一轮优化依据
   * 验收：能导出反馈数据并做简单统计

5. **更严格评测**

   * 做法：加入"引用必须来自检索片段白名单"的校验
   * 验收：`伪引用率` 可统计并下降

---

## 12. License

MIT

```

---

### 你现在的 README 里我建议你立刻改的 3 个点（最关键）
1) **统一命令**：你的 `ingest` 改成 `ingest-repo`（避免用户照 README 跑不起来）。  
2) **统一 env 命名**：保留 `LLM_BASE_URL/LLM_MODEL/QDRANT_URL/...` 这一套即可；你那套 `LLAMACPP_HOST/PORT/MODEL_PATH` 会和 OpenAI 兼容调用方式冲突、也更难维护。  
3) **Quickstart 前置**：招聘/面试的人只看 30 秒，Quickstart 放最上面提升转化率。

如果你把你仓库的 **实际 CLI 命令/文件名**（比如 `coderag.cli ingest` 还是 `ingest-repo`）确认一下，我还能再做一次"完全对齐代码实现"的最终版，保证 README 命令 100% 可跑。
```