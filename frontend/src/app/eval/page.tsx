'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';

export default function EvalPage() {
  const queryClient = useQueryClient();
  const [testSetPath, setTestSetPath] = useState('data/eval/coderag_eval_v1.json');
  const [isRunning, setIsRunning] = useState(false);

  // 获取评测结果
  const {
    data: evalResults,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['evalResults'],
    queryFn: api.getEvalResults,
  });

  // 运行评测
  const runEvalMutation = useMutation({
    mutationFn: api.runEval,
    onMutate: () => {
      setIsRunning(true);
    },
    onSuccess: (data) => {
      setIsRunning(false);
      toast.success('评测任务已启动！');
      // 定时刷新结果
      const interval = setInterval(() => {
        queryClient.invalidateQueries({ queryKey: ['evalResults'] });
      }, 5000);
      // 1分钟后停止刷新
      setTimeout(() => clearInterval(interval), 60000);
    },
    onError: () => {
      setIsRunning(false);
      toast.error('评测任务启动失败');
    },
  });

  const handleRunEval = () => {
    runEvalMutation.mutate(testSetPath);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">评测结果</h1>
        <p className="text-muted-foreground">查看评测结果，运行新的评测任务</p>
      </div>

      {/* 操作区 */}
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <label htmlFor="test-set-path" className="text-sm font-medium">测试集路径</label>
          <Input
            id="test-set-path"
            value={testSetPath}
            onChange={(e) => setTestSetPath(e.target.value)}
            placeholder="请输入测试集路径"
            disabled={isRunning}
          />
        </div>

        <Button
          onClick={handleRunEval}
          disabled={isRunning}
        >
          {isRunning ? '运行中...' : '运行评测'}
        </Button>
      </div>

      {/* 评测结果列表 */}
      <div>
        <h2 className="text-lg font-semibold mb-4">评测历史</h2>
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
          <p className="text-red-500">获取评测结果失败</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>时间</TableHead>
                <TableHead>精确率</TableHead>
                <TableHead>召回率</TableHead>
                <TableHead>F1分数</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {evalResults?.map((result) => (
                <TableRow key={result.id}>
                  <TableCell>
                    {new Date(result.timestamp).toLocaleString('zh-CN')}
                  </TableCell>
                  <TableCell>{(result.metrics.precision * 100).toFixed(1)}%</TableCell>
                  <TableCell>{(result.metrics.recall * 100).toFixed(1)}%</TableCell>
                  <TableCell>{(result.metrics.f1 * 100).toFixed(1)}%</TableCell>
                </TableRow>
              )) || (
                <TableRow>
                  <TableCell colSpan={4} className="text-center">
                    暂无评测结果
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
