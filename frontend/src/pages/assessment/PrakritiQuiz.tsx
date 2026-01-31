import React, { useState } from 'react';
import { ArrowLeft, ArrowRight, Check } from 'lucide-react';
import { Card, CardContent, Button, ProgressBar, DoshaBarChart } from '../../components/ui';
import { Link, useNavigate } from 'react-router-dom';

interface Question {
  id: number;
  category: string;
  question: string;
  options: { value: 'vata' | 'pitta' | 'kapha'; label: string }[];
}

const questions: Question[] = [
  {
    id: 1,
    category: 'Body Frame',
    question: 'How would you describe your body frame?',
    options: [
      { value: 'vata', label: 'Thin and light, difficulty gaining weight' },
      { value: 'pitta', label: 'Medium build, well-proportioned' },
      { value: 'kapha', label: 'Large and sturdy, gains weight easily' },
    ],
  },
  {
    id: 2,
    category: 'Skin',
    question: 'How would you describe your skin?',
    options: [
      { value: 'vata', label: 'Dry, rough, thin, cool' },
      { value: 'pitta', label: 'Warm, oily, prone to redness or rashes' },
      { value: 'kapha', label: 'Thick, oily, cool, smooth' },
    ],
  },
  {
    id: 3,
    category: 'Hair',
    question: 'How would you describe your hair?',
    options: [
      { value: 'vata', label: 'Dry, brittle, frizzy, dark' },
      { value: 'pitta', label: 'Fine, soft, early graying or balding' },
      { value: 'kapha', label: 'Thick, oily, lustrous, wavy' },
    ],
  },
  {
    id: 4,
    category: 'Appetite',
    question: 'How would you describe your appetite?',
    options: [
      { value: 'vata', label: 'Variable, sometimes strong, sometimes weak' },
      { value: 'pitta', label: 'Strong, intense, irritable if meals are skipped' },
      { value: 'kapha', label: 'Steady but slow, can skip meals easily' },
    ],
  },
  {
    id: 5,
    category: 'Digestion',
    question: 'How is your digestion generally?',
    options: [
      { value: 'vata', label: 'Irregular, tendency toward gas and bloating' },
      { value: 'pitta', label: 'Strong, can digest most foods, occasional acidity' },
      { value: 'kapha', label: 'Slow, heavy feeling after meals' },
    ],
  },
  {
    id: 6,
    category: 'Sleep',
    question: 'How would you describe your sleep pattern?',
    options: [
      { value: 'vata', label: 'Light, easily disturbed, tendency for insomnia' },
      { value: 'pitta', label: 'Moderate, wake up if too warm' },
      { value: 'kapha', label: 'Deep and long, difficulty waking up' },
    ],
  },
  {
    id: 7,
    category: 'Energy',
    question: 'How is your energy throughout the day?',
    options: [
      { value: 'vata', label: 'Comes in bursts, easily exhausted' },
      { value: 'pitta', label: 'Moderate to high, well-managed' },
      { value: 'kapha', label: 'Steady but slow to start, good stamina' },
    ],
  },
  {
    id: 8,
    category: 'Temperature',
    question: 'What is your temperature preference?',
    options: [
      { value: 'vata', label: 'Prefer warmth, easily feel cold' },
      { value: 'pitta', label: 'Prefer cool, easily overheat' },
      { value: 'kapha', label: 'Adaptable, dislike cold and damp' },
    ],
  },
  {
    id: 9,
    category: 'Mental Activity',
    question: 'How would you describe your mental activity?',
    options: [
      { value: 'vata', label: 'Quick, restless, creative, many ideas' },
      { value: 'pitta', label: 'Sharp, focused, analytical, ambitious' },
      { value: 'kapha', label: 'Calm, steady, methodical, good memory' },
    ],
  },
  {
    id: 10,
    category: 'Emotional Tendency',
    question: 'When stressed, you tend to feel:',
    options: [
      { value: 'vata', label: 'Anxious, worried, fearful' },
      { value: 'pitta', label: 'Irritable, frustrated, angry' },
      { value: 'kapha', label: 'Withdrawn, sad, attached' },
    ],
  },
  {
    id: 11,
    category: 'Speech',
    question: 'How would you describe your speech?',
    options: [
      { value: 'vata', label: 'Fast, talkative, sometimes scattered' },
      { value: 'pitta', label: 'Clear, sharp, convincing' },
      { value: 'kapha', label: 'Slow, deliberate, melodious' },
    ],
  },
  {
    id: 12,
    category: 'Learning Style',
    question: 'How do you learn new information?',
    options: [
      { value: 'vata', label: 'Quick to learn, quick to forget' },
      { value: 'pitta', label: 'Moderate pace, good comprehension' },
      { value: 'kapha', label: 'Slow to learn, excellent retention' },
    ],
  },
];

