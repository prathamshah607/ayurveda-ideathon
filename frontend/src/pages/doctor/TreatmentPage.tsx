import React, { useState } from 'react';
import { FileText, Download, Printer, Send, Sparkles } from 'lucide-react';
import {
  Card,
  CardContent,
  Button,
  Select,
  Input,
  Accordion,
  AccordionItem,
  Badge,
} from '../../components/ui';

// Placeholder treatment plan data
const mockTreatmentPlan = {
  phases: [
    {
      name: 'Phase 1: Nidana Parivarjana',
      duration: 'Days 1-7',
      objectives: [
        'Remove causative factors',
        'Reduce Vata aggravating diet and lifestyle',
        'Establish baseline health metrics',
      ],
      dietaryChanges: [
        'Avoid cold, dry, and raw foods',
        'Include warm, moist, and nourishing foods',
        'Reduce caffeine and stimulants',
        'Increase ghee and healthy oils',
      ],
      lifestyleModifications: [
        'Regular sleep schedule (10 PM to 6 AM)',
        'Gentle yoga and stretching',
        'Avoid excessive travel and stress',
        'Daily self-massage with warm sesame oil (Abhyanga)',
      ],
    },
    {
      name: 'Phase 2: Deepana-Pachana',
      duration: 'Days 8-21',
      objectives: [
        'Kindle digestive fire (Agni)',
        'Clear accumulated toxins (Ama)',
        'Prepare body for deeper cleansing',
      ],
      dietaryChanges: [
        'Light, easily digestible meals',
        'Include digestive spices: ginger, cumin, coriander',
        'Warm water with lemon in morning',
        'Avoid heavy, fried foods',
      ],
      lifestyleModifications: [
        'Eat only when hungry',
        'Avoid snacking between meals',
        'Light exercise: walking 20-30 minutes daily',
        'Practice pranayama: Anulom Vilom',
      ],
    },
    {
      name: 'Phase 3: Shodhana',
      duration: 'Days 22-35',
      objectives: [
        'Purification therapy as appropriate',
        'Remove deep-seated doshas',
        'Restore doshic balance',
      ],
      dietaryChanges: [
        'Follow specific diet as per Panchakarma protocol',
        'Light khichdi with ghee',
        'Plenty of warm water',
      ],
      lifestyleModifications: [
        'Complete rest during therapy',
        'Avoid exposure to cold and wind',
        'Limited physical activity',
        'Mental rest and meditation',
      ],
    },
    {
      name: 'Phase 4: Shamana',
      duration: 'Ongoing (4-8 weeks)',
      objectives: [
        'Pacify remaining doshic imbalance',
        'Strengthen affected tissues (Dhatus)',
        'Restore normal function',
      ],
      dietaryChanges: [
        'Vata-pacifying diet',
        'Regular meal times',
        'Warm, cooked foods preferred',
      ],
      lifestyleModifications: [
        'Gradual return to normal activities',
        'Regular yoga practice',
        'Stress management techniques',
        'Adequate sleep',
      ],
    },
    {
      name: 'Phase 5: Rasayana',
      duration: 'Maintenance',
      objectives: [
        'Rejuvenation and rebuilding',
        'Prevent recurrence',
        'Optimize long-term health',
      ],
      dietaryChanges: [
        'Balanced diet according to Prakriti',
        'Include rejuvenating foods: milk, ghee, almonds',
        'Seasonal dietary adjustments (Ritucharya)',
      ],
      lifestyleModifications: [
        'Maintain daily routine (Dinacharya)',
        'Seasonal routines (Ritucharya)',
        'Regular exercise appropriate for constitution',
        'Periodic panchakarma as maintenance',
      ],
    },
  ],
  formulations: [
    { name: 'Yogaraja Guggulu', dosage: '2 tablets', timing: 'After meals', duration: '3 months', anupana: 'Warm water' },
    { name: 'Ashwagandha Churna', dosage: '3g', timing: 'Before bed', duration: '3 months', anupana: 'Warm milk' },
    { name: 'Dashamoola Kashayam', dosage: '15ml', timing: 'Morning empty stomach', duration: '1 month', anupana: 'Equal water' },
    { name: 'Mahanarayan Tailam', dosage: 'External', timing: 'Evening', duration: 'Ongoing', anupana: 'For local application' },
  ],
  pathya: [
    'Warm, freshly cooked meals',
    'Regular meal timings',
    'Adequate rest and sleep',
    'Gentle exercise like yoga',
    'Stress management',
    'Warm water intake',
    'Oil massage (Abhyanga)',
  ],
  apathya: [
    'Cold, raw, dry foods',
    'Irregular meals and fasting',
    'Excessive physical exertion',
    'Late nights and irregular sleep',
    'Suppression of natural urges',
    'Cold water and refrigerated items',
    'Excessive travel',
  ],
};

