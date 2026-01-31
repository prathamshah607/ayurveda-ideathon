import React, { useState } from 'react';
import { Activity, AlertCircle, Clock, TrendingUp } from 'lucide-react';
import {
  Card,
  CardContent,
  Button,
  Select,
  Input,
  Badge,
  Alert,
} from '../../components/ui';
import type { DiseaseStage } from '../../api/types';
import { DISEASE_STAGE_NAMES } from '../../api/types';

const diseases = [
  { value: 'amavata', label: 'Amavata (Rheumatoid conditions)' },
  { value: 'prameha', label: 'Prameha (Diabetes)' },
  { value: 'raktapitta', label: 'Raktapitta (Bleeding disorders)' },
  { value: 'kushtha', label: 'Kushtha (Skin diseases)' },
  { value: 'vatarakta', label: 'Vatarakta (Gout)' },
  { value: 'sandhigata', label: 'Sandhigata Vata (Osteoarthritis)' },
];

const mockProgression = {
  disease: 'Amavata',
  currentStage: 2 as DiseaseStage,
  projectedProgression: [
    {
      stage: 2 as DiseaseStage,
      name: 'Prakopa',
      estimatedDays: 0,
      symptoms: ['Aggravated Vata and Kapha', 'Initial joint discomfort', 'Mild morning stiffness'],
      interventions: ['Langhana (fasting)', 'Swedana (fomentation)', 'Deepana herbs'],
    },
    {
      stage: 3 as DiseaseStage,
      name: 'Prasara',
      estimatedDays: 45,
      symptoms: ['Spreading inflammation', 'Multiple joint involvement', 'Digestive disturbances'],
      interventions: ['Virechana therapy', 'Ama pachana', 'Anti-inflammatory herbs'],
    },
    {
      stage: 4 as DiseaseStage,
      name: 'Sthana Samshraya',
      estimatedDays: 90,
      symptoms: ['Localized joint damage', 'Swelling and pain', 'Movement restriction'],
      interventions: ['Basti therapy', 'Local treatments', 'Rasayana therapy'],
    },
    {
      stage: 5 as DiseaseStage,
      name: 'Vyakti',
      estimatedDays: 180,
      symptoms: ['Full manifestation', 'Joint deformity begins', 'Systemic symptoms'],
      interventions: ['Intensive Panchakarma', 'Long-term management', 'Disability prevention'],
    },
  ],
  urgencyLevel: 'moderate' as const,
  interventionRecommendations: [
    'Immediate dietary modifications to reduce Ama',
    'Start Deepana-Pachana protocol within 1 week',
    'Consider early Panchakarma intervention',
    'Regular follow-up every 2 weeks',
  ],
};

