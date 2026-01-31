import React from 'react';
import { TrendingUp, TrendingDown, Activity, Shield } from 'lucide-react';
import {
  Card,
  CardContent,
  CircularProgress,
  DoshaBarChart,
  RiskBadge,
  ProgressBar,
} from '../../components/ui';

// Placeholder data
const mockPredictions = {
  overallHealthScore: 78,
  doshaBalance: { vata: 45, pitta: 30, kapha: 25 },
  predictions: [
    { condition: 'Arthritis', riskLevel: 'high' as const, oneYearRisk: 35, fiveYearRisk: 65, preventionTips: ['Daily joint mobility exercises', 'Anti-inflammatory diet', 'Regular Abhyanga with medicated oils', 'Consider Panchakarma therapy'] },
    { condition: 'Digestive Disorders', riskLevel: 'moderate' as const, oneYearRisk: 25, fiveYearRisk: 45, preventionTips: ['Eat at regular times', 'Avoid incompatible food combinations', 'Include digestive spices', 'Practice mindful eating'] },
    { condition: 'Anxiety/Stress', riskLevel: 'moderate' as const, oneYearRisk: 30, fiveYearRisk: 50, preventionTips: ['Daily meditation practice', 'Regular pranayama', 'Ashwagandha supplementation', 'Maintain sleep routine'] },
    { condition: 'Diabetes', riskLevel: 'low' as const, oneYearRisk: 10, fiveYearRisk: 25, preventionTips: ['Maintain healthy weight', 'Regular physical activity', 'Limit processed foods', 'Include bitter foods in diet'] },
  ],
  doshaTrajectory: [
    { timeframe: 'Current', projectedBalance: { vata: 45, pitta: 30, kapha: 25 } },
    { timeframe: '3 months', projectedBalance: { vata: 40, pitta: 32, kapha: 28 } },
    { timeframe: '6 months', projectedBalance: { vata: 35, pitta: 33, kapha: 32 } },
  ],
  preventionPlan: {
    immediate: [
      'Start daily Abhyanga (self-massage) with warm sesame oil',
      'Follow Vata-pacifying diet strictly',
      'Establish regular sleep routine by 10 PM',
    ],
    shortTerm: [
      'Complete Panchakarma consultation',
      'Begin recommended herbal protocol',
      'Join yoga classes focusing on joint health',
      'Reduce work-related stress triggers',
    ],
    longTerm: [
      'Maintain regular exercise routine',
      'Follow seasonal routines (Ritucharya)',
      'Annual Panchakarma for maintenance',
      'Regular health check-ups every 6 months',
    ],
  },
};

