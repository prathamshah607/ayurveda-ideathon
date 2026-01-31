import { DOCTOR_ENDPOINTS, PATIENT_ENDPOINTS, REFERENCE_ENDPOINTS } from './endpoints';
import type {
  ApiResponse,
  DiagnosisRequest,
  DiagnosisResult,
  TreatmentPlan,
  DrugInteraction,
  Contraindication,
  DecisionSupportRequest,
  DecisionSupportResponse,
  ProgressionRequest,
  ProgressionResponse,
  SymptomCheckRequest,
  SymptomCheckResponse,
  HealthPredictionResponse,
  ChatRequest,
  ChatResponse,
  DoshaInfo,
  DhatuInfo,
  AgniType,
} from './types';

// ============================================
// HELPER FUNCTIONS
// ============================================

async function apiRequest<T>(
  url: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.message || 'An error occurred',
      };
    }

    return {
      success: true,
      data,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}

// ============================================
// DOCTOR API SERVICES
// ============================================

export const doctorApi = {
  // Diagnosis
  runDiagnosis: (request: DiagnosisRequest) =>
    apiRequest<DiagnosisResult>(DOCTOR_ENDPOINTS.DIAGNOSE, {
      method: 'POST',
      body: JSON.stringify(request),
    }),

  checkRedFlags: (symptoms: string[]) =>
    apiRequest<{ redFlags: string[] }>(DOCTOR_ENDPOINTS.RED_FLAGS, {
      method: 'POST',
      body: JSON.stringify({ symptoms }),
    }),

  assessPrakriti: (answers: Record<string, string>) =>
    apiRequest<{ prakriti: string; breakdown: Record<string, number> }>(
      DOCTOR_ENDPOINTS.PRAKRITI_ASSESSMENT,
      {
        method: 'POST',
        body: JSON.stringify({ answers }),
      }
    ),

  // Treatment
  generateTreatmentPlan: (patientId: string, diagnosis: string) =>
    apiRequest<TreatmentPlan>(DOCTOR_ENDPOINTS.TREATMENT_PLAN, {
      method: 'POST',
      body: JSON.stringify({ patientId, diagnosis }),
    }),

  // Decision Support
  checkInteractions: (medications: string[]) =>
    apiRequest<{ interactions: DrugInteraction[] }>(
      DOCTOR_ENDPOINTS.INTERACTIONS,
      {
        method: 'POST',
        body: JSON.stringify({ medications }),
      }
    ),

  checkContraindications: (treatment: string, conditions: string[]) =>
    apiRequest<{ contraindications: Contraindication[] }>(
      DOCTOR_ENDPOINTS.CONTRAINDICATIONS,
      {
        method: 'POST',
        body: JSON.stringify({ treatment, conditions }),
      }
    ),

  getDecisionSupport: (request: DecisionSupportRequest) =>
    apiRequest<DecisionSupportResponse>(DOCTOR_ENDPOINTS.DECISION_SUPPORT, {
      method: 'POST',
      body: JSON.stringify(request),
    }),

  // Disease Progression
  modelProgression: (request: ProgressionRequest) =>
    apiRequest<ProgressionResponse>(DOCTOR_ENDPOINTS.PROGRESSION, {
      method: 'POST',
      body: JSON.stringify(request),
    }),

  getIntervention: (disease: string, stage: number) =>
    apiRequest<{ interventions: string[] }>(DOCTOR_ENDPOINTS.INTERVENTION, {
      method: 'POST',
      body: JSON.stringify({ disease, stage }),
    }),

  // Image Analysis (Placeholders)
  analyzeTongue: (imageFile: File) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    return apiRequest<{ analysis: string }>(DOCTOR_ENDPOINTS.TONGUE_ANALYSIS, {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set content-type for FormData
    });
  },

  analyzeNail: (imageFile: File) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    return apiRequest<{ analysis: string }>(DOCTOR_ENDPOINTS.NAIL_ANALYSIS, {
      method: 'POST',
      body: formData,
      headers: {},
    });
  },
};

// ============================================
// PATIENT API SERVICES
// ============================================

export const patientApi = {
  checkSymptoms: (request: SymptomCheckRequest) =>
    apiRequest<SymptomCheckResponse>(PATIENT_ENDPOINTS.SYMPTOM_CHECK, {
      method: 'POST',
      body: JSON.stringify(request),
    }),

  getHealthPredictions: (patientId: string) =>
    apiRequest<HealthPredictionResponse>(PATIENT_ENDPOINTS.PREDICTIONS, {
      method: 'POST',
      body: JSON.stringify({ patientId }),
    }),

  getQuickRiskCheck: (conditions: string[]) =>
    apiRequest<{ risks: Record<string, number> }>(PATIENT_ENDPOINTS.QUICK_RISK, {
      method: 'POST',
      body: JSON.stringify({ conditions }),
    }),

  chat: (request: ChatRequest) =>
    apiRequest<ChatResponse>(PATIENT_ENDPOINTS.CHAT, {
      method: 'POST',
      body: JSON.stringify(request),
    }),

  // Image Analysis (Placeholders)
  analyzeTongue: (imageFile: File) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    return apiRequest<{ analysis: string }>(PATIENT_ENDPOINTS.TONGUE_ANALYSIS, {
      method: 'POST',
      body: formData,
      headers: {},
    });
  },

  analyzeNail: (imageFile: File) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    return apiRequest<{ analysis: string }>(PATIENT_ENDPOINTS.NAIL_ANALYSIS, {
      method: 'POST',
      body: formData,
      headers: {},
    });
  },
};

// ============================================
// REFERENCE DATA SERVICES
// ============================================

export const referenceApi = {
  getDoshas: () =>
    apiRequest<DoshaInfo[]>(REFERENCE_ENDPOINTS.DOSHAS, {
      method: 'GET',
    }),

  getDhatus: () =>
    apiRequest<DhatuInfo[]>(REFERENCE_ENDPOINTS.DHATUS, {
      method: 'GET',
    }),

  getAgniTypes: () =>
    apiRequest<AgniType[]>(REFERENCE_ENDPOINTS.AGNI_TYPES, {
      method: 'GET',
    }),
};
