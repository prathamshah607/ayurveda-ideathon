import React, { useState } from 'react';
import { Camera, Play, Sparkles } from 'lucide-react';
import {
  Card,
  CardContent,
  Button,
  Select,
  TagInput,
  QuickSelectChips,
  ImageUpload,
  Accordion,
  AccordionItem,
  Input,
  Alert,
  RedFlagAlert,
  DoshaChart,
  ProgressBar,
  Badge,
  Skeleton,
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
  'Weight Loss',
];

const prakritiOptions = [
  { value: 'vata', label: 'Vata' },
  { value: 'pitta', label: 'Pitta' },
  { value: 'kapha', label: 'Kapha' },
  { value: 'vata-pitta', label: 'Vata-Pitta' },
  { value: 'pitta-kapha', label: 'Pitta-Kapha' },
  { value: 'vata-kapha', label: 'Vata-Kapha' },
  { value: 'tridosha', label: 'Tridosha' },
];

// Placeholder diagnosis results
const mockDiagnosisResult = {
  differentialDiagnosis: [
    { condition: 'Vata Vyadhi (Vata Disorder)', confidence: 85, description: 'Imbalance in Vata dosha causing joint pain and nervous system issues' },
    { condition: 'Amavata (Rheumatoid Condition)', confidence: 72, description: 'Accumulation of Ama in joints with Vata aggravation' },
    { condition: 'Sandhigata Vata', confidence: 65, description: 'Degenerative joint condition due to Vata' },
  ],
  prakritiAssessment: { vata: 45, pitta: 30, kapha: 25 },
  vikritiAssessment: { vata: 65, pitta: 25, kapha: 10 },
  redFlags: [],
  recommendedTests: [
    'Nadi Pariksha (Pulse diagnosis)',
    'Mutra Pariksha (Urine analysis)',
    'Complete blood count',
    'ESR and CRP levels',
  ],
};

