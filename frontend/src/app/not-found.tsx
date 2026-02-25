'use client';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center">
      <h1 className="text-4xl font-bold mb-4">404</h1>
      <p className="text-xl mb-8">页面未找到</p>
      <a
        href="/dashboard"
        className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
      >
        返回首页
      </a>
    </div>
  );
}
