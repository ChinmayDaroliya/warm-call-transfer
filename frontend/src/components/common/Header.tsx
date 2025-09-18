'use client'; 

import React from 'react';
import { Button } from '@/components/ui/button';
import { useUIStore } from '@/store';
import { Menu, Phone, User } from 'lucide-react';
import Link from 'next/link';

export const Header: React.FC = () => {
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);

  return (
    <header className="bg-background border-b border-border px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        {/* <Button variant="ghost" size="icon" onClick={toggleSidebar}>
          <Menu size={20} />
        </Button> */}
        <div className="flex items-center space-x-2">
          <Phone size={24} className="text-primary" />
          <h1 className="text-xl font-semibold">Warm Transfer System</h1>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <Button variant="outline" size="sm" >
          <Link href="/agent" className='flex items-center gap-2'>
          <User size={16} className="mr-2" />
          Agent Dashboard
          </Link>
        </Button>
        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
          <span className="text-primary-foreground text-sm font-medium">A</span>
        </div>
      </div>
    </header>
  );
};
