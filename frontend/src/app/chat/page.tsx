'use client';
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useChatStore } from '@/store/chatStore';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';

export default function ChatPage() {
  const [currentRepoId, setCurrentRepoId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const { messages, addMessage, clearMessages } = useChatStore();

  // 获取代码库列表
  const {
    data: repos,
    isLoading: isLoadingRepos,
    error: errorRepos,
  } = useQuery({
    queryKey: ['repos'],
    queryFn: api.getRepos,
  });

  // 发送问题
  const queryMutation = useMutation({
    mutationFn: ({ question, repoId }: { question: string; repoId?: string }) =>
      api.queryRAG(question, repoId),
    onMutate: () => {
      setIsLoading(true);
    },
    onSuccess: (data) => {
      // 添加AI回复
      addMessage({
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: data.answer,
        references: data.references,
        created_at: new Date().toISOString(),
      });
      setIsLoading(false);
    },
    onError: (error) => {
      console.error('Query error:', error);
      // 添加错误消息
      addMessage({
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: '抱歉，查询失败，请稍后重试。',
        created_at: new Date().toISOString(),
      });
      setIsLoading(false);
      toast.error('查询失败，请稍后重试');
    },
  });

  const handleSubmit = (question: string) => {
    // 添加用户消息
    addMessage({
      id: `msg-${Date.now()}`,
      role: 'user',
      content: question,
      created_at: new Date().toISOString(),
    });

    // 发送查询
    queryMutation.mutate({ question, repoId: currentRepoId || undefined });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">RAG 问答</h1>
        <p className="text-muted-foreground">向代码库提问，获取带引用的回答</p>
      </div>

      {/* 代码库选择 */}
      <div className="w-full max-w-md">
        <Select value={currentRepoId} onValueChange={setCurrentRepoId}>
          <SelectTrigger>
            <SelectValue placeholder="选择代码库" />
          </SelectTrigger>
          <SelectContent>
            {isLoadingRepos ? (
              <SelectItem value="">加载中...</SelectItem>
            ) : errorRepos ? (
              <SelectItem value="">加载失败</SelectItem>
            ) : (
              repos?.map((repo) => (
                <SelectItem key={repo.id} value={repo.id}>
                  {repo.name}
                </SelectItem>
              )) || (
                <SelectItem value="">暂无代码库</SelectItem>
              )
            )}
          </SelectContent>
        </Select>
      </div>

      {/* 聊天区域 */}
      <div className="flex-1 space-y-4 overflow-y-auto max-h-[60vh] border rounded-lg p-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-40 text-muted-foreground">
            <p>开始向代码库提问吧！</p>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}

        {/* 加载状态 */}
        {isLoading && (
          <div className="flex items-center justify-start">
            <div className="bg-muted rounded-lg p-4 max-w-[80%]">
              <div className="text-sm font-medium mb-2">AI</div>
              <div className="text-sm">AI 正在思考...</div>
            </div>
          </div>
        )}
      </div>

      {/* 输入区域 */}
      <div className="w-full max-w-2xl">
        <ChatInput onSubmit={handleSubmit} disabled={isLoading} />
      </div>
    </div>
  );
}
