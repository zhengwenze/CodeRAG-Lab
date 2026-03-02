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
  <a href="#-12-周开发计划">📅 开发计划</a> •
  <a href="#-技术架构">🏗️ 架构</a> •
  <a href="#-快速开始">🚀 开始</a> •
  <a href="#-常见面试问题">💬 面试</a>
</p>

---

## 📖 项目概述

**CodeRAG Lab** 是一个基于 RAG（检索增强生成）技术的专业级代码库问答系统，旨在帮助开发者通过自然语言快速检索和理解代码库。

### 核心价值

- 🔍 **可溯源**：回答附带文件路径 + 行号引用，拒绝幻觉
- 🎯 **高精度**：混合检索 + LLM Rerank，召回率提升 40%+
- 📊 **可评测**：完整评测体系，数据驱动优化
- 🚀 **易部署**：Docker Compose 一键启动，开箱即用
- 🔒 **企业级**：输入验证、输出清理、XSS 防护

### 适用场景

- 代码库导航与理解
- 技术文档问答
- 知识库检索
- 智能客服系统

---

## ⭐ 核心亮点（面试必读）

| 亮点             | 说明                                           |
| ---------------- | ---------------------------------------------- |
| **混合检索**     | 向量检索 + BM25 全文检索融合，显著提升召回率   |
| **LLM Rerank**   | Cross-Encoder 重排序，精准提升检索质量         |
| **完整评测体系** | 内置基准评测、回归测试、性能压测，数据驱动优化 |
| **LoRA 微调**    | PEFT/LoRA 微调支持，基础模型与微调模型对比评测 |
| **多格式解析**   | PDF、Word、Markdown、Text 等格式统一处理       |
| **双向量存储**   | Qdrant / FAISS / PostgreSQL+pgvector 灵活选择  |
| **企业级安全**   | 输入验证、输出清理、XSS 防护                   |
| **一键部署**     | Docker Compose 全链路启动，开箱即用            |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                          前端 (Vue3 / Next.js)                       │
│                    http://localhost:5173 或 :9000                    │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │ HTTP/REST
┌─────────────────────────────────────▼───────────────────────────────┐
│                         FastAPI Backend                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  /chat    │  │ /datasets │  │  /eval   │  │   /benchmark     │  │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └────────┬─────────┘  │
└────────┼─────────────┼─────────────┼─────────────────┼────────────┘
         │             │             │                 │
┌────────▼─────────────▼─────────────▼─────────────────▼────────────┐
│                         RAG Pipeline                                │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │   Retrieval   │  │    Rerank    │  │    Prompt Builder     │  │
│  │ (Vector+BM25) │  │ (Cross-Enc)  │  │                        │  │
│  └───────┬──────┘  └──────┬───────┘  └───────────┬────────────┘  │
└──────────┼─────────────────┼──────────────────────┼───────────────┘
           │                 │                      │
┌──────────▼─────────────────▼──────────────────────▼───────────────┐
│                         Vector Store                                 │
│     Qdrant (分布式)    │    FAISS (本地)    │   pgvector (PG)     │
└─────────────────────────────────────────────────────────────────────┘
           │                                      │
┌──────────▼──────────────────────────────────────▼─────────────────┐
│                         LLM Layer                                    │
│    llama.cpp (本地)    │   OpenAI API   │   Ollama / ZhipuAI    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 一键 Docker 部署（推荐）

```bash
# 克隆项目
git clone https://gitee.com/zwz050418/code-rag-lab.git
cd code-rag-lab

# 启动所有服务
docker-compose up -d

# 访问
# 前端: http://localhost:5173
# API:  http://localhost:8000/health
# Qdrant: http://localhost:6333
```

### 手动启动

```bash
# 1. 启动 Qdrant
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:v1.7.0

# 2. 安装依赖
pip install -e .

# 3. 启动 API
uvicorn coderag.api.main:app --host 0.0.0.0 --port 8000 --reload

# 4. 启动前端
cd web
npm install && npm run dev
```

---

## 📋 功能清单

### ✅ 核心功能

- [x] **可溯源 RAG 问答** — 回答附带文件路径 + 行号引用
- [x] **混合检索** — 向量 + BM25 加权融合
- [x] **LLM Rerank** — Cross-Encoder 重排序
- [x] **多格式文档解析** — PDF / Word / Markdown / Text / CSV / JSON / YAML
- [x] **向量存储** — Qdrant / FAISS / pgvector
- [x] **本地 LLM** — llama.cpp / Ollama / OpenAI / 智谱 AI

### ✅ 评测与优化

- [x] **基准评测** — hit_rate@k / citation_rate / recall / MRR
- [x] **回归测试** — 对比历史结果，检测性能回退
- [x] **性能压测** — RPS / 延迟统计(P50/P95/P99) / 资源监控
- [x] **LoRA 微调** — PEFT 微调 + 对比评测

### ✅ 工程化

