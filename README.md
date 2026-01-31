# 🌿 Ayurveda Modular API v2.0 - Complete Integration Guide

A comprehensive, AI-powered REST API for Ayurvedic healthcare featuring RAG (Retrieval-Augmented Generation) from classical texts, clinical decision support, and predictive health analytics. Built for seamless integration into healthcare systems, research platforms, and patient-facing applications.

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Quick Start & Setup](#quick-start--setup)
3. [Architecture & Technology](#architecture--technology)
4. [API Endpoints - Complete Reference](#api-endpoints---complete-reference)
5. [Data Models & Schemas](#data-models--schemas)
6. [Integration Patterns](#integration-patterns)
7. [Error Handling & Status Codes](#error-handling--status-codes)
8. [Rate Limiting & Performance](#rate-limiting--performance)
9. [Authentication & Security](#authentication--security)
10. [Classical Text Sources](#classical-text-sources)
11. [Examples & Workflows](#examples--workflows)

---

## System Overview

### 8 Specialized Modules

| Module | Purpose | Output | Integration Point |
|--------|---------|--------|-------------------|
| **DoctorModule** | Clinical-grade outputs for practitioners | Structured JSON with medical terminology | EMR systems, clinical dashboards |
| **PatientModule** | User-friendly health guidance | Simplified language, actionable advice | Patient portals, mobile apps |
| **AyushModule** | AYUSH Ministry aligned responses | Research-backed, citation-heavy | Government systems, academic research |
| **FutureTrendsModule** | Predictive disease risk modeling | Risk scores, prevention plans | Preventive health programs, wellness apps |
| **DiagnosisModule** | AI-assisted differential diagnosis | Ranked conditions with confidence scores | Diagnostic support tools, clinical workflows |
| **PersonalizedTreatmentModule** | Multi-phase treatment protocols | Phased plans with formulations | Treatment planning systems |
| **DecisionSupportModule** | Drug interactions & contraindications | Safety warnings with severity levels | Pharmacy systems, prescribing tools |
| **ProgressionModelingModule** | Shat Kriyakala 6-stage disease progression | Stage tracking with interventions | Disease monitoring, prognosis tools |

---

## Quick Start & Setup

### Installation

```bash
# Clone repository
git clone <repo-url>
cd ayurveda_ayush

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="gsk_xxxxxxxxxxxx"
export PORT=8000

# Start server
python ayurveda_server.py
```

### Requirements File (`requirements.txt`)

```
fastapi==0.104.1
uvicorn==0.24.0
langchain==0.1.0
langchain-groq==0.0.10
chromadb==0.4.10
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
```

### Initial Database Setup

```bash
# Ensure vector databases exist in:
# - ./chroma_db_asthrid/       (Ashtanga Hridaya)
# - ./chroma_sushruta/         (Sushruta Samhita)
# - ./chroma_db_ayurgenix/     (Clinical database)

# If missing, run embedding scripts:
python databases&embeddings/charaka_embeddings.ipynb
python databases&embeddings/ah_embeddings.py
python databases&embeddings/sushruta_embeddings.py
```

### Verification

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "modules": [...]}
```

---

## Architecture & Technology

### Tech Stack

```
Client Layer
    ↓
FastAPI (REST Endpoints) - ayurveda_server.py
    ↓
AyurvedaAPI (Business Logic) - ayurveda_api.py
    ↓
┌─────────────────────────────────────┐
│ 8 Specialized AI Modules            │
├─────────────────────────────────────┤
│ • DoctorModule                      │
│ • PatientModule                     │
│ • AyushModule                       │
│ • FutureTrendsModule                │
│ • DiagnosisModule                   │
│ • PersonalizedTreatmentModule       │
│ • DecisionSupportModule             │
│ • ProgressionModelingModule         │
└─────────────────────────────────────┘
    ↓
AyurvedaRAGEngine (Vector Search & Generation)
    ↓
┌──────────────┬──────────────┬──────────────┐
│ ChromaDB     │ ChromaDB     │ ChromaDB     │
│ Ashtanga     │ Sushruta     │ AyurGenix    │
│ Hridaya      │ Samhita      │ Clinical DB  │
└──────────────┴──────────────┴──────────────┘
    ↓
LLM: Groq (openai/gpt-oss-120b)
```

### Key Configuration

| Setting | Value | Notes |
|---------|-------|-------|
| **LLM Model** | `openai/gpt-oss-120b` | Via Groq API |
| **Temperature** | 0.1 | Low randomness for consistency |
| **Max Tokens** | 4096 | Per request limit |
| **Context Limit** | 6000 chars | To stay within token budget |
| **Vector DB** | ChromaDB | Local file-based |
| **Embeddings** | HuggingFace (multilingual) | Supports English & Sanskrit |
| **Framework** | FastAPI | Async-capable, auto docs |

---

## API Endpoints - Complete Reference

### Base URL
```
http://localhost:8000
```

### Response Format (All Endpoints)

**Success Response (HTTP 200):**
```json
{
  "success": true,
  "data": {
    "result_field_1": "value",
    "result_field_2": ["array", "of", "values"]
  }
}
```

**Error Response (HTTP 4xx/5xx):**
```json
{
  "success": false,
  "detail": "Error message describing what went wrong"
}
```

---

## HEALTH & SYSTEM ENDPOINTS

### 1. GET `/` - Root/Welcome
Returns API introduction and documentation links.

**Request:**
```bash
curl http://localhost:8000/
```

**Response (HTTP 200):**
```json
{
  "message": "Welcome to Ayurveda Modular API v2.0",
  "docs_url": "http://localhost:8000/docs",
  "redoc_url": "http://localhost:8000/redoc"
}
```

---

### 2. GET `/api/v1/health` - Health Check
System status and module availability check.

**Request:**
```bash
curl http://localhost:8000/api/v1/health
```

**Response (HTTP 200):**
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "timestamp": "2026-01-31T14:00:00Z",
  "modules": {
    "doctor": "ready",
    "patient": "ready",
    "ayush": "ready",
    "trends": "ready",
    "diagnosis": "ready",
    "treatment": "ready",
    "decision_support": "ready",
    "progression": "ready"
  },
  "database_status": {
    "ashtanga_hridaya": "loaded (1200 documents)",
    "sushruta_samhita": "loaded (800 documents)",
    "ayurgenix": "loaded (367 disease profiles)"
  },
  "llm_status": "connected"
}
```

---

## CORE MODULE ENDPOINTS

### 3. POST `/api/v1/doctor` - Doctor Module Query
Clinical-grade response for healthcare practitioners.

**Request Body Schema:**
```json
{
  "question": "string (required) - Clinical question in any format",
  "user_profile": {
    "age": "integer (optional)",
    "gender": "M|F (optional)",
    "known_prakriti": "vata|pitta|kapha|vata_pitta|pitta_kapha|vata_kapha|tridosha (optional)",
    "current_symptoms": ["string array (optional)"],
    "medical_history": ["string array (optional)"],
    "current_medications": ["string array (optional)"]
  }
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/doctor \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the Ayurvedic pathophysiology and treatment for rheumatoid arthritis?",
    "user_profile": {
      "age": 45,
      "gender": "F",
      "known_prakriti": "vata_kapha",
      "current_symptoms": ["joint pain", "swelling", "morning stiffness"]
    }
  }'
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": {
    "query_id": "abc123def456",
    "question": "What is the Ayurvedic pathophysiology and treatment for rheumatoid arthritis?",
    "clinical_assessment": {
      "ayurvedic_condition": "Amavata",
      "samprapti": {
        "nidana": "Etiology - causative factors",
        "purvarupa": "Prodromal symptoms observed",
        "rupa": "Clinical manifestations present",
        "upashaya": "Factors that improve symptoms",
        "anupashaya": "Factors that worsen symptoms"
      },
      "dosha_analysis": {
        "primary_dosha": "vata",
        "secondary_dosha": "kapha",
        "state": "vriddhi",
        "vikriti_description": "Vata and Kapha aggravation with Agni deficiency"
      },
      "dhatu_affected": ["rakta", "mamsa", "asthi"],
      "agni_status": "manda",
      "ama_present": true,
      "ama_assessment": "High ama accumulation noted"
    },
    "treatment_protocol": {
      "phase_1": "Nidana Parivarjana - Remove causative factors",
      "phase_2": "Deepana-Pachana - Kindle digestive fire",
      "phase_3": "Shodhana - Panchakarma purification",
      "phase_4": "Shamana - Palliative treatment",
      "phase_5": "Rasayana - Rejuvenation"
    },
    "formulations": [
      {
        "name": "Maharasnadi Taila",
        "dosage": "10ml",
        "frequency": "Twice daily with warm water",
        "anupana": "Warm water",
        "duration": "2-3 months"
      }
    ],
    "pathya": ["Warm foods", "Oil massage", "Gentle exercise"],
    "apathya": ["Cold foods", "Excess salt", "Dairy"],
    "classical_references": [
      {
        "text": "Ashtanga Hridaya",
        "chapter": "Nidana Sthana 15",
        "verse": "Amavata Nidana"
      }
    ]
  }
}
```

**Status Codes:**
- `200 OK` - Successful response
- `400 Bad Request` - Invalid question format
- `500 Internal Server Error` - LLM generation failed

---

### 4. GET `/api/v1/doctor` - Doctor Module Documentation
Returns endpoint information and example payloads.

---

### 5. POST `/api/v1/patient` - Patient Module Query
User-friendly, simplified responses for patients.

**Request Body Schema:**
```json
{
  "question": "string (required)"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/patient \
  -H "Content-Type: application/json" \
  -d '{"question": "How can I improve my digestion naturally?"}'
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": {
    "response": "Your digestive health can improve through simple lifestyle changes...",
    "home_remedies": [
      "Ginger tea before meals",
      "Warm lemon water in morning",
      "Chew food slowly"
    ],
    "dietary_changes": [
      "Eat cooked foods instead of raw",
      "Include spices: turmeric, cumin, ginger",
      "Avoid cold drinks"
    ],
    "lifestyle_tips": [
      "10-minute walk after meals",
      "Regular meal times",
      "Avoid eating when stressed"
    ]
  }
}
```

---

### 6. POST `/api/v1/ayush` - AYUSH Module Query
Government-aligned, research-backed responses with citations.

**Request Body Schema:**
```json
{
  "question": "string (required)"
}
```

**Response Includes:**
- Classical Sanskrit verse citations
- Modern research references
- Safety and contraindication information
- Regulatory compliance notes
- WHO traditional medicine alignment

---

## CHAT INTERFACE ENDPOINTS

### 7. POST `/api/v1/chat/doctor` - Doctor Chat
Conversational interface for clinical queries.

**Request Body Schema:**
```json
{
  "query": "string (required) - Conversational query",
  "conversation_history": [
    {
      "role": "user|assistant",
      "content": "string"
    }
  ]
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/doctor \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What dosage of Ashwagandha for anxiety?"
  }'
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "response": "For anxiety management, Ashwagandha dosage typically ranges from 300-600mg daily...",
  "references": [
    {
      "source": "Ashtanga Hridaya",
      "section": "Materia Medica"
    }
  ],
  "module": "doctor"
}
```

---

### 8. POST `/api/v1/chat/patient` - Patient Chat
Patient-friendly conversational interface.

**Same request/response structure as doctor chat, but with simplified language.**

---

### 9. POST `/api/v1/chat/ayush` - AYUSH Chat
Research and regulatory-focused conversational interface.

---

### 10. POST `/api/v1/chat/all` - Multi-Module Chat
Queries all three modules simultaneously.

**Request Body Schema:**
```json
{
  "query": "string (required)",
  "include_modules": ["doctor", "patient", "ayush"],
  "combine_responses": "boolean (optional, default: false)"
}
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "responses": {
    "doctor": "Clinical response...",
    "patient": "Simplified response...",
    "ayush": "Research-backed response..."
  }
}
```

---

## FUTURE TRENDS & PREDICTION ENDPOINTS

### 11. POST `/api/v1/trends` - Comprehensive Health Prediction
Full predictive analysis and disease risk assessment.

**Request Body Schema:**
```json
{
  "user_profile": {
    "age": "integer (required)",
    "gender": "M|F (required)",
    "height_cm": "number (optional)",
    "weight_kg": "number (optional)",
    "bmi": "number (calculated if height/weight provided)",
    "known_prakriti": "enum (optional)",
    "current_symptoms": ["string array"],
    "family_history": ["string array"],
    "medical_history": ["string array"],
    "current_medications": ["string array"],
    "lifestyle": {
      "diet": "vegetarian|non-vegetarian|mixed",
      "exercise_level": "sedentary|light|moderate|vigorous",
      "sleep_hours": "number",
      "sleep_quality": "poor|fair|good|excellent",
      "stress_level": "low|moderate|high|severe",
      "work_type": "sedentary|active"
    },
    "current_season": "varsha|sharad|hemanta|shishira|vasanta|grishma (optional)"
  }
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/trends \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "age": 45,
      "gender": "M",
      "height_cm": 175,
      "weight_kg": 85,
      "known_prakriti": "kapha_pitta",
      "current_symptoms": ["fatigue", "joint stiffness", "weight gain"],
      "family_history": ["diabetes", "hypertension"],
      "lifestyle": {
        "diet": "non-vegetarian",
        "exercise_level": "sedentary",
        "sleep_hours": 6,
        "stress_level": "high"
      }
    }
  }'
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": {
    "query_id": "trend123abc",
    "assessment_date": "2026-01-31T14:30:00Z",
    "prakriti_analysis": {
      "determined_prakriti": "kapha_pitta",
      "confidence": 0.87,
      "prakriti_breakdown": {
        "kapha": 45,
        "pitta": 40,
        "vata": 15
      },
      "indicators": ["Weight tendency", "Strong digestion", "Stable mind"]
    },
    "vikriti_analysis": {
      "current_imbalance": "kapha",
      "severity": "moderate",
      "description": "Kapha imbalance manifesting as weight gain and lethargy",
      "affected_doshas": {
        "kapha": {
          "state": "vriddhi",
          "signs": ["Weight gain", "Sluggishness", "Excess sleep"]
        }
      }
    },
    "disease_risk_predictions": [
      {
        "disease_name": "Type 2 Diabetes",
        "risk_level": "high",
        "probability_6_months": 0.15,
        "probability_1_year": 0.28,
        "probability_5_years": 0.65,
        "risk_factors_present": ["Weight gain", "Sedentary lifestyle", "Family history"],
        "dosha_connection": "Kapha-Pitta imbalance affecting Meda dhatu and Agni",
        "early_warning_signs": ["Increased thirst", "Frequent urination", "Fatigue"],
        "preventive_herbs": ["Guduchi", "Neem", "Fenugreek"],
        "dietary_prevention": [
          "Reduce refined carbohydrates",
          "Include bitter foods",
          "Warm spices (turmeric, ginger)"
        ],
        "lifestyle_prevention": [
          "Daily exercise 30+ minutes",
          "Regular meal times",
          "Stress management"
        ]
      },
      {
        "disease_name": "Hypertension",
        "risk_level": "moderate",
        "probability_1_year": 0.22,
        "probability_5_years": 0.45
      }
    ],
    "dosha_trajectory": {
      "current_state": "Kapha and Pitta aggravated",
      "if_uncorrected_6_months": "Further weight gain, possible skin issues",
      "if_uncorrected_1_year": "Chronic disease manifestation likely",
      "if_uncorrected_5_years": "Multiple complications possible",
      "correction_path": "Kapha-reducing diet, regular exercise, Pitta-cooling herbs"
    },
    "agni_assessment": {
      "current_agni_type": "manda",
      "ama_level": "moderate",
      "ama_signs": ["Sluggishness", "Weight gain", "Digestive heaviness"],
      "agni_correction_protocol": [
        "Warm, light foods",
        "Spices to kindle fire",
        "Regular exercise"
      ]
    },
    "corrective_measures": {
      "diet": {
        "foods_to_add": ["Mung beans", "Leafy greens", "Ginger"],
        "foods_to_avoid": ["Heavy dairy", "Refined sugar", "Fried foods"],
        "meal_timing": "Regular times (7am, 12pm, 6pm)",
        "portion_guidance": "Moderate portions, eat when hungry"
      },
      "lifestyle": {
        "wake_time": "6:00 AM",
        "sleep_time": "10:00 PM",
        "exercise_type": "Brisk walking or yoga",
        "exercise_timing": "Morning or before sunset",
        "stress_management": ["Meditation", "Pranayama", "Abhyanga massage"]
      },
      "herbs": [
        {
          "name": "Guduchi",
          "dosage": "500mg",
          "timing": "Twice daily with meals",
          "purpose": "Boost immunity and metabolism"
        }
      ],
      "panchakarma": {
        "indicated": true,
        "urgency": "recommended",
        "procedures": ["Udwartana", "Virechana"],
        "optimal_season": "Sharad (autumn)",
        "frequency": "Annual or bi-annual"
      }
    },
    "health_scores": {
      "overall": 58,
      "dosha_balance": 52,
      "agni": 45,
      "ojas": 60,
      "dhatu_health": 55,
      "mala_elimination": 48
    },
    "priority_plan": {
      "immediate_1_month": [
        "Start daily 30-min walk",
        "Eliminate refined sugar",
        "Take Guduchi supplement"
      ],
      "short_term_3_months": [
        "Weight loss target: 3-5kg",
        "Agni-strengthening diet routine",
        "Stress management practice"
      ],
      "long_term_1_year": [
        "Achieve healthy BMI",
        "Complete Panchakarma course",
        "Establish sustainable lifestyle"
      ]
    }
  }
}
```

---

### 12. POST `/api/v1/trends/quick` - Quick Risk Assessment
Rapid screening based on symptoms (no profile needed).

**Request Body Schema:**
```json
{
  "symptoms": ["string array (required)"],
  "age": "integer (optional)",
  "gender": "M|F (optional)"
}
```

**Response:**
Simplified version of `/trends` with just disease risks and immediate recommendations.

---

## AI DIAGNOSIS MODULE ENDPOINTS

### 13. POST `/api/v1/diagnose` - Full AI Diagnosis
Comprehensive diagnosis using Nidana Panchaka framework.

**Request Body Schema:**
```json
{
  "symptoms": ["string array (required) - List of symptoms"],
  "user_profile": {
    "age": "integer (optional)",
    "gender": "M|F (optional)",
    "known_prakriti": "enum (optional)",
    "medical_history": ["string array (optional)"],
    "current_medications": ["string array (optional)"],
    "duration": "string (optional) - e.g., '2 weeks'"
  }
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": [
      "joint pain worse in morning",
      "swelling in small joints",
      "stiffness > 1 hour",
      "fatigue"
    ],
    "user_profile": {
      "age": 42,
      "gender": "F",
      "known_prakriti": "vata",
      "medical_history": ["thyroid disorder"]
    }
  }'
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": {
    "query_id": "diag456xyz",
    "timestamp": "2026-01-31T14:45:00Z",
    "differential_diagnosis": [
      {
        "rank": 1,
        "ayurvedic_name": "Amavata",
        "modern_correlation": "Rheumatoid Arthritis",
        "confidence": 0.92,
        "supporting_symptoms": [
          "joint pain",
          "swelling",
          "morning stiffness"
        ],
        "opposing_symptoms": []
      },
      {
        "rank": 2,
        "ayurvedic_name": "Sandhigata Vata",
        "modern_correlation": "Osteoarthritis",
        "confidence": 0.65,
        "supporting_symptoms": ["joint pain", "stiffness"]
      }
    ],
    "prakriti_assessment": {
      "determined_prakriti": "vata",
      "confidence": 0.78
    },
    "vikriti_assessment": {
      "imbalanced_dosha": "vata",
      "imbalance_type": "aggravated",
      "severity": "moderate"
    },
    "red_flags": [],
    "requires_emergency": false,
    "recommended_investigations": [
      "ESR (Erythrocyte Sedimentation Rate)",
      "RA Factor (Rheumatoid Factor)",
      "CRP (C-Reactive Protein)"
    ]
  }
}
```

---

### 14. POST `/api/v1/diagnose/prakriti` - Prakriti Assessment
Detailed constitution analysis through questionnaire.

**Request Body Schema:**
```json
{
  "physical_traits": {
    "body_frame": "thin|medium|broad",
    "body_weight": "low|normal|high",
    "skin": "dry|normal|oily",
    "skin_color": "dark|medium|fair",
    "hair": "dry|normal|oily",
    "hair_type": "thin|medium|thick",
    "hair_color": "black|brown|blonde",
    "appetite": "poor|normal|strong",
    "appetite_consistency": "variable|normal|consistent",
    "digestion": "poor|normal|strong",
    "stool_consistency": "loose|normal|hard",
    "stool_frequency": "variable|normal|constipated",
    "urine": "scanty|normal|profuse",
    "sweat": "scanty|normal|profuse"
  },
  "mental_traits": {
    "mind": "active|moderate|calm",
    "memory": "quick_forget|average|strong",
    "concentration": "poor|average|strong",
    "sleep_pattern": "light|moderate|deep",
    "sleep_need": "little|moderate|much",
    "speech_style": "fast|moderate|slow",
    "thinking_style": "quick|moderate|slow",
    "emotions": "variable|stable|emotional",
    "emotional_response": "anxious|balanced|calm"
  },
  "preferences": {
    "climate": "warm|moderate|cold",
    "food_temperature": "hot|moderate|cold",
    "food_taste": "light|varied|heavy"
  }
}
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": {
    "prakriti": "vata",
    "prakriti_percentages": {
      "vata": 65,
      "pitta": 25,
      "kapha": 10
    },
    "confidence": 0.85,
    "characteristics": [
      "Quick metabolism",
      "Variable appetite",
      "Light sleep",
      "Active mind"
    ],
    "vulnerabilities": [
      "Anxiety tendency",
      "Joint issues",
      "Digestive irregularity",
      "Dry skin"
    ],
    "balancing_recommendations": {
      "diet": [
        "Warm, oily, grounding foods",
        "Sweet, sour, salty tastes",
        "Regular meal times",
        "Avoid excessive raw/cold foods"
      ],
      "lifestyle": [
        "Consistent daily routine",
        "Oil massage (Abhyanga) daily",
        "Grounding activities",
        "Warm weather preferred"
      ],
      "herbs": [
        "Ashwagandha",
        "Bala",
        "Shatavari",
        "Brahmi"
      ]
    }
  }
}
```

---

### 15. POST `/api/v1/diagnose/red-flags` - Emergency Warning Signs
Identifies immediately dangerous symptoms.

**Request Body Schema:**
```json
{
  "symptoms": ["string array (required)"]
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/diagnose/red-flags \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": [
      "severe chest pain",
      "difficulty breathing",
      "sudden weakness"
    ]
  }'
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": {
    "red_flags": [
      "severe chest pain",
      "difficulty breathing"
    ],
    "requires_emergency": true,
    "recommendation": "SEEK IMMEDIATE MEDICAL ATTENTION",
    "emergency_services": "Call 911 or local emergency number"
  }
}
```

---

## PERSONALIZED TREATMENT ENDPOINTS

### 16. POST `/api/v1/treatment-plan` - Generate Treatment Protocol
Multi-phase personalized treatment algorithm.

**Request Body Schema:**
```json
{
  "diagnosis": "string (required) - Condition to treat",
  "profile": {
    "age": "integer (required)",
    "gender": "M|F (required)",
    "known_prakriti": "enum (optional)",
    "vikriti": "enum (optional)",
    "agni_type": "sama|vishama|tikshna|manda (optional)",
    "bala": "hina|madhyama|uttama (optional)",
    "current_medications": ["string array (optional)"],
    "allergies": ["string array (optional)"],
    "contraindications": ["string array (optional)"],
    "lifestyle": {
      "diet": "string (optional)",
      "exercise": "string (optional)",
      "stress_level": "string (optional)"
    },
    "medical_history": ["string array (optional)"]
  }
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/treatment-plan \
  -H "Content-Type: application/json" \
  -d '{
    "diagnosis": "Amavata (Rheumatoid Arthritis)",
    "profile": {
      "age": 45,
      "gender": "F",
      "known_prakriti": "vata_kapha",
      "bala": "madhyama",
      "current_medications": ["levothyroxine"],
      "lifestyle": {
        "diet": "vegetarian",
        "exercise": "sedentary",
        "stress_level": "high"
      }
    }
  }'
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": {
    "plan_id": "plan789def",
    "created_at": "2026-01-31T15:00:00Z",
    "diagnosis": "Amavata",
    "patient_profile": {...},
    "treatment_goals": [
      "Reduce inflammation",
      "Strengthen digestive fire",
      "Rebuild tissue (Dhatus)"
    ],
    "contraindications": ["NSAIDs sensitivity"],
    "phases": [
      {
        "phase_number": 1,
        "phase_name": "Nidana Parivarjana",
        "duration": "7-14 days",
        "objectives": [
          "Identify and remove causative factors",
          "Patient education"
        ],
        "dietary_changes": {
          "foods_to_include": ["Ginger", "Turmeric", "Warm broths"],
          "foods_to_avoid": ["Cold foods", "Heavy dairy", "Processed foods"]
        },
        "lifestyle_modifications": [
          "Regular routine",
          "Adequate rest",
          "Stress reduction"
        ],
        "monitoring": [
          "Track symptom changes daily",
          "Monitor energy levels"
        ]
      },
      {
        "phase_number": 2,
        "phase_name": "Deepana-Pachana",
        "duration": "14-21 days",
        "objectives": [
          "Kindle digestive fire",
          "Begin digesting accumulated ama"
        ],
        "formulations": [
          {
            "name": "Trikatu Churna",
            "dosage": "1/4 tsp",
            "frequency": "Twice daily",
            "timing": "Before meals",
            "anupana": "Warm water",
            "duration": "3 weeks"
          }
        ]
      },
      {
        "phase_number": 3,
        "phase_name": "Shodhana (Panchakarma)",
        "duration": "28-42 days",
        "panchakarma_procedures": [
          {
            "procedure": "Virechana",
            "frequency": "Once weekly",
            "duration": "4 weeks",
            "purpose": "Purge excess Pitta and ama"
          }
        ]
      },
      {
        "phase_number": 4,
        "phase_name": "Shamana",
        "duration": "60+ days",
        "objectives": [
          "Palliative treatment",
          "Symptom management"
        ],
        "formulations": [
          {
            "name": "Maharasnadi Taila",
            "dosage": "10ml",
            "frequency": "Twice daily",
            "anupana": "Warm water",
            "duration": "Ongoing"
          }
        ]
      },
      {
        "phase_number": 5,
        "phase_name": "Rasayana",
        "duration": "90+ days",
        "objectives": [
          "Tissue rejuvenation",
          "Immune strengthening"
        ],
        "formulations": [
          {
            "name": "Ashwagandha Churna",
            "dosage": "1/2 tsp",
            "frequency": "Once daily",
            "timing": "Evening with milk",
            "duration": "Indefinite"
          }
        ]
      }
    ],
    "panchakarma_indicated": true,
    "panchakarma_procedures": ["Virechana", "Basti", "Nasya"],
    "rasayana_protocol": ["Ashwagandha", "Shatavari"],
    "total_duration": "3-6 months",
    "follow_up_schedule": [
      "Weekly for first month",
      "Bi-weekly for next 2 months",
      "Monthly thereafter"
    ],
    "emergency_signs": [
      "Severe pain",
      "High fever (>103F)",
      "Inability to move"
    ],
    "compatibility_score": 0.87
  }
}
```

---

## CLINICAL DECISION SUPPORT ENDPOINTS

### 17. POST `/api/v1/decision-support/interactions` - Herb-Drug Interaction Check
Identifies interactions between Ayurvedic herbs and allopathic medicines.

**Request Body Schema:**
```json
{
  "herbs_medicines": ["string array (required) - herb/medicine names"]
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/decision-support/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "herbs_medicines": [
      "ashwagandha",
      "brahmi",
      "warfarin",
      "metformin"
    ]
  }'
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": [
    {
      "item1": "ashwagandha",
      "item2": "warfarin",
      "interaction_type": "pharmacodynamic",
      "severity": "moderate",
      "severity_color": "orange",
      "mechanism": "May enhance anticoagulant effect",
      "clinical_significance": "INR may increase, increasing bleeding risk",
      "recommendation": "Monitor INR closely. Consider ashwagandha dose reduction or alternative herb.",
      "monitoring_parameters": ["INR", "Bleeding signs"]
    },
    {
      "item1": "brahmi",
      "item2": "warfarin",
      "interaction_type": "minor",
      "severity": "mild",
      "mechanism": "Minimal interaction expected"
    },
    {
      "item1": "ashwagandha",
      "item2": "metformin",
      "interaction_type": "none",
      "severity": "none",
      "mechanism": "No significant interaction"
    }
  ]
}
```

---

### 18. POST `/api/v1/decision-support/contraindications` - Contraindication Check
Determines if treatments are contraindicated for patient conditions.

**Request Body Schema:**
```json
{
  "treatment": "string (required) - Treatment/procedure name",
  "patient_conditions": ["string array (required) - Patient's conditions/states"]
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/decision-support/contraindications \
  -H "Content-Type: application/json" \
  -d '{
    "treatment": "virechana",
    "patient_conditions": ["pregnancy", "debilitated", "heart valve disease"]
  }'
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": [
    {
      "treatment": "virechana",
      "contraindicated_for": "pregnancy",
      "severity": "absolute",
      "severity_color": "red",
      "contraindication_type": "absolute_contraindication",
      "reason": "Virechana can harm fetus and cause miscarriage",
      "alternative": "Mild Shamana therapy recommended. Panchakarma after delivery.",
      "timing_note": "Can be done 6 weeks postpartum"
    },
    {
      "treatment": "virechana",
      "contraindicated_for": "debilitated",
      "severity": "relative",
      "severity_color": "yellow",
      "contraindication_type": "relative_contraindication",
      "reason": "Patient lacks strength for purification therapy",
      "alternative": "Build strength with Brimhana therapy first (1-2 weeks), then consider Shodhana"
    },
    {
      "treatment": "virechana",
      "contraindicated_for": "heart valve disease",
      "severity": "absolute",
      "reason": "Risk of dehydration complications",
      "alternative": "Consult cardiologist. Use Shamana only."
    }
  ]
}
```

---

### 19. POST `/api/v1/decision-support` - Comprehensive Decision Support
Full clinical decision support for complex scenarios.

**Request Body Schema:**
```json
{
  "scenario": "string (required) - Clinical scenario description",
  "patient_profile": {
    "age": "integer",
    "gender": "M|F",
    "conditions": ["string array"],
    "current_medications": ["string array"],
    "bala": "hina|madhyama|uttama",
    "agni": "sama|vishama|tikshna|manda"
  }
}
```

**Response Includes:**
- Primary treatment recommendation
- Contraindication analysis
- Drug interaction analysis
- Personalized dosing
- Monitoring parameters
- Alternative treatments if primary contraindicated

---

## DISEASE PROGRESSION ENDPOINTS

### 20. POST `/api/v1/progression` - Model Disease Progression
Models disease progression through Shat Kriyakala (6-stage) framework.

**Request Body Schema:**
```json
{
  "disease": "string (required) - Disease name",
  "current_stage": "integer (required, 1-6) - Current Shat Kriyakala stage",
  "duration_days": "integer (required) - Days since disease onset"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/progression \
  -H "Content-Type: application/json" \
  -d '{
    "disease": "Type 2 Diabetes",
    "current_stage": 2,
    "duration_days": 90
  }'
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": {
    "disease": "Type 2 Diabetes",
    "current_stage": {
      "number": 2,
      "name": "Prakopa",
      "english_name": "Provocation/Aggravation",
      "description": "Doshas are being aggravated but not yet spread to other body parts",
      "characteristics": ["Subtle symptoms", "Aggravation without localization"],
      "duration": "Variable, typically weeks to months"
    },
    "stage_details": {
      "pathophysiology": "Kapha and Pitta vitiation increasing, Agni declining",
      "clinical_features": ["Increased thirst", "Weight changes", "Fatigue"],
      "tissue_involvement": "Meda dhatu primarily affected"
    },
    "progression_timeline": [
      {
        "stage": 3,
        "name": "Prasara",
        "expected_timeframe": "45-60 days from now",
        "expected_manifestations": "Symptoms spreading to related tissues"
      },
      {
        "stage": 4,
        "name": "Sthana Samshraya",
        "expected_timeframe": "90-120 days from now",
        "expected_manifestations": "Disease localization in weak organs"
      },
      {
        "stage": 5,
        "name": "Vyakti",
        "expected_timeframe": "150-180 days from now",
        "expected_manifestations": "Full disease manifestation"
      },
      {
        "stage": 6,
        "name": "Bheda",
        "expected_timeframe": "6+ months",
        "expected_manifestations": "Complications and chronicity"
      }
    ],
    "intervention_urgency": "high",
    "intervention_rationale": "Early intervention at Prakopa stage can prevent progression to Prasara",
    "recommended_interventions": [
      "Deepana-Pachana (digestive fire strengthening)",
      "Dietary modification",
      "Regular exercise protocol",
      "Stress reduction techniques"
    ],
    "prevention_priorities": [
      "Kindle Agni to prevent ama formation",
      "Reduce Kapha through diet/lifestyle",
      "Regular blood sugar monitoring"
    ]
  }
}
```

**Shat Kriyakala Stages:**

| Stage | Name | Translation | Characteristics | Intervention Point |
|-------|------|-------------|-----------------|-------------------|
| 1 | Sanchaya | Accumulation | Dosha imbalance begins | Prevention possible |
| 2 | Prakopa | Provocation | Doshas aggravated | Highly reversible |
| 3 | Prasara | Spread | Moves to other tissues | Treatment urgent |
| 4 | Sthana Samshraya | Localization | Fixed in weak organ | Symptomatic treatment |
| 5 | Vyakti | Manifestation | Full disease present | Chronic management |
| 6 | Bheda | Complications | Sequelae develop | Damage control |

---

### 21. POST `/api/v1/progression/intervention` - Get Stage-Specific Intervention
Tailored interventions based on current disease stage.

**Request Body Schema:**
```json
{
  "disease": "string (required)",
  "current_stage": "integer (required, 1-6)"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/progression/intervention \
  -H "Content-Type: application/json" \
  -d '{
    "disease": "Type 2 Diabetes",
    "current_stage": 3
  }'
```

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": {
    "stage": 3,
    "stage_name": "Prasara",
    "intervention_type": "Shodhana (Purification) Indicated",
    "stage_description": "Disease spreading - doshas moving to other tissues",
    "specific_procedures": [
      {
        "procedure": "Virechana",
        "frequency": "Weekly",
        "duration": "4-6 weeks",
        "rationale": "Purge excess Pitta-Kapha to stop progression"
      },
      {
        "procedure": "Basti",
        "frequency": "Bi-weekly",
        "duration": "8 weeks",
        "rationale": "Support digestive function"
      }
    ],
    "urgency": "high",
    "urgency_color": "red",
    "rationale": "At Prasara stage, Shodhana can still prevent localization to specific organs. Delay increases chronicity risk.",
    "expected_outcomes": [
      "Stop disease progression",
      "Prevent stage 4 localization",
      "Restore metabolic balance"
    ],
    "follow_up_interval": "Every 2 weeks during procedures, then monthly"
  }
}
```

---

## BATCH & COMBINED ENDPOINTS

### 22. POST `/api/v1/query-all` - Query All Core Modules
Single request to query Doctor, Patient, and AYUSH modules simultaneously.

**Request Body Schema:**
```json
{
  "question": "string (required)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "question": "...",
    "doctor_response": "Clinical response for practitioners...",
    "patient_response": "Simplified response for patients...",
    "ayush_response": "Research-backed response with citations..."
  }
}
```

---

### 23. POST `/api/v1/batch/doctor` - Batch Doctor Queries
Process multiple questions in one request.

**Request Body Schema:**
```json
{
  "questions": ["string array (required, max 10)"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "processed_count": 3,
    "results": [
      {
        "question": "Treatment for Amavata",
        "response": "..."
      },
      {
        "question": "Panchakarma for skin diseases",
        "response": "..."
      }
    ]
  }
}
```

---

## REFERENCE DATA ENDPOINTS

### 24. GET `/api/v1/doshas` - Dosha Reference Information
Returns detailed information about Vata, Pitta, and Kapha doshas.

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": {
    "vata": {
      "element": "Air + Ether",
      "qualities": ["dry", "light", "cold", "mobile", "subtle"],
      "seat": "Large intestine, bones, nervous system",
      "functions": [
        "Movement",
        "Sensory perception",
        "Elimination",
        "Speech"
      ],
      "imbalance_signs": [
        "Anxiety",
        "Constipation",
        "Dry skin",
        "Joint pain"
      ]
    },
    "pitta": {
      "element": "Fire + Water",
      "qualities": ["hot", "sharp", "oily", "pungent"],
      "seat": "Small intestine, liver, blood",
      "functions": [
        "Digestion",
        "Metabolism",
        "Intelligence",
        "Courage"
      ],
      "imbalance_signs": [
        "Acidity",
        "Inflammation",
        "Anger",
        "Skin rashes"
      ]
    },
    "kapha": {
      "element": "Water + Earth",
      "qualities": ["heavy", "cold", "oily", "stable", "dull"],
      "seat": "Chest, stomach, joints",
      "functions": [
        "Stability",
        "Lubrication",
        "Strength",
        "Immunity"
      ],
      "imbalance_signs": [
        "Weight gain",
        "Lethargy",
        "Congestion",
        "Depression"
      ]
    }
  }
}
```

---

### 25. GET `/api/v1/dhatus` - Dhatu (Tissue) Reference
Returns the 7 tissue types and their functions.

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": {
    "dhatus": [
      {
        "number": 1,
        "name": "Rasa",
        "translation": "Plasma/Chyle",
        "elements": ["Water", "Fire"],
        "function": "Nourishment and immunity",
        "location": "Heart and vessels",
        "imbalance": ["Weakness", "Poor immunity", "Dry skin"]
      },
      {
        "number": 2,
        "name": "Rakta",
        "translation": "Blood",
        "elements": ["Fire", "Water"],
        "function": "Oxygenation and vitality",
        "location": "Liver and arteries",
        "imbalance": ["Anemia", "Skin conditions", "Inflammation"]
      },
      {
        "number": 3,
        "name": "Mamsa",
        "translation": "Muscle",
        "elements": ["Earth", "Water"],
        "function": "Strength and structure",
        "location": "Muscles and organs",
        "imbalance": ["Weakness", "Poor muscle tone", "Weight issues"]
      },
      {
        "number": 4,
        "name": "Meda",
        "translation": "Fat",
        "elements": ["Earth", "Water"],
        "function": "Lubrication and insulation",
        "location": "Subcutaneous tissue",
        "imbalance": ["Obesity", "Sluggishness", "Joint problems"]
      },
      {
        "number": 5,
        "name": "Asthi",
        "translation": "Bone",
        "elements": ["Air", "Earth"],
        "function": "Support and structure",
        "location": "Skeletal system",
        "imbalance": ["Weak bones", "Joint pain", "Poor teeth"]
      },
      {
        "number": 6,
        "name": "Majja",
        "translation": "Bone Marrow",
        "elements": ["Water", "Earth"],
        "function": "Nervous system and lubrication",
        "location": "Inside bones",
        "imbalance": ["Weakness", "Tremor", "Dizziness"]
      },
      {
        "number": 7,
        "name": "Shukra",
        "translation": "Reproductive",
        "elements": ["Water", "Earth"],
        "function": "Reproduction and vitality",
        "location": "Reproductive organs",
        "imbalance": ["Infertility", "Low libido", "Fatigue"]
      }
    ]
  }
}
```

---

### 26. GET `/api/v1/agni-types` - Digestive Fire Types Reference

**Response (HTTP 200):**
```json
{
  "success": true,
  "data": {
    "agni_types": [
      {
        "name": "Sama Agni",
        "translation": "Balanced Digestive Fire",
        "dosha_association": "Balanced",
        "characteristics": [
          "Regular appetite",
          "Good digestion",
          "Healthy elimination",
          "Strong immunity"
        ],
        "recommendations": ["Maintain current lifestyle", "Regular routine"]
      },
      {
        "name": "Vishama Agni",
        "translation": "Irregular Digestive Fire",
        "dosha_association": "Vata-predominant",
        "characteristics": [
          "Variable appetite",
          "Irregular digestion",
          "Bloating and gas",
          "Constipation alternating with loose stool"
        ],
        "recommendations": [
          "Warm, oily foods",
          "Spices: ginger, asafetida",
          "Regular meal times"
        ]
      },
      {
        "name": "Tikshna Agni",
        "translation": "Sharp/Strong Digestive Fire",
        "dosha_association": "Pitta-predominant",
        "characteristics": [
          "Strong appetite",
          "Quick digestion",
          "Hyperacidity",
          "Loose stools"
        ],
        "recommendations": [
          "Cool foods",
          "Coconut and ghee",
          "Avoid spicy foods",
          "Eat at moderate times"
        ]
      },
      {
        "name": "Manda Agni",
        "translation": "Weak Digestive Fire",
        "dosha_association": "Kapha-predominant",
        "characteristics": [
          "Poor appetite",
          "Slow digestion",
          "Heavy feeling",
          "Sluggishness"
        ],
        "recommendations": [
          "Light, dry foods",
          "Warm spices",
          "Ginger before meals",
          "Regular exercise"
        ]
      }
    ]
  }
}
```

---

## Data Models & Schemas

### User Profile Schema

```typescript
interface UserProfile {
  age?: number;
  gender?: "M" | "F";
  height_cm?: number;
  weight_kg?: number;
  bmi?: number;
  known_prakriti?: DoshaType;
  current_symptoms?: string[];
  family_history?: string[];
  medical_history?: string[];
  current_medications?: string[];
  allergies?: string[];
  lifestyle?: {
    diet?: "vegetarian" | "non-vegetarian" | "mixed";
    exercise_level?: "sedentary" | "light" | "moderate" | "vigorous";
    sleep_hours?: number;
    sleep_quality?: "poor" | "fair" | "good" | "excellent";
    stress_level?: "low" | "moderate" | "high" | "severe";
    work_type?: string;
  };
}
```

### Enums

```typescript
// Dosha Types
type DoshaType = 
  | "vata"
  | "pitta"
  | "kapha"
  | "vata_pitta"
  | "pitta_kapha"
  | "vata_kapha"
  | "kapha_pitta"
  | "tridosha";

// Dosha States
type DoshaState = "sama" | "vriddhi" | "kshaya";

// Agni Types
type AgniType = "sama" | "vishama" | "tikshna" | "manda";

// Bala (Strength)
type Bala = "hina" | "madhyama" | "uttama";

// Risk Levels
type RiskLevel = "low" | "moderate" | "high" | "critical";

// Severity
type Severity = "none" | "mild" | "moderate" | "severe" | "absolute" | "relative";

// Shat Kriyakala Stages
type DiseaseStage = 1 | 2 | 3 | 4 | 5 | 6;
```

---

## Integration Patterns

### Error Response Format

All errors follow this format:

```json
{
  "success": false,
  "detail": "Descriptive error message"
}
```

### HTTP Status Codes

| Code | Scenario |
|------|----------|
| 200 | Successful request |
| 400 | Bad request (invalid input) |
| 422 | Validation error (schema mismatch) |
| 500 | Internal server error (LLM failure) |
| 503 | Service unavailable (database issue) |

### Rate Limiting

- **Limit**: 100 requests per minute per IP
- **Header**: `X-RateLimit-Remaining`
- **Exceeded**: Returns 429 Too Many Requests

### Timeout

- **API Timeout**: 30 seconds per request
- **LLM Timeout**: 20 seconds per generation
- Long-running operations (Panchakarma planning) may take full 30 seconds

---

## Classical Text Sources

The API retrieves knowledge from three ChromaDB vector stores:

| Database | Source | Content | Documents |
|----------|--------|---------|-----------|
| `chroma_db_asthrid` | **Ashtanga Hridaya** by Vagbhata (7th century) | Comprehensive Ayurvedic treatise covering diagnostics, pathology, treatment | ~1200 |
| `chroma_sushruta` | **Sushruta Samhita** (1200 BCE) | Surgical techniques, anatomy, pharmacology | ~800 |
| `chroma_db_ayurgenix` | **AyurGenix Clinical Database** | 367 disease profiles with modern correlations, epidemiology | 367 |

---

## Examples & Workflows

### Workflow 1: Patient with Joint Pain

```
1. POST /api/v1/diagnose/red-flags
   Input: ["severe joint pain", "fever"]
   Output: Check if emergency

2. POST /api/v1/diagnose
   Input: Symptoms + age + gender
   Output: Differential diagnosis (Amavata vs Sandhigata Vata)

3. POST /api/v1/trends
   Input: Full health profile
   Output: Disease progression risks

4. POST /api/v1/treatment-plan
   Input: Top diagnosis + patient profile
   Output: 5-phase treatment protocol

5. POST /api/v1/decision-support/interactions
   Input: Proposed medicines + current meds
   Output: Safety warnings

6. POST /api/v1/progression
   Input: Disease + current stage
   Output: Timeline and urgency
```

### Workflow 2: Preventive Care

```
1. POST /api/v1/diagnose/prakriti
   Input: Questionnaire
   Output: Constitution (Prakriti)

2. POST /api/v1/trends
   Input: Complete health profile
   Output: Disease risk predictions

3. GET /api/v1/doshas
   Output: Educational information

4. POST /api/v1/chat/patient
   Input: Questions about prevention
   Output: Personalized guidance
```

### Workflow 3: Emergency Screening

```
1. POST /api/v1/diagnose/red-flags
   Input: Patient symptoms
   If: requires_emergency = true
   → Recommend immediate medical attention
   Else: Continue to full diagnosis
```

---

## Performance Optimization Tips

1. **Cache prakriti assessments** - They don't change frequently
2. **Batch similar queries** - Use `/api/v1/batch/doctor` for multiple questions
3. **Use `/trends/quick`** for rapid screening (faster than full `/trends`)
4. **Store diagnosis results** - Don't re-diagnose same patient
5. **Request only needed modules** - Use specific endpoints, not `/query-all`

---

## LLM Configuration (For Reference)

```python
# Current Settings
model = "openai/gpt-oss-120b"  # Via Groq API
temperature = 0.1               # Low for consistency
max_tokens = 4096              # Per response
context_limit = 6000           # Max characters of context

# Note: If rate limited, the system automatically falls back to:
# model = "llama-3.3-70b-versatile"

# Request tokens budget:
# - Prompt: ~2000 tokens avg
# - Context: ~1500 tokens avg  
# - Response: ~1500 tokens avg
# Total: ~5000 tokens per request (within 12K limit for llama)
```

---

## Support & Debugging

### Common Issues

**Issue**: "Rate Limited - Too many requests"
- **Solution**: Implement exponential backoff (1s, 2s, 4s, 8s...)
- **Alternative**: Use `/trends/quick` instead of `/trends`

**Issue**: "Internal Server Error on /diagnose"
- **Solution**: Ensure all symptom inputs are strings (not integers)
- **Check**: `symptoms` array must have at least 1 element

**Issue**: "Empty prediction results"
- **Solution**: Ensure user_profile has at least 3 fields filled
- **Required minimum**: age, gender, symptoms

### Debugging

Add these headers to requests:
```
X-Debug-Mode: true
X-Verbose: true
```

Response will include execution times and prompt text used.

---

**Last Updated**: January 31, 2026  
**API Version**: 2.1.0  
**Status**: Production Ready

Built for the Ayurveda + AI Hackathon 🌿
