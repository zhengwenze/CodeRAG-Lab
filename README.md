# CodeRAG Lab — 可溯源代码库智能助手

一个基于 RAG 技术的专业级代码库问答系统，支持**精准检索、可验证引用、系统化评测和企业级部署**。

## 核心价值
- **可溯源 RAG**：回答附带来源引用，支持代码片段定位和行号级精度
- **完整评测体系**：内置基准评测和回归测试，确保系统性能稳定
- **工程化服务**：FastAPI 接口、Docker 部署、GitHub Actions CI/CD
- **现代化前端**：Next.js 15+ 界面，支持代码库管理、RAG 问答、评测和微调
- **本地 LLM 支持**：集成 llama.cpp，支持私有部署和离线运行

## Quickstart（快速跑通）

### 0) 前置依赖
- Python 3.10+
- Poetry
- Docker Desktop（用于 Qdrant）
- llama.cpp 的 `llama-server.exe`（OpenAI Compatible API）
- Node.js 18+（用于前端）
- npm 或 yarn（用于前端依赖管理）
- （可选）Git Bash（方便运行 make；没有 make 也可手动执行命令）

### 1) 启动 Qdrant
```bash
docker compose up -d
```

### 2) 启动 llama.cpp（OpenAI 兼容）

**macOS/Linux:**

```bash
llama-server -hf ggml-org/gemma-3-1b-it-GGUF --port 8080
```

**Windows:**

```cmd
llama-server -m D:\models\your-model-q4_k_m.gguf --port 8080
```

> 💡 **建议**：先用小模型跑通链路，后续可换成本地 GGUF 模型

验证：

```bash
curl http://127.0.0.1:8080/v1/models
```

### 3) 安装后端依赖 + 启动 API

```bash
copy .env.example .env
poetry install
poetry run uvicorn coderag.api.main:app --host 127.0.0.1 --port 8000 --reload
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

### 4) 安装前端依赖 + 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端访问地址：http://localhost:9000

### 5) 入库一个 repo

**方法一：使用前端界面**
- 访问 http://localhost:9000/dashboard
- 填写代码库名称
- 选择代码库文件
- 点击"入库"按钮

**方法二：使用命令行**

```bash
poetry run python -m coderag.cli ingest-repo --repo "D:\path\to\repo"
```

### 6) 开始使用

访问 http://localhost:9000/chat，选择代码库并开始提问。

---

## 1. 你将得到什么（功能与卖点）

* ✅ **可溯源问答（Citations）**：回答必须引用检索到的代码/文档片段（文件路径 + 行号）
* ✅ **检索可解释（Explainable Retrieval）**：返回 top-k 命中片段及相似度分数（调参依据）
* ✅ **离线评测（Eval）**：输出 `hit_rate@k`、`citation_rate`、`contains_rate`，并保存评测结果文件
* ✅ **回归测试框架**：自动对比历史评测结果，检测性能回退
* ✅ **推理层可插拔（Provider Pattern）**：默认 llama.cpp（OpenAI 兼容），后续可替换其他推理引擎
* ✅ **工程化骨架（Production-ready Skeleton）**：FastAPI + Docker(Qdrant) + Poetry + 测试/CI
* ✅ **现代化前端界面**：Next.js 15+、TypeScript、Tailwind CSS、响应式设计
* ✅ **完整的用户交互**：代码库管理、聊天界面、评测结果、模型微调
* ✅ **LoRA 微调支持**：集成 LoRA/QLoRA 微调，支持基础模型与微调模型对比评测

---

## 2. 架构概览

```
      +------------------+
      |    前端界面      |
      |  http://localhost:9000 |
      +--------+--------+
               |
               v
        +------+-------+             +----------------------+
        |   FastAPI    |   HTTP      |   llama.cpp server   |
        | /chat /ingest+-----------> | OpenAI-compatible API|
        +------+-------+             | /v1/chat/completions |
               |
        retrieve v
        +------+-------+
        | 向量存储      |
        | Qdrant/FAISS |
        +--------------+
