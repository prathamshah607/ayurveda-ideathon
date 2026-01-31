import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Leaf, Mail, Lock, Eye, EyeOff } from 'lucide-react';
import { Button, Input, Tabs, TabPanel } from '../../components/ui';

export function LoginPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'doctor' | 'patient'>('doctor');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // TODO: Implement actual login
    await new Promise((resolve) => setTimeout(resolve, 1000));
    
    // Navigate based on role
    if (activeTab === 'doctor') {
      navigate('/doctor/dashboard');
    } else {
      navigate('/patient/dashboard');
    }
    
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left side - Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <Leaf className="text-white" size={24} />
            </div>
            <span className="font-heading text-xl font-bold text-primary">Ayurveda AI</span>
          </Link>

          <h1 className="font-heading text-3xl font-bold text-text-primary mb-2">
            Welcome Back
          </h1>
          <p className="text-text-secondary mb-8">
            Sign in to continue your wellness journey
          </p>

          {/* Role Tabs */}
          <Tabs
            tabs={[
              { id: 'doctor', label: 'Doctor Login' },
              { id: 'patient', label: 'Patient Login' },
            ]}
            activeTab={activeTab}
            onChange={(id) => setActiveTab(id as 'doctor' | 'patient')}
            className="mb-8"
          />

          <TabPanel isActive={true}>
            <form onSubmit={handleSubmit} className="space-y-6">
              <Input
                label="Email Address"
                type="email"
                placeholder="you@example.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                leftIcon={<Mail size={18} />}
                required
              />

              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                leftIcon={<Lock size={18} />}
                rightIcon={
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="hover:text-primary transition-colors"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                }
                required
              />

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span className="text-text-secondary">Remember me</span>
                </label>
                <Link to="/forgot-password" className="text-primary hover:underline">
                  Forgot Password?
                </Link>
              </div>

              <Button
                type="submit"
                className="w-full"
                size="lg"
                isLoading={isLoading}
              >
                Sign In
              </Button>

              {/* Divider */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-background text-text-secondary">
                    Or continue with
                  </span>
                </div>
              </div>

              {/* Google OAuth */}
              <button
                type="button"
                className="w-full flex items-center justify-center gap-3 px-4 py-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                <span className="text-text-secondary font-medium">Google</span>
              </button>

              <p className="text-center text-text-secondary">
                Don't have an account?{' '}
                <Link
                  to={`/register?role=${activeTab}`}
                  className="text-primary font-medium hover:underline"
                >
                  Sign up
                </Link>
              </p>
            </form>
          </TabPanel>
        </div>
      </div>

      {/* Right side - Decorative */}
      <div className="hidden lg:flex flex-1 bg-gradient-to-br from-primary to-primary-dark items-center justify-center p-16">
        <div className="text-center text-white">
          <Leaf size={80} className="mx-auto mb-8 opacity-80" />
          <h2 className="font-heading text-4xl font-bold mb-4">
            Ancient Wisdom,<br />Modern Intelligence
          </h2>
          <p className="text-white/80 text-lg max-w-md mx-auto">
            Join thousands of practitioners and patients who trust Ayurveda AI 
            for personalized, holistic healthcare.
          </p>
        </div>
      </div>
    </div>
  );
}
