import React from 'react';
import { Bell, Search, User, ChevronDown } from 'lucide-react';

interface HeaderProps {
  userName?: string;
  userRole?: 'doctor' | 'patient';
  showSearch?: boolean;
}

export function Header({ userName = 'User', userRole = 'doctor', showSearch = true }: HeaderProps) {
  return (
    <header className="bg-surface border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Search */}
        {showSearch && (
          <div className="relative w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" size={20} />
            <input
              type="text"
              placeholder={userRole === 'doctor' ? 'Search patients, conditions...' : 'Search...'}
              className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-200 bg-background text-text-primary placeholder:text-text-secondary/60 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-200"
            />
          </div>
        )}
        {!showSearch && <div />}

        {/* Right side */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <button className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors">
            <Bell size={22} className="text-text-secondary" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-error rounded-full" />
          </button>

          {/* User menu */}
          <button className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors">
            <div className="w-9 h-9 bg-primary/10 rounded-full flex items-center justify-center">
              <User size={20} className="text-primary" />
            </div>
            <div className="text-left">
              <p className="text-sm font-medium text-text-primary">{userName}</p>
              <p className="text-xs text-text-secondary capitalize">{userRole}</p>
            </div>
            <ChevronDown size={16} className="text-text-secondary" />
          </button>
        </div>
      </div>
    </header>
  );
}
