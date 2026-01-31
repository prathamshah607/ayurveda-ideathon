import React, { useState } from 'react';
import { AlertTriangle, Pill, Stethoscope, MessageSquare, Search } from 'lucide-react';
import {
  Card,
  CardContent,
  Button,
  Tabs,
  TabPanel,
  TagInput,
  Select,
  Textarea,
  Input,
  SeverityBadge,
  Alert,
} from '../../components/ui';

// Placeholder data
const mockInteractions = [
  { drug1: 'Ashwagandha', drug2: 'Thyroid medication', severity: 'major' as const, description: 'Ashwagandha may increase thyroid hormone levels, potentially causing hyperthyroidism symptoms when combined with thyroid medications.', recommendation: 'Monitor thyroid levels closely. Consider adjusting thyroid medication dose.' },
  { drug1: 'Triphala', drug2: 'Metformin', severity: 'moderate' as const, description: 'Triphala may enhance the glucose-lowering effect of Metformin, potentially causing hypoglycemia.', recommendation: 'Monitor blood glucose levels. May need to reduce Metformin dose.' },
  { drug1: 'Guggulu', drug2: 'Warfarin', severity: 'critical' as const, description: 'Guggulu may increase the anticoagulant effect of Warfarin, significantly increasing bleeding risk.', recommendation: 'Avoid combination or monitor INR frequently. Consider alternative treatments.' },
];

const mockContraindications = [
  { treatment: 'Panchakarma Vamana', condition: 'Pregnancy', severity: 'absolute' as const, explanation: 'Vamana (therapeutic vomiting) is contraindicated during pregnancy due to risk of miscarriage.', alternatives: ['Gentle Abhyanga', 'Dietary modifications', 'Mild herbal supplements'] },
  { treatment: 'Virechana', condition: 'Ulcerative Colitis', severity: 'relative' as const, explanation: 'Strong purgation may exacerbate inflammatory bowel conditions.', alternatives: ['Mild Virechana with supervision', 'Basti therapy instead', 'Shamana therapy'] },
];

const commonHerbs = [
  'Ashwagandha',
  'Triphala',
  'Guggulu',
  'Brahmi',
  'Shatavari',
  'Trikatu',
  'Guduchi',
  'Amalaki',
  'Haritaki',
  'Arjuna',
];

const treatments = [
  { value: 'vamana', label: 'Panchakarma - Vamana' },
  { value: 'virechana', label: 'Panchakarma - Virechana' },
  { value: 'basti', label: 'Panchakarma - Basti' },
  { value: 'nasya', label: 'Panchakarma - Nasya' },
  { value: 'raktamokshana', label: 'Raktamokshana' },
  { value: 'shirodhara', label: 'Shirodhara' },
];

