'use client';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';

// 训练表单Schema
const trainFormSchema = z.object({
  base_model: z.string().min(1, '请选择基础模型'),
  lora_rank: z.number().int().min(1).max(64),
  epochs: z.number().int().min(1).max(10),
});

type TrainFormValues = z.infer<typeof trainFormSchema>;

export default function TrainPage() {
  const form = useForm<TrainFormValues>({
    resolver: zodResolver(trainFormSchema),
    defaultValues: {
      base_model: 'codellama/CodeLlama-7b-Instruct-hf',
      lora_rank: 8,
      epochs: 3,
    },
  });

  // 获取训练状态
  const {
    data: trainStatus,
    isLoading: isLoadingStatus,
    error: errorStatus,
  } = useQuery({
    queryKey: ['trainStatus'],
    queryFn: api.getTrainStatus,
    refetchInterval: 3000, // 每3秒刷新一次
  });

  // 开始训练
  const startTrainMutation = useMutation({
    mutationFn: api.startTrain,
    onSuccess: () => {
      toast.success('训练任务已启动！');
    },
    onError: () => {
      toast.error('训练任务启动失败');
    },
  });

  const handleSubmit = (data: TrainFormValues) => {
    startTrainMutation.mutate(data);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">模型微调</h1>
        <p className="text-muted-foreground">配置并启动模型微调任务</p>
      </div>

      {/* 配置表单 */}
      <div className="w-full max-w-md space-y-4">
        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="base-model">基础模型</Label>
            <Select
              value={form.getValues('base_model')}
              onValueChange={(value) => form.setValue('base_model', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="选择基础模型" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="codellama/CodeLlama-7b-Instruct-hf">
                  CodeLlama-7b-Instruct
                </SelectItem>
                <SelectItem value="mistralai/Mistral-7B-v0.1">
                  Mistral-7B-v0.1
                </SelectItem>
                <SelectItem value="meta-llama/Llama-2-7b-chat-hf">
                  Llama-2-7b-chat
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="lora-rank">LoRA Rank</Label>
            <Input
              id="lora-rank"
              type="number"
              {...form.register('lora_rank', { valueAsNumber: true })}
              min={1}
              max={64}
            />
            {form.formState.errors.lora_rank && (
              <p className="text-red-500 text-sm">
                {form.formState.errors.lora_rank.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="epochs">训练轮数 (Epochs)</Label>
            <Input
              id="epochs"
              type="number"
              {...form.register('epochs', { valueAsNumber: true })}
              min={1}
              max={10}
            />
            {form.formState.errors.epochs && (
              <p className="text-red-500 text-sm">
                {form.formState.errors.epochs.message}
              </p>
            )}
          </div>

          <Button type="submit" disabled={startTrainMutation.isPending}>
            {startTrainMutation.isPending ? '启动中...' : '开始训练'}
          </Button>
        </form>
      </div>

      {/* 训练状态 */}
      <div className="w-full max-w-md space-y-4">
        <h2 className="text-lg font-semibold">训练状态</h2>
        {isLoadingStatus ? (
          <div className="text-muted-foreground">加载中...</div>
        ) : errorStatus ? (
          <div className="text-red-500">获取训练状态失败</div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">状态:</span>
              <span className={`text-sm font-medium ${
                trainStatus?.status === 'running' ? 'text-blue-500' :
                trainStatus?.status === 'completed' ? 'text-green-500' :
                trainStatus?.status === 'failed' ? 'text-red-500' :
                'text-muted-foreground'
              }`}>
                {trainStatus?.status === 'idle' && '空闲'}
                {trainStatus?.status === 'running' && '运行中'}
                {trainStatus?.status === 'completed' && '完成'}
                {trainStatus?.status === 'failed' && '失败'}
                {!trainStatus && '未知'}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">当前轮数:</span>
              <span className="text-sm">
                {trainStatus?.current_epoch || 0}/{form.getValues('epochs')}
              </span>
            </div>

            {trainStatus?.loss !== null && (
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Loss:</span>
                <span className="text-sm">{trainStatus?.loss?.toFixed(4)}</span>
              </div>
            )}

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">进度:</span>
                <span className="text-sm">{trainStatus?.progress_percent || 0}%</span>
              </div>
              <Progress value={trainStatus?.progress_percent || 0} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