export function PrakritiQuiz() {
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<number, 'vata' | 'pitta' | 'kapha'>>({});
  const [showResults, setShowResults] = useState(false);

  const progress = ((currentQuestion + 1) / questions.length) * 100;

  const handleAnswer = (value: 'vata' | 'pitta' | 'kapha') => {
    setAnswers((prev) => ({ ...prev, [questions[currentQuestion].id]: value }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion((prev) => prev + 1);
    } else {
      setShowResults(true);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion((prev) => prev - 1);
    }
  };

  const calculateResults = () => {
    const counts = { vata: 0, pitta: 0, kapha: 0 };
    Object.values(answers).forEach((answer) => {
      counts[answer]++;
    });

    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    return {
      vata: Math.round((counts.vata / total) * 100),
      pitta: Math.round((counts.pitta / total) * 100),
      kapha: Math.round((counts.kapha / total) * 100),
    };
  };

  const getDominantDosha = (results: { vata: number; pitta: number; kapha: number }) => {
    const entries = Object.entries(results) as [string, number][];
    entries.sort((a, b) => b[1] - a[1]);

    if (entries[0][1] - entries[1][1] < 10) {
      return `${entries[0][0].charAt(0).toUpperCase() + entries[0][0].slice(1)}-${entries[1][0].charAt(0).toUpperCase() + entries[1][0].slice(1)}`;
    }
    return entries[0][0].charAt(0).toUpperCase() + entries[0][0].slice(1);
  };

  const getDoshaDescription = (dosha: string) => {
    const descriptions: Record<string, string> = {
      Vata: 'You are creative, quick-thinking, and enthusiastic. When balanced, you are full of joy and vitality. Focus on grounding practices, warm foods, and regular routines.',
      Pitta: 'You are intelligent, driven, and courageous. When balanced, you are a natural leader with sharp intellect. Focus on cooling practices, moderate exercise, and avoiding excessive heat.',
      Kapha: 'You are calm, loving, and stable. When balanced, you are the rock for others with great endurance. Focus on stimulating activities, light foods, and variety in routine.',
      'Vata-Pitta': 'You combine the creativity of Vata with the drive of Pitta. Focus on balancing warmth with cooling, maintaining routines while allowing flexibility.',
      'Vata-Kapha': 'You combine the creativity of Vata with the stability of Kapha. Focus on stimulating yet grounding practices, warm and light foods.',
      'Pitta-Kapha': 'You combine the intensity of Pitta with the endurance of Kapha. Focus on cooling and stimulating practices, avoiding heavy and hot foods.',
      'Pitta-Vata': 'You combine the drive of Pitta with the creativity of Vata. Focus on cooling and grounding practices, regular meals and rest.',
      'Kapha-Vata': 'You combine the stability of Kapha with the adaptability of Vata. Focus on warming and stimulating practices, regular exercise.',
      'Kapha-Pitta': 'You combine the endurance of Kapha with the intensity of Pitta. Focus on light, cooling foods and stimulating activities.',
    };
    return descriptions[dosha] || descriptions.Vata;
  };

  if (showResults) {
    const results = calculateResults();
    const dominantDosha = getDominantDosha(results);

    return (
      <div className="animate-fade-in max-w-2xl mx-auto">
        <Card className="text-center">
          <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Check className="text-primary" size={40} />
          </div>
          <h1 className="font-heading text-2xl font-bold text-text-primary mb-2">
            Your Prakriti Results
          </h1>
          <p className="text-text-secondary mb-6">
            Based on your answers, here is your constitutional analysis
          </p>

          <CardContent>
            {/* Dominant Dosha */}
            <div className="mb-8">
              <p className="text-sm text-text-secondary mb-1">Your Dominant Constitution</p>
              <p className="font-heading text-4xl font-bold text-primary">{dominantDosha}</p>
            </div>

            {/* Breakdown */}
            <div className="mb-8">
              <DoshaBarChart breakdown={results} />
            </div>

            {/* Description */}
            <div className="p-4 bg-primary/5 rounded-lg text-left mb-6">
              <h3 className="font-medium text-text-primary mb-2">What This Means</h3>
              <p className="text-sm text-text-secondary">{getDoshaDescription(dominantDosha)}</p>
            </div>

            {/* Recommendations */}
            <div className="grid md:grid-cols-3 gap-4 text-left mb-6">
              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="font-medium text-primary text-sm mb-1">🍽️ Diet</p>
                <p className="text-xs text-text-secondary">
                  {dominantDosha.includes('Vata')
                    ? 'Warm, moist, grounding foods'
                    : dominantDosha.includes('Pitta')
                    ? 'Cool, refreshing foods'
                    : 'Light, warm, stimulating foods'}
                </p>
              </div>
              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="font-medium text-primary text-sm mb-1">🧘 Exercise</p>
                <p className="text-xs text-text-secondary">
                  {dominantDosha.includes('Vata')
                    ? 'Gentle yoga, walking, swimming'
                    : dominantDosha.includes('Pitta')
                    ? 'Moderate intensity, cooling'
                    : 'Vigorous, stimulating activities'}
                </p>
              </div>
              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="font-medium text-primary text-sm mb-1">💤 Lifestyle</p>
                <p className="text-xs text-text-secondary">
                  {dominantDosha.includes('Vata')
                    ? 'Regular routine, early sleep'
                    : dominantDosha.includes('Pitta')
                    ? 'Avoid overwork, stay cool'
                    : 'Wake early, stay active'}
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/patient/profile">
                <Button>Save to Profile</Button>
              </Link>
              <Link to="/patient/dashboard">
                <Button variant="outline">Go to Dashboard</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentQ = questions[currentQuestion];
  const currentAnswer = answers[currentQ.id];

  return (
    <div className="animate-fade-in max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="font-heading text-3xl font-bold text-text-primary mb-2">
          Prakriti Assessment
        </h1>
        <p className="text-text-secondary">
          Discover your unique mind-body constitution
        </p>
      </div>

      {/* Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-sm text-text-secondary mb-2">
          <span>Question {currentQuestion + 1} of {questions.length}</span>
          <span>{currentQ.category}</span>
        </div>
        <ProgressBar value={progress} color="primary" size="sm" />
      </div>

      {/* Question Card */}
      <Card className="mb-6">
        <CardContent>
          <h2 className="font-heading text-xl font-semibold text-text-primary mb-6">
            {currentQ.question}
          </h2>

          <div className="space-y-3">
            {currentQ.options.map((option) => (
              <button
                key={option.value}
                onClick={() => handleAnswer(option.value)}
                className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
                  currentAnswer === option.value
                    ? 'border-primary bg-primary/5'
                    : 'border-gray-200 hover:border-primary/30'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                      currentAnswer === option.value
                        ? 'border-primary bg-primary'
                        : 'border-gray-300'
                    }`}
                  >
                    {currentAnswer === option.value && (
                      <Check size={12} className="text-white" />
                    )}
                  </div>
                  <span className="text-text-primary">{option.label}</span>
                </div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={handlePrevious}
          disabled={currentQuestion === 0}
          leftIcon={<ArrowLeft size={18} />}
        >
          Previous
        </Button>
        <Button
          onClick={handleNext}
          disabled={!currentAnswer}
          rightIcon={<ArrowRight size={18} />}
        >
          {currentQuestion === questions.length - 1 ? 'See Results' : 'Next'}
        </Button>
      </div>

      {/* Skip Option */}
      <p className="text-center text-sm text-text-secondary mt-6">
        <Link to="/patient/dashboard" className="hover:underline">
          Skip for now →
        </Link>
      </p>
    </div>
  );
}