```

* **前端**：Next.js 15+、TypeScript、Tailwind CSS，提供直观的用户界面
* **FastAPI**：RAG 编排（检索→拼 prompt→调用 LLM→返回引用）
* **向量存储**：支持 Qdrant（分布式）和 FAISS（本地）
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

  frontend/              # 前端项目
    src/
      app/              # Next.js App Router
        dashboard/       # 代码库管理页
        chat/            # RAG 问答页
        eval/            # 评测结果页
        train/           # 模型微调页
      components/        # UI 组件
      lib/              # 工具函数和 API 封装
      types/            # TypeScript 类型定义
      store/            # Zustand 状态管理

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
        faiss_store.py
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
# 基础配置
PROJECT_NAME=CodeRAG Lab
ENVIRONMENT=development
DEBUG=True

# API配置
API_HOST=0.0.0.0
API_PORT=8000

# 向量库配置
VECTOR_STORE=qdrant  # faiss 或 qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=coderag

# FAISS 配置
FAISS_INDEX_PATH=data/faiss_index
FAISS_METADATA_PATH=data/faiss_metadata.pkl

# 嵌入模型配置
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIM=384

# LLM配置
LLM_PROVIDER=llamacpp

# llama.cpp配置
LLAMACPP_HOST=localhost
LLAMACPP_PORT=8080
LLAMACPP_MODEL_PATH=./models/model.gguf

# 检索配置
TOP_K=5
TOP_P=0.95
TEMPERATURE=0.7

# 分块配置
CHUNK_SIZE=1000
CHUNK_OVERLAP=100

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/coderag.log

# 评测配置
EVAL_DATASET_PATH=data/eval/coderag_eval_v1.json
EVAL_OUTPUT_PATH=data/runs/

# 数据目录
DATA_DIR=data
```

> ⚠️ 如果你改 embedding 模型，向量维度可能变化，需要同步调整 Qdrant collection 的向量维度（初期建议先别换 embedding）。

---

## 5. 前端使用指南

### 5.1 代码库管理（/dashboard）

- **上传代码库**：填写代码库名称，选择代码库文件，点击"入库"按钮
- **查看代码库列表**：显示已入库的代码库，包括文件数量和创建时间
- **任务状态**：实时显示上传和处理状态

### 5.2 RAG 问答（/chat）

- **选择代码库**：从下拉菜单中选择要查询的代码库
- **输入问题**：在输入框中输入你的问题
- **查看回答**：AI 会生成带有引用的回答
- **查看引用**：点击引用卡片查看完整代码片段

### 5.3 评测结果（/eval）

- **运行评测**：输入测试集路径，点击"运行评测"按钮
- **查看评测历史**：显示历史评测结果，包括精确率、召回率、F1分数

### 5.4 模型微调（/train）

- **配置微调参数**：选择基础模型、设置 LoRA Rank 和训练轮数
- **开始训练**：点击"开始训练"按钮启动训练任务
- **查看训练状态**：实时显示训练进度、Loss 值和当前轮数

---

## 6. API 接口说明

### 6.1 `GET /health`

返回：

```json
{ "status": "ok" }
```

### 6.2 `POST /ingest/repo`

请求：

```json
{
  "repo_path": "D:\path\to\repo",
  "glob": "**/*"
}
```

响应：

```json
{
  "files": 123,
  "chunks": 456,
  "collection": "coderag"
}
```

### 6.3 `POST /chat`

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

### 6.4 `POST /ask`

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

### 6.5 前端 API 接口

前端通过以下接口与后端通信：

- `GET /api/repos`：获取代码库列表
- `POST /api/repos/upload`：上传代码库文件
- `POST /api/repos/process`：处理代码库
- `POST /api/query`：RAG 问答查询
- `POST /api/eval/run`：运行评测
- `GET /api/eval/results`：获取评测结果
- `POST /api/train/start`：开始模型微调
- `GET /api/train/status`：获取训练状态

---

## 7. 入库（Ingest Repo）

