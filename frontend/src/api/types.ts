// ============================================
// USER & AUTH TYPES
// ============================================

export type UserRole = 'doctor' | 'patient';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  avatar?: string;
  createdAt: string;
}

export interface DoctorProfile extends User {
  role: 'doctor';
  licenseNumber: string;
  specialization: string;
  clinicName: string;
  credentials: string;
}

export interface PatientProfile extends User {
  role: 'patient';
  age: number;
  gender: 'male' | 'female' | 'other';
  knownConditions: string[];
  prakriti?: PrakritiResult;
}

export interface LoginCredentials {
  email: string;
  password: string;
  role: UserRole;
}

export interface RegisterDoctorData {
  name: string;
  email: string;
  password: string;
  licenseNumber: string;
  specialization: string;
  clinicName: string;
  credentials: string;
}

export interface RegisterPatientData {
  name: string;
  email: string;
  password: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  knownConditions: string[];
}

// ============================================
// DOSHA & PRAKRITI TYPES
// ============================================

export type DoshaType = 'Vata' | 'Pitta' | 'Kapha';
export type PrakritiType = 'Vata' | 'Pitta' | 'Kapha' | 'Vata-Pitta' | 'Pitta-Kapha' | 'Vata-Kapha' | 'Tridosha';

export interface DoshaBreakdown {
  vata: number;
  pitta: number;
  kapha: number;
}

export interface PrakritiResult {
  dominantDosha: PrakritiType;
  breakdown: DoshaBreakdown;
  description: string;
  recommendations: string[];
}

// ============================================
// DIAGNOSIS TYPES
// ============================================

export interface DiagnosisRequest {
  patientId?: string;
  symptoms: string[];
  tongueImageUrl?: string;
  nailImageUrl?: string;
  patientProfile: {
    age: number;
    gender: string;
    prakriti?: PrakritiType;
    medicalHistory: string[];
    currentMedications: string[];
  };
}

export interface DiagnosisResult {
  differentialDiagnosis: {
    condition: string;
    confidence: number;
    description: string;
  }[];
  prakritiAssessment: DoshaBreakdown;
  vikritiAssessment: DoshaBreakdown;
  redFlags: string[];
  tongueAnalysis?: ImageAnalysisResult;
  nailAnalysis?: ImageAnalysisResult;
  recommendedTests: string[];
}

export interface ImageAnalysisResult {
  imageUrl: string;
  findings: {
    observation: string;
    significance: string;
    doshaImplication: DoshaType;
  }[];
  overallAssessment: string;
}

// ============================================
// TREATMENT PLAN TYPES
// ============================================

export interface TreatmentPhase {
  name: string;
  duration: string;
  objectives: string[];
  dietaryChanges: string[];
  lifestyleModifications: string[];
}

export interface Formulation {
  name: string;
  dosage: string;
  timing: string;
  duration: string;
  anupana: string;
}

export interface TreatmentPlan {
  id: string;
  patientId: string;
  diagnosis: string;
  phases: TreatmentPhase[];
  formulations: Formulation[];
  pathya: string[]; // Do's
  apathya: string[]; // Don'ts
  createdAt: string;
  doctorId: string;
}

// ============================================
// DECISION SUPPORT TYPES
// ============================================

export interface DrugInteraction {
  drug1: string;
  drug2: string;
  severity: 'critical' | 'major' | 'moderate' | 'minor';
  description: string;
  recommendation: string;
}

export interface Contraindication {
  treatment: string;
  condition: string;
  severity: 'absolute' | 'relative';
  explanation: string;
  alternatives: string[];
}

export interface DecisionSupportRequest {
  clinicalScenario: string;
  patientProfile: {
    age: number;
    gender: string;
    conditions: string[];
    medications: string[];
  };
}

export interface DecisionSupportResponse {
  recommendations: string[];
  warnings: string[];
  references: string[];
}

// ============================================
// DISEASE PROGRESSION TYPES
// ============================================

export type DiseaseStage = 1 | 2 | 3 | 4 | 5 | 6;

export const DISEASE_STAGE_NAMES: Record<DiseaseStage, string> = {
  1: 'Sanchaya',
  2: 'Prakopa',
  3: 'Prasara',
  4: 'Sthana Samshraya',
  5: 'Vyakti',
  6: 'Bheda',
};

export interface ProgressionRequest {
  disease: string;
  currentStage: DiseaseStage;
  durationDays: number;
}

export interface StageProgression {
  stage: DiseaseStage;
  name: string;
  estimatedDays: number;
  symptoms: string[];
  interventions: string[];
}

export interface ProgressionResponse {
  disease: string;
  currentStage: DiseaseStage;
  projectedProgression: StageProgression[];
  urgencyLevel: 'low' | 'moderate' | 'high' | 'critical';
  interventionRecommendations: string[];
}

// ============================================
// PATIENT MODULE TYPES
// ============================================

export interface SymptomCheckRequest {
  symptoms: string[];
  patientProfile?: {
    age?: number;
    gender?: string;
    prakriti?: PrakritiType;
  };
}

export interface SymptomCheckResponse {
  redFlags: string[];
  possibleConditions: {
    name: string;
    explanation: string;
    likelihood: 'low' | 'moderate' | 'high';
  }[];
  selfCareRecommendations: {
    dietary: string[];
    lifestyle: string[];
    homeRemedies: string[];
  };
  disclaimer: string;
}

export interface HealthPrediction {
  condition: string;
  riskLevel: 'low' | 'moderate' | 'high';
  oneYearRisk: number;
  fiveYearRisk: number;
  preventionTips: string[];
}

export interface HealthPredictionResponse {
  overallHealthScore: number;
  doshaBalance: DoshaBreakdown;
  predictions: HealthPrediction[];
  doshaTrajectory: {
    timeframe: string;
    projectedBalance: DoshaBreakdown;
  }[];
  preventionPlan: {
    immediate: string[];
    shortTerm: string[];
    longTerm: string[];
  };
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatRequest {
  message: string;
  conversationHistory?: ChatMessage[];
  patientContext?: {
    prakriti?: PrakritiType;
    conditions?: string[];
  };
}

export interface ChatResponse {
  message: string;
  suggestedQuestions?: string[];
}

// ============================================
// REFERENCE DATA TYPES
// ============================================

export interface DoshaInfo {
  name: DoshaType;
  elements: string[];
  qualities: string[];
  bodyType: string;
  personality: string;
  imbalanceSigns: string[];
  balancingTips: string[];
}

export interface DhatuInfo {
  name: string;
  function: string;
  relatedDosha: DoshaType;
  imbalanceSigns: string[];
}

export interface AgniType {
  name: string;
  associatedDosha: DoshaType;
  characteristics: string[];
  recommendations: string[];
}

// ============================================
// API RESPONSE WRAPPER
// ============================================

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// ============================================
// DASHBOARD STATS TYPES
// ============================================

export interface DoctorDashboardStats {
  totalPatients: number;
  pendingConsultations: number;
  activeTreatmentPlans: number;
  alerts: number;
}

export interface PatientActivity {
  id: string;
  patientName: string;
  action: string;
  timestamp: string;
}
