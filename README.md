# 🌿 Ayurveda AYUSH - AI-Powered Ayurvedic Healthcare Platform

A comprehensive, full-stack healthcare application that combines ancient Ayurvedic wisdom with modern AI technology. Built using RAG (Retrieval-Augmented Generation) from classical Sanskrit texts, this platform provides clinical decision support, personalized treatment planning, and predictive health analytics.

## 🎯 Project Overview

This project delivers an AI-powered Ayurvedic consultation system featuring:

- **8 Specialized AI Modules** for different healthcare use cases
- **RAG-based Knowledge Retrieval** from classical texts (Ashtanga Hridaya, Sushruta Samhita)
- **Clinical Decision Support** with herb-drug interaction checking
- **Predictive Health Analytics** with disease risk modeling
- **Modern React Frontend** with structured, parseable outputs

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)            │
│  • Doctor/Patient/AYUSH Chat Interfaces                     │
│  • Structured Output Views                                  │
│  • Future Trends Dashboard                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI REST Server                       │
│  • 25+ API Endpoints                                        │
│  • Async Request Handling                                   │
│  • Auto-generated OpenAPI Docs                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              AyurvedaAPI - 8 Specialized Modules            │
├─────────────────────────────────────────────────────────────┤
│ • DoctorModule         - Clinical JSON outputs              │
│ • PatientModule        - User-friendly guidance             │
│ • AyushModule          - Government-aligned analysis        │
│ • FutureTrendsModule   - Risk prediction                    │
│ • DiagnosisModule      - AI-assisted diagnosis              │
│ • TreatmentModule      - Personalized protocols             │
│ • DecisionSupportModule - Drug interaction checking         │
│ • ProgressionModule    - Disease stage modeling             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              RAG Engine (LangChain + Groq LLM)              │
│  • Multi-source retrieval                                   │
│  • Context-aware generation                                 │
│  • Structured JSON output parsing                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────┬──────────────┬───────────────────────────────┐
│  ChromaDB    │  ChromaDB    │  ChromaDB                     │
│  Ashtanga    │  Sushruta    │  AyurGenix                    │
│  Hridaya     │  Samhita     │  Clinical DB                  │
└──────────────┴──────────────┴───────────────────────────────┘
```

---

## ✨ Key Features

### 🩺 Clinical Decision Support
- **Differential Diagnosis** using Nidana Panchaka (5-fold diagnostic) framework
- **Prakriti Assessment** (constitutional analysis) via questionnaire
- **Red Flag Detection** for emergency symptoms
- **Herb-Drug Interaction Checking** with severity levels

### 📊 Predictive Analytics
- **Disease Risk Prediction** (1-year, 5-year probabilities)
- **Shat Kriyakala Staging** (6-stage disease progression model)
- **Personalized Prevention Plans** based on constitution

### 💊 Treatment Planning
- **5-Phase Treatment Protocols** (Nidana Parivarjana → Rasayana)
- **Panchakarma Recommendations** with contraindication checks
- **Herbal Formulation Suggestions** with dosage and timing

### 📚 Classical Text Integration
- **Ashtanga Hridaya** - Dosha theory, daily routines, lifestyle
- **Sushruta Samhita** - Surgical procedures, anatomy, pathology
- **Citation Support** - Chapter, verse, and page references

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Core language |
| **FastAPI** | REST API framework |
| **LangChain** | LLM orchestration |
| **Groq API** | LLM inference (GPT-4 class) |
| **ChromaDB** | Vector database |
| **HuggingFace** | Multilingual embeddings |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **TypeScript** | Type safety |
| **Vite** | Build tool |
| **React Router** | Navigation |
| **CSS Modules** | Styling |

---

## 📁 Project Structure

```
ayurveda_ayush/
├── backend/
│   ├── ayurveda_api.py          # Core API with 8 modules
│   ├── ayurveda_server.py       # FastAPI server
│   ├── dual_persona_rag.py      # RAG engine implementation
│   ├── disease_risk_mapper.py   # Risk prediction logic
│   ├── test_api.py              # API test suite
│   ├── requirements.txt         # Python dependencies
│   ├── chroma_db_asthrid/       # Ashtanga Hridaya vectors
│   ├── chroma_sushruta/         # Sushruta Samhita vectors
│   ├── chroma_db_ayurgenix/     # Clinical database vectors
│   └── databases&embeddings/    # Embedding generation scripts
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main application
│   │   ├── pages/
│   │   │   ├── DoctorChat.tsx   # Doctor consultation
│   │   │   ├── PatientChat.tsx  # Patient guidance
│   │   │   ├── AyushChat.tsx    # AYUSH framework
│   │   │   ├── FutureTrends.tsx # Predictive analytics
│   │   │   ├── DoctorStructured.tsx
│   │   │   ├── PatientStructured.tsx
│   │   │   └── AyushStructured.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
└── README.md                    # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API Key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Start server
python ayurveda_server.py
```

Server runs at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## 📡 API Endpoints

### Core Modules
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/doctor` | POST | Clinical consultation |
| `/api/v1/patient` | POST | Patient guidance |
| `/api/v1/ayush` | POST | AYUSH framework analysis |
| `/api/v1/trends` | POST | Health risk prediction |

