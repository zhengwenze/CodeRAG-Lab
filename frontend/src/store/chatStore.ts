import { create } from 'zustand';
import type { Message } from '@/types';

interface ChatState {
  messages: Message[];
  addMessage: (msg: Message) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  addMessage: (msg) => set((state) => ({
    messages: [...state.messages, msg],
  })),
  clearMessages: () => set({ messages: [] }),
}));
