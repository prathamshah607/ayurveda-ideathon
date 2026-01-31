import React from 'react';
import { BookOpen, Play, Clock, ArrowRight } from 'lucide-react';
import { Card, CardContent, Button, Badge } from '../../components/ui';

const topics = [
  {
    id: 1,
    title: 'Understanding Doshas',
    description: 'Learn about Vata, Pitta, and Kapha - the three fundamental energies that govern your body and mind.',
    icon: '🌀',
    articles: 5,
    readTime: '15 min',
    category: 'Fundamentals',
  },
  {
    id: 2,
    title: 'Seasonal Routines (Ritucharya)',
    description: 'Discover how to adapt your diet and lifestyle according to seasons for optimal health.',
    icon: '🌸',
    articles: 4,
    readTime: '12 min',
    category: 'Lifestyle',
  },
  {
    id: 3,
    title: 'Digestive Health (Agni)',
    description: 'Understand the importance of digestive fire and how to strengthen it naturally.',
    icon: '🔥',
    articles: 6,
    readTime: '18 min',
    category: 'Health',
  },
  {
    id: 4,
    title: 'Daily Routine (Dinacharya)',
    description: 'Master the Ayurvedic daily routine for balanced energy and better health.',
    icon: '☀️',
    articles: 4,
    readTime: '10 min',
    category: 'Lifestyle',
  },
  {
    id: 5,
    title: 'Yoga & Pranayama',
    description: 'Explore breathing techniques and yoga practices suited to your constitution.',
    icon: '🧘',
    articles: 8,
    readTime: '25 min',
    category: 'Practice',
  },
  {
    id: 6,
    title: 'Ayurvedic Diet Basics',
    description: 'Learn the principles of Ayurvedic nutrition and how to eat for your dosha.',
    icon: '🥗',
    articles: 7,
    readTime: '20 min',
    category: 'Nutrition',
  },
  {
    id: 7,
    title: 'Self-Massage (Abhyanga)',
    description: 'Discover the healing benefits of daily oil massage and how to practice it.',
    icon: '💆',
    articles: 3,
    readTime: '8 min',
    category: 'Practice',
  },
  {
    id: 8,
    title: 'Herbal Remedies',
    description: 'Learn about common Ayurvedic herbs and their healing properties.',
    icon: '🌿',
    articles: 10,
    readTime: '30 min',
    category: 'Remedies',
  },
];

const featuredArticle = {
  title: 'The Complete Guide to Your Prakriti',
  description: 'Understanding your unique constitution is the first step to personalized Ayurvedic care. This comprehensive guide walks you through everything you need to know about Prakriti.',
  readTime: '12 min read',
  image: '🎯',
};

export function LearnAyurveda() {
  return (
    <div className="animate-fade-in">
      <div className="mb-6">
        <h1 className="font-heading text-2xl font-bold text-text-primary">Learn Ayurveda</h1>
        <p className="text-text-secondary">Educational resources to deepen your understanding</p>
      </div>

      {/* Featured Article */}
      <Card className="mb-8 bg-gradient-to-r from-primary/5 to-accent/5 border-primary/10">
        <CardContent className="flex flex-col md:flex-row items-center gap-6">
          <div className="w-24 h-24 bg-primary/10 rounded-2xl flex items-center justify-center text-5xl flex-shrink-0">
            {featuredArticle.image}
          </div>
          <div className="flex-1 text-center md:text-left">
            <Badge variant="primary" className="mb-2">Featured</Badge>
            <h2 className="font-heading text-xl font-semibold text-text-primary mb-2">
              {featuredArticle.title}
            </h2>
            <p className="text-text-secondary mb-3">{featuredArticle.description}</p>
            <div className="flex items-center justify-center md:justify-start gap-4">
              <span className="flex items-center gap-1 text-sm text-text-secondary">
                <Clock size={14} />
                {featuredArticle.readTime}
              </span>
              <Button size="sm" rightIcon={<ArrowRight size={16} />}>
                Start Reading
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Topics Grid */}
      <h2 className="font-heading text-xl font-semibold text-text-primary mb-4">
        Browse Topics
      </h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {topics.map((topic) => (
          <Card key={topic.id} hover className="cursor-pointer group">
            <CardContent>
              <div className="text-4xl mb-4">{topic.icon}</div>
              <Badge variant="default" size="sm" className="mb-2">
                {topic.category}
              </Badge>
              <h3 className="font-heading text-lg font-semibold text-text-primary mb-2 group-hover:text-primary transition-colors">
                {topic.title}
              </h3>
              <p className="text-sm text-text-secondary mb-4 line-clamp-2">
                {topic.description}
              </p>
              <div className="flex items-center justify-between text-xs text-text-secondary">
                <span className="flex items-center gap-1">
                  <BookOpen size={12} />
                  {topic.articles} articles
                </span>
                <span className="flex items-center gap-1">
                  <Clock size={12} />
                  {topic.readTime}
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Tips Section */}
      <Card className="mt-8">
        <div className="flex items-center gap-2 mb-4">
          <Play className="text-primary" size={24} />
          <h2 className="font-heading text-xl font-semibold text-text-primary">
            Quick Video Tips
          </h2>
        </div>
        <CardContent>
          <div className="grid sm:grid-cols-3 gap-4">
            {[
              { title: 'Morning Routine for Vata', duration: '5:30' },
              { title: 'Simple Pranayama Techniques', duration: '7:15' },
              { title: 'How to Do Self-Massage', duration: '8:45' },
            ].map((video, index) => (
              <div
                key={index}
                className="relative bg-gray-100 rounded-xl aspect-video flex items-center justify-center group cursor-pointer overflow-hidden"
              >
                <div className="absolute inset-0 bg-primary/80 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
                    <Play className="text-primary" size={24} />
                  </div>
                </div>
                <div className="text-center p-4">
                  <p className="font-medium text-text-primary text-sm">{video.title}</p>
                  <p className="text-xs text-text-secondary mt-1">{video.duration}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