export function DecisionSupportPage() {
  const [activeTab, setActiveTab] = useState('interactions');
  
  // Interactions state
  const [selectedMedications, setSelectedMedications] = useState<string[]>([]);
  const [showInteractionResults, setShowInteractionResults] = useState(false);
  
  // Contraindications state
  const [selectedTreatment, setSelectedTreatment] = useState('');
  const [patientConditions, setPatientConditions] = useState<string[]>([]);
  const [showContraResults, setShowContraResults] = useState(false);
  
  // Clinical scenario state
  const [clinicalScenario, setClinicalScenario] = useState('');
  const [showScenarioResults, setShowScenarioResults] = useState(false);

  return (
    <div className="animate-fade-in">
      <div className="mb-6">
        <h1 className="font-heading text-2xl font-bold text-text-primary">Decision Support</h1>
        <p className="text-text-secondary">AI-powered clinical decision assistance for safe prescribing</p>
      </div>

      <Card>
        <Tabs
          tabs={[
            { id: 'interactions', label: 'Drug Interactions', icon: <Pill size={18} /> },
            { id: 'contraindications', label: 'Contraindications', icon: <AlertTriangle size={18} /> },
            { id: 'scenario', label: 'Clinical Scenario', icon: <MessageSquare size={18} /> },
          ]}
          activeTab={activeTab}
          onChange={setActiveTab}
          className="mb-6"
        />

        {/* Drug Interactions Tab */}
        <TabPanel isActive={activeTab === 'interactions'}>
          <CardContent className="space-y-6">
            <div className="max-w-2xl">
              <TagInput
                label="Select Herbs & Medicines"
                placeholder="Type or select medications..."
                value={selectedMedications}
                onChange={setSelectedMedications}
                suggestions={commonHerbs}
              />
              <div className="mt-4">
                <Button
                  onClick={() => setShowInteractionResults(true)}
                  disabled={selectedMedications.length < 2}
                  leftIcon={<Search size={18} />}
                >
                  Check Interactions
                </Button>
              </div>
            </div>

            {showInteractionResults && (
              <div className="mt-6">
                <h3 className="font-medium text-text-primary mb-4">Interaction Results</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200 bg-gray-50">
                        <th className="text-left py-3 px-4 font-medium text-text-primary">Drug 1</th>
                        <th className="text-left py-3 px-4 font-medium text-text-primary">Drug 2</th>
                        <th className="text-left py-3 px-4 font-medium text-text-primary">Severity</th>
                        <th className="text-left py-3 px-4 font-medium text-text-primary">Description</th>
                        <th className="text-left py-3 px-4 font-medium text-text-primary">Recommendation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mockInteractions.map((interaction, index) => (
                        <tr key={index} className="border-b border-gray-100">
                          <td className="py-3 px-4 font-medium">{interaction.drug1}</td>
                          <td className="py-3 px-4 font-medium">{interaction.drug2}</td>
                          <td className="py-3 px-4">
                            <SeverityBadge severity={interaction.severity} />
                          </td>
                          <td className="py-3 px-4 text-text-secondary text-sm max-w-xs">{interaction.description}</td>
                          <td className="py-3 px-4 text-text-secondary text-sm max-w-xs">{interaction.recommendation}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </CardContent>
        </TabPanel>

        {/* Contraindications Tab */}
        <TabPanel isActive={activeTab === 'contraindications'}>
          <CardContent className="space-y-6">
            <div className="max-w-2xl space-y-4">
              <Select
                label="Treatment / Procedure"
                options={treatments}
                value={selectedTreatment}
                onChange={(e) => setSelectedTreatment(e.target.value)}
                placeholder="Select treatment..."
              />
              <TagInput
                label="Patient Conditions"
                placeholder="Add patient conditions..."
                value={patientConditions}
                onChange={setPatientConditions}
                suggestions={['Pregnancy', 'Diabetes', 'Hypertension', 'Heart Disease', 'Ulcerative Colitis', 'Epilepsy']}
              />
              <Button
                onClick={() => setShowContraResults(true)}
                disabled={!selectedTreatment || patientConditions.length === 0}
                leftIcon={<Search size={18} />}
              >
                Check Contraindications
              </Button>
            </div>

            {showContraResults && (
              <div className="mt-6 space-y-4">
                <h3 className="font-medium text-text-primary">Contraindication Results</h3>
                {mockContraindications.map((contra, index) => (
                  <Card key={index} className={contra.severity === 'absolute' ? 'border-error/30 bg-error/5' : 'border-warning/30 bg-warning/5'}>
                    <CardContent>
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-medium text-text-primary">{contra.treatment}</h4>
                          <p className="text-sm text-text-secondary">Condition: {contra.condition}</p>
                        </div>
                        <SeverityBadge severity={contra.severity === 'absolute' ? 'critical' : 'major'} />
                      </div>
                      <p className="text-text-secondary mb-3">{contra.explanation}</p>
                      <div>
                        <p className="font-medium text-text-primary text-sm mb-2">Alternatives:</p>
                        <ul className="list-disc list-inside text-text-secondary text-sm">
                          {contra.alternatives.map((alt, i) => (
                            <li key={i}>{alt}</li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </TabPanel>

        {/* Clinical Scenario Tab */}
        <TabPanel isActive={activeTab === 'scenario'}>
          <CardContent className="space-y-6">
            <div className="max-w-3xl space-y-4">
              <Textarea
                label="Describe the Clinical Scenario"
                placeholder="A 45-year-old male patient presents with joint pain, morning stiffness, and fatigue for the past 3 months. He has a history of..."
                value={clinicalScenario}
                onChange={(e) => setClinicalScenario(e.target.value)}
                className="min-h-[150px]"
              />
              
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-text-primary mb-3">Patient Context (Optional)</h4>
                <div className="grid md:grid-cols-2 gap-4">
                  <Input label="Age" type="number" placeholder="Years" />
                  <Select
                    label="Gender"
                    options={[
                      { value: 'male', label: 'Male' },
                      { value: 'female', label: 'Female' },
                      { value: 'other', label: 'Other' },
                    ]}
                    placeholder="Select"
                  />
                </div>
              </div>

              <Button
                onClick={() => setShowScenarioResults(true)}
                disabled={!clinicalScenario}
                leftIcon={<Stethoscope size={18} />}
              >
                Get Decision Support
              </Button>
            </div>

            {showScenarioResults && (
              <div className="mt-6 space-y-4">
                <Alert type="info" title="AI-Generated Recommendation">
                  <p className="mb-4">Based on the clinical scenario, here are the recommendations:</p>
                  
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-text-primary">Assessment</h4>
                      <p className="text-text-secondary text-sm">
                        The presentation suggests a Vata-predominant condition affecting the joints (Sandhigata Vata). 
                        Morning stiffness indicates possible Ama accumulation with Vata aggravation.
                      </p>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-text-primary">Recommended Approach</h4>
                      <ul className="list-disc list-inside text-text-secondary text-sm">
                        <li>Begin with Deepana-Pachana to clear Ama</li>
                        <li>Snehana (oleation) with appropriate medicated oils</li>
                        <li>Swedana (fomentation) to reduce stiffness</li>
                        <li>Consider Basti therapy as primary Panchakarma</li>
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-text-primary">Cautions</h4>
                      <ul className="list-disc list-inside text-text-secondary text-sm">
                        <li>Rule out inflammatory arthritis before starting treatment</li>
                        <li>Check for any cardiovascular conditions</li>
                        <li>Assess digestive fire (Agni) status before Panchakarma</li>
                      </ul>
                    </div>
                  </div>
                </Alert>
              </div>
            )}
          </CardContent>
        </TabPanel>
      </Card>
    </div>
  );
}
