import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Leaf, Mail, Lock, Eye, EyeOff, User, Building, Award, Stethoscope } from 'lucide-react';
import { Button, Input, Select, TagInput } from '../../components/ui';

const specializations = [
  { value: 'kayachikitsa', label: 'Kayachikitsa (Internal Medicine)' },
  { value: 'shalya', label: 'Shalya Tantra (Surgery)' },
  { value: 'shalakya', label: 'Shalakya Tantra (ENT/Ophthalmology)' },
  { value: 'kaumarabhritya', label: 'Kaumarabhritya (Pediatrics)' },
  { value: 'agadatantra', label: 'Agada Tantra (Toxicology)' },
  { value: 'rasayana', label: 'Rasayana (Rejuvenation)' },
  { value: 'panchakarma', label: 'Panchakarma' },
  { value: 'other', label: 'Other' },
];

const commonConditions = [
  'Diabetes',
  'Hypertension',
  'Thyroid disorders',
  'Arthritis',
  'Digestive issues',
  'Skin conditions',
  'Respiratory issues',
  'Anxiety/Stress',
  'Sleep disorders',
  'None',
];

export function RegisterPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialRole = searchParams.get('role') as 'doctor' | 'patient' || 'patient';
  
  const [role, setRole] = useState<'doctor' | 'patient'>(initialRole);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Common fields
  const [commonData, setCommonData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  // Doctor fields
  const [doctorData, setDoctorData] = useState({
    licenseNumber: '',
    specialization: '',
    clinicName: '',
    credentials: '',
  });

  // Patient fields
  const [patientData, setPatientData] = useState({
    age: '',
    gender: '',
    conditions: [] as string[],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // TODO: Implement actual registration
    await new Promise((resolve) => setTimeout(resolve, 1000));
    
    // Navigate based on role
    if (role === 'doctor') {
      navigate('/doctor/dashboard');
    } else {
      navigate('/patient/dashboard');
    }
    
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left side - Decorative */}
      <div className="hidden lg:flex flex-1 bg-gradient-to-br from-primary to-primary-dark items-center justify-center p-16">
        <div className="text-center text-white">
          <Leaf size={80} className="mx-auto mb-8 opacity-80" />
          <h2 className="font-heading text-4xl font-bold mb-4">
            Begin Your<br />Wellness Journey
          </h2>
          <p className="text-white/80 text-lg max-w-md mx-auto">
            Create your account and unlock the power of AI-enhanced 
            Ayurvedic healthcare tailored just for you.
          </p>
        </div>
      </div>

      {/* Right side - Form */}
      <div className="flex-1 flex items-center justify-center p-8 overflow-y-auto">
        <div className="w-full max-w-lg py-8">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <Leaf className="text-white" size={24} />
            </div>
            <span className="font-heading text-xl font-bold text-primary">Ayurveda AI</span>
          </Link>

          <h1 className="font-heading text-3xl font-bold text-text-primary mb-2">
            Create Account
          </h1>
          <p className="text-text-secondary mb-8">
            Join us to experience personalized Ayurvedic care
          </p>

          {/* Role Selection */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-text-primary mb-3">
              I am a:
            </label>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setRole('doctor')}
                className={`
                  flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all duration-200
                  ${
                    role === 'doctor'
                      ? 'border-primary bg-primary/5 text-primary'
                      : 'border-gray-200 text-text-secondary hover:border-gray-300'
                  }
                `}
              >
                <Stethoscope size={32} />
                <span className="font-medium">Doctor</span>
              </button>
              <button
                type="button"
                onClick={() => setRole('patient')}
                className={`
                  flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all duration-200
                  ${
                    role === 'patient'
                      ? 'border-primary bg-primary/5 text-primary'
                      : 'border-gray-200 text-text-secondary hover:border-gray-300'
                  }
                `}
              >
                <User size={32} />
                <span className="font-medium">Patient</span>
              </button>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Common Fields */}
            <Input
              label="Full Name"
              type="text"
              placeholder="Enter your full name"
              value={commonData.name}
              onChange={(e) => setCommonData({ ...commonData, name: e.target.value })}
              leftIcon={<User size={18} />}
              required
            />

            <Input
              label="Email Address"
              type="email"
              placeholder="you@example.com"
              value={commonData.email}
              onChange={(e) => setCommonData({ ...commonData, email: e.target.value })}
              leftIcon={<Mail size={18} />}
              required
            />

            {/* Doctor-specific Fields */}
            {role === 'doctor' && (
              <>
                <Input
                  label="License Number"
                  type="text"
                  placeholder="Your AYUSH/BAMS registration number"
                  value={doctorData.licenseNumber}
                  onChange={(e) => setDoctorData({ ...doctorData, licenseNumber: e.target.value })}
                  leftIcon={<Award size={18} />}
                  required
                />

                <Select
                  label="Specialization"
                  options={specializations}
                  value={doctorData.specialization}
                  onChange={(e) => setDoctorData({ ...doctorData, specialization: e.target.value })}
                  placeholder="Select your specialization"
                  required
                />

                <Input
                  label="Clinic/Hospital Name"
                  type="text"
                  placeholder="Where do you practice?"
                  value={doctorData.clinicName}
                  onChange={(e) => setDoctorData({ ...doctorData, clinicName: e.target.value })}
                  leftIcon={<Building size={18} />}
                />

                <Input
                  label="Credentials"
                  type="text"
                  placeholder="e.g., BAMS, MD (Ayu), PhD"
                  value={doctorData.credentials}
                  onChange={(e) => setDoctorData({ ...doctorData, credentials: e.target.value })}
                  helperText="Your degrees and certifications"
                />
              </>
            )}

            {/* Patient-specific Fields */}
            {role === 'patient' && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Age"
                    type="number"
                    placeholder="Your age"
                    value={patientData.age}
                    onChange={(e) => setPatientData({ ...patientData, age: e.target.value })}
                    min="1"
                    max="120"
                    required
                  />
                  <Select
                    label="Gender"
                    options={[
                      { value: 'male', label: 'Male' },
                      { value: 'female', label: 'Female' },
                      { value: 'other', label: 'Other' },
                    ]}
                    value={patientData.gender}
                    onChange={(e) => setPatientData({ ...patientData, gender: e.target.value })}
                    placeholder="Select"
                    required
                  />
                </div>

                <TagInput
                  label="Known Health Conditions"
                  placeholder="Type or select conditions"
                  value={patientData.conditions}
                  onChange={(conditions) => setPatientData({ ...patientData, conditions })}
                  suggestions={commonConditions}
                />
              </>
            )}

            {/* Password Fields */}
            <Input
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Create a strong password"
              value={commonData.password}
              onChange={(e) => setCommonData({ ...commonData, password: e.target.value })}
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
              helperText="Minimum 8 characters with letters and numbers"
              required
            />

            <Input
              label="Confirm Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Confirm your password"
              value={commonData.confirmPassword}
              onChange={(e) => setCommonData({ ...commonData, confirmPassword: e.target.value })}
              leftIcon={<Lock size={18} />}
              error={
                commonData.confirmPassword && commonData.password !== commonData.confirmPassword
                  ? "Passwords don't match"
                  : undefined
              }
              required
            />

            {/* Terms */}
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                className="w-4 h-4 mt-0.5 rounded border-gray-300 text-primary focus:ring-primary"
                required
              />
              <span className="text-sm text-text-secondary">
                I agree to the{' '}
                <a href="#" className="text-primary hover:underline">Terms of Service</a>
                {' '}and{' '}
                <a href="#" className="text-primary hover:underline">Privacy Policy</a>
              </span>
            </label>

            <Button
              type="submit"
              className="w-full"
              size="lg"
              isLoading={isLoading}
            >
              Create Account
            </Button>

            <p className="text-center text-text-secondary">
              Already have an account?{' '}
              <Link to="/login" className="text-primary font-medium hover:underline">
                Sign in
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
