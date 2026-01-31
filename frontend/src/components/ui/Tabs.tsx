import React from 'react';

interface TabsProps {
  tabs: { id: string; label: string; icon?: React.ReactNode }[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

export function Tabs({ tabs, activeTab, onChange, className = '' }: TabsProps) {
  return (
    <div className={`border-b border-gray-200 ${className}`}>
      <nav className="flex gap-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => onChange(tab.id)}
            className={`
              flex items-center gap-2 px-4 py-3 font-medium text-sm border-b-2 transition-all duration-200
              ${
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-text-secondary hover:text-text-primary hover:border-gray-300'
              }
            `}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );
}

interface TabPanelProps {
  isActive: boolean;
  children: React.ReactNode;
  className?: string;
}

export function TabPanel({ isActive, children, className = '' }: TabPanelProps) {
  if (!isActive) return null;
  
  return (
    <div className={`animate-fade-in ${className}`}>
      {children}
    </div>
  );
}
