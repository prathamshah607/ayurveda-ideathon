import React, { useState } from 'react';
import { Search, AlertTriangle, Sparkles, Heart, Salad, Home } from 'lucide-react';
import {
  Card,
  CardContent,
  Button,
  TagInput,
  QuickSelectChips,
  Alert,
  RedFlagAlert,
  Badge,
} from '../../components/ui';

const commonSymptoms = [
  'Fatigue',
  'Headache',
  'Joint Pain',
  'Indigestion',
  'Bloating',
  'Constipation',
  'Insomnia',
  'Anxiety',
  'Skin Rash',
  'Cough',
  'Fever',
  'Back Pain',
  'Nausea',
  'Dizziness',
  'Muscle Aches',
];

// Placeholder results
const mockResults = {
  redFlags: [],
  possibleConditions: [
    {
      name: 'Vata Imbalance',
      explanation: 'Your symptoms suggest an excess of Vata dosha, which governs movement and nervous system functions.',
      likelihood: 'high' as const,
      whatThisMeans: 'Vata imbalance often manifests as anxiety, irregular digestion, joint discomfort, and sleep disturbances. It may be triggered by irregular routines, cold weather, or excessive stress.',
    },
    {
      name: 'Digestive Weakness (Mandagni)',
      explanation: 'Low digestive fire may be contributing to your symptoms of fatigue and bloating.',
      likelihood: 'moderate' as const,
      whatThisMeans: 'When Agni (digestive fire) is low, food is not properly digested, leading to toxin (Ama) accumulation. This can cause fatigue, heaviness, and various other symptoms.',
    },
    {
      name: 'Stress-Related Condition',
      explanation: 'Your symptom pattern may be influenced by elevated stress levels.',
      likelihood: 'moderate' as const,
      whatThisMeans: 'Chronic stress affects the mind-body connection, often manifesting as physical symptoms. Ayurveda views this as a disturbance in Prana Vata.',
    },
  ],
  selfCare: {
    dietary: [
      'Eat warm, freshly cooked meals',
      'Avoid cold, raw, and dry foods',
      'Include ghee and healthy oils',
      'Drink warm water throughout the day',
      'Favor sweet, sour, and salty tastes',
    ],
    lifestyle: [
      'Maintain regular sleep schedule (10 PM - 6 AM)',
      'Practice gentle yoga and stretching',
      'Daily self-massage with warm sesame oil',
      'Reduce screen time, especially before bed',
      'Take short walks after meals',
    ],
    homeRemedies: [
      'Ginger tea with honey after meals',
      'Warm milk with turmeric and nutmeg at bedtime',
      'Triphala powder before bed for digestion',
      'Nasya with sesame oil for stress relief',
    ],
  },
};

export function SymptomChecker() {
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [isChecking, setIsChecking] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [expandedCondition, setExpandedCondition] = useState<string | null>(null);

  const handleCheck = async () => {
    setIsChecking(true);
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setIsChecking(false);
    setShowResults(true);
  };

  const likelihoodColors = {
    low: 'success',
    moderate: 'warning',
    high: 'error',
  } as const;

  return (
    <div className="animate-fade-in max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="font-heading text-3xl font-bold text-text-primary mb-2">
          Symptom Checker
        </h1>
        <p className="text-text-secondary">
          Tell us how you're feeling and get personalized Ayurvedic insights
        </p>
      </div>

      {/* Input Section */}
      <Card className="mb-6">
        <CardContent className="space-y-6">
          <TagInput
            label="What symptoms are you experiencing?"
            placeholder="Type a symptom and press Enter..."
            value={symptoms}
            onChange={setSymptoms}
            suggestions={commonSymptoms}
          />

          <QuickSelectChips
            label="Quick Select Common Symptoms"
            options={commonSymptoms}
            selected={symptoms}
            onChange={setSymptoms}
          />

          <Button
            size="lg"
            className="w-full"
            onClick={handleCheck}
            isLoading={isChecking}
            disabled={symptoms.length === 0}
            leftIcon={<Search size={20} />}
          >
            Check Symptoms
          </Button>
        </CardContent>
      </Card>

      {/* Results Section */}
      {showResults && (
        <div className="space-y-6">
          {/* Disclaimer */}
          <Alert type="info" title="Important Notice">
            <p>
              This symptom checker is for informational purposes only and is not a substitute for 
              professional medical advice, diagnosis, or treatment. Always consult a qualified 
              healthcare provider with any questions about your health.
            </p>
          </Alert>

          {/* Red Flags */}
          {mockResults.redFlags.length > 0 && (
            <RedFlagAlert flags={mockResults.redFlags} />
          )}

          {/* Possible Conditions */}
          <Card>
            <h2 className="font-heading text-xl font-semibold text-text-primary mb-4">
              Possible Conditions
            </h2>
            <CardContent className="space-y-4">
              {mockResults.possibleConditions.map((condition) => (
                <div
                  key={condition.name}
                  className="p-4 rounded-lg border border-gray-200 hover:border-primary/30 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium text-text-primary">{condition.name}</h3>
                    <Badge variant={likelihoodColors[condition.likelihood]} size="sm">
                      {condition.likelihood === 'high' ? 'Likely' : condition.likelihood === 'moderate' ? 'Possible' : 'Less Likely'}
                    </Badge>
                  </div>
                  <p className="text-text-secondary text-sm mb-3">{condition.explanation}</p>
                  <button
                    onClick={() => setExpandedCondition(expandedCondition === condition.name ? null : condition.name)}
                    className="text-sm text-primary font-medium hover:underline"
                  >
                    {expandedCondition === condition.name ? 'Hide details' : 'What does this mean?'}
                  </button>
                  {expandedCondition === condition.name && (
                    <div className="mt-3 p-3 bg-primary/5 rounded-lg">
                      <p className="text-sm text-text-secondary">{condition.whatThisMeans}</p>
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Self-Care Recommendations */}
          <Card>
            <h2 className="font-heading text-xl font-semibold text-text-primary mb-4">
              Self-Care Recommendations
            </h2>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-6">
                {/* Dietary */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Salad size={20} className="text-success" />
                    <h3 className="font-medium text-text-primary">Dietary Tips</h3>
                  </div>
                  <ul className="space-y-2">
                    {mockResults.selfCare.dietary.map((tip, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-text-secondary">
                        <span className="text-success">•</span>
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Lifestyle */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Heart size={20} className="text-primary" />
                    <h3 className="font-medium text-text-primary">Lifestyle Changes</h3>
                  </div>
                  <ul className="space-y-2">
                    {mockResults.selfCare.lifestyle.map((tip, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-text-secondary">
                        <span className="text-primary">•</span>
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Home Remedies */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Home size={20} className="text-accent" />
                    <h3 className="font-medium text-text-primary">Home Remedies</h3>
                  </div>
                  <ul className="space-y-2">
                    {mockResults.selfCare.homeRemedies.map((remedy, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-text-secondary">
                        <span className="text-accent">•</span>
                        {remedy}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Button */}
          <div className="flex justify-center">
            <Button variant="outline" leftIcon={<Sparkles size={18} />}>
              Share with My Doctor
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
