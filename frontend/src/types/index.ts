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

// API 响应类型
export interface UploadResponse {
  task_id: string;
  status: string;
}

export interface ProcessResponse {
  message: string;
  chunks_count: number;
}

export interface QueryResponse {
  answer: string;
  references: Reference[];
}

export interface EvalRunResponse {
  task_id: string;
}

export interface TrainStartResponse {
  job_id: string;
}