export function TreatmentPage() {
  const [selectedPatient, setSelectedPatient] = useState('');
  const [diagnosis, setDiagnosis] = useState('');
  const [showPlan, setShowPlan] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGeneratePlan = async () => {
    setIsGenerating(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsGenerating(false);
    setShowPlan(true);
  };

  return (
    <div className="animate-fade-in">
      <div className="mb-6">
        <h1 className="font-heading text-2xl font-bold text-text-primary">Treatment Plans</h1>
        <p className="text-text-secondary">Generate comprehensive Ayurvedic treatment protocols</p>
      </div>

      {/* Input Section */}
      <Card className="mb-6">
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <Select
              label="Select Patient"
              options={[
                { value: 'p1', label: 'Rajesh Kumar (ID: P001)' },
                { value: 'p2', label: 'Priya Sharma (ID: P002)' },
                { value: 'p3', label: 'Amit Patel (ID: P003)' },
              ]}
              value={selectedPatient}
              onChange={(e) => setSelectedPatient(e.target.value)}
              placeholder="Choose a patient..."
            />
            <Input
              label="Diagnosis"
              placeholder="Enter or select diagnosis..."
              value={diagnosis}
              onChange={(e) => setDiagnosis(e.target.value)}
            />
          </div>

          {selectedPatient && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-text-primary mb-2">Patient Summary</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-text-secondary">Age:</span>
                  <span className="ml-2 font-medium">45 years</span>
                </div>
                <div>
                  <span className="text-text-secondary">Gender:</span>
                  <span className="ml-2 font-medium">Male</span>
                </div>
                <div>
                  <span className="text-text-secondary">Prakriti:</span>
                  <span className="ml-2 font-medium">Vata-Pitta</span>
                </div>
                <div>
                  <span className="text-text-secondary">Vikriti:</span>
                  <span className="ml-2 font-medium">Vata ↑</span>
                </div>
              </div>
            </div>
          )}

          <Button
            onClick={handleGeneratePlan}
            isLoading={isGenerating}
            disabled={!selectedPatient || !diagnosis}
            leftIcon={<Sparkles size={18} />}
          >
            Generate Treatment Plan
          </Button>
        </CardContent>
      </Card>

      {/* Treatment Plan Display */}
      {showPlan && (
        <div className="space-y-6">
          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button variant="outline" leftIcon={<Download size={18} />}>
              Export PDF
            </Button>
            <Button variant="outline" leftIcon={<Printer size={18} />}>
              Print
            </Button>
            <Button variant="outline" leftIcon={<Send size={18} />}>
              Send to Patient
            </Button>
          </div>

          {/* Treatment Phases */}
          <Card>
            <h2 className="font-heading text-xl font-semibold text-text-primary mb-4">
              Treatment Protocol
            </h2>
            <CardContent>
              <Accordion>
                {mockTreatmentPlan.phases.map((phase, index) => (
                  <AccordionItem
                    key={index}
                    title={phase.name}
                    badge={<Badge variant="primary" size="sm">{phase.duration}</Badge>}
                    defaultOpen={index === 0}
                  >
                    <div className="space-y-4 pl-2">
                      <div>
                        <h4 className="font-medium text-text-primary mb-2">Objectives</h4>
                        <ul className="list-disc list-inside text-text-secondary space-y-1">
                          {phase.objectives.map((obj, i) => (
                            <li key={i}>{obj}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium text-text-primary mb-2">Dietary Changes</h4>
                        <ul className="list-disc list-inside text-text-secondary space-y-1">
                          {phase.dietaryChanges.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium text-text-primary mb-2">Lifestyle Modifications</h4>
                        <ul className="list-disc list-inside text-text-secondary space-y-1">
                          {phase.lifestyleModifications.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </AccordionItem>
                ))}
              </Accordion>
            </CardContent>
          </Card>

          {/* Formulations Table */}
          <Card>
            <h2 className="font-heading text-xl font-semibold text-text-primary mb-4">
              Formulations & Medications
            </h2>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-medium text-text-primary">Name</th>
                      <th className="text-left py-3 px-4 font-medium text-text-primary">Dosage</th>
                      <th className="text-left py-3 px-4 font-medium text-text-primary">Timing</th>
                      <th className="text-left py-3 px-4 font-medium text-text-primary">Duration</th>
                      <th className="text-left py-3 px-4 font-medium text-text-primary">Anupana</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockTreatmentPlan.formulations.map((med, index) => (
                      <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 font-medium text-primary">{med.name}</td>
                        <td className="py-3 px-4 text-text-secondary">{med.dosage}</td>
                        <td className="py-3 px-4 text-text-secondary">{med.timing}</td>
                        <td className="py-3 px-4 text-text-secondary">{med.duration}</td>
                        <td className="py-3 px-4 text-text-secondary">{med.anupana}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Pathya / Apathya */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <h2 className="font-heading text-lg font-semibold text-success mb-4 flex items-center gap-2">
                ✓ Pathya (Do's)
              </h2>
              <CardContent>
                <ul className="space-y-2">
                  {mockTreatmentPlan.pathya.map((item, index) => (
                    <li key={index} className="flex items-start gap-2 text-text-secondary">
                      <span className="text-success mt-1">•</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
            <Card>
              <h2 className="font-heading text-lg font-semibold text-error mb-4 flex items-center gap-2">
                ✗ Apathya (Don'ts)
              </h2>
              <CardContent>
                <ul className="space-y-2">
                  {mockTreatmentPlan.apathya.map((item, index) => (
                    <li key={index} className="flex items-start gap-2 text-text-secondary">
                      <span className="text-error mt-1">•</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
