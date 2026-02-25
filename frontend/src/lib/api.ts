const API_BASE_URL = 'http://localhost:8000';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Reference {
  file_path: string;
  start_line?: number;
  end_line?: number;
  content: string;
  score: number;
}

interface RetrievalResult {
  file_path: string;
  content: string;
  score: number;
  rank: number;
}

interface ChatResponse {
  id: string;
  message: string;
  references: Reference[];
  retrieval_results: RetrievalResult[];
  timestamp: string;
}

interface EvalResult {
  id: string;
  timestamp: string;
  metrics: {
    recall_at_k: number;
    mrr: number;
    accuracy: number;
    no_reference_rate: number;
  };
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  // 健康检查
  async healthCheck() {
    return fetchApi<{ status: string; version: string }>('/health');
  },

  // 获取代码库列表
  async getRepos() {
    return fetchApi<Array<{ id: string; name: string; files_count: number; created_at: string }>>('/api/repos');
  },

  // 上传代码库
  async uploadRepo(file: File, repoName: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('repo_name', repoName);
    
    const response = await fetch(`${API_BASE_URL}/api/repos/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error('Upload failed');
    }
    return response.json();
  },

  // 处理代码库
  async processRepo(repoName: string) {
    return fetchApi<{ message: string; chunks_count: number }>('/api/repos/process', {
      method: 'POST',
      body: JSON.stringify({ repo_name: repoName }),
    });
  },

  // RAG 问答
  async queryRAG(question: string, repoId?: string, topK = 5) {
    const response = await fetchApi<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify({
        messages: [{ role: 'user', content: question }],
        top_k: topK,
        stream: false,
        include_hits: true,
      }),
    });
    return {
      answer: response.message,
      references: response.references,
      retrievalResults: response.retrieval_results,
    };
  },

  // 仅检索（不调用 LLM）
  async ask(query: string, topK = 5) {
    return fetchApi<{
      query: string;
      results: RetrievalResult[];
      timestamp: string;
    }>('/ask', {
      method: 'POST',
      body: JSON.stringify({ query, top_k: topK }),
    });
  },

  // 运行评测
  async runEval(datasetPath: string, topK = 5) {
    return fetchApi<{ task_id: string; status: string }>('/eval/run', {
      method: 'POST',
      body: JSON.stringify({ dataset_path: datasetPath, top_k: topK }),
    });
  },

  // 获取评测结果列表
  async getEvalResults() {
    return fetchApi<{ files: string[] }>('/eval/results');
  },

  // 获取指定评测结果
  async getEvalResult(filename: string) {
    return fetchApi<EvalResult>(`/eval/results/${filename}`);
  },

  // 获取训练状态
  async getTrainStatus() {
    return fetchApi<{ status: string; current_epoch: number; loss: number | null; progress_percent: number }>('/train/status');
  },

  // 开始训练
  async startTrain(config: {
    base_model: string;
    lora_rank: number;
    epochs: number;
    dataset_path: string;
  }) {
    return fetchApi<{ task_id: string; status: string }>('/train/start', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  },
};
