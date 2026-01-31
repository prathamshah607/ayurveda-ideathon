import React from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  TrendingUp,
  MessageCircle,
  Calendar,
  Heart,
  ArrowRight,
  CheckCircle,
  Sparkles,
} from 'lucide-react';
import { Card, CardContent, Button, CircularProgress, ProgressBar, Badge } from '../../components/ui';

// Placeholder data
const healthQuote = "Health is the greatest gift, contentment the greatest wealth, faithfulness the best relationship. – Buddha";

const upcomingActions = [
  { id: 1, title: 'Take morning medication', time: '8:00 AM', completed: true },
  { id: 2, title: 'Practice Pranayama', time: '9:00 AM', completed: true },
  { id: 3, title: 'Follow dietary guidelines', time: 'All day', completed: false },
  { id: 4, title: 'Evening Abhyanga', time: '6:00 PM', completed: false },
];

const quickLinks = [
  { label: 'Check Symptoms', icon: Search, path: '/patient/symptoms', color: 'primary' },
  { label: 'View Predictions', icon: TrendingUp, path: '/patient/predictions', color: 'success' },
  { label: 'Chat with AI', icon: MessageCircle, path: '/patient/chat', color: 'info' },
];

export function PatientDashboard() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome Card */}
      <Card className="bg-gradient-to-r from-primary to-secondary text-white">
        <CardContent>
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <h1 className="font-heading text-2xl font-bold mb-2">
                Namaste, Rahul! 🙏
              </h1>
              <p className="text-white/80 max-w-lg italic">
                "{healthQuote}"
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Sparkles size={20} />
              <span className="text-sm">Day 14 of your wellness journey</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Health Score */}
        <Card>
          <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
            Health Score
          </h2>
          <CardContent className="flex flex-col items-center">
            <CircularProgress
              value={78}
              size={140}
              strokeWidth={12}
              color="primary"
              label="Overall Health"
            />
            <p className="mt-4 text-center text-text-secondary">
              Your health is <span className="text-success font-medium">Good</span>. 
              Keep following your treatment plan!
            </p>
          </CardContent>
        </Card>

        {/* Treatment Progress */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-lg font-semibold text-text-primary">
              Current Treatment
            </h2>
            <Badge variant="primary">Phase 2</Badge>
          </div>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-text-secondary mb-1">Deepana-Pachana Protocol</p>
                <p className="text-xs text-text-secondary">Dr. Sharma</p>
              </div>
              <ProgressBar value={45} showValue label="Progress" color="primary" />
              <div className="pt-2">
                <p className="text-sm font-medium text-text-primary mb-2">Today's Tasks</p>
                {upcomingActions.slice(0, 3).map((action) => (
                  <div key={action.id} className="flex items-center gap-2 py-1">
                    {action.completed ? (
                      <CheckCircle size={16} className="text-success" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                    )}
                    <span className={`text-sm ${action.completed ? 'text-text-secondary line-through' : 'text-text-primary'}`}>
                      {action.title}
                    </span>
                  </div>
                ))}
              </div>
              <Link to="/patient/treatments">
                <Button variant="outline" size="sm" className="w-full" rightIcon={<ArrowRight size={16} />}>
                  View Full Plan
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
            Quick Actions
          </h2>
          <CardContent className="space-y-3">
            {quickLinks.map((link) => {
              const Icon = link.icon;
              return (
                <Link key={link.label} to={link.path}>
                  <Button
                    variant="outline"
                    className="w-full justify-between"
                    leftIcon={<Icon size={20} />}
                    rightIcon={<ArrowRight size={18} />}
                  >
                    {link.label}
                  </Button>
                </Link>
              );
            })}
          </CardContent>

          {/* Prakriti Status */}
          <div className="mt-6 pt-6 border-t border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-text-primary">Your Prakriti</span>
              <Badge variant="primary">Vata-Pitta</Badge>
            </div>
            <p className="text-xs text-text-secondary">
              Constitution assessment completed on Jan 10, 2026
            </p>
            <Link to="/assessment/prakriti" className="text-xs text-primary hover:underline mt-1 inline-block">
              Retake Assessment →
            </Link>
          </div>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Upcoming Reminders */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-lg font-semibold text-text-primary">
              Today's Schedule
            </h2>
            <Calendar size={20} className="text-text-secondary" />
          </div>
          <CardContent>
            <div className="space-y-3">
              {upcomingActions.map((action) => (
                <div
                  key={action.id}
                  className={`flex items-center justify-between p-3 rounded-lg ${
                    action.completed ? 'bg-success/5' : 'bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    {action.completed ? (
                      <CheckCircle size={20} className="text-success" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-primary" />
                    )}
                    <span className={action.completed ? 'text-text-secondary line-through' : 'text-text-primary'}>
                      {action.title}
                    </span>
                  </div>
                  <span className="text-sm text-text-secondary">{action.time}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Health Insights */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-lg font-semibold text-text-primary">
              Health Insights
            </h2>
            <Heart size={20} className="text-error" />
          </div>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-primary/5 rounded-lg border border-primary/10">
                <h3 className="font-medium text-primary mb-1">Dosha Balance Improving</h3>
                <p className="text-sm text-text-secondary">
                  Your Vata imbalance is showing signs of improvement. Continue with the current regimen.
                </p>
              </div>
              <div className="p-4 bg-warning/5 rounded-lg border border-warning/10">
                <h3 className="font-medium text-warning mb-1">Seasonal Tip</h3>
                <p className="text-sm text-text-secondary">
                  Winter season can aggravate Vata. Focus on warm, nourishing foods and oil massage.
                </p>
              </div>
              <Link to="/patient/predictions">
                <Button variant="ghost" size="sm" rightIcon={<ArrowRight size={16} />}>
                  View Full Health Report
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
