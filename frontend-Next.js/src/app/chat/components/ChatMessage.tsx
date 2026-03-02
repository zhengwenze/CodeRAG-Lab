'use client';
import type { Message } from '@/types';
import ReferenceCard from './ReferenceCard';

export default function ChatMessage({ message }: { message: Message }) {
  if (!message) {
    return null;
  }

  return (
    <div
      className={`flex flex-col gap-2 ${message.role === 'user' ? 'items-end' : 'items-start'}`}
    >
      <div
        className={`max-w-[80%] rounded-lg p-4 ${message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}
      >
        <div className="text-sm font-medium mb-2">
          {message.role === 'user' ? '你' : 'AI'}
        </div>
        <div className="whitespace-pre-wrap">{message.content || ''}</div>
      </div>
      
      {/* 显示引用 */}
      {message.role === 'assistant' && 
       message.references && 
       Array.isArray(message.references) && 
       message.references.length > 0 && (
        <div className="w-full max-w-[80%] space-y-2">
          {message.references.map((ref, index) => (
            <ReferenceCard 
              key={ref.file_path + ref.start_line + index} 
              reference={ref} 
            />
          ))}
        </div>
      )}
    </div>
  );
}
