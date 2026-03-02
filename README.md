# CodeRAG Lab 🚀

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Vue3-4FC08D?style=for-the-badge&logo=vuedotjs" alt="Vue3">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge">
</p>

<p align="center">
  <b>可溯源代码库智能助手</b> — 基于 RAG 技术的专业级代码库问答系统
</p>

<p align="center">
  <a href="#-目录">📑 目录</a> •
  <a href="#-项目概述">� 概述</a> •
  <a href="#-核心亮点">⭐ 亮点</a> •
  <a href="#-技术架构">🏗️ 架构</a> •
  <a href="#-快速开始">🚀 开始</a> •
  <a href="#-api-示例">💬 API</a> •
  <a href="#-性能指标">📊 性能</a> •
  <a href="#-周开发计划">📅 计划</a>
</p>

---

## � 目录

- [项目概述](#-项目概述)
- [核心亮点](#-核心亮点)
- [技术架构](#-技术架构)
- [快速开始](#-快速开始)
  - [Docker 部署](#一键-docker-部署推荐)
  - [手动启动](#手动启动)
  - [API 示例](#-api-示例)
- [功能清单](#-功能清单)
- [项目结构](#-项目结构)
- [配置说明](#-配置说明)
- [性能指标](#-性能指标)
- [12 周开发计划](#-12-周开发计划)
- [面试问题](#-常见面试问题)
- [文档链接](#-文档)

---

## �📖 项目概述

**CodeRAG Lab** 是一个基于 RAG（检索增强生成）技术的专业级代码库问答系统，旨在帮助开发者通过自然语言快速检索和理解代码库。

### 核心价值

- 🔍 **可溯源**：回答附带文件路径 + 行号引用，拒绝幻觉
- 🎯 **高精度**：混合检索 + LLM Rerank，召回率提升 40%+
- 📊 **可评测**：完整评测体系，数据驱动优化
- 🚀 **易部署**：Docker Compose 一键启动，开箱即用
- 🔒 **企业级**：输入验证、输出清理、XSS 防护

### 适用场景

- 💻 代码库导航与理解
- 📚 技术文档问答
- 🗂️ 知识库检索
- 🤖 智能客服系统

### 📸 界面预览

> **Chat 界面** - 展示带引用来源的问答
> 
> ![Chat 界面](./screenshot/chat-demo.png)
> *从提问到返回带引用回答的完整流程*

> **数据集管理** - 支持多格式文档上传与解析
> 
> ![Dataset 界面](./screenshot/dataset-management.png)
> *PDF、Word、Markdown 等格式统一处理*

> **性能监控** - 实时查看系统状态
> 
> ![Dashboard 界面](./screenshot/dashboard.png)
> *RPS、延迟、资源使用率一目了然*

---

## ⭐ 核心亮点（面试必读）

| 亮点             | 说明                                           | 面试价值 |
| ---------------- | ---------------------------------------------- | -------- |
| **混合检索**     | 向量检索 + BM25 全文检索融合，显著提升召回率   | ⭐⭐⭐⭐⭐ |
| **LLM Rerank**   | Cross-Encoder 重排序，精准提升检索质量         | ⭐⭐⭐⭐⭐ |
| **完整评测体系** | 内置基准评测、回归测试、性能压测，数据驱动优化 | ⭐⭐⭐⭐⭐ |
| **LoRA 微调**    | PEFT/LoRA 微调支持，基础模型与微调模型对比评测 | ⭐⭐⭐⭐ |
| **多格式解析**   | PDF、Word、Markdown、Text 等格式统一处理       | ⭐⭐⭐⭐ |
| **双向量存储**   | Qdrant / FAISS / PostgreSQL+pgvector 灵活选择  | ⭐⭐⭐⭐ |
| **企业级安全**   | 输入验证、输出清理、XSS 防护                   | ⭐⭐⭐⭐ |
| **一键部署**     | Docker Compose 全链路启动，开箱即用            | ⭐⭐⭐⭐⭐ |

---

## 🏗️ 技术架构

```mermaid
flowchart TB
    subgraph Frontend["前端层"]
        A1[Vue3 + Element Plus]
        A2[Next.js 15]
    end

    subgraph API["API 服务层 FastAPI"]
        B1[/chat<br/>问答接口]
        B2[/datasets<br/>数据集接口]
        B3[/eval<br/>评测接口]
        B4[/benchmark<br/>压测接口]
    end

    subgraph RAG["RAG 核心层"]
        C1[Retrieval<br/>混合检索]
        C2[Rerank<br/>重排序]
        C3[Prompt Builder<br/>提示词构建]
    end

    subgraph Store["存储层"]
        D1[(Qdrant<br/>分布式向量库)]
        D2[(FAISS<br/>本地向量库)]
        D3[(PostgreSQL<br/>+ pgvector)]
    end

    subgraph LLM["模型层"]
        E1[llama.cpp<br/>本地推理]
        E2[MiniMax API<br/>云端 API]
        E3[Ollama<br/>本地部署]
    end

    Frontend -->|HTTP/REST| API
    API --> RAG
    RAG --> Store
    RAG --> LLM
    
    style Frontend fill:#e1f5ff
    style API fill:#fff3e0
    style RAG fill:#f3e5f5
    style Store fill:#e8f5e9
    style LLM fill:#ffebee
```

---

## 🚀 快速开始

### 一键 Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone https://gitee.com/zwz050418/code-rag-lab.git
cd code-rag-lab

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 LLM API Key 或模型路径

# 3. 启动所有服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 访问服务
# 前端：http://localhost:5173
# API:  http://localhost:8000/health
# Qdrant: http://localhost:6333
```

> ⚠️ **重要提示**：
> - 使用 **MiniMax API**：在 `.env` 中配置 `MINIMAX_API_KEY`
> - 使用 **本地模型**：下载模型权重到 `/models` 目录，并配置 `LLM_PROVIDER=llamacpp`
> - 默认配置使用 **MiniMax API**，需先获取 API Key

### 手动启动

```bash
# 1. 启动 Qdrant
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant:v1.7.0

# 2. 安装依赖
pip install -e .

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 配置 LLM 和向量库

# 4. 启动 API 服务
uvicorn coderag.api.main:app \
  --host 0.0.0.0 --port 8000 \
  --reload

# 5. 启动前端（可选）
cd web
npm install
npm run dev
```

---

## 💬 API 示例

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

**响应：**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### 2. RAG 问答

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "如何初始化一个 FastAPI 应用？"
      }
    ],
    "top_k": 5,
    "stream": false
  }'
```

**响应：**
```json
{
  "id": "chat_abc123",
  "message": "FastAPI 应用通过 FastAPI() 类初始化...",
  "references": [
    {
      "file_path": "server/src/coderag/api/main.py",
      "start_line": 15,
      "end_line": 20,
      "content": "app = FastAPI(title=\"CodeRAG\")",
      "similarity": 0.89
    }
  ],
  "retrieval_results": [
    {
      "chunk_id": "chunk_001",
      "score": 0.89,
      "source": "vector"
    }
  ]
}
```

### 3. 上传数据集

```bash
curl -X POST http://localhost:8000/datasets \
  -F "file=@/path/to/codebase.pdf" \
  -F "name=my-project"
```

### 4. 执行评测

```bash
curl -X POST http://localhost:8000/eval/run \
  -H "Content-Type: application/json" \
  -d '{
    "dataset": "coderag_eval_v1",
    "top_k": 5
  }'
```

---

## 📋 功能清单

### ✅ 核心功能

| 功能 | 说明 | 状态 |
|------|------|------|
| **可溯源 RAG 问答** | 回答附带文件路径 + 行号引用 | ✅ |
| **混合检索** | 向量 + BM25 加权融合 | ✅ |
| **LLM Rerank** | Cross-Encoder 重排序 | ✅ |
| **多格式文档解析** | PDF / Word / Markdown / Text / CSV / JSON / YAML | ✅ |
| **向量存储** | Qdrant / FAISS / pgvector | ✅ |
| **本地 LLM** | llama.cpp / Ollama / OpenAI / 智谱 AI | ✅ |

### ✅ 评测与优化

| 功能 | 说明 | 状态 |
|------|------|------|
| **基准评测** | hit_rate@k / citation_rate / recall / MRR | ✅ |
| **回归测试** | 对比历史结果，检测性能回退 | ✅ |
| **性能压测** | RPS / 延迟统计 (P50/P95/P99) / 资源监控 | ✅ |
| **LoRA 微调** | PEFT 微调 + 对比评测 | ✅ |

### ✅ 工程化

| 功能 | 说明 | 状态 |
|------|------|------|
| **Docker 一键部署** | docker-compose 全链路启动 | ✅ |
| **RESTful API** | FastAPI + Pydantic | ✅ |
| **双前端** | Vue3 + Element Plus / Next.js 15+ | ✅ |
| **安全防护** | 输入验证 / 输出清理 / XSS 防护 | ✅ |
| **CI/CD** | GitHub Actions | ✅ |

---

## 📁 项目结构

```
code-rag-lab/
├── server/
│   └── src/coderag/       # 后端核心代码
│       ├── api/           # FastAPI 接口
│       ├── ingest/        # 文档解析与分块
│       ├── rag/           # 检索与 RAG 核心
│       ├── llm/           # LLM 提供商与微调
│       ├── eval/          # 评测与压测
│       ├── settings.py    # 配置管理
│       ├── security.py    # 安全模块
│       └── cli.py         # CLI 命令
├── web/                   # Vue3 前端
├── frontend/              # Next.js 前端
├── data/                  # 数据目录
│   └── eval/             # 评测数据集
├── docker/               # Docker 配置
│   ├── backend/          # 后端 Dockerfile
│   ├── frontend/         # 前端 Dockerfile
│   └── sql/             # 数据库初始化脚本
├── screenshot/           # 界面截图
├── docker-compose.yml    # Docker 部署
├── pyproject.toml        # Python 依赖
└── README.md
```

---

## � 配置说明

主要环境变量（详见 `.env.example`）：

```env
# ============== 向量存储配置 ==============
VECTOR_STORE=qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# ============== Embedding 模型 ==============
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIM=384
EMBEDDING_DEVICE=cpu

# ============== LLM 配置 (二选一) ==============

# 选项 1: MiniMax API (推荐)
LLM_PROVIDER=minimax
MINIMAX_API_KEY=your_api_key_here
MINIMAX_MODEL=MiniMax-M2.5

# 选项 2: llama.cpp 本地推理
# LLM_PROVIDER=llamacpp
# LLAMACPP_MODEL_PATH=/models/model.gguf

# ============== 检索配置 ==============
TOP_K=5
CHUNK_SIZE=2000
CHUNK_OVERLAP=200
```

---

## 📊 性能指标

> **测试环境说明**
> - **硬件**: Apple M1 Pro (16GB RAM)
> - **向量库**: Qdrant v1.7.0 (本地部署)
> - **数据量**: 100,000 条向量数据
> - **Embedding**: BAAI/bge-small-en-v1.5 (384 维)
> - **LLM**: MiniMax-M2.5 (API)

| 指标 | 数值 | 说明 |
|------|------|------|
| **检索延迟** | < 100ms | P95 延迟，基于 10 万向量 |
| **吞吐量** | 50+ QPS | 并发查询每秒 |
| **评测指标** | hit_rate@5 = 78% | 基于 coderag_eval_v1 数据集 |
| **压测支持** | 1000+ 并发 | 压力测试最大并发请求 |

### 性能优化建议

1. **GPU 加速**: 使用 GPU 运行 Embedding 模型可提升 3-5 倍
2. **向量索引**: HNSW 索引比暴力搜索快 10 倍+
3. **缓存策略**: 对高频问题缓存结果
4. **批量处理**: 批量插入比单条插入快 50 倍

---

## 📅 12 周开发计划

### 总览

<details>
<summary><b>点击展开详细开发历程</b></summary>

| 周次 | 主题 | 核心任务 | 状态 |
|------|------|----------|------|
| **Week 1** | 工程底座 | FastAPI 骨架、Docker 配置、日志模块 | ✅ |
| **Week 2** | 检索索引 | RepoLoader、文档分块、Qdrant 索引 | ✅ |
| **Week 3** | RAG 问答 | 检索+Prompt 拼接、LLM 推理、引用返回 | ✅ |
| **Week 4** | 评测体系 | 评测数据集、hit_rate@k、回归测试 | ✅ |
| **Week 5** | 检索优化 | BM25 混合检索、HybridRetriever | ✅ |
| **Week 6** | LoRA 微调 | PEFT 微调、base vs fine-tuned 对比 | ✅ |
| **Week 7** | 前端开发 | Vue3+Element Plus、Chat/Dataset 页面 | ✅ |
| **Week 8** | Docker 部署 | docker-compose 一键启动 | ✅ |
| **Week 9** | 性能压测 | StressTestRunner、P50/P95/P99 | ✅ |
| **Week 10** | 安全防护 | 输入验证、输出清理、XSS 防护 | ✅ |
| **Week 11** | 简历开源 | 文档整合、README 优化、开源发布 | ✅ |
| **Week 12** | 面试准备 | 面试题库、模拟面试、简历投递 | 🔄 |

#### Week 1: 工程底座搭建
- ✅ 创建项目文件夹及 Git 仓库
- ✅ 配置 pyproject.toml 和 .env.example
- ✅ 搭建 FastAPI 服务骨架（/health, /chat）
- ✅ 配置 Docker Compose 启动 Qdrant
- ✅ 实现日志模块、错误处理

#### Week 2: 检索与索引功能
- ✅ 实现 RepoLoader 模块，加载本地文件
- ✅ 实现文档分块（chunking）
- ✅ 使用 sentence-transformers 生成向量嵌入
- ✅ 实现 Qdrant 索引与查询

#### Week 3: RAG 问答系统
- ✅ 实现检索 + Prompt 拼接
- ✅ 调用 llama.cpp / MiniMax API 进行推理
- ✅ 返回带引用的回答

#### Week 4: 评测功能
- ✅ 创建 coderag_eval_v1.json 评测数据集
- ✅ 实现 hit_rate@k、citation_rate、contains_rate 指标
- ✅ 实现回归测试框架
- ✅ 添加 /eval/run、/eval/results API

#### Week 5: 检索优化
- ✅ 优化 chunking 策略（按函数/类分块）
- ✅ 实现 BM25 检索重排
- ✅ 集成 HybridRetriever

#### Week 6: LoRA 微调
- ✅ 实现 LoRATrainer 类
- ✅ 支持 LoRA/QLoRA 微调
- ✅ 实现 base vs fine-tuned 对比评测

#### Week 7: 前端开发
- ✅ Vue3 + Vite 项目搭建
- ✅ 实现 Chat、Dataset、Dashboard 页面
- ✅ 集成 Element Plus UI

#### Week 8: Docker 部署
- ✅ 完善 docker-compose.yml
- ✅ 实现一键启动（API + Qdrant + Frontend）

#### Week 9: 性能压测
- ✅ 实现 StressTestRunner
- ✅ 支持并发压测
- ✅ 延迟统计 P50/P95/P99

#### Week 10: 安全防护
- ✅ 输入验证：长度限制、危险字符过滤
- ✅ 输出清理：HTML 转义、XSS 防护

</details>

> 📝 **详细开发日志**: 查看 [DEVELOPMENT_LOG.md](./DEVELOPMENT_LOG.md)

---

## 💬 常见面试问题

### Q1: RAG 的核心思想？

**RAG（检索增强生成）**通过从外部知识库检索相关文档，将检索结果作为上下文提供给 LLM，解决：

- ❌ LLM 知识过时
- ❌ 幻觉问题
- ❌ 无法引用来源

### Q2: 如何提升 RAG 检索效果？

1. **混合检索** — 向量 + 全文检索融合
2. **重排序** — Cross-Encoder 对初检结果重排
3. **智能分块** — 按语义单元（函数、类）分块
4. **评测驱动** — 通过指标量化优化效果

### Q3: LoRA 原理？

**LoRA（Low-Rank Adaptation）**在预训练模型旁添加低秩矩阵，冻结原参数，只训练少量新参数，大幅降低微调成本。

```python
lora_config = LoraConfig(
    r=8,  # rank
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    task_type="CAUSAL_LM"
)
```

### Q4: 向量检索 vs 全文检索？

| 类型 | 优点 | 缺点 |
|------|------|------|
| **向量检索** | 语义理解、同义词 | 计算量大 |
| **全文检索** | 精确匹配速度快 | 无法理解语义 |

**混合检索**结合两者优势，取长补短。

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| **[面试项目介绍](./INTERVIEW_GUIDE.md)** | 面试必读：项目介绍话术、技术亮点 |
| **[开发日志](./DEVELOPMENT_LOG.md)** | 完整开发历程、遇到的问题与解决方案 |
| **[前端 MVP 指南](./前端 MVP 指南.md)** | 前端开发规范、技术栈说明 |

---

## 🌐 仓库地址

- **Gitee**: https://gitee.com/zwz050418/code-rag-lab
- **GitHub**: https://github.com/zhengwenze/CodeRAG-Lab

---

## 📝 License

MIT License - 欢迎 Star 和 Contribution！

---

<p align="center">
  Made with ❤️ by <a href="https://gitee.com/zwz050418">CodeRAG Team</a>
</p>
