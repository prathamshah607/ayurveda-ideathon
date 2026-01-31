import React from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  Clock,
  Pill,
  AlertTriangle,
  Stethoscope,
  Activity,
  Bell,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';
import { Card, CardContent, Button, Badge } from '../../components/ui';

// Placeholder data
const stats = [
  { label: 'Total Patients', value: '247', icon: Users, color: 'text-info', bgColor: 'bg-info/10' },
  { label: 'Pending Consultations', value: '12', icon: Clock, color: 'text-warning', bgColor: 'bg-warning/10' },
  { label: 'Active Treatment Plans', value: '38', icon: Pill, color: 'text-success', bgColor: 'bg-success/10' },
  { label: 'Alerts', value: '3', icon: AlertTriangle, color: 'text-error', bgColor: 'bg-error/10' },
];

const recentActivity = [
  { id: 1, patient: 'Rajesh Kumar', action: 'Completed Prakriti assessment', time: '10 mins ago', type: 'assessment' },
  { id: 2, patient: 'Priya Sharma', action: 'Started new treatment plan', time: '1 hour ago', type: 'treatment' },
  { id: 3, patient: 'Amit Patel', action: 'Uploaded tongue image', time: '2 hours ago', type: 'upload' },
  { id: 4, patient: 'Sunita Devi', action: 'Requested consultation', time: '3 hours ago', type: 'consultation' },
  { id: 5, patient: 'Vikram Singh', action: 'Drug interaction alert', time: '4 hours ago', type: 'alert' },
];

const quickActions = [
  { label: 'New Diagnosis', icon: Stethoscope, path: '/doctor/diagnose', color: 'primary' },
  { label: 'Check Interactions', icon: AlertTriangle, path: '/doctor/decision-support', color: 'warning' },
  { label: 'View Alerts', icon: Bell, path: '/doctor/alerts', color: 'error' },
];

export function DoctorDashboard() {
  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome Card */}
      <Card className="bg-gradient-to-r from-primary to-primary-light text-white">
        <CardContent className="flex items-center justify-between">
          <div>
            <h1 className="font-heading text-2xl font-bold mb-1">
              Good Morning, Dr. Sharma! 🌿
            </h1>
            <p className="text-white/80">{today}</p>
          </div>
          <div className="text-right">
            <p className="text-white/80 text-sm">Today's Schedule</p>
            <p className="text-2xl font-bold">8 Appointments</p>
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} hover>
              <CardContent className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-secondary mb-1">{stat.label}</p>
                  <p className="text-3xl font-bold text-text-primary">{stat.value}</p>
                </div>
                <div className={`w-14 h-14 ${stat.bgColor} rounded-xl flex items-center justify-center`}>
                  <Icon className={stat.color} size={28} />
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-heading text-xl font-semibold text-text-primary">
              Recent Patient Activity
            </h2>
            <Link to="/doctor/patients" className="text-primary text-sm font-medium hover:underline">
              View All
            </Link>
          </div>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-primary font-medium">
                      {activity.patient.split(' ').map((n) => n[0]).join('')}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-text-primary">{activity.patient}</p>
                    <p className="text-sm text-text-secondary truncate">{activity.action}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-xs text-text-secondary">{activity.time}</p>
                    {activity.type === 'alert' && (
                      <Badge variant="error" size="sm">Alert</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <h2 className="font-heading text-xl font-semibold text-text-primary mb-6">
            Quick Actions
          </h2>
          <CardContent className="space-y-3">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <Link key={action.label} to={action.path}>
                  <Button
                    variant="outline"
                    className="w-full justify-between"
                    leftIcon={<Icon size={20} />}
                    rightIcon={<ArrowRight size={18} />}
                  >
                    {action.label}
                  </Button>
                </Link>
              );
            })}
          </CardContent>

          {/* Mini Stats */}
          <div className="mt-6 pt-6 border-t border-gray-100">
            <h3 className="text-sm font-medium text-text-secondary mb-4">This Week</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-text-secondary">Diagnoses</span>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-text-primary">24</span>
                  <TrendingUp size={14} className="text-success" />
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-text-secondary">Treatments Started</span>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-text-primary">18</span>
                  <TrendingUp size={14} className="text-success" />
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-text-secondary">Follow-ups</span>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-text-primary">32</span>
                  <Activity size={14} className="text-info" />
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
