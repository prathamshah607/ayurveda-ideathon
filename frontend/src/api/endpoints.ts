// API Base URL - Change this based on your environment
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// ============================================
// DOCTOR MODULE ENDPOINTS
// ============================================

export const DOCTOR_ENDPOINTS = {
  // Diagnosis
  DIAGNOSE: `${API_BASE_URL}/diagnose`,
  RED_FLAGS: `${API_BASE_URL}/diagnose/red-flags`,
  PRAKRITI_ASSESSMENT: `${API_BASE_URL}/diagnose/prakriti`,
  
  // Treatment
  TREATMENT_PLAN: `${API_BASE_URL}/treatment-plan`,
  
  // Decision Support
  INTERACTIONS: `${API_BASE_URL}/decision-support/interactions`,
  CONTRAINDICATIONS: `${API_BASE_URL}/decision-support/contraindications`,
  DECISION_SUPPORT: `${API_BASE_URL}/decision-support`,
  
  // Disease Progression
  PROGRESSION: `${API_BASE_URL}/progression`,
  INTERVENTION: `${API_BASE_URL}/progression/intervention`,
  
  // Image Analysis (Placeholders)
  TONGUE_ANALYSIS: `${API_BASE_URL}/analyze/tongue`,
  NAIL_ANALYSIS: `${API_BASE_URL}/analyze/nail`,
} as const;

// ============================================
// PATIENT MODULE ENDPOINTS
// ============================================

export const PATIENT_ENDPOINTS = {
  // Symptom Check
  SYMPTOM_CHECK: `${API_BASE_URL}/patient`,
  
  // Health Predictions
  PREDICTIONS: `${API_BASE_URL}/trends`,
  QUICK_RISK: `${API_BASE_URL}/trends/quick`,
  
  // Chat
  CHAT: `${API_BASE_URL}/chat/patient`,
  
  // Image Analysis (Placeholders)
  TONGUE_ANALYSIS: `${API_BASE_URL}/analyze/tongue`,
  NAIL_ANALYSIS: `${API_BASE_URL}/analyze/nail`,
} as const;

// ============================================
// REFERENCE DATA ENDPOINTS
// ============================================

export const REFERENCE_ENDPOINTS = {
  DOSHAS: `${API_BASE_URL}/doshas`,
  DHATUS: `${API_BASE_URL}/dhatus`,
  AGNI_TYPES: `${API_BASE_URL}/agni-types`,
} as const;

// ============================================
// AUTH ENDPOINTS (Placeholder)
// ============================================

export const AUTH_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/auth/login`,
  REGISTER: `${API_BASE_URL}/auth/register`,
  LOGOUT: `${API_BASE_URL}/auth/logout`,
  REFRESH: `${API_BASE_URL}/auth/refresh`,
  ME: `${API_BASE_URL}/auth/me`,
} as const;