export function ProgressionPage() {
  const [selectedDisease, setSelectedDisease] = useState('');
  const [currentStage, setCurrentStage] = useState<DiseaseStage>(1);
  const [duration, setDuration] = useState('');
  const [showResults, setShowResults] = useState(false);

  const handleModelProgression = () => {
    setShowResults(true);
  };

  const stageColors = {
    1: 'bg-green-500',
    2: 'bg-yellow-500',
    3: 'bg-orange-500',
    4: 'bg-red-400',
    5: 'bg-red-500',
    6: 'bg-red-600',
  };

  return (
    <div className="animate-fade-in">
      <div className="mb-6">
        <h1 className="font-heading text-2xl font-bold text-text-primary">Disease Progression</h1>
        <p className="text-text-secondary">Model disease progression using Shatkriyakala framework</p>
      </div>

      {/* Input Section */}
      <Card className="mb-6">
        <CardContent className="space-y-6">
          <div className="grid md:grid-cols-3 gap-6">
            <Select
              label="Select Disease"
              options={diseases}
              value={selectedDisease}
              onChange={(e) => setSelectedDisease(e.target.value)}
              placeholder="Choose a disease..."
            />
            <div>
              <label className="block text-sm font-medium text-text-primary mb-1.5">
                Current Stage
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="range"
                  min="1"
                  max="6"
                  value={currentStage}
                  onChange={(e) => setCurrentStage(parseInt(e.target.value) as DiseaseStage)}
                  className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <span className="text-sm font-medium text-primary w-20">
                  Stage {currentStage}
                </span>
              </div>
              <p className="text-xs text-text-secondary mt-1">
                {DISEASE_STAGE_NAMES[currentStage]}
              </p>
            </div>
            <Input
              label="Duration (days)"
              type="number"
              placeholder="Days since onset"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
            />
          </div>

          <Button
            onClick={handleModelProgression}
            disabled={!selectedDisease}
            leftIcon={<TrendingUp size={18} />}
          >
            Model Progression
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {showResults && (
        <div className="space-y-6">
          {/* Urgency Alert */}
          <Alert
            type={mockProgression.urgencyLevel === 'high' ? 'error' : mockProgression.urgencyLevel === 'moderate' ? 'warning' : 'info'}
            title={`Urgency Level: ${mockProgression.urgencyLevel.charAt(0).toUpperCase() + mockProgression.urgencyLevel.slice(1)}`}
          >
            Early intervention is recommended to prevent progression to later stages.
          </Alert>

          {/* Visual Timeline */}
          <Card>
            <h2 className="font-heading text-xl font-semibold text-text-primary mb-6">
              Progression Timeline (Shatkriyakala)
            </h2>
            <CardContent>
              <div className="relative">
                {/* Timeline line */}
                <div className="absolute top-6 left-0 right-0 h-1 bg-gray-200 rounded">
                  <div 
                    className="h-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded"
                    style={{ width: `${((currentStage - 1) / 5) * 100}%` }}
                  />
                </div>

                {/* Stage markers */}
                <div className="relative flex justify-between">
                  {([1, 2, 3, 4, 5, 6] as DiseaseStage[]).map((stage) => {
                    const isCurrent = stage === currentStage;
                    const isPast = stage < currentStage;
                    const progressionData = mockProgression.projectedProgression.find(p => p.stage === stage);
                    
                    return (
                      <div key={stage} className="flex flex-col items-center" style={{ width: '16%' }}>
                        <div
                          className={`
                            w-12 h-12 rounded-full flex items-center justify-center text-white font-bold
                            ${isCurrent ? stageColors[stage] + ' ring-4 ring-offset-2 ring-primary/30' : ''}
                            ${isPast ? stageColors[stage] : ''}
                            ${!isPast && !isCurrent ? 'bg-gray-300' : ''}
                            transition-all duration-300
                          `}
                        >
                          {stage}
                        </div>
                        <div className="mt-3 text-center">
                          <p className={`text-sm font-medium ${isCurrent ? 'text-primary' : 'text-text-primary'}`}>
                            {DISEASE_STAGE_NAMES[stage]}
                          </p>
                          {progressionData && stage >= currentStage && (
                            <p className="text-xs text-text-secondary mt-1">
                              {progressionData.estimatedDays === 0 ? '(Current)' : `+${progressionData.estimatedDays} days`}
                            </p>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Stage Details */}
          <div className="grid md:grid-cols-2 gap-6">
            {mockProgression.projectedProgression.map((stage) => (
              <Card 
                key={stage.stage}
                className={stage.stage === currentStage ? 'ring-2 ring-primary' : ''}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full ${stageColors[stage.stage]} flex items-center justify-center text-white font-bold text-sm`}>
                      {stage.stage}
                    </div>
                    <div>
                      <h3 className="font-medium text-text-primary">{stage.name}</h3>
                      {stage.stage === currentStage && (
                        <Badge variant="primary" size="sm">Current Stage</Badge>
                      )}
                    </div>
                  </div>
                  {stage.estimatedDays > 0 && (
                    <div className="flex items-center gap-1 text-text-secondary text-sm">
                      <Clock size={14} />
                      +{stage.estimatedDays} days
                    </div>
                  )}
                </div>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-text-primary mb-2">Expected Symptoms</h4>
                      <ul className="list-disc list-inside text-text-secondary text-sm space-y-1">
                        {stage.symptoms.map((symptom, i) => (
                          <li key={i}>{symptom}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-text-primary mb-2">Recommended Interventions</h4>
                      <ul className="list-disc list-inside text-text-secondary text-sm space-y-1">
                        {stage.interventions.map((intervention, i) => (
                          <li key={i}>{intervention}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Intervention Recommendations */}
          <Card>
            <h2 className="font-heading text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
              <Activity className="text-primary" size={24} />
              Intervention Recommendations
            </h2>
            <CardContent>
              <ul className="space-y-3">
                {mockProgression.interventionRecommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center flex-shrink-0 text-white text-sm font-medium">
                      {index + 1}
                    </div>
                    <span className="text-text-secondary">{rec}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
