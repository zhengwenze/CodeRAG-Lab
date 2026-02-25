下面这份是**专门给 AI 编程助手（Cursor / Windsurf / ChatGPT Canvas / GitHub Copilot 等）看的“面向 2025–2026 的现代化前端 MVP 需求文档”**。  
目标：让 AI 能只看这份文档，就写出**结构、技术栈、接口调用方式完全符合当前主流实践**的前端代码，无需你额外解释技术细节。
---
## 一、技术栈选型（2025–2026 主流）
结合 2025 年前端趋势报告和 React 技术栈推荐：React 仍是主导框架，Next.js 是全栈应用首选，Tailwind 已成默认样式方案，TanStack 生态（Query、Router）在数据获取与路由方面快速崛起，TypeScript + Zod 成类型校验标准组合。
**AI 必须使用的技术栈：**
- 框架：**Next.js 15+（App Router，Server Components + Server Actions）**
- 语言：**TypeScript 严格模式**
- 样式：**Tailwind CSS**（仅布局类，不做视觉设计）
- 数据获取（服务端状态）：**TanStack Query v5（React Query）**
- 客户端状态管理：**Zustand**（轻量、2025 年仍在快速增长）
- 表单：**React Hook Form + Zod**（2025 年最主流组合）
- UI 组件：**Shadcn/ui（基于 Radix UI，复制源码进项目）**
- 图标：**Lucide React**
- 工具链（可选但推荐）：**Biome**（Rust 工具链，替代 ESLint + Prettier）
**不使用**：Redux、Axios、老版 Create React App、传统 CSS-in-JS（如 styled-components）等已被视为“偏旧”的方案。
---
## 二、项目结构与目录约定
AI 需要按以下结构创建文件（目录命名要语义化）：
```text
src/
  app/
    layout.tsx           # 根布局（侧边栏 + 全局 Provider）
    page.tsx             # 首页，重定向到 /dashboard
    dashboard/
      page.tsx           # 代码库管理页
    chat/
      page.tsx           # RAG 问答页
      components/
        ChatMessage.tsx
        ChatInput.tsx
        ReferenceCard.tsx
    eval/
      page.tsx           # 评测页
    train/
      page.tsx           # 模型微调页
  components/
    ui/                  # Shadcn/ui 组件（button, input, card, table, dialog, toast 等）
    shared/              # 通用业务组件（Sidebar, PageContainer 等）
  lib/
    api.ts               # fetch 封装，供 TanStack Query 调用
    utils.ts             # 工具函数（cn 等）
  hooks/
    useChat.ts           # 聊天相关 Hook（可选）
  types/
    index.ts             # 全局 TS 类型定义（Repo, Message, Reference, EvalResult, TrainStatus 等）
  store/
    chatStore.ts         # Zustand：聊天消息状态
```
---
## 三、API 契约（前端视角）
后端是现有 FastAPI 服务，前端通过 HTTP 调用。  
AI 需要根据这些接口定义 TypeScript 类型，并封装 fetch 函数。
假设后端基础地址：`process.env.NEXT_PUBLIC_API_URL`（默认 `http://localhost:8000`）。
### 3.1 代码库管理
- `GET /api/repos`  
  响应示例：
  ```json
  [
    {
      "id": "repo-1",
      "name": "coderag-lab",
      "files_count": 123,
      "created_at": "2025-03-01T10:00:00Z"
    }
  ]
  ```
- `POST /api/repos/upload`（上传文件/压缩包）  
  请求：`FormData`（字段名：`file`）  
  响应：
  ```json
  {
    "task_id": "task-123",
    "status": "processing"
  }
  ```
- `POST /api/repos/process`（触发分块与入库）  
  请求：
  ```json
  {
    "repo_name": "coderag-lab",
    "branch": "main"
  }
  ```
  响应：
  ```json
  {
    "message": "success",
    "chunks_count": 1024
  }
  ```
### 3.2 RAG 问答
- `POST /api/query`  
  请求：
  ```json
  {
    "question": "这个项目里如何实现 FAISS 索引？",
    "top_k": 5,
    "repo_id": "repo-1"
  }
  ```
  响应：
  ```json
  {
    "answer": "在 `src/index/faiss_index.py` 中实现了 FAISS 索引的构建和查询…",
    "references": [
      {
        "file_path": "src/index/faiss_index.py",
        "content": "def build_faiss_index(embeddings): ...",
        "start_line": 10,
        "end_line": 45,
        "score": 0.92
      }
    ]
  }
  ```
