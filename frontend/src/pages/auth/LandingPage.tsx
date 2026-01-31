import React from 'react';
import { Link } from 'react-router-dom';
import { Leaf, Stethoscope, User, ArrowRight, Heart, Brain, Shield, Sparkles } from 'lucide-react';
import { Button } from '../../components/ui';

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Diagnosis',
    description: 'Intelligent symptom analysis using ancient Ayurvedic wisdom combined with modern AI.',
  },
  {
    icon: Heart,
    title: 'Personalized Treatment',
    description: 'Custom treatment plans tailored to your unique Prakriti (constitution).',
  },
  {
    icon: Shield,
    title: 'Safe & Natural',
    description: 'Evidence-based recommendations with safety checks and drug interaction alerts.',
  },
  {
    icon: Sparkles,
    title: 'Holistic Approach',
    description: 'Address root causes with diet, lifestyle, and herbal formulations.',
  },
];

export function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="bg-surface/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                <Leaf className="text-white" size={24} />
              </div>
              <span className="font-heading text-xl font-bold text-primary">Ayurveda AI</span>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/login">
                <Button variant="ghost">Login</Button>
              </Link>
              <Link to="/register">
                <Button variant="primary">Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-accent/10 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-7xl mx-auto px-6 py-24">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="font-heading text-5xl md:text-6xl font-bold text-text-primary mb-6">
              Ancient Wisdom,{' '}
              <span className="text-primary">Modern Intelligence</span>
            </h1>
            <p className="text-xl text-text-secondary mb-10 leading-relaxed">
              Experience the power of Ayurveda enhanced by artificial intelligence. 
              Get personalized health insights, diagnosis support, and treatment plans 
              rooted in 5,000 years of traditional wisdom.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
              <Link to="/register?role=doctor">
                <Button
                  size="lg"
                  variant="primary"
                  leftIcon={<Stethoscope size={22} />}
                  rightIcon={<ArrowRight size={20} />}
                  className="min-w-[200px]"
                >
                  I'm a Doctor
                </Button>
              </Link>
              <Link to="/register?role=patient">
                <Button
                  size="lg"
                  variant="outline"
                  leftIcon={<User size={22} />}
                  rightIcon={<ArrowRight size={20} />}
                  className="min-w-[200px]"
                >
                  I'm a Patient
                </Button>
              </Link>
            </div>

            {/* Trust badges */}
            <div className="flex items-center justify-center gap-8 text-sm text-text-secondary">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-success rounded-full" />
                <span>AYUSH Compliant</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-success rounded-full" />
                <span>Verified by Ayurvedic Physicians</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-success rounded-full" />
                <span>Evidence-Based</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-surface">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="font-heading text-3xl md:text-4xl font-bold text-text-primary mb-4">
              Bridging Traditional Medicine with Modern Technology
            </h2>
            <p className="text-lg text-text-secondary max-w-2xl mx-auto">
              Our platform combines the depth of Ayurvedic knowledge with cutting-edge AI 
              to provide accurate, personalized healthcare solutions.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="p-6 rounded-xl bg-background border border-gray-100 hover:shadow-lg transition-shadow duration-300"
                >
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                    <Icon className="text-primary" size={24} />
                  </div>
                  <h3 className="font-heading text-lg font-semibold text-text-primary mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-text-secondary">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* For Doctors Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <span className="text-primary font-medium">For Practitioners</span>
              <h2 className="font-heading text-3xl md:text-4xl font-bold text-text-primary mt-2 mb-6">
                Empower Your Practice with AI-Assisted Diagnosis
              </h2>
              <ul className="space-y-4">
                {[
                  'Differential diagnosis with confidence scoring',
                  'Drug interaction and contraindication alerts',
                  'Disease progression modeling (Shatkriyakala)',
                  'Automated treatment plan generation',
                  'Tongue and nail analysis (coming soon)',
                ].map((item, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <span className="text-text-secondary">{item}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-8">
                <Link to="/register?role=doctor">
                  <Button size="lg" leftIcon={<Stethoscope size={20} />}>
                    Join as Doctor
                  </Button>
                </Link>
              </div>
            </div>
            <div className="bg-gradient-to-br from-primary/5 to-accent/5 rounded-2xl p-8 aspect-square flex items-center justify-center">
              <div className="text-center">
                <Stethoscope size={120} className="text-primary/30 mx-auto mb-4" />
                <p className="text-text-secondary">Doctor Dashboard Preview</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* For Patients Section */}
      <section className="py-24 bg-surface">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="order-2 lg:order-1 bg-gradient-to-br from-accent/5 to-primary/5 rounded-2xl p-8 aspect-square flex items-center justify-center">
              <div className="text-center">
                <User size={120} className="text-primary/30 mx-auto mb-4" />
                <p className="text-text-secondary">Patient Dashboard Preview</p>
              </div>
            </div>
            <div className="order-1 lg:order-2">
              <span className="text-accent font-medium">For Patients</span>
              <h2 className="font-heading text-3xl md:text-4xl font-bold text-text-primary mt-2 mb-6">
                Understand Your Health the Ayurvedic Way
              </h2>
              <ul className="space-y-4">
                {[
                  'Discover your Prakriti (constitution) with our quiz',
                  'AI-powered symptom checker with personalized insights',
                  'Health risk predictions based on your profile',
                  'Chat with our Ayurveda AI assistant',
                  'Track your treatment progress',
                  'Learn from curated Ayurvedic content',
                ].map((item, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-accent rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <span className="text-text-secondary">{item}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-8">
                <Link to="/register?role=patient">
                  <Button size="lg" variant="secondary" leftIcon={<User size={20} />}>
                    Join as Patient
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-text-primary py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center">
                <Leaf className="text-white" size={24} />
              </div>
              <span className="font-heading text-xl font-bold text-white">Ayurveda AI</span>
            </div>
            <p className="text-white/60 text-sm">
              Powered by Ayurveda AI • Ancient Wisdom, Modern Intelligence
            </p>
            <div className="flex items-center gap-6 text-sm text-white/60">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