### Diagnosis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/diagnose` | POST | Full AI diagnosis |
| `/api/v1/diagnose/prakriti` | POST | Constitution assessment |
| `/api/v1/diagnose/red-flags` | POST | Emergency detection |

### Treatment
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/treatment-plan` | POST | Personalized protocol |
| `/api/v1/decision-support/interactions` | POST | Drug interactions |
| `/api/v1/progression` | POST | Disease staging |

### Reference Data
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/doshas` | GET | Dosha information |
| `/api/v1/dhatus` | GET | Tissue types |
| `/api/v1/agni-types` | GET | Digestive fire types |

---

## 🧪 Running Tests

```bash
cd backend
python test_api.py
```

This runs comprehensive tests across all 8 modules with colored output.

---

## 📖 Example Usage

### Doctor Consultation
```bash
curl -X POST http://localhost:8000/api/v1/doctor \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the Ayurvedic treatment for rheumatoid arthritis?"
  }'
```

### Health Risk Prediction
```bash
curl -X POST http://localhost:8000/api/v1/trends \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "gender": "M",
    "current_symptoms": ["fatigue", "joint pain"],
    "family_history": ["diabetes"],
    "lifestyle": {
      "exercise_level": "sedentary",
      "stress_level": "high"
    }
  }'
```

---

## 🌿 Classical Sources

This system is built on authentic Ayurvedic knowledge from:

1. **Ashtanga Hridaya** by Vagbhata
   - Dosha theory and Prakriti
   - Dinacharya (daily routine)
   - Ritucharya (seasonal regimens)

2. **Sushruta Samhita** by Sushruta
   - Surgical procedures
   - Anatomy (Sharira Sthana)
   - Pathology and treatment

3. **Charaka Samhita** (referenced)
   - Internal medicine
   - Diagnostic principles

---

## 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key for LLM |
| `PORT` | Server port (default: 8000) |

---

## 📊 Output Formats

The API returns structured JSON suitable for:
- **EMR/EHR Integration** - Clinical decision support
- **Mobile Apps** - Patient-facing features
- **Research Platforms** - Citation-heavy academic outputs
- **Government Systems** - AYUSH Ministry compliance

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is for educational and research purposes. Classical Ayurvedic knowledge is in the public domain.

---

## 🙏 Acknowledgments

- Classical Ayurvedic texts and their authors
- Ministry of AYUSH, Government of India
- LangChain and Groq teams for excellent tools

---

**Built with ❤️ for the intersection of ancient wisdom and modern AI**
