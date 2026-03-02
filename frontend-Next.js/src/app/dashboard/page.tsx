'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const [repoName, setRepoName] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'completed'>('idle');

  // 获取代码库列表
  const {
    data: repos,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['repos'],
    queryFn: api.getRepos,
    refetchInterval: 30000, // 每30秒刷新一次
  });

  // 上传代码库
  const uploadMutation = useMutation({
    mutationFn: api.uploadRepo,
    onMutate: () => {
      setStatus('uploading');
    },
    onSuccess: async () => {
      setStatus('processing');
      // 调用processRepo
      try {
        await api.processRepo(repoName);
        setStatus('completed');
        toast.success('代码库入库成功！');
        // 刷新代码库列表
        queryClient.invalidateQueries({ queryKey: ['repos'] });
        // 重置表单
        setRepoName('');
        setFile(null);
        setTimeout(() => setStatus('idle'), 2000);
      } catch (error) {
        toast.error('代码库处理失败');
        setStatus('idle');
      }
    },
    onError: () => {
      toast.error('代码库上传失败');
      setStatus('idle');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      toast.error('请选择文件');
      return;
    }
    if (!repoName) {
      toast.error('请输入代码库名称');
      return;
    }
    uploadMutation.mutate(file);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">代码库管理</h1>
        <p className="text-muted-foreground">管理已入库的代码库，支持上传新代码库</p>
      </div>

      {/* 上传表单 */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <label htmlFor="repo-name" className="text-sm font-medium">代码库名称</label>
          <Input
            id="repo-name"
            value={repoName}
            onChange={(e) => setRepoName(e.target.value)}
            placeholder="请输入代码库名称"
            disabled={status !== 'idle'}
          />
        </div>

        <div className="flex flex-col gap-2">
          <label htmlFor="repo-file" className="text-sm font-medium">选择文件</label>
          <Input
            id="repo-file"
            type="file"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            disabled={status !== 'idle'}
          />
        </div>

        <Button
          type="submit"
          disabled={status !== 'idle' || !file || !repoName}
        >
          {status === 'idle' && '入库'}
          {status === 'uploading' && '上传中...'}
          {status === 'processing' && '处理中...'}
          {status === 'completed' && '完成'}
        </Button>

        {error && <p className="text-red-500 text-sm">获取代码库列表失败</p>}
      </form>

      {/* 代码库列表 */}
      <div>
        <h2 className="text-lg font-semibold mb-4">已入库代码库</h2>
        {isLoading ? (
          // Loading状态
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-1/4" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            ))}
          </div>
        ) : error ? (
          <p className="text-red-500">获取代码库列表失败</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>代码库名称</TableHead>
                <TableHead>文件数量</TableHead>
                <TableHead>创建时间</TableHead>
                <TableHead>状态</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {repos?.map((repo) => (
                <TableRow key={repo.id}>
                  <TableCell>{repo.name}</TableCell>
                  <TableCell>{repo.files_count}</TableCell>
                  <TableCell>
                    {new Date(repo.created_at).toLocaleString('zh-CN')}
                  </TableCell>
                  <TableCell>
                    <span className="text-green-500">已入库</span>
                  </TableCell>
                </TableRow>
              )) || (
                <TableRow>
                  <TableCell colSpan={4} className="text-center">
                    暂无代码库
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
