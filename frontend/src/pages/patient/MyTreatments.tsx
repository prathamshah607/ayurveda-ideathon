import React from 'react';
import { Calendar, CheckCircle, MessageSquare, ChevronDown } from 'lucide-react';
import {
  Card,
  CardContent,
  Button,
  ProgressBar,
  Badge,
  Accordion,
  AccordionItem,
} from '../../components/ui';

// Placeholder data
const activeTreatment = {
  name: 'Vata Balancing Protocol',
  doctor: 'Dr. Ayush Sharma',
  startDate: 'January 15, 2026',
  currentPhase: 2,
  totalPhases: 5,
  phaseName: 'Deepana-Pachana',
  progress: 45,
  dailyChecklist: [
    { id: 1, task: 'Morning medication (Triphala)', time: '6:30 AM', completed: true },
    { id: 2, task: 'Abhyanga (self-massage)', time: '7:00 AM', completed: true },
    { id: 3, task: 'Pranayama practice', time: '7:30 AM', completed: false },
    { id: 4, task: 'Lunch with digestive herbs', time: '12:30 PM', completed: false },
    { id: 5, task: 'Evening Ashwagandha', time: '8:00 PM', completed: false },
    { id: 6, task: 'Bedtime routine (warm milk)', time: '9:30 PM', completed: false },
  ],
  currentPhaseDetails: {
    objectives: ['Kindle digestive fire (Agni)', 'Clear accumulated toxins', 'Prepare for deeper cleansing'],
    dietaryGuidelines: ['Light, warm meals', 'Include ginger and cumin', 'Avoid cold foods'],
    medications: [
      { name: 'Triphala Churna', dosage: '3g', timing: 'Morning, empty stomach' },
      { name: 'Ashwagandha', dosage: '500mg', timing: 'Evening with warm milk' },
      { name: 'Trikatu', dosage: '1g', timing: 'Before meals' },
    ],
  },
};

const treatmentHistory = [
  { id: 1, name: 'Digestive Reset Protocol', doctor: 'Dr. Priya Patel', date: 'Oct 2025', status: 'Completed' },
  { id: 2, name: 'Stress Management Program', doctor: 'Dr. Ayush Sharma', date: 'Aug 2025', status: 'Completed' },
];

export function MyTreatments() {
  return (
    <div className="animate-fade-in">
      <div className="mb-6">
        <h1 className="font-heading text-2xl font-bold text-text-primary">My Treatments</h1>
        <p className="text-text-secondary">Track your treatment progress and daily tasks</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Active Treatment */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <div className="flex items-start justify-between mb-4">
              <div>
                <Badge variant="primary" className="mb-2">Active Treatment</Badge>
                <h2 className="font-heading text-xl font-semibold text-text-primary">
                  {activeTreatment.name}
                </h2>
                <p className="text-sm text-text-secondary">
                  {activeTreatment.doctor} • Started {activeTreatment.startDate}
                </p>
              </div>
              <Button variant="outline" size="sm" leftIcon={<MessageSquare size={16} />}>
                Contact Doctor
              </Button>
            </div>

            <CardContent>
              {/* Progress */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">
                    Phase {activeTreatment.currentPhase} of {activeTreatment.totalPhases}: {activeTreatment.phaseName}
                  </span>
                  <span className="text-sm text-text-secondary">{activeTreatment.progress}%</span>
                </div>
                <ProgressBar value={activeTreatment.progress} color="primary" size="md" />
                
                {/* Phase indicators */}
                <div className="flex justify-between mt-3">
                  {Array.from({ length: activeTreatment.totalPhases }).map((_, index) => (
                    <div
                      key={index}
                      className={`flex flex-col items-center ${
                        index + 1 <= activeTreatment.currentPhase ? 'text-primary' : 'text-gray-300'
                      }`}
                    >
                      <div
                        className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                          index + 1 < activeTreatment.currentPhase
                            ? 'bg-primary text-white'
                            : index + 1 === activeTreatment.currentPhase
                            ? 'bg-primary/20 text-primary border-2 border-primary'
                            : 'bg-gray-100 text-gray-400'
                        }`}
                      >
                        {index + 1 < activeTreatment.currentPhase ? '✓' : index + 1}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Current Phase Details */}
              <div className="p-4 bg-primary/5 rounded-lg border border-primary/10">
                <h3 className="font-medium text-text-primary mb-3">Current Phase Objectives</h3>
                <ul className="space-y-1">
                  {activeTreatment.currentPhaseDetails.objectives.map((obj, index) => (
                    <li key={index} className="flex items-center gap-2 text-sm text-text-secondary">
                      <span className="text-primary">•</span>
                      {obj}
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Daily Checklist */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-heading text-lg font-semibold text-text-primary">
                Today's Tasks
              </h2>
              <div className="flex items-center gap-2 text-sm text-text-secondary">
                <Calendar size={16} />
                <span>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}</span>
              </div>
            </div>
            <CardContent>
              <div className="space-y-3">
                {activeTreatment.dailyChecklist.map((item) => (
                  <label
                    key={item.id}
                    className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
                      item.completed ? 'bg-success/5' : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={item.completed}
                        onChange={() => {}}
                        className="w-5 h-5 rounded-full text-primary focus:ring-primary"
                      />
                      <span className={item.completed ? 'text-text-secondary line-through' : 'text-text-primary'}>
                        {item.task}
                      </span>
                    </div>
                    <span className="text-sm text-text-secondary">{item.time}</span>
                  </label>
                ))}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
                <span className="text-sm text-text-secondary">
                  {activeTreatment.dailyChecklist.filter((t) => t.completed).length} of{' '}
                  {activeTreatment.dailyChecklist.length} completed
                </span>
                <Button variant="ghost" size="sm">
                  Set Reminders
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Medications */}
          <Card>
            <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
              Current Medications
            </h2>
            <CardContent className="space-y-3">
              {activeTreatment.currentPhaseDetails.medications.map((med, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium text-primary">{med.name}</p>
                  <p className="text-sm text-text-secondary">
                    {med.dosage} • {med.timing}
                  </p>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Dietary Guidelines */}
          <Card>
            <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
              Dietary Guidelines
            </h2>
            <CardContent>
              <ul className="space-y-2">
                {activeTreatment.currentPhaseDetails.dietaryGuidelines.map((guideline, index) => (
                  <li key={index} className="flex items-center gap-2 text-sm text-text-secondary">
                    <span className="text-success">✓</span>
                    {guideline}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Treatment History */}
          <Card>
            <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">
              Treatment History
            </h2>
            <CardContent>
              <Accordion>
                {treatmentHistory.map((treatment) => (
                  <AccordionItem
                    key={treatment.id}
                    title={treatment.name}
                    badge={<Badge variant="success" size="sm">{treatment.status}</Badge>}
                  >
                    <div className="text-sm text-text-secondary space-y-1">
                      <p>Doctor: {treatment.doctor}</p>
                      <p>Completed: {treatment.date}</p>
                    </div>
                  </AccordionItem>
                ))}
              </Accordion>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