### 3.3 评测管理
- `POST /api/eval/run`  
  请求：
  ```json
  {
    "test_set_path": "datasets/eval_set_01.json"
  }
  ```
  响应：
  ```json
  {
    "task_id": "eval-task-1"
  }
  ```
- `GET /api/eval/results`  
  响应：
  ```json
  [
    {
      "id": "eval-1",
      "timestamp": "2025-03-01T12:00:00Z",
      "metrics": {
        "precision": 0.85,
        "recall": 0.80,
        "f1": 0.82
      }
    }
  ]
  ```
### 3.4 模型微调
- `POST /api/train/start`  
  请求：
  ```json
  {
    "base_model": "codellama/CodeLlama-7b-Instruct-hf",
    "lora_rank": 8,
    "epochs": 3
  }
  ```
  响应：
  ```json
  {
    "job_id": "job-1"
  }
  ```
- `GET /api/train/status`  
  响应：
  ```json
  {
    "status": "running",
    "current_epoch": 1,
    "loss": 0.25,
    "progress_percent": 33
  }
  ```
---
## 四、数据模型与 TypeScript 类型
AI 在 `src/types/index.ts` 中至少定义以下类型（可使用 Zod 做 schema，再推导出类型）：
```ts
// 代码库
export interface Repo {
  id: string;
  name: string;
  files_count: number;
  created_at: string; // ISO
}
// RAG 引用
export interface Reference {
  file_path: string;
  content: string;
  start_line: number;
  end_line: number;
  score: number;
}
// 一条聊天消息
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  references?: Reference[];
  created_at: string;
}
// 评测结果
export interface EvalResult {
  id: string;
  timestamp: string;
  metrics: {
    precision: number;
    recall: number;
    f1: number;
  };
}
// 训练状态
export interface TrainStatus {
  status: 'idle' | 'running' | 'completed' | 'failed';
  current_epoch: number;
  loss: number | null;
  progress_percent: number;
}
```
---
## 五、API 封装（src/lib/api.ts）
AI 需要使用 **原生 fetch**，封装一个统一的 `fetcher` 供 TanStack Query 使用，示例：
```ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export async function fetcher<T>(
  input: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(`${API_BASE}${input}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`API error: ${res.status} ${text}`);
  }
  return res.json() as Promise<T>;
}
```
然后为每个接口封装具体函数，例如：
```ts
export const api = {
  getRepos: () => fetcher<Repo[]>('/api/repos'),
  uploadRepo: (file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    return fetcher<{ task_id: string; status: string }>('/api/repos/upload', {
      method: 'POST',
      body: fd,
    });
  },
  queryRAG: (question: string, repoId?: string) =>
    fetcher<{ answer: string; references: Reference[] }>('/api/query', {
      method: 'POST',
      body: JSON.stringify({
        question,
        top_k: 5,
        repo_id: repoId,
      }),
    }),
  runEval: (testSetPath: string) =>
    fetcher<{ task_id: string }>('/api/eval/run', {
      method: 'POST',
      body: JSON.stringify({ test_set_path: testSetPath }),
    }),
  getEvalResults: () => fetcher<EvalResult[]>('/api/eval/results'),
  startTrain: (payload: { base_model: string; lora_rank: number; epochs: number }) =>
    fetcher<{ job_id: string }>('/api/train/start', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getTrainStatus: () => fetcher<TrainStatus>('/api/train/status'),
};
```
---
## 六、全局布局与路由
### 6.1 根布局（app/layout.tsx）
- 使用 **Next.js App Router 的 `layout.tsx`** 作为根布局。
- 布局结构：左侧侧边栏 + 右侧内容区。
- 全局 Provider：
  - `QueryClientProvider`（TanStack Query）
  - `TooltipProvider`（Shadcn/ui）
  - 自定义 `ToastProvider`（使用 Shadcn/ui 的 toast/sonner）
侧边栏导航项：
- Dashboard：`/dashboard`
- Chat：`/chat`
- Evaluation：`/eval`
- Training：`/train`
### 6.2 路由结构
- `/`：重定向到 `/dashboard`。
- `/dashboard`：代码库管理页。
- `/chat`：RAG 问答页。
- `/eval`：评测结果页。
- `/train`：模型微调页。
AI 使用 **Next.js 的文件路由约定** 实现，无需额外路由库。
---
## 七、页面一：代码库管理（/dashboard）
**目标**：展示已入库代码库列表，支持上传代码库并触发入库。
### 7.1 UI 结构
1. 顶部操作区：
   - 一个 `<input type="file">` 用于选择代码库压缩包（或单文件）。
   - 一个 `<input>` 输入 Repo 名称。
   - 一个 `<button> 入库 </button>`。
   - 显示当前任务状态（上传中、处理中、完成）。
2. 数据表格：
   - 使用 Shadcn/ui 的 `<Table>` 组件。
   - 列：Repo Name、Files Count、Created At、状态（如最近任务状态）。
   - 加载状态：使用 `<Skeleton>` 行占位。
### 7.2 数据获取与状态
- 使用 `useQuery` 获取 `api.getRepos()`，缓存 key 为 `['repos']`。
- 上传与处理：
  - 使用 `useMutation` 封装上传逻辑：
    - 先调用 `uploadRepo`；
    - 成功后调用 `processRepo`；
  - 成功后调用 `queryClient.invalidateQueries(['repos'])` 刷新列表。
### 7.3 交互细节
- 点击“入库”时：
  - 按钮显示 Loading 文案，禁用按钮。
  - 成功后弹出 toast（使用 Shadcn/ui 的 toast）。
  - 失败时在按钮下方展示错误信息（不弹窗）。
- 列表自动每 30 秒刷新一次（使用 `refetchInterval: 30000`）。
---
## 八、页面二：RAG 问答交互（/chat）
这是 MVP 的核心页面，需要高度结构化。
### 8.1 状态设计（Zustand）
在 `src/store/chatStore.ts` 中定义：
```ts
type ChatState = {
  messages: Message[];
  addMessage: (msg: Message) => void;
  clearMessages: () => void;
};
```
### 8.2 UI 结构
1. 顶部：一个下拉框选择当前 Repo（`repo_id`），数据来自 `useQuery(['repos'])`。
2. 中间：聊天区域：
   - 使用一个 `flex flex-col gap-2` 的容器。
   - 遍历 `messages`，区分 `user` 和 `assistant` 消息：
     - 用户消息：右对齐，浅背景。
     - AI 消息：左对齐，显示回答文本 + 引用卡片。
3. 引用卡片：
   - 使用 `<Card>` 组件。
   - 显示：`file_path`、`start_line - end_line`、代码片段截取前 100 字符。
   - 点击卡片：
     - 使用 `<Dialog>` 或 `<Drawer>` 展示完整 `content`。
4. 底部输入区：
   - `<Textarea>` + “发送” `<Button>`。
   - 支持 `Enter` 发送，`Shift+Enter` 换行。
### 8.3 发送问题逻辑
- 使用 `useMutation` 调用 `api.queryRAG(question, currentRepoId)`。
- 发送前：
  - 先往 `chatStore` 中添加一条用户消息（乐观更新）。
  - 输入框清空。
- 请求中：
  - 在 UI 显示“AI 正在思考…”占位消息。
- 成功：
  - 移除占位消息，往 `chatStore` 添加 AI 回复消息（包含 `references`）。
- 失败：
  - 在聊天区域内展示一条红色错误消息。
---
## 九、页面三：评测结果（/eval）
### 9.1 UI 结构
1. 顶部操作区：
   - 一个输入框填写测试集路径（可先简单写一个默认值）。
   - 一个 `<button> 运行评测 </button>`。
2. 结果列表：
   - 使用 `<Table>` 展示历史评测结果：
     - Timestamp
     - Precision
     - Recall
     - F1 Score
   - 每行状态（完成 / 进行中）。
### 9.2 数据与交互
- 使用 `useQuery(['evalResults'])` 获取 `api.getEvalResults()`。
- 使用 `useMutation` 运行评测：
  - 调用 `api.runEval(testSetPath)`。
  - 成功后：显示“评测任务已启动” toast，并定时刷新列表（可设置 `refetchInterval` 5 秒，直到检测到状态完成）。
---
## 十、页面四：模型微调（/train）
### 10.1 UI 结构
1. 配置表单：
   - Base Model（下拉选择，可先写几个固定选项）。
   - LoRA Rank（数字输入框）。
   - Epochs（数字输入框）。
   - `<button> 开始训练 </button>`。
2. 训练状态区：
   - 状态：idle / running / completed / failed。
   - 当前 Epoch / 总 Epoch。
   - Loss 值。
   - 进度条：使用 `<Progress>` 组件，值来自 `progress_percent`。
### 10.2 数据与交互
- 使用 `useQuery(['trainStatus'])` 获取 `api.getTrainStatus()`。
- 当 `status === 'running'` 时，设置 `refetchInterval: 3000` 轮询更新。
- 开始训练：
  - 使用 `useMutation` 调用 `api.startTrain(payload)`。
  - 成功后，toast 提示“训练任务已启动”，并开始轮询状态。
---
## 十一、表单与校验（React Hook Form + Zod）
**示例：训练表单 Schema（Zod）**
```ts
import { z } from 'zod';
export const trainFormSchema = z.object({
  base_model: z.string().min(1, '请选择基础模型'),
  lora_rank: z.number().int().min(1).max(64),
  epochs: z.number().int().min(1).max(10),
});
export type TrainFormValues = z.infer<typeof trainFormSchema>;
```
在 `train/page.tsx` 中，使用 `useForm` + `zodResolver`：
```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
export default function TrainPage() {
  const form = useForm<TrainFormValues>({
    resolver: zodResolver(trainFormSchema),
    defaultValues: {
      base_model: 'codellama/CodeLlama-7b-Instruct-hf',
      lora_rank: 8,
      epochs: 3,
    },
  });
  // 在 onSubmit 中调用 useMutation
}
```
---
## 十二、给 AI 助手的执行指令（必须遵守）
1. **技术栈严格执行**：  
   使用 Next.js 15+ App Router、Tailwind、TanStack Query v5、Zustand、React Hook Form + Zod、Shadcn/ui、Lucide React。不使用 Redux、Axios 等“老方案”。
2. **不写自定义 CSS 文件**：  
   所有样式通过 Tailwind 类名实现，仅保证布局清晰、可读，不做视觉设计。
3. **组件拆分**：  
   不要把所有逻辑写在一个文件里。  
   - 每个页面至少拆出一个 `*PageContent.tsx` 或组件文件夹。
   - Chat 页面必须拆成 `ChatMessage.tsx`、`ChatInput.tsx`、`ReferenceCard.tsx` 等。
4. **错误处理与 Loading 状态**：
   - 所有 API 调用使用 `try-catch`，错误信息展示在 UI 上（toast 或行内提示）。
   - 所有表格/列表必须处理 Loading 态（使用 `<Skeleton>` 或简单文本提示）。
5. **Mock 数据兼容**：
   - 在开发模式下，如果后端未启动，要保证界面不崩溃（可返回空数组 / 默认对象）。
   - 可在 `src/lib/api.ts` 中设置一个 `const IS_MOCK = false;` 开关，方便本地调试。
6. **引用交互**：
   - Chat 页面中，引用卡片要有 hover 效果（如背景色变化）。
   - 点击卡片时，使用 `<Dialog>` 或 `<Drawer>` 展示完整代码片段。
---
## 十三、总结：AI 输出物的要求
AI 助手拿到这份 MVP 文档后，必须输出：
1. 一个完整的 Next.js 项目结构（包括 `app/`、`components/`、`lib/`、`types/`、`store/` 等）。
2. 所有页面和关键组件的 TSX 文件。
3. 所有 API 封装、类型定义、Zustand store、表单校验 schema。
4. 确保前端：
   - 技术栈符合 2025–2026 主流趋势；
   - 能与你现有的 FastAPI 后端对接；
   - 交互逻辑完整，可运行、可演示。
你可以把这份文档直接丢给 AI，让它“按文档实现前端”，无需你再解释技术细节。
