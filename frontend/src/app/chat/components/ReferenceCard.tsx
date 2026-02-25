'use client';
import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import type { Reference } from '@/types';

export default function ReferenceCard({ reference }: { reference: Reference }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!reference) {
    return null;
  }

  return (
    <>
      <Card
        className="cursor-pointer transition-all hover:shadow-md"
        onClick={() => setIsOpen(true)}
      >
        <CardContent className="p-4">
          <div className="flex justify-between items-start mb-2">
            <div className="font-medium text-sm truncate">
              {reference.file_path || ''}
            </div>
            <div className="text-xs text-muted-foreground">
              行 {reference.start_line || 0}-{reference.end_line || 0}
            </div>
          </div>
          <div className="text-sm text-muted-foreground mb-2">
            相似度: {Math.round((reference.score || 0) * 100)}%
          </div>
          <div className="text-sm bg-muted/50 p-2 rounded whitespace-pre-wrap line-clamp-2">
            {reference.content || ''}
          </div>
        </CardContent>
      </Card>

      {/* 引用详情对话框 */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-auto">
          <DialogHeader>
            <DialogTitle>
              {reference.file_path || ''} (行 {reference.start_line || 0}-{reference.end_line || 0})
            </DialogTitle>
          </DialogHeader>
          <div className="mt-4">
            <div className="text-sm text-muted-foreground mb-4">
              相似度: {Math.round((reference.score || 0) * 100)}%
            </div>
            <pre className="bg-muted p-4 rounded overflow-x-auto text-sm">
              {reference.content || ''}
            </pre>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