### 7.1 使用前端界面
- 访问 http://localhost:9000/dashboard
- 填写代码库名称
- 选择代码库文件
- 点击"入库"按钮

### 7.2 使用命令行

```bash
poetry run python -m coderag.cli ingest-repo --repo "D:\path\to\repo"
```

默认只读取常见文本文件（py/md/java/ts/json/yaml 等）。可在：

* `src/coderag/ingest/repo_loader.py` 修改允许的后缀集合。

---

## 8. 评测（Eval）

> **评测是"玩具 vs 生产"的分水岭**：你最终要能回答——"效果好不好？改动后变好了还是变差了？"

### 8.1 评测数据格式

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

### 8.2 运行评测

**方法一：使用前端界面**
- 访问 http://localhost:9000/eval
- 填写测试集路径
- 点击"运行评测"按钮

**方法二：使用命令行**

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

## 9. 模型微调（Training）

### 9.1 使用前端界面
- 访问 http://localhost:9000/train
- 选择基础模型
- 设置 LoRA Rank 和训练轮数
- 点击"开始训练"按钮
- 查看训练状态和进度

### 9.2 配置说明

- **Base Model**：选择要微调的基础模型
- **LoRA Rank**：LoRA 微调的秩，一般为 8-64
- **Epochs**：训练轮数，一般为 3-10

---

## 10. Makefile（可选）

> Win10 没有 make 的话可忽略，直接手动执行命令即可。

常用：

* `make qdrant-up`：启动 Qdrant
* `make run`：启动后端服务
* `make ingest REPO=...`：入库代码库
* `make eval DATA=...`：运行评测
* `make test`：运行测试

---

## 11. 工程化亮点（写简历时怎么量化）

你可以把这些写成"可验证成果"：

* **可溯源回答**：回答引用 `[SOURCE n]`，并返回引用片段与来源路径
* **离线评测**：自建评测集 N 条；`hit_rate@k` / `citation_rate` 等指标可复现
* **回归能力**：每次改 chunking / prompt / 检索参数都能对比指标
* **一键启动**：Docker 启动 Qdrant；API 一条命令启动；llama.cpp 服务对接
* **测试与 CI**：pytest + GitHub Actions（确保改动不破坏关键路径）
* **现代化前端**：使用 Next.js 15+、TypeScript、Tailwind CSS 构建完整界面
* **全栈开发**：后端 FastAPI + 前端 Next.js，完整的前后端对接

---

## 12. 常见问题（Win10）

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

### Q4：前端启动失败

* 确认 Node.js 版本 >= 18
* 确认前端依赖已安装：`npm install`
* 检查端口 `9000` 是否占用

### Q5：embedding 维度不匹配

* 初期建议先用 `all-MiniLM-L6-v2` 或 `BAAI/bge-small-en-v1.5`（维度为 384）
* 换 embedding 后，需要同步调整 Qdrant collection 的向量维度，并重建 collection

### Q6：代码库入库失败

* 检查代码库路径是否正确
* 检查代码库文件是否过大
* 检查文件权限是否正常

---

## 13. Roadmap（后续迭代建议：做法 + 验收标准）

1. **引用升级到行号**

   * 做法：chunk 时记录 `start_line/end_line`，payload 带上行号
   * 验收：citations 里能显示 `path:line_start-line_end`

2. **检索增强：rerank 或混合检索（BM25+向量）**

   * 验收：评测集 `hit_rate@k` 或正确率有可量化提升（例如 +5%）

3. **前端功能增强**

   * 做法：添加更多交互功能，如代码库管理、模型管理等
   * 验收：前端界面功能完整，用户体验良好

4. **反馈闭环**

   * 做法：记录用户对回答的"有用/没用"，作为下一轮优化依据
   * 验收：能导出反馈数据并做简单统计

5. **更严格评测**

   * 做法：加入"引用必须来自检索片段白名单"的校验
   * 验收：`伪引用率` 可统计并下降

升级小建议：
LLM框架: 可考虑 LangChain （虽然这个项目没用，但业界常用）
---

## 14. License

MIT

```

```
