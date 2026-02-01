# 🌿 Ayurveda Modular API v2.0

A comprehensive, AI-powered REST API for Ayurvedic healthcare, featuring RAG (Retrieval-Augmented Generation) from classical texts, clinical decision support, and predictive health analytics.

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Architecture](#-architecture)
3. [Quick Start](#-quick-start)
4. [API Endpoints Reference](#-api-endpoints-reference)
   - [Health & System](#health--system)
   - [Core Modules](#core-modules)
   - [Chat Interface](#chat-interface)
   - [Future Trends & Prediction](#future-trends--prediction)
   - [AI Diagnosis Module](#ai-diagnosis-module)
   - [Personalized Treatment Module](#personalized-treatment-module)
   - [Clinical Decision Support](#clinical-decision-support)
   - [Disease Progression Module](#disease-progression-module)
   - [Batch & Combined](#batch--combined)
   - [Reference Data](#reference-data)
5. [Data Models](#-data-models)
6. [Classical Text Sources](#-classical-text-sources)
7. [Error Handling](#-error-handling)

---

## 🎯 Overview

This API provides **8 specialized modules** for Ayurvedic healthcare:

| Module | Purpose | Use Case |
|--------|---------|----------|
| **DoctorModule** | Clinical JSON outputs for practitioners | EMR integration, clinical documentation |
| **PatientModule** | User-friendly guidance | Patient-facing apps, health portals |
| **AyushModule** | AYUSH Ministry aligned analysis | Government compliance, research |
| **FutureTrendsModule** | Health risk prediction | Preventive care, wellness programs |
| **DiagnosisModule** | AI-assisted diagnosis | Clinical decision support |
| **PersonalizedTreatmentModule** | Treatment algorithms | Treatment planning |
| **DecisionSupportModule** | Drug interactions & contraindications | Safety checks |
| **ProgressionModelingModule** | Disease progression modeling | Prognosis, intervention timing |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Server (ayurveda_server.py)         │
├─────────────────────────────────────────────────────────────────┤
│                     AyurvedaAPI (ayurveda_api.py)               │
├─────────────┬─────────────┬─────────────┬───────────────────────┤
│  Doctor     │  Patient    │   AYUSH     │   FutureTrends        │
│  Module     │  Module     │   Module    │   Module              │
├─────────────┼─────────────┼─────────────┼───────────────────────┤
│  Diagnosis  │ Treatment   │  Decision   │  Progression          │
│  Module     │  Module     │  Support    │  Modeling             │
├─────────────┴─────────────┴─────────────┴───────────────────────┤
│                 AyurvedaRAGEngine (Vector Retrieval)            │
├─────────────────────────────────────────────────────────────────┤
│  ChromaDB: Ashtanga Hridaya │ Sushruta Samhita │ AyurGenix DB   │
└─────────────────────────────────────────────────────────────────┘
```

**LLM Backend**: Groq API with `openai/gpt-oss-120b` model  
**Vector Store**: ChromaDB with HuggingFace embeddings  
**Framework**: FastAPI with Pydantic validation

---

## 🚀 Quick Start

### Prerequisites

```bash
pip install fastapi uvicorn langchain langchain-groq chromadb pydantic
```

### Environment Setup

```bash
export GROQ_API_KEY="your-groq-api-key"
```

### Start Server

```bash
python ayurveda_server.py
# Server runs on http://localhost:8000
```

### API Documentation

| Interface | URL |
|-----------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

---

## 📡 API Endpoints Reference

### Health & System

#### `GET /` - Root
Returns API welcome message and documentation links.

#### `GET /api/v1/health` - Health Check
Returns server status and module availability.

```bash
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "modules": ["doctor", "patient", "ayush", "trends", "diagnosis", "treatment", "decision_support", "progression"]
}
```

---

### Core Modules

#### `POST /api/v1/doctor` - Doctor Module Query
Clinical query endpoint returning structured JSON for healthcare practitioners.

**Request:**
```json
{
  "question": "What is the Ayurvedic treatment for Amavata (rheumatoid arthritis)?",
  "user_profile": {
    "age": 45,
    "gender": "F",
    "known_prakriti": "vata_kapha"
  }
}
```

**Response includes:**
- `clinical_assessment`: Samprapti (pathogenesis), dosha analysis, dhatu involvement
- `treatment_protocol`: Shodhana, Shamana, Rasayana recommendations
- `formulations`: Specific Ayurvedic medicines with dosages
- `classical_references`: Citations from Ashtanga Hridaya, Sushruta Samhita

---

#### `POST /api/v1/patient` - Patient Module Query
User-friendly responses for patients and general public.

**Request:**
```json
{
  "question": "How can I improve my digestion naturally?"
}
```

**Response includes:**
- Simple language explanations
- Practical home remedies
- Dietary recommendations
- Lifestyle modifications

---

#### `POST /api/v1/ayush` - AYUSH Module Query
Analysis aligned with AYUSH Ministry guidelines and WHO traditional medicine standards.

**Request:**
```json
{
  "question": "Evidence-based research on Ashwagandha for stress"
}
```

**Response includes:**
- Classical references with verse citations
- Modern research integration
- Safety and efficacy data
- Regulatory considerations

---

### Chat Interface

Conversational endpoints for flexible, natural language interactions.

#### `POST /api/v1/chat/doctor` - Doctor Chat
```json
{
  "query": "Explain the treatment approach for a patient with Vata-predominant IBS"
}
```

**Response:**
```json
{
  "success": true,
  "response": "For Vata-predominant IBS (Grahani)...",
  "references": [
    {"source": "Ashtanga Hridaya", "chapter": "Chikitsa Sthana 10"}
  ],
  "module": "doctor"
}
```

#### `POST /api/v1/chat/patient` - Patient Chat
Same format, simplified language for patients.

#### `POST /api/v1/chat/ayush` - AYUSH Chat
Same format, with research and regulatory focus.

#### `POST /api/v1/chat/all` - Multi-Module Chat
Query all three modules simultaneously for comprehensive responses.

```json
{
  "query": "Weekly treatment plan for managing chronic fatigue",
  "include_modules": ["doctor", "patient", "ayush"]
}
```

---

### Future Trends & Prediction

#### `POST /api/v1/trends` - Comprehensive Health Prediction
Full predictive analysis based on user health profile.

**Request:**
```json
{
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
      "exercise": "sedentary",
      "sleep_hours": 6,
      "stress_level": "high"
    },
    "medical_history": ["hypothyroidism"]
  }
}
```

**Response includes:**
- `prakriti_analysis`: Constitution determination with confidence score
- `vikriti_analysis`: Current dosha imbalance assessment
- `disease_risk_predictions`: Array of diseases with probability scores
- `dosha_trajectory`: Predicted progression if uncorrected
- `agni_assessment`: Digestive fire status and ama (toxin) levels
- `corrective_measures`: Diet, lifestyle, herbs, panchakarma recommendations
- `health_scores`: Overall health metrics (0-100)
- `priority_plan`: Immediate, short-term, long-term action items

---

#### `POST /api/v1/trends/quick` - Quick Risk Assessment
Rapid screening based on symptoms only.

**Request:**
```json
{
  "symptoms": ["fatigue", "bloating", "brain fog"],
  "age": 35,
  "gender": "F"
}
```

---

### AI Diagnosis Module

#### `POST /api/v1/diagnose` - Full AI Diagnosis
Comprehensive diagnosis using Nidana Panchaka framework.

**Request:**
```json
{
  "symptoms": [
    "joint pain worse in morning",
    "swelling in small joints",
    "stiffness lasting > 1 hour",
    "fatigue"
  ],
  "user_profile": {
    "age": 42,
    "gender": "F",
    "known_prakriti": "vata",
    "medical_history": ["thyroid disorder"]
  }
}
```

**Response includes:**
- `differential_diagnosis`: Ranked list of possible conditions
  - `condition_name`: Ayurvedic name (e.g., "Amavata")
  - `modern_correlation`: Western equivalent (e.g., "Rheumatoid Arthritis")
  - `confidence`: 0.0 to 1.0
  - `supporting_symptoms`: Which symptoms match
- `prakriti_assessment`: Constitution analysis
- `vikriti_assessment`: Current imbalance
- `red_flags`: Emergency warning signs if present
- `recommended_investigations`: Suggested tests/examinations

---

#### `POST /api/v1/diagnose/prakriti` - Prakriti Assessment
Detailed constitution analysis.

**Request:**
```json
{
  "physical_traits": {
    "body_frame": "thin",
    "skin": "dry",
    "hair": "dry, rough",
    "appetite": "variable",
    "digestion": "irregular"
  },
  "mental_traits": {
    "mind": "quick, restless",
    "memory": "quick to learn, quick to forget",
    "sleep": "light, interrupted"
  },
  "preferences": {
    "climate": "dislikes cold",
    "food": "prefers warm foods"
  }
}
```

**Response:**
```json
{
  "prakriti": "vata",
  "prakriti_percentage": {
    "vata": 65,
    "pitta": 25,
    "kapha": 10
  },
  "confidence": 0.85,
  "characteristics": ["Quick metabolism", "Variable appetite", "Light sleep"],
  "vulnerabilities": ["Anxiety", "Joint issues", "Digestive irregularity"],
  "balancing_recommendations": {
    "diet": ["Warm, oily, grounding foods"],
    "lifestyle": ["Regular routine", "Oil massage (Abhyanga)"],
    "herbs": ["Ashwagandha", "Bala", "Shatavari"]
  }
}
```

---

#### `POST /api/v1/diagnose/red-flags` - Emergency Warning Signs Check
Identifies symptoms requiring immediate medical attention.

**Request:**
```json
{
  "symptoms": [
    "severe chest pain",
    "difficulty breathing",
    "sudden weakness"
  ]
}
```

**Response:**
```json
{
  "red_flags": [
    "severe chest pain",
    "difficulty breathing"
  ],
  "requires_emergency": true,
  "recommendation": "SEEK IMMEDIATE MEDICAL ATTENTION"
}
```

---

### Personalized Treatment Module

#### `POST /api/v1/treatment-plan` - Generate Treatment Protocol
Multi-phase personalized treatment algorithm.

**Request:**
```json
{
  "diagnosis": "Amavata (Rheumatoid Arthritis)",
  "profile": {
    "age": 45,
    "gender": "F",
    "agni_type": "vishama",
    "bala": "madhyama",
    "known_prakriti": "vata_kapha",
    "vikriti": "vata_kapha",
    "current_medications": ["levothyroxine"],
    "lifestyle": {
      "diet": "vegetarian",
      "exercise": "sedentary",
      "stress_level": "high"
    },
    "medical_history": ["thyroid disorder"]
  }
}
```

**Response includes:**
- `plan_id`: Unique treatment protocol ID
- `treatment_goals`: Specific therapeutic objectives
- `phases`: Array of treatment phases:
  1. **Nidana Parivarjana**: Removing causative factors
  2. **Deepana-Pachana**: Kindling digestive fire, digesting ama
  3. **Shodhana (Panchakarma)**: Purification therapies
  4. **Shamana**: Palliative treatment
  5. **Rasayana**: Rejuvenation therapy
- `formulations`: Specific medicines with:
  - Name (Sanskrit and English)
  - Dosage
  - Anupana (vehicle)
  - Timing
  - Duration
- `pathya` (Do's): Recommended diet and activities
- `apathya` (Don'ts): Contraindicated foods and activities
- `panchakarma_indicated`: Boolean + specific procedures if true
- `follow_up_schedule`: Review appointments
- `emergency_signs`: When to seek immediate help

---

### Clinical Decision Support

#### `POST /api/v1/decision-support/interactions` - Herb-Drug Interaction Check
Checks for interactions between Ayurvedic herbs and modern medicines.

**Request:**
```json
{
  "herbs_medicines": [
    "ashwagandha",
    "brahmi",
    "warfarin",
    "metformin"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "item1": "ashwagandha",
      "item2": "warfarin",
      "interaction_type": "pharmacodynamic",
      "severity": "moderate",
      "mechanism": "May enhance anticoagulant effect",
      "recommendation": "Monitor INR closely, consider dose adjustment"
    }
  ]
}
```

---

#### `POST /api/v1/decision-support/contraindications` - Contraindication Check
Checks if a treatment is contraindicated for patient conditions.

**Request:**
```json
{
  "treatment": "virechana",
  "patient_conditions": [
    "pregnancy",
    "debilitated",
    "heart_valve"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "treatment": "virechana",
      "contraindicated_for": "pregnancy",
      "severity": "absolute",
      "alternative": "Mild Shamana therapy after delivery"
    },
    {
      "treatment": "virechana",
      "contraindicated_for": "debilitated",
      "severity": "relative",
      "alternative": "Build strength first with Brimhana therapy"
    }
  ]
}
```

---

#### `POST /api/v1/decision-support` - Comprehensive Decision Support
Full clinical decision support for complex scenarios.

**Request:**
```json
{
  "scenario": "Patient with diabetes wants to use Guduchi and Shilajit",
  "patient_profile": {
    "age": 55,
    "conditions": ["Type 2 Diabetes", "Hypertension"],
    "current_medications": ["metformin", "lisinopril"],
    "bala": "madhyama",
    "agni": "manda"
  }
}
```

**Response includes:**
- `treatment_decision`: Primary recommendation
- `safety_assessment`: Drug interaction analysis
- `dosage_recommendations`: Personalized dosing
- `monitoring_parameters`: What to track
- `alternatives`: If primary option contraindicated

---

### Disease Progression Module

#### `POST /api/v1/progression` - Model Disease Progression
Models disease progression using Shat Kriyakala (6-stage) framework.

**Request:**
```json
{
  "disease": "Type 2 Diabetes",
  "current_stage": 2,
  "duration_days": 90
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "disease": "Type 2 Diabetes",
    "current_stage": {
      "number": 2,
      "name": "Prakopa",
      "description": "Aggravation phase - doshas becoming vitiated"
    },
    "progression_timeline": [
      {"stage": 3, "name": "Prasara", "expected_days": 45},
      {"stage": 4, "name": "Sthana Samshraya", "expected_days": 90}
    ],
    "intervention_urgency": "moderate",
    "recommended_interventions": [
      "Deepana-Pachana therapy",
      "Dietary modification",
      "Exercise protocol"
    ]
  }
}
```

**Shat Kriyakala Stages:**
| Stage | Name | Description |
|-------|------|-------------|
| 1 | Sanchaya | Accumulation of doshas |
| 2 | Prakopa | Aggravation/provocation |
| 3 | Prasara | Spread to other sites |
| 4 | Sthana Samshraya | Localization in weak tissue |
| 5 | Vyakti | Manifestation of disease |
| 6 | Bheda | Complications/chronicity |

---

#### `POST /api/v1/progression/intervention` - Get Intervention Recommendation
Stage-specific intervention guidance.

**Request:**
```json
{
  "disease": "Type 2 Diabetes",
  "current_stage": 3
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "stage": 3,
    "stage_name": "Prasara",
    "intervention_type": "Shodhana indicated",
    "specific_procedures": ["Virechana", "Basti"],
    "urgency": "high",
    "rationale": "Doshas spreading - purification needed before localization"
  }
}
```

---

### Batch & Combined

#### `POST /api/v1/query-all` - Query All Core Modules
Single request to Doctor, Patient, and AYUSH modules.

```json
{
  "question": "Treatment for chronic gastritis"
}
```

#### `POST /api/v1/batch/doctor` - Batch Doctor Queries
Process multiple questions in one request.

```json
{
  "questions": [
    "Treatment for Amavata",
    "Panchakarma for skin diseases",
    "Rasayana for elderly"
  ]
}
```

---

### Reference Data

Static reference endpoints for Ayurvedic concepts.

#### `GET /api/v1/doshas` - Dosha Reference
Returns information about Vata, Pitta, Kapha.

#### `GET /api/v1/dhatus` - Dhatu Reference
Returns the 7 tissue types (Rasa, Rakta, Mamsa, Meda, Asthi, Majja, Shukra).

#### `GET /api/v1/agni-types` - Agni Types Reference
Returns digestive fire types (Sama, Vishama, Tikshna, Manda).

---

## 📊 Data Models

### UserHealthProfile
```typescript
{
  age: number;
  gender: "M" | "F";
  height_cm?: number;
  weight_kg?: number;
  known_prakriti?: "vata" | "pitta" | "kapha" | "vata_pitta" | "pitta_kapha" | "vata_kapha" | "tridosha";
  current_symptoms?: string[];
  family_history?: string[];
  medical_history?: string[];
  current_medications?: string[];
  lifestyle?: {
    diet: string;
    exercise: string;
    sleep_hours: number;
    stress_level: "low" | "moderate" | "high";
  };
}
```

### DoshaType Enum
```
vata | pitta | kapha | vata_pitta | pitta_kapha | vata_kapha | kapha_pitta | tridosha
```

### Risk Level Enum
```
low | moderate | high | critical
```

### Severity Enum
```
none | mild | moderate | severe
```

---

## 📚 Classical Text Sources

The API retrieves knowledge from three ChromaDB vector stores:

| Database | Source Text | Content |
|----------|-------------|---------|
| `chroma_db_asthrid` | **Ashtanga Hridaya** | Comprehensive Ayurvedic treatise by Vagbhata |
| `chroma_sushruta` | **Sushruta Samhita** | Surgical and medical knowledge |
| `chroma_db_ayurgenix` | **AyurGenix Clinical DB** | 367 disease profiles with modern correlations |

---

## ⚠️ Error Handling

All endpoints return consistent error format:

```json
{
  "success": false,
  "detail": "Error message here"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 422 | Validation Error - Schema mismatch |
| 500 | Internal Server Error |

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key for LLM | Required |
| `PORT` | Server port | 8000 |

### LLM Settings (in ayurveda_api.py)

```python
model = "openai/gpt-oss-120b"
temperature = 0.1
max_tokens = 4096
context_limit = 6000  # chars
```

---

## 📝 Example Workflows

### 1. New Patient Consultation Flow

```bash
# Step 1: Assess Prakriti
POST /api/v1/diagnose/prakriti

# Step 2: Check current symptoms
POST /api/v1/diagnose

# Step 3: Get risk predictions
POST /api/v1/trends

# Step 4: Generate treatment plan
POST /api/v1/treatment-plan

# Step 5: Check drug interactions
POST /api/v1/decision-support/interactions
```

### 2. Emergency Screening

```bash
# Check for red flags first
POST /api/v1/diagnose/red-flags

# If no emergency, proceed with diagnosis
POST /api/v1/diagnose
```

### 3. Treatment Monitoring

```bash
# Track disease progression
POST /api/v1/progression

# Get stage-specific interventions
POST /api/v1/progression/intervention
```

---

## 📄 License

This project is for educational and research purposes. Always consult qualified healthcare professionals for medical advice.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

**Built with ❤️ for the Ayurveda + AI Hackathon**
