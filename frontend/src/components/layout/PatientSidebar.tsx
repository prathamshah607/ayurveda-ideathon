import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  User,
  Search,
  TrendingUp,
  MessageCircle,
  Calendar,
  BookOpen,
  Settings,
  LogOut,
  Leaf,
} from 'lucide-react';

const menuItems = [
  { path: '/patient/dashboard', label: 'My Health', icon: Home },
  { path: '/patient/profile', label: 'My Profile', icon: User },
  { path: '/patient/symptoms', label: 'Symptom Checker', icon: Search },
  { path: '/patient/predictions', label: 'Health Predictions', icon: TrendingUp },
  { path: '/patient/chat', label: 'Ask AI', icon: MessageCircle },
  { path: '/patient/treatments', label: 'My Treatments', icon: Calendar },
  { path: '/patient/learn', label: 'Learn Ayurveda', icon: BookOpen },
];

const bottomMenuItems = [
  { path: '/patient/settings', label: 'Settings', icon: Settings },
];

export function PatientSidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 bg-surface border-r border-gray-200 min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-100">
        <Link to="/patient/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <Leaf className="text-white" size={24} />
          </div>
          <div>
            <h1 className="font-heading text-lg font-bold text-primary">Ayurveda AI</h1>
            <p className="text-xs text-text-secondary">Your Wellness Journey</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-1">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200
                    ${
                      isActive
                        ? 'bg-primary text-white shadow-md'
                        : 'text-text-secondary hover:bg-primary/5 hover:text-primary'
                    }
                  `}
                >
                  <Icon size={20} />
                  <span className="font-medium">{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Bottom menu */}
      <div className="p-4 border-t border-gray-100">
        <ul className="space-y-1">
          {bottomMenuItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200
                    ${
                      isActive
                        ? 'bg-primary text-white shadow-md'
                        : 'text-text-secondary hover:bg-primary/5 hover:text-primary'
                    }
                  `}
                >
                  <Icon size={20} />
                  <span className="font-medium">{item.label}</span>
                </Link>
              </li>
            );
          })}
          <li>
            <button
              className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-text-secondary hover:bg-error/5 hover:text-error transition-all duration-200"
              onClick={() => {
                // TODO: Implement logout
                console.log('Logout clicked');
              }}
            >
              <LogOut size={20} />
              <span className="font-medium">Logout</span>
            </button>
          </li>
        </ul>
      </div>
    </aside>
  );
}