export function HealthPredictions() {
  return (
    <div className="animate-fade-in">
      <div className="mb-6">
        <h1 className="font-heading text-2xl font-bold text-text-primary">Health Predictions</h1>
        <p className="text-text-secondary">AI-powered health risk assessment based on your profile</p>
      </div>

      {/* Top Row - Score and Dosha */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {/* Overall Health Score */}
        <Card>
          <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
            Overall Health Score
          </h2>
          <CardContent className="flex flex-col items-center">
            <CircularProgress
              value={mockPredictions.overallHealthScore}
              size={160}
              strokeWidth={14}
              color={mockPredictions.overallHealthScore >= 70 ? 'success' : mockPredictions.overallHealthScore >= 50 ? 'warning' : 'error'}
            />
            <p className="mt-4 text-center text-text-secondary">
              Your health score is{' '}
              <span className="font-medium text-success">
                {mockPredictions.overallHealthScore >= 70 ? 'Good' : mockPredictions.overallHealthScore >= 50 ? 'Fair' : 'Needs Attention'}
              </span>
            </p>
            <div className="flex items-center gap-2 mt-2 text-sm text-success">
              <TrendingUp size={16} />
              <span>+5 from last month</span>
            </div>
          </CardContent>
        </Card>

        {/* Dosha Balance */}
        <Card>
          <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
            Current Dosha Balance
          </h2>
          <CardContent>
            <DoshaBarChart breakdown={mockPredictions.doshaBalance} />
            <div className="mt-4 p-3 bg-warning/5 rounded-lg border border-warning/10">
              <p className="text-sm text-text-secondary">
                <span className="font-medium text-warning">Vata Elevation Detected:</span>{' '}
                Focus on grounding practices and warm, nourishing foods.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Risk Cards */}
      <Card className="mb-6">
        <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
          Health Risk Assessment
        </h2>
        <CardContent>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {mockPredictions.predictions.map((prediction) => (
              <div
                key={prediction.condition}
                className={`p-4 rounded-xl border-2 ${
                  prediction.riskLevel === 'high'
                    ? 'border-error/30 bg-error/5'
                    : prediction.riskLevel === 'moderate'
                    ? 'border-warning/30 bg-warning/5'
                    : 'border-success/30 bg-success/5'
                }`}
              >
                <RiskBadge risk={prediction.riskLevel} className="mb-3" />
                <h3 className="font-medium text-text-primary mb-2">{prediction.condition}</h3>
                <div className="space-y-2">
                  <div>
                    <p className="text-xs text-text-secondary">1-Year Risk</p>
                    <p className="text-xl font-bold text-text-primary">{prediction.oneYearRisk}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary">5-Year Risk</p>
                    <ProgressBar
                      value={prediction.fiveYearRisk}
                      size="sm"
                      color={prediction.riskLevel === 'high' ? 'error' : prediction.riskLevel === 'moderate' ? 'warning' : 'success'}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Dosha Trajectory */}
      <Card className="mb-6">
        <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
          Projected Dosha Trajectory
        </h2>
        <CardContent>
          <p className="text-text-secondary mb-4">
            Based on your current treatment plan, here's how your dosha balance is expected to improve:
          </p>
          <div className="grid md:grid-cols-3 gap-6">
            {mockPredictions.doshaTrajectory.map((point, index) => (
              <div key={index} className="text-center">
                <p className="font-medium text-text-primary mb-3">{point.timeframe}</p>
                <DoshaBarChart breakdown={point.projectedBalance} />
              </div>
            ))}
          </div>
          <div className="mt-4 flex items-center justify-center gap-2 text-success">
            <TrendingDown size={18} />
            <span className="text-sm font-medium">Vata expected to normalize by 6 months</span>
          </div>
        </CardContent>
      </Card>

      {/* Prevention Plan */}
      <Card>
        <div className="flex items-center gap-2 mb-4">
          <Shield className="text-primary" size={24} />
          <h2 className="font-heading text-lg font-semibold text-text-primary">
            Personalized Prevention Plan
          </h2>
        </div>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            {/* Immediate */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 bg-error/10 rounded-full flex items-center justify-center">
                  <Activity className="text-error" size={16} />
                </div>
                <h3 className="font-medium text-text-primary">This Week</h3>
              </div>
              <ul className="space-y-2">
                {mockPredictions.preventionPlan.immediate.map((action, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-text-secondary">
                    <span className="text-error font-bold">•</span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>

            {/* Short Term */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 bg-warning/10 rounded-full flex items-center justify-center">
                  <Activity className="text-warning" size={16} />
                </div>
                <h3 className="font-medium text-text-primary">1-3 Months</h3>
              </div>
              <ul className="space-y-2">
                {mockPredictions.preventionPlan.shortTerm.map((action, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-text-secondary">
                    <span className="text-warning font-bold">•</span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>

            {/* Long Term */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 bg-success/10 rounded-full flex items-center justify-center">
                  <Activity className="text-success" size={16} />
                </div>
                <h3 className="font-medium text-text-primary">Long Term</h3>
              </div>
              <ul className="space-y-2">
                {mockPredictions.preventionPlan.longTerm.map((action, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-text-secondary">
                    <span className="text-success font-bold">•</span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
