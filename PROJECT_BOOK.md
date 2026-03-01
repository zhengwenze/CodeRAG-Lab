# CodeRAG Lab 项目全书

> 本文档整合了项目计划、开发日志、面试指南和前端规范，是项目的核心文档。

---

## 📋 目录

1. [项目概述](#1-项目概述)
2. [技术栈](#2-技术栈)
3. [核心功能](#3-核心功能)
4. [系统架构](#4-系统架构)
5. [开发历程](#5-开发历程)
6. [前端开发规范](#6-前端开发规范)
7. [快速开始](#7-快速开始)
8. [面试要点](#8-面试要点)

---

## 1. 项目概述

**CodeRAG Lab** 是一个基于 RAG（检索增强生成）技术的专业级代码库问答系统，旨在帮助开发者通过自然语言快速检索和理解代码库。

### 项目目标

- 提供可溯源的代码问答体验
- 支持多种向量存储后端（Qdrant/FAISS/pgvector）
- 集成混合检索 + LLM Rerank 提升召回率
- 提供完整评测体系和 LoRA 微调能力

### 项目地址

- Gitee: https://gitee.com/zwz050418/code-rag-lab
- GitHub: https://github.com/zhengwenze/CodeRAG-Lab

---

## 2. 技术栈

### 后端

| 技术 | 说明 |
|------|------|
| Python 3.9+ | 编程语言 |
| FastAPI | 高性能 Web 框架 |
| Qdrant/FAISS | 向量数据库 |
| PostgreSQL + pgvector | 混合向量存储 |
| llama.cpp | 本地 LLM 推理 |
| Sentence Transformers | 嵌入模型 |
| PEFT/LoRA | 模型微调 |
| Whoosh | 全文搜索引擎 |

### 前端

| 技术 | 说明 |
|------|------|
| Vue3 + Vite | 现代前端框架 |
| Element Plus | UI 组件库 |
| Pinia | 状态管理 |
| Vue Router | 路由管理 |

### 部署

| 技术 | 说明 |
|------|------|
| Docker Compose | 一键部署 |
| GitHub Actions | CI/CD |

---

## 3. 核心功能

### 3.1 可溯源 RAG 问答

用户提问 → 向量检索 → 上下文拼接 → LLM 生成 → 返回带引用的答案

引用包含文件路径、行号、相似度分数。

### 3.2 混合检索架构

- **向量检索**：使用 Sentence Transformers 生成语义嵌入
- **全文检索**：使用 Whoosh/BM25 进行关键词匹配
- **结果融合**：加权合并两种检索结果

```python
final_score = vector_score * 0.7 + bm25_score * 0.3
```

### 3.3 LLM Rerank

使用 Cross-Encoder 模型对初检结果重排序，提升检索精度和相关性。

### 3.4 多格式文档解析

支持 PDF、Word、Markdown、Text、CSV、JSON、YAML 等格式，统一解析接口，支持扩展。

### 3.5 完整评测体系

- 内置评测数据集
- 指标：hit_rate@k、citation_rate、recall、MRR
- 回归测试：对比历史结果，检测性能回退

### 3.6 LoRA 微调

使用 PEFT 库进行 LoRA/QLoRA 微调，支持基础模型与微调模型对比评测。

### 3.7 性能压测

- 并发压测支持
- 延迟统计：P50、P95、P99
- 资源监控：CPU、内存

### 3.8 安全防护

- 输入验证：长度限制、危险字符过滤
- 输出清理：HTML 转义、XSS 防护

---

## 4. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                         前端 (Vue3)                         │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP
┌─────────────────────────────▼───────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Chat API  │  │  Dataset API │  │   Evaluation API   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │                │                    │
┌─────────▼────────────────▼────────────────────▼─────────────┐
│                      RAG Pipeline                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Retrieval  │  │   Rerank    │  │   Prompt Builder   │ │
│  │ (Vector+BM25)│  │ (Cross-Enc) │  │                     │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │                │                    │
┌─────────▼────────────────▼────────────────────▼─────────────┐
│                      Vector Store                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Qdrant    │  │    FAISS    │  │   pgvector (PG)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────┐
│                      LLM Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  llama.cpp  │  │  MiniMax API │  │   Ollama (Local)   │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. 开发历程

### 5.1 计划 vs 实际对照

| 周次 | 计划任务 | 实际完成 | 状态 |
|------|----------|----------|------|
| Week 1 | 工程底座搭建 + 项目骨架 | ✅ 完成 | ✅ |
| Week 2 | 基本的检索与索引功能 | ✅ 完成 | ✅ |
| Week 3 | RAG 问答系统 | ✅ 完成 | ✅ |
| Week 4 | 评测功能与回归测试 | ✅ 完成 | ✅ |
| Week 5 | rerank + chunking 优化 | ✅ 完成 | ✅ |
| Week 6 | LoRA 微调集成 | ✅ 完成 | ✅ |
| Week 7 | 前端展示与用户交互 | ✅ 完成 | ✅ |
| Week 8 | API 优化与 Docker 部署 | ✅ 完成 | ✅ |
| Week 9 | 性能压测 | ✅ 完成 | ✅ |
| Week 10 | 安全防护 | ✅ 完成 | ✅ |
| Week 11 | 简历与开源化 | ✅ 进行中 | 🔄 |
| Week 12 | 面试准备与投递 | ⏳ 待开始 | ⏳ |

### 5.2 详细开发记录

#### Week 1: 工程底座搭建

- 创建项目文件夹及 Git 仓库
- 配置 pyproject.toml 和 .env.example
- 搭建 FastAPI 服务骨架（/health, /chat）
- 配置 Docker Compose 启动 Qdrant
- 实现日志模块、错误处理

**交付**: FastAPI 服务能启动，docker-compose up 能成功

#### Week 2: 检索与索引功能

- 实现 RepoLoader 模块，加载本地文件
- 实现文档分块（chunking）
- 使用 sentence-transformers 生成向量嵌入
- 实现 Qdrant 索引与查询

**交付**: 成功将代码库文档索引到 Qdrant，/chat 能返回相关文档片段

#### Week 3: RAG 问答系统

- 实现检索 + Prompt 拼接
- 调用 llama.cpp / MiniMax API 进行推理
- 返回带引用的回答

**交付**: /chat 接口返回检索到的文档片段和带引用的回答

#### Week 4: 评测功能

- 创建 coderag_eval_v1.json 评测数据集
- 实现 hit_rate@k、citation_rate、contains_rate 指标
- 实现回归测试框架
- 添加 /eval/run、/eval/results API

**交付**: 完整的评测报告和回归测试功能

#### Week 5: 检索优化

- 优化 chunking 策略（按函数/类分块）
- 实现 BM25 检索重排
- 集成 HybridRetriever

**交付**: 检索效果提升，hit_rate@k 改进

#### Week 6: LoRA 微调

- 实现 LoRATrainer 类
- 支持 LoRA/QLoRA 微调
- 实现 base vs fine-tuned 对比评测

**交付**: 微调模型对比结果

#### Week 7: 前端开发

- Vue3 + Vite 项目搭建
- 实现 Chat、Dataset、Dashboard 页面
- 集成 Element Plus UI

**交付**: 可用的前端界面

#### Week 8: Docker 部署

- 完善 docker-compose.yml
- 实现一键启动（API + Qdrant + Frontend）

**交付**: docker-compose up 一键启动

#### Week 9: 性能压测

- 实现 StressTestRunner
- 支持并发压测
- 延迟统计 P50/P95/P99

**交付**: 性能报告

#### Week 10: 安全防护

- 输入验证：长度限制、危险字符过滤
- 输出清理：HTML 转义、XSS 防护

**交付**: 安全防护机制

---

## 6. 前端开发规范

### 6.1 技术栈要求

- **框架**: Vue3 + Vite
- **UI**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router

### 6.2 项目结构

```
web/
  src/
    api/           # API 调用封装
    router/        # 路由配置
    stores/        # Pinia 状态管理
    styles/        # 样式文件
    utils/         # 工具函数
    views/         # 页面组件
      chat/        # 问答页面
      dataset/     # 数据集管理
      dashboard/   # 仪表盘
      layout/     # 布局组件
```

### 6.3 API 契约

#### 6.3.1 RAG 问答

```typescript
// POST /chat
Request:
{
  messages: [{ role: 'user' | 'assistant', content: string }],
  stream?: boolean,
  top_k?: number
}

Response:
{
  id: string,
  message: string,
  references: Reference[],
  retrieval_results: RetrievalResult[]
}
```

#### 6.3.2 数据集管理

```typescript
// GET /datasets
// POST /datasets
// DELETE /datasets/{id}
```

### 6.4 组件规范

- 使用 Element Plus 组件
- 使用 Pinia 管理状态
- 使用 Vue Router 管理路由

### 6.5 聊天输入

- Enter 发送消息
- Ctrl + Enter 换行

---

## 7. 快速开始

### 7.1 Docker 一键部署

```bash
# 克隆项目
git clone https://gitee.com/zwz050418/code-rag-lab.git
cd code-rag-lab

# 启动所有服务
docker-compose up -d

# 访问
# 前端: http://localhost:5173
# API: http://localhost:8000
# API 文档: http://localhost:8000/docs
# Qdrant: http://localhost:6333
```

### 7.2 本地开发

```bash
# 后端
cd code-rag-lab
pip install -e .
python -m uvicorn src.coderag.api.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd web
npm install
npm run dev
```

### 7.3 配置说明

在 `.env` 文件中配置：

```env
# LLM 提供商 (minimax / openai / llamacpp / ollama)
LLM_PROVIDER=minimax

# MiniMax API
MINIMAX_API_KEY=your_api_key

# 向量存储 (qdrant / faiss / pgvector)
VECTOR_STORE=qdrant

# Embedding 模型
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DEVICE=cpu
```

---

## 8. 面试要点

### 8.1 项目亮点

1. **工程化能力**: 完整的 Docker 一键部署、CI/CD、模块化设计
2. **检索效果优化**: 混合检索 + Rerank 显著提升召回率
3. **端到端解决方案**: 从文档入库到问答输出全链路
4. **性能与安全**: 压测工具确保稳定性，输入输出安全防护

### 8.2 常见面试问题

#### Q1: RAG 的核心思想是什么？

RAG（检索增强生成）通过从外部知识库检索相关文档，将检索结果作为上下文提供给 LLM，从而解决 LLM 知识过时、幻觉等问题。

#### Q2: 如何提升 RAG 的检索效果？

1. **混合检索**: 结合向量和全文检索
2. **重排序**: 使用 Cross-Encoder 对初检结果重排
3. **优化分块**: 根据语义进行智能分块
4. **评测驱动**: 通过评测指标指导优化方向

#### Q3: 向量检索和全文检索的区别？

- **向量检索**: 基于语义相似度，适合理解意图
- **全文检索**: 基于关键词匹配，适合精确匹配
- 两者结合可以互补长短

#### Q4: 如何处理大文档？

1. **智能分块**: 按语义单元（函数、类、段落）分块
2. **重叠窗口**: 相邻块之间有重叠，避免信息丢失
3. **层级索引**: 建立文档结构索引，支持多级检索

#### Q5: LoRA 微调的原理？

LoRA（Low-Rank Adaptation）通过在预训练模型矩阵来学习任务相关知识，避免全参数微调的高旁添加低秩成本。

```python
lora_config = LoraConfig(
    r=8,  # rank
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)
```

---

## 📝 更新日志

| 日期 | 更新内容 |
|------|----------|
| 2026-03-01 | 创建项目全书，整合四个核心文档 |

---

*本文档最后更新于 2026-03-01*