export function DiagnosisPage() {
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [tongueImage, setTongueImage] = useState<string | null>(null);
  const [nailImage, setNailImage] = useState<string | null>(null);

  const [patientProfile, setPatientProfile] = useState({
    patient: '',
    age: '',
    gender: '',
    prakriti: '',
    medicalHistory: [] as string[],
    currentMedications: [] as string[],
  });

  const handleRunDiagnosis = async () => {
    setIsAnalyzing(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsAnalyzing(false);
    setShowResults(true);
  };

  const handleImageSelect = (type: 'tongue' | 'nail') => (file: File) => {
    const url = URL.createObjectURL(file);
    if (type === 'tongue') {
      setTongueImage(url);
    } else {
      setNailImage(url);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="mb-6">
        <h1 className="font-heading text-2xl font-bold text-text-primary">Diagnosis Tool</h1>
        <p className="text-text-secondary">AI-powered differential diagnosis based on symptoms and analysis</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left Column - Input Panel */}
        <div className="space-y-6">
          {/* Patient Selector */}
          <Card>
            <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">Patient Selection</h2>
            <CardContent>
              <Select
                label="Select Patient"
                options={[
                  { value: 'new', label: '+ New Patient' },
                  { value: 'p1', label: 'Rajesh Kumar (ID: P001)' },
                  { value: 'p2', label: 'Priya Sharma (ID: P002)' },
                  { value: 'p3', label: 'Amit Patel (ID: P003)' },
                ]}
                value={patientProfile.patient}
                onChange={(e) => setPatientProfile({ ...patientProfile, patient: e.target.value })}
                placeholder="Choose a patient..."
              />
            </CardContent>
          </Card>

          {/* Symptom Input */}
          <Card>
            <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">Symptoms</h2>
            <CardContent className="space-y-4">
              <TagInput
                label="Enter Symptoms"
                placeholder="Type symptoms and press Enter..."
                value={symptoms}
                onChange={setSymptoms}
                suggestions={commonSymptoms}
              />
              <QuickSelectChips
                label="Quick Add"
                options={commonSymptoms}
                selected={symptoms}
                onChange={setSymptoms}
              />
            </CardContent>
          </Card>

          {/* Image Analysis */}
          <Card>
            <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">Image Analysis</h2>
            <CardContent className="space-y-4">
              <ImageUpload
                label="Tongue Analysis"
                icon={<Camera size={18} className="text-primary" />}
                onImageSelect={handleImageSelect('tongue')}
                previewUrl={tongueImage || undefined}
                onRemove={() => setTongueImage(null)}
                analysisStatus={tongueImage ? 'pending' : 'none'}
              />
              <ImageUpload
                label="Nail Analysis"
                icon={<Camera size={18} className="text-primary" />}
                onImageSelect={handleImageSelect('nail')}
                previewUrl={nailImage || undefined}
                onRemove={() => setNailImage(null)}
                analysisStatus={nailImage ? 'pending' : 'none'}
              />
            </CardContent>
          </Card>

          {/* Patient Profile Accordion */}
          <Card padding="sm">
            <Accordion>
              <AccordionItem title="Patient Profile" icon={<Sparkles size={18} />}>
                <div className="space-y-4 px-2">
                  <div className="grid grid-cols-2 gap-4">
                    <Input
                      label="Age"
                      type="number"
                      value={patientProfile.age}
                      onChange={(e) => setPatientProfile({ ...patientProfile, age: e.target.value })}
                      placeholder="Years"
                    />
                    <Select
                      label="Gender"
                      options={[
                        { value: 'male', label: 'Male' },
                        { value: 'female', label: 'Female' },
                        { value: 'other', label: 'Other' },
                      ]}
                      value={patientProfile.gender}
                      onChange={(e) => setPatientProfile({ ...patientProfile, gender: e.target.value })}
                      placeholder="Select"
                    />
                  </div>
                  <Select
                    label="Known Prakriti"
                    options={prakritiOptions}
                    value={patientProfile.prakriti}
                    onChange={(e) => setPatientProfile({ ...patientProfile, prakriti: e.target.value })}
                    placeholder="Select constitution..."
                  />
                  <TagInput
                    label="Medical History"
                    placeholder="Add conditions..."
                    value={patientProfile.medicalHistory}
                    onChange={(v) => setPatientProfile({ ...patientProfile, medicalHistory: v })}
                  />
                  <TagInput
                    label="Current Medications"
                    placeholder="Add medications..."
                    value={patientProfile.currentMedications}
                    onChange={(v) => setPatientProfile({ ...patientProfile, currentMedications: v })}
                  />
                </div>
              </AccordionItem>
            </Accordion>
          </Card>

          {/* Run Diagnosis Button */}
          <Button
            size="lg"
            className="w-full"
            leftIcon={<Play size={20} />}
            onClick={handleRunDiagnosis}
            isLoading={isAnalyzing}
            disabled={symptoms.length === 0}
          >
            {isAnalyzing ? 'Analyzing...' : 'Run Diagnosis'}
          </Button>
        </div>

        {/* Right Column - Results Panel */}
        <div className="space-y-6">
          {!showResults && !isAnalyzing && (
            <Card className="h-96 flex items-center justify-center">
              <div className="text-center text-text-secondary">
                <Sparkles size={48} className="mx-auto mb-4 opacity-30" />
                <p className="text-lg font-medium">Run diagnosis to see results</p>
                <p className="text-sm">Enter symptoms and click "Run Diagnosis"</p>
              </div>
            </Card>
          )}

          {isAnalyzing && (
            <div className="space-y-6">
              <Card>
                <Skeleton className="h-6 w-48 mb-4" />
                <Skeleton className="h-4 w-full mb-2" />
                <Skeleton className="h-4 w-3/4 mb-2" />
                <Skeleton className="h-4 w-5/6" />
              </Card>
              <Card>
                <Skeleton className="h-40 w-full" />
              </Card>
            </div>
          )}

          {showResults && (
            <>
              {/* Red Flags Alert */}
              {mockDiagnosisResult.redFlags.length > 0 && (
                <RedFlagAlert flags={mockDiagnosisResult.redFlags} />
              )}

              {/* Differential Diagnosis */}
              <Card>
                <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
                  Differential Diagnosis
                </h2>
                <CardContent className="space-y-4">
                  {mockDiagnosisResult.differentialDiagnosis.map((dx, index) => (
                    <div key={index} className="p-4 rounded-lg bg-gray-50">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-text-primary">{dx.condition}</h3>
                        <Badge variant={dx.confidence > 80 ? 'success' : dx.confidence > 60 ? 'warning' : 'default'}>
                          {dx.confidence}% match
                        </Badge>
                      </div>
                      <p className="text-sm text-text-secondary mb-3">{dx.description}</p>
                      <ProgressBar value={dx.confidence} size="sm" color={dx.confidence > 80 ? 'success' : dx.confidence > 60 ? 'warning' : 'info'} />
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Prakriti & Vikriti Assessment */}
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <h3 className="font-medium text-text-primary mb-4">Prakriti Assessment</h3>
                  <DoshaChart breakdown={mockDiagnosisResult.prakritiAssessment} size="sm" />
                </Card>
                <Card>
                  <h3 className="font-medium text-text-primary mb-4">Vikriti (Current Imbalance)</h3>
                  <DoshaChart breakdown={mockDiagnosisResult.vikritiAssessment} size="sm" />
                </Card>
              </div>

              {/* Tongue Analysis Placeholder */}
              {tongueImage && (
                <Card>
                  <h3 className="font-medium text-text-primary mb-4">📷 Tongue Analysis Results</h3>
                  <CardContent>
                    <Alert type="info">
                      <p className="font-medium">Analysis Pending</p>
                      <p className="text-sm">Tongue image analysis feature coming soon. Results will show coating, color, and dosha implications.</p>
                    </Alert>
                  </CardContent>
                </Card>
              )}

              {/* Recommended Tests */}
              <Card>
                <h3 className="font-medium text-text-primary mb-4">Recommended Tests</h3>
                <CardContent>
                  <ul className="space-y-2">
                    {mockDiagnosisResult.recommendedTests.map((test, index) => (
                      <li key={index} className="flex items-center gap-3">
                        <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary" />
                        <span className="text-text-secondary">{test}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Action Buttons */}
              <div className="flex gap-4">
                <Button className="flex-1" variant="primary">
                  Generate Treatment Plan
                </Button>
                <Button className="flex-1" variant="outline">
                  Save to Patient Record
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