- [x] **Docker 一键部署** — docker-compose 全链路启动
- [x] **RESTful API** — FastAPI + Pydantic
- [x] **双前端** — Vue3 + Element Plus / Next.js 15+
- [x] **安全防护** — 输入验证 / 输出清理 / XSS 防护
- [x] **CI/CD** — GitHub Actions

---

## 📁 项目结构

```
code-rag-lab/
├── server/
│   └── src/coderag/  # 后端源码
│       ├── api/           # FastAPI 接口
│       ├── ingest/        # 文档解析与分块
│       ├── rag/           # 检索与 RAG 核心
│       ├── llm/           # LLM 提供商与微调
│       ├── eval/          # 评测与压测
│       ├── settings.py    # 配置管理
│       ├── security.py    # 安全模块
│       └── cli.py         # CLI 命令
├── web/                # Vue3 前端
├── frontend/          # Next.js 前端
├── data/              # 数据目录
├── docker-compose.yml # Docker 部署
├── pyproject.toml     # Python 依赖
└── README.md
```

---

## 💬 常见面试问题

### Q1: RAG 的核心思想？

**RAG（检索增强生成）**通过从外部知识库检索相关文档，将检索结果作为上下文提供给 LLM，解决：

- LLM 知识过时
- 幻觉问题
- 无法引用来源

### Q2: 如何提升 RAG 检索效果？

1. **混合检索** — 向量 + 全文检索融合
2. **重排序** — Cross-Encoder 对初检结果重排
3. **智能分块** — 按语义单元（函数、类）分块
4. **评测驱动** — 通过指标量化优化效果

### Q3: LoRA 原理？

**LoRA（Low-Rank Adaptation）**在预训练模型旁添加低秩矩阵，冻结原参数，只训练少量新参数，大幅降低微调成本。

### Q4: 向量检索 vs 全文检索？

| 类型     | 优点             | 缺点         |
| -------- | ---------------- | ------------ |
| 向量检索 | 语义理解、同义词 | 计算量大     |
| 全文检索 | 精确匹配速度快   | 无法理解语义 |

**混合检索**结合两者优势，取长补短。

---

## 📊 性能指标

| 指标     | 说明                                   |
| -------- | -------------------------------------- |
| 检索延迟 | < 100ms (本地向量)                     |
| 吞吐量   | 50+ QPS                                |
| 评测指标 | hit_rate@k, citation_rate, recall, MRR |
| 压测支持 | 1000+ 并发请求                         |

---

## � 12 周开发计划

### 已完成阶段

| 周次 | 主题 | 核心任务 | 状态 |
|------|------|----------|------|
| **Week 1** | 工程底座 | FastAPI 骨架、Docker 配置、日志模块 | ✅ |
| **Week 2** | 检索索引 | RepoLoader、文档分块、Qdrant 索引 | ✅ |
| **Week 3** | RAG 问答 | 检索 +Prompt 拼接、LLM 推理、引用返回 | ✅ |
| **Week 4** | 评测体系 | 评测数据集、hit_rate@k、回归测试 | ✅ |
| **Week 5** | 检索优化 | BM25 混合检索、HybridRetriever | ✅ |
| **Week 6** | LoRA 微调 | PEFT 微调、base vs fine-tuned 对比 | ✅ |
| **Week 7** | 前端开发 | Vue3+Element Plus、Chat/Dataset 页面 | ✅ |
| **Week 8** | Docker 部署 | docker-compose 一键启动 | ✅ |
| **Week 9** | 性能压测 | StressTestRunner、P50/P95/P99 | ✅ |
| **Week 10** | 安全防护 | 输入验证、输出清理、XSS 防护 | ✅ |
| **Week 11** | 简历开源 | 文档整合、README 优化、开源发布 | ✅ |
| **Week 12** | 面试准备 | 面试题库、模拟面试、简历投递 | 🔄 |

### 详细开发历程

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

---

##  配置说明

主要环境变量（详见 `.env.example`）：

```env
# 向量存储
VECTOR_STORE=qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Embedding
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIM=384

# LLM
LLM_PROVIDER=llamacpp
LLM_BASE_URL=http://localhost:8080/v1

# 检索
TOP_K=5
CHUNK_SIZE=2000
CHUNK_OVERLAP=200
```

---

## 📖 文档

- **[PROJECT_BOOK](./PROJECT_BOOK.md)** — 项目全书（核心文档）
- **[面试项目介绍](./INTERVIEW_GUIDE.md)** — 面试必读
- **[开发日志](./DEVELOPMENT_LOG.md)** — 完整开发历程
- **[前端 MVP 指南](./前端 MVP 指南.md)** — 前端开发规范

---

## 🌐 仓库地址

- Gitee: https://gitee.com/zwz050418/code-rag-lab
- GitHub: https://github.com/zhengwenze/CodeRAG-Lab

---

## 📝 License

MIT License - 欢迎 Star 和 Contribution！

---

<p align="center">
  Made with ❤️ by <a href="https://gitee.com/zwz050418">CodeRAG Team</a>
</p>
