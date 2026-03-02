'use client';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { Home, MessageSquare, BarChart2, Cpu } from 'lucide-react';
import { usePathname } from 'next/navigation';

interface NavItem {
  title: string;
  href: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: <Home className="h-5 w-5" />,
  },
  {
    title: 'Chat',
    href: '/chat',
    icon: <MessageSquare className="h-5 w-5" />,
  },
  {
    title: 'Evaluation',
    href: '/eval',
    icon: <BarChart2 className="h-5 w-5" />,
  },
  {
    title: 'Training',
    href: '/train',
    icon: <Cpu className="h-5 w-5" />,
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r bg-muted/50 p-4">
      <div className="mb-8">
        <h1 className="text-xl font-bold">CodeRAG Lab</h1>
        <p className="text-sm text-muted-foreground">可溯源代码库助手</p>
      </div>
      <nav className="space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center space-x-2 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              'hover:bg-muted',
              item.href === pathname ? 'bg-muted font-semibold' : ''
            )}
            aria-current={item.href === pathname ? 'page' : undefined}
          >
            {item.icon}
            <span>{item.title}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
}
