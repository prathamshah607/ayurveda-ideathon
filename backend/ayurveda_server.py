"""
Ayurveda API Server
====================
FastAPI server for the Ayurveda Modular API.

Run with: uvicorn ayurveda_server:app --reload --port 8000
Or: python ayurveda_server.py
"""

import os
import sys
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ayurveda_api import AyurvedaAPI


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class QueryRequest(BaseModel):
    """Basic query request"""
    question: str = Field(..., description="The health/medical query", min_length=3)
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the Ayurvedic treatment for diabetes?"
            }
        }


class UserHealthProfile(BaseModel):
    """Enhanced user health data for comprehensive trend analysis"""
    # Basic Information
    age: int = Field(..., ge=1, le=120, description="User's age")
    gender: str = Field(..., pattern="^(M|F|Male|Female|Other)$", description="Gender")
    
    # Body Measurements
    height_cm: Optional[float] = Field(default=None, ge=50, le=300, description="Height in centimeters")
    weight_kg: Optional[float] = Field(default=None, ge=10, le=500, description="Weight in kilograms")
    bmi: Optional[float] = Field(default=None, ge=10, le=70, description="Body Mass Index (auto-calculated if height/weight provided)")
    
    # Constitutional Assessment
    known_prakriti: Optional[str] = Field(
        default=None,
        pattern="^(vata|pitta|kapha|vata_pitta|pitta_kapha|vata_kapha|tridosha)?$",
        description="Known Prakriti constitution if previously assessed"
    )
    current_dosha_symptoms: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="Current symptoms by dosha: {vata: [...], pitta: [...], kapha: [...]}"
    )
    
    # Agni and Digestion
    agni_type: Optional[str] = Field(
        default=None,
        pattern="^(sama|vishama|tikshna|manda)?$",
        description="Digestive fire type: sama (balanced), vishama (irregular), tikshna (intense), manda (slow)"
    )
    digestion_issues: List[str] = Field(default=[], description="Digestion problems: bloating, acidity, constipation, etc.")
    
    # Current Health Status
    current_symptoms: List[str] = Field(default=[], description="Current health symptoms")
    
    # Diet and Nutrition
    diet_type: Optional[str] = Field(
        default=None,
        description="vegetarian, vegan, non_vegetarian, eggetarian, pescatarian"
    )
    meal_timing: Optional[Dict[str, str]] = Field(
        default=None,
        description="Meal times: {breakfast: '8:00 AM', lunch: '1:00 PM', dinner: '7:00 PM'}"
    )
    food_cravings: List[str] = Field(default=[], description="Sweet, salty, sour, spicy, fried foods, etc.")
    foods_avoided: List[str] = Field(default=[], description="Foods not tolerated or avoided")
    water_intake: Optional[str] = Field(default=None, description="Daily water intake: low, moderate, high")
    
    # Sleep Assessment
    sleep_hours: Optional[float] = Field(default=None, ge=0, le=24, description="Average sleep hours")
    sleep_quality: Optional[str] = Field(
        default=None,
        description="poor, average, good, excellent"
    )
    wake_time: Optional[str] = Field(default=None, description="Usual wake time (e.g., '6:30 AM')")
    sleep_time: Optional[str] = Field(default=None, description="Usual sleep time (e.g., '10:30 PM')")
    
    # Elimination Assessment (Mala)
    bowel_regularity: Optional[str] = Field(
        default=None,
        description="regular, constipated, loose, irregular"
    )
    urination_frequency: Optional[str] = Field(
        default=None,
        description="normal, frequent, infrequent, painful"
    )
    sweating_pattern: Optional[str] = Field(
        default=None,
        description="normal, excessive, minimal, foul-smelling"
    )
    
    # Mental/Emotional State
    mental_state: Optional[str] = Field(
        default=None,
        description="calm, anxious, irritable, depressed, stressed, balanced"
    )
    concentration_level: Optional[str] = Field(
        default=None,
        description="good, poor, variable, difficulty_focusing"
    )
    
    # Lifestyle Factors (Enhanced)
    lifestyle: Dict[str, Any] = Field(
        default={},
        description="Comprehensive lifestyle: diet, exercise, sleep_hours, stress_level, occupation, screen_time"
    )
    
    # Medical History
    medical_history: List[str] = Field(default=[], description="Past medical conditions")
    family_history: List[str] = Field(default=[], description="Family medical history")
    current_medications: List[str] = Field(default=[], description="Current medications/supplements")
    allergies: List[str] = Field(default=[], description="Known allergies")
    
    # Environmental Factors
    current_season: Optional[str] = Field(
        default=None,
        description="varsha, sharad, hemanta, shishira, vasanta, grishma"
    )
    climate_type: Optional[str] = Field(
        default=None,
        description="tropical, temperate, cold, dry, humid, coastal"
    )
    
    # Occupation/Activity
    occupation_type: Optional[str] = Field(
        default=None,
        description="sedentary, light_activity, moderate_activity, heavy_labor, mixed"
    )
    toxin_exposure: List[str] = Field(default=[], description="Environmental toxins: pollution, chemicals, smoke, etc.")
    
    # Previous Assessments
    prakriti_assessment: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Previous Prakriti assessment results if available"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 35,
                "gender": "M",
                "height_cm": 175,
                "weight_kg": 78,
                "known_prakriti": "vata_pitta",
                "current_dosha_symptoms": {
                    "vata": ["dry skin", "anxiety", "bloating"],
                    "pitta": ["acidity", "irritability"],
                    "kapha": []
                },
                "agni_type": "vishama",
                "digestion_issues": ["bloating after meals", "occasional acidity"],
                "current_symptoms": ["fatigue", "joint pain", "poor digestion"],
                "diet_type": "vegetarian",
                "meal_timing": {
                    "breakfast": "8:30 AM",
                    "lunch": "1:00 PM",
                    "dinner": "8:00 PM"
                },
                "food_cravings": ["sweets", "fried foods"],
                "sleep_hours": 6.5,
                "sleep_quality": "average",
                "wake_time": "6:30 AM",
                "sleep_time": "11:30 PM",
                "bowel_regularity": "constipated",
                "sweating_pattern": "minimal",
                "mental_state": "stressed",
                "lifestyle": {
                    "diet": "vegetarian",
                    "exercise": "moderate",
                    "stress_level": "high",
                    "occupation": "IT professional",
                    "screen_time": "8+ hours"
                },
                "medical_history": ["hypertension"],
                "family_history": ["diabetes", "heart disease"],
                "current_season": "hemanta",
                "occupation_type": "sedentary"
            }
        }


class BatchQueryRequest(BaseModel):
    """Batch query request for multiple questions"""
    questions: List[str] = Field(..., min_length=1, max_length=10)


class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    data: Any
    error: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

# Global API instance
api: Optional[AyurvedaAPI] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    global api
    print("🌿 Starting Ayurveda API Server...")
    api = AyurvedaAPI()
    print("✅ Server ready!")
    yield
    print("👋 Shutting down Ayurveda API Server...")


app = FastAPI(
    title="Ayurveda Modular API",
    description="""
    ## 🌿 Comprehensive Ayurvedic Knowledge API with AI Clinical Support
    
    This API provides **two interface styles** for Ayurvedic health queries:
    
    ---
    
    ## 📊 Structured JSON Endpoints
    For programmatic access with strict schemas - ideal for applications, dashboards, and data processing.
    
    ### Core Modules:
    - **Doctor** `/api/v1/doctor`: Clinical JSON outputs (Samprapti, Chikitsa, Prognosis)
    - **Patient** `/api/v1/patient`: User-friendly structured guidance
    - **AYUSH** `/api/v1/ayush`: Ministry-aligned analysis (Panchamahabhuta, Tridosha, Saptadhatu)
    - **Future Trends** `/api/v1/trends`: Risk prediction based on health data
    
    ### Advanced Clinical AI:
    - **AI Diagnosis** `/api/v1/diagnose`: Nidana Panchaka diagnosis with confidence scores
    - **Personalized Treatment** `/api/v1/treatment-plan`: Multi-phase treatment algorithms
    - **Clinical Decision Support** `/api/v1/decision-support`: Drug-herb interactions
    - **Disease Progression** `/api/v1/progression`: Shat Kriyakala modeling
    
    ---
    
    ## 💬 Chat Interface Endpoints
    For flexible, conversational responses - ideal for complex queries like "generate a weekly treatment plan".
    
    - **Doctor Chat** `/api/v1/chat/doctor`: Comprehensive clinical consultations
    - **Patient Chat** `/api/v1/chat/patient`: Detailed patient-friendly explanations
    - **AYUSH Chat** `/api/v1/chat/ayush`: Complete framework analysis
    - **Multi-Mode** `/api/v1/chat/all`: All perspectives in one call
    
    ---
    
    ### Data Sources:
    - 📚 Ashtanga Hridaya (Classical Ayurvedic principles)
    - 📚 Sushruta Samhita (Surgical and diagnostic knowledge)
    - 📚 AyurGenix Clinical Database (Modern disease treatments)
    
    ### AI Capabilities:
    - ✅ Personalised treatment algorithms
    - ✅ Decision-support systems
    - ✅ Predictive modelling for disease progression
    - ✅ AI-assisted diagnosis using Ayurvedic parameters
    - ✅ Flexible chat interface for complex queries
    """,
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", tags=["Health"])
async def root():
    """API root - health check and info"""
    return {
        "name": "Ayurveda Modular API",
        "version": "2.1.0",
        "status": "healthy",
        "modules": {
            "core": ["doctor", "patient", "ayush", "future_trends"],
            "advanced": ["diagnosis", "treatment", "decision_support", "progression"],
            "chat": ["doctor_chat", "patient_chat", "ayush_chat"]
        },
        "docs": "/docs"
    }


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "modules_loaded": api is not None,
        "available_endpoints": {
            "structured_json": {
                "core": [
                    "/api/v1/doctor",
                    "/api/v1/patient",
                    "/api/v1/ayush",
                    "/api/v1/trends",
                    "/api/v1/trends/quick",
                    "/api/v1/query-all"
                ],
                "ai_diagnosis": [
                    "/api/v1/diagnose",
                    "/api/v1/diagnose/prakriti",
                    "/api/v1/diagnose/red-flags"
                ],
                "personalized_treatment": [
                    "/api/v1/treatment-plan"
                ],
                "decision_support": [
                    "/api/v1/decision-support",
                    "/api/v1/decision-support/interactions",
                    "/api/v1/decision-support/contraindications"
                ],
                "progression_modeling": [
                    "/api/v1/progression",
                    "/api/v1/progression/intervention"
                ]
            },
            "chat_interface": [
                "/api/v1/chat/doctor",
                "/api/v1/chat/patient", 
                "/api/v1/chat/ayush",
                "/api/v1/chat/all"
            ]
        },
        "notes": {
            "structured_json": "Use these endpoints for programmatic access with strict JSON schemas",
            "chat_interface": "Use these endpoints for flexible, conversational responses ideal for complex queries like treatment plans"
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# DOCTOR MODULE
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/v1/doctor", tags=["Doctor Module"], response_model=APIResponse)
async def doctor_query(request: QueryRequest):
    """
    ## Clinical Query for Ayurvedic Practitioners
    
    Returns structured clinical analysis including:
    - **Samprapti**: Complete pathology (Nidana, Purvarupa, Rupa, etc.)
    - **Dosha Analysis**: Primary/secondary dosha, state, vikriti
    - **Dhatu Assessment**: Affected tissues
    - **Agni Status**: Digestive fire evaluation
    - **Chikitsa Sutra**: Treatment protocol
    - **Shodhana/Shamana**: Purification and palliative treatments
    - **Formulations**: Detailed herbal medicines with dosage
    - **Pathya/Apathya**: Diet and lifestyle recommendations
    - **Prognosis**: Sadhya, Krichra-sadhya, Yapya, or Asadhya
    - **Classical References**: Citations from source texts
    """
    try:
        response = api.doctor_query(request.question, output_format='dict')
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/doctor", tags=["Doctor Module"])
async def doctor_query_get(
    question: str = Query(..., description="Clinical query", min_length=3)
):
    """GET version of doctor query for simple requests"""
    try:
        response = api.doctor_query(question, output_format='dict')
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# PATIENT MODULE
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/v1/patient", tags=["Patient Module"], response_model=APIResponse)
async def patient_query(request: QueryRequest):
    """
    ## User-Friendly Query for Casual Visitors
    
    Returns easy-to-understand guidance including:
    - **Condition Summary**: Simple explanation of the issue
    - **Ayurvedic Perspective**: How Ayurveda views this condition
    - **Dietary Advice**: What to eat and avoid
    - **Lifestyle Tips**: Actionable daily changes
    - **Home Remedies**: Safe remedies with instructions
    - **Yoga Recommendations**: Beneficial practices
    - **Safety Notes**: When to see a doctor
    """
    try:
        response = api.patient_query(request.question, output_format='dict')
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/patient", tags=["Patient Module"])
async def patient_query_get(
    question: str = Query(..., description="Health question", min_length=3)
):
    """GET version of patient query for simple requests"""
    try:
        response = api.patient_query(question, output_format='dict')
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# AYUSH MODULE
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/v1/ayush", tags=["AYUSH Module"], response_model=APIResponse)
async def ayush_query(request: QueryRequest):
    """
    ## AYUSH Ministry Aligned Comprehensive Analysis
    
    Returns complete Ayurvedic framework analysis:
    - **Panchamahabhuta**: Five element analysis (Akasha, Vayu, Agni, Jala, Prithvi)
    - **Tridosha**: Vata, Pitta, Kapha assessment with state
    - **Saptadhatu**: Seven tissue impact (Rasa to Shukra)
    - **Agni Analysis**: Digestive fire type and Ama assessment
    - **Mala Analysis**: Waste elimination status (Purisha, Mutra, Sweda)
    - **Swasthya Path**: Holistic health recommendations
    - **Interventions**: Ahara, Vihara, Aushadhi, Yoga/Pranayama
    - **Classical References**: Source text citations
    """
    try:
        response = api.ayush_query(request.question, output_format='dict')
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ayush", tags=["AYUSH Module"])
async def ayush_query_get(
    question: str = Query(..., description="Query for AYUSH analysis", min_length=3)
):
    """GET version of AYUSH query for simple requests"""
    try:
        response = api.ayush_query(question, output_format='dict')
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# CHAT ENDPOINTS (Free-form Conversational Interface)
# ═══════════════════════════════════════════════════════════════════════════════
# These endpoints return natural language responses instead of structured JSON.
# Ideal for complex queries like "generate a weekly treatment plan" or detailed
# clinical consultations that don't fit rigid schemas.
# ═══════════════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    """Request for chat-style conversational responses"""
    message: str = Field(..., description="The question or request in natural language", min_length=3)
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Generate a comprehensive 7-day treatment plan for a Vata-predominant patient with chronic joint pain and constipation"
            }
        }


class ChatResponse(BaseModel):
    """Chat-style response wrapper"""
    success: bool
    query_id: str
    mode: str
    response: str
    references: List[Dict[str, Any]] = []
    databases_consulted: List[str] = []


@app.post("/api/v1/chat/doctor", tags=["Chat Interface"], response_model=ChatResponse)
async def chat_doctor(request: ChatRequest):
    """
    ## Clinical Chat Interface for Ayurvedic Practitioners
    
    Free-form conversational interface for complex clinical queries.
    Returns comprehensive, natural language clinical guidance.
    
    ### Best for:
    - Complex treatment plans (weekly/monthly protocols)
    - Detailed case discussions
    - Multi-phase treatment strategies
    - Comparative analysis of treatment approaches
    - Any query requiring flexible, comprehensive response
    
    ### Response includes:
    - Full clinical analysis with Samprapti
    - Detailed treatment protocols with dosages
    - Phase-wise Panchakarma recommendations
    - Day-by-day or week-by-week schedules when requested
    - Classical references and citations
    
    **Note**: For structured JSON output, use `/api/v1/doctor` instead.
    """
    try:
        result = api.doctor.chat(request.message)
        return ChatResponse(
            success=True,
            query_id=result["query_id"],
            mode=result["mode"],
            response=result["response"],
            references=result.get("references", []),
            databases_consulted=result.get("databases_consulted", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/chat/patient", tags=["Chat Interface"], response_model=ChatResponse)
async def chat_patient(request: ChatRequest):
    """
    ## Patient-Friendly Chat Interface
    
    Conversational interface that explains Ayurvedic concepts in simple terms.
    Perfect for patients seeking comprehensive yet accessible guidance.
    
    ### Best for:
    - Detailed lifestyle change programs
    - Complete weekly diet and routine plans
    - Step-by-step home remedy instructions
    - Understanding conditions in simple terms
    - Personalized wellness programs
    
    ### Response includes:
    - Easy-to-understand explanations
    - Day-by-day actionable plans when requested
    - Specific recipes and preparation methods
    - Yoga and exercise instructions
    - Safety notes and precautions
    
    **Note**: For structured JSON output, use `/api/v1/patient` instead.
    """
    try:
        result = api.patient.chat(request.message)
        return ChatResponse(
            success=True,
            query_id=result["query_id"],
            mode=result["mode"],
            response=result["response"],
            references=result.get("references", []),
            databases_consulted=result.get("databases_consulted", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/chat/ayush", tags=["Chat Interface"], response_model=ChatResponse)
async def chat_ayush(request: ChatRequest):
    """
    ## AYUSH Framework Chat Interface
    
    Comprehensive analysis through the complete Ayurvedic framework
    as recognized by the Ministry of AYUSH.
    
    ### Best for:
    - Complete constitutional analysis
    - Detailed Panchamahabhuta/Tridosha breakdowns
    - Holistic health program design
    - Academic/research-level queries
    - Integration of all AYUSH principles
    
    ### Response includes:
    - Five Element (Panchamahabhuta) analysis
    - Tridosha assessment with state
    - Saptadhatu (tissue) evaluation
    - Agni and Ama analysis
    - Comprehensive intervention recommendations
    
    **Note**: For structured JSON output, use `/api/v1/ayush` instead.
    """
    try:
        result = api.ayush.chat(request.message)
        return ChatResponse(
            success=True,
            query_id=result["query_id"],
            mode=result["mode"],
            response=result["response"],
            references=result.get("references", []),
            databases_consulted=result.get("databases_consulted", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class MultiChatRequest(BaseModel):
    """Request for multiple chat perspectives"""
    message: str = Field(..., description="The question or request", min_length=3)
    modes: List[str] = Field(
        default=["doctor", "patient", "ayush"],
        description="Which perspectives to include: doctor, patient, ayush"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is the complete Ayurvedic approach to managing diabetes?",
                "modes": ["doctor", "patient", "ayush"]
            }
        }


@app.post("/api/v1/chat/all", tags=["Chat Interface"], response_model=APIResponse)
async def chat_all_modes(request: MultiChatRequest):
    """
    ## Multi-Perspective Chat Interface
    
    Get responses from multiple perspectives in a single call.
    Perfect for comprehensive understanding from different viewpoints.
    
    ### Modes available:
    - **doctor**: Clinical perspective for practitioners
    - **patient**: User-friendly guidance
    - **ayush**: Ministry-aligned comprehensive analysis
    
    ### Returns:
    All requested perspectives in one response, each with its own
    detailed analysis of the query.
    """
    try:
        results = {}
        
        if "doctor" in request.modes:
            results["doctor"] = api.doctor.chat(request.message)
        
        if "patient" in request.modes:
            results["patient"] = api.patient.chat(request.message)
        
        if "ayush" in request.modes:
            results["ayush"] = api.ayush.chat(request.message)
        
        return APIResponse(success=True, data=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/chat/doctor", tags=["Chat Interface"])
async def chat_doctor_get(
    message: str = Query(..., description="Clinical query for chat response", min_length=3)
):
    """GET version of doctor chat for simple requests"""
    try:
        result = api.doctor.chat(message)
        return ChatResponse(
            success=True,
            query_id=result["query_id"],
            mode=result["mode"],
            response=result["response"],
            references=result.get("references", []),
            databases_consulted=result.get("databases_consulted", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/chat/patient", tags=["Chat Interface"])
async def chat_patient_get(
    message: str = Query(..., description="Patient query for chat response", min_length=3)
):
    """GET version of patient chat for simple requests"""
    try:
        result = api.patient.chat(message)
        return ChatResponse(
            success=True,
            query_id=result["query_id"],
            mode=result["mode"],
            response=result["response"],
            references=result.get("references", []),
            databases_consulted=result.get("databases_consulted", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/chat/ayush", tags=["Chat Interface"])
async def chat_ayush_get(
    message: str = Query(..., description="AYUSH query for chat response", min_length=3)
):
    """GET version of AYUSH chat for simple requests"""
    try:
        result = api.ayush.chat(message)
        return ChatResponse(
            success=True,
            query_id=result["query_id"],
            mode=result["mode"],
            response=result["response"],
            references=result.get("references", []),
            databases_consulted=result.get("databases_consulted", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# FUTURE TRENDS MODULE (Enhanced)
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/v1/trends", tags=["Future Trends Module"], response_model=APIResponse)
async def predict_trends(request: UserHealthProfile):
    """
    ## Comprehensive Future Health Risk Prediction (Enhanced)
    
    Uses multi-stage retrieval and disease risk mapping to analyze user health data.
    
    ### Input Data (Extended):
    - **Body Metrics**: age, gender, height, weight, BMI
    - **Constitution**: known_prakriti, current_dosha_symptoms
    - **Digestion**: agni_type, digestion_issues
    - **Diet**: diet_type, meal_timing, food_cravings
    - **Sleep**: sleep_hours, sleep_quality, wake/sleep_time
    - **Elimination**: bowel_regularity, urination, sweating
    - **Mental State**: mental_state, concentration_level
    - **History**: medical_history, family_history, allergies
    - **Environment**: current_season, climate_type, occupation
    
    ### Returns:
    - **Prakriti Analysis**: Constitution with confidence score
    - **Vikriti Analysis**: Current dosha imbalance assessment
    - **Disease Risk Predictions**: From AyurGenixAI database with probabilities
    - **Health Scores**: Overall, Dosha balance, Agni, Ojas, Dhatu, Mala
    - **Dosha Trajectory**: If uncorrected 6-month/1-year/5-year predictions
    - **Dhatu Assessment**: Seven tissue health analysis
    - **Agni Optimization**: Digestive fire correction protocol
    - **Corrective Measures**: Diet, lifestyle, herbs, panchakarma, yoga
    - **Seasonal Calendar**: Season-wise vulnerability mapping
    - **Prevention Plan**: Tiered immediate/short/medium/long-term actions
    """
    try:
        user_data = request.model_dump()
        response = api.predict_health_trends(user_data, output_format='dict')
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class QuickRiskRequest(BaseModel):
    """Minimal request for quick risk assessment"""
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., pattern="^(M|F|Male|Female|Other)$")
    bmi: Optional[float] = Field(default=None, ge=10, le=70)
    known_prakriti: Optional[str] = Field(default=None)
    current_symptoms: List[str] = Field(default=[])
    family_history: List[str] = Field(default=[])
    lifestyle: Dict[str, Any] = Field(default={})
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 45,
                "gender": "M",
                "bmi": 28.5,
                "known_prakriti": "vata",
                "current_symptoms": ["fatigue", "joint pain"],
                "family_history": ["diabetes", "hypertension"],
                "lifestyle": {"stress_level": "high", "exercise": "sedentary"}
            }
        }


@app.post("/api/v1/trends/quick", tags=["Future Trends Module"], response_model=APIResponse)
async def quick_risk_assessment(request: QuickRiskRequest):
    """
    ## Quick Disease Risk Assessment (No LLM)
    
    Ultra-fast risk assessment using pre-computed disease risk scores.
    Uses the AyurGenixAI dataset mapping for instant predictions.
    
    Returns top 5 disease risks with:
    - Risk scores
    - Probabilities (6-month, 1-year, 5-year)
    - Preventive measures
    - Warning signs
    
    **Note**: For comprehensive analysis with Ayurvedic context, use `/api/v1/trends`
    """
    try:
        user_data = request.model_dump()
        
        # Access the future_trends module directly for quick assessment
        if hasattr(api, 'future_trends') and hasattr(api.future_trends, 'get_quick_risk_assessment'):
            risks = api.future_trends.get_quick_risk_assessment(user_data)
            return APIResponse(success=True, data={
                "quick_risks": risks,
                "note": "This is a quick assessment. For comprehensive analysis, use /api/v1/trends"
            })
        else:
            # Fallback to full analysis
            response = api.predict_health_trends(user_data, output_format='dict')
            return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# AI-ASSISTED DIAGNOSIS MODULE
# ─────────────────────────────────────────────────────────────────────────────

class DiagnosisRequest(BaseModel):
    """Request for AI-assisted diagnosis"""
    symptoms: List[str] = Field(..., min_length=1, description="List of presenting symptoms")
    profile: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional patient profile with Prakriti, age, gender, etc."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": ["fatigue", "joint pain", "dry skin", "constipation", "anxiety"],
                "profile": {
                    "age": 42,
                    "gender": "F",
                    "prakriti": "vata_pitta",
                    "medical_history": ["thyroid disorder"]
                }
            }
        }


class PrakritiAssessmentRequest(BaseModel):
    """Request for Prakriti constitution assessment"""
    questionnaire_responses: Dict[str, str] = Field(
        ...,
        description="Responses to Prakriti questionnaire"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "questionnaire_responses": {
                    "body_frame": "thin",
                    "skin_type": "dry",
                    "hair_type": "dry",
                    "appetite": "variable",
                    "sleep_pattern": "light",
                    "temperature_preference": "warm",
                    "stress_response": "anxiety",
                    "memory": "quick_to_learn_quick_to_forget",
                    "activity_level": "restless",
                    "digestion": "irregular"
                }
            }
        }


class RedFlagCheckRequest(BaseModel):
    """Request to check for emergency warning signs"""
    symptoms: List[str] = Field(..., min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": ["severe chest pain", "difficulty breathing", "sudden weakness"]
            }
        }


@app.post("/api/v1/diagnose", tags=["AI Diagnosis Module"], response_model=APIResponse)
async def diagnose(request: DiagnosisRequest):
    """
    ## AI-Assisted Diagnosis Using Ayurvedic Parameters
    
    Analyzes symptoms through Nidana Panchaka (5-fold diagnostic framework):
    - **Nidana**: Etiology/causative factors
    - **Purvarupa**: Prodromal symptoms
    - **Rupa**: Clinical features
    - **Upashaya**: Therapeutic tests
    - **Samprapti**: Pathogenesis
    
    ### Returns:
    - **Differential Diagnoses**: Ranked list with confidence scores
    - **Prakriti Assessment**: Constitutional evaluation
    - **Vikriti Assessment**: Current imbalance status
    - **Nidana Panchaka Analysis**: Complete diagnostic workup
    - **Red Flags**: Emergency warning signs if any
    - **Recommended Tests**: Further investigations
    """
    try:
        response = api.diagnose(
            symptoms=request.symptoms,
            profile=request.profile,
            output_format='dict'
        )
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/diagnose/prakriti", tags=["AI Diagnosis Module"], response_model=APIResponse)
async def assess_prakriti(request: PrakritiAssessmentRequest):
    """
    ## Prakriti (Constitutional Type) Assessment
    
    Determines inherent constitution based on questionnaire responses.
    
    ### Returns:
    - **Dominant Dosha**: Primary constitutional type
    - **Secondary Dosha**: Secondary influence if dual-type
    - **Constitution Type**: Single (vata/pitta/kapha) or dual (vata_pitta, etc.)
    - **Confidence Score**: Assessment reliability
    - **Characteristic Traits**: Physical, mental, emotional traits
    """
    try:
        response = api.assess_prakriti(
            questionnaire_responses=request.questionnaire_responses,
            output_format='dict'
        )
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/diagnose/red-flags", tags=["AI Diagnosis Module"], response_model=APIResponse)
async def check_red_flags(request: RedFlagCheckRequest):
    """
    ## Emergency Warning Signs Check
    
    Identifies symptoms requiring immediate medical attention.
    
    ### Returns:
    - **Red Flags**: List of emergency warning signs detected
    - **Requires Emergency**: Boolean indicating urgency
    - **Recommendation**: Action guidance
    """
    try:
        response = api.check_red_flags(
            symptoms=request.symptoms,
            output_format='dict'
        )
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# PERSONALIZED TREATMENT MODULE
# ─────────────────────────────────────────────────────────────────────────────

class TreatmentPlanRequest(BaseModel):
    """Request for personalized treatment plan"""
    diagnosis: str = Field(..., description="Primary diagnosis or condition")
    profile: Dict[str, Any] = Field(
        ...,
        description="Patient profile with Prakriti, Vikriti, age, lifestyle, etc."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "diagnosis": "Amavata (Rheumatoid Arthritis)",
                "profile": {
                    "age": 45,
                    "gender": "F",
                    "prakriti": "vata",
                    "vikriti": "vata_kapha",
                    "agni_type": "vishama",
                    "bala": "madhyama",
                    "lifestyle": {
                        "diet": "vegetarian",
                        "exercise": "sedentary",
                        "stress_level": "high"
                    },
                    "medical_history": ["thyroid disorder"],
                    "current_medications": ["levothyroxine"]
                }
            }
        }


@app.post("/api/v1/treatment-plan", tags=["Personalized Treatment Module"], response_model=APIResponse)
async def generate_treatment_plan(request: TreatmentPlanRequest):
    """
    ## Personalized Ayurvedic Treatment Algorithm
    
    Generates multi-phase treatment protocol based on patient profile:
    
    ### Treatment Phases:
    1. **Nidana Parivarjana**: Removing causative factors
    2. **Shodhana (Panchakarma)**: Purification therapies
    3. **Shamana**: Palliative treatment
    4. **Rasayana**: Rejuvenation
    
    ### Returns:
    - **Treatment ID**: Unique protocol identifier
    - **Primary Condition**: Diagnosis being treated
    - **Phases**: Detailed phase-wise protocol
    - **Formulations**: Personalized medicines with dosages
    - **Pathya (Do's)**: Recommended diet and lifestyle
    - **Apathya (Don'ts)**: Contraindicated foods and activities
    - **Duration**: Expected treatment timeline
    - **Follow-up Schedule**: Review appointments
    - **Expected Outcomes**: Prognosis by phase
    """
    try:
        response = api.generate_treatment_plan(
            diagnosis=request.diagnosis,
            profile=request.profile,
            output_format='dict'
        )
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# CLINICAL DECISION SUPPORT MODULE
# ─────────────────────────────────────────────────────────────────────────────

class DrugInteractionRequest(BaseModel):
    """Request to check herb-drug interactions"""
    herbs_medicines: List[str] = Field(..., min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "herbs_medicines": ["ashwagandha", "brahmi", "warfarin", "metformin"]
            }
        }


class ContraindicationRequest(BaseModel):
    """Request to check treatment contraindications"""
    treatment: str = Field(..., description="Treatment or herb to check")
    patient_conditions: List[str] = Field(..., description="Patient's conditions/states")
    
    class Config:
        json_schema_extra = {
            "example": {
                "treatment": "virechana",
                "patient_conditions": ["pregnancy", "debilitated", "hemorrhoids"]
            }
        }


class DecisionSupportRequest(BaseModel):
    """Request for comprehensive clinical decision support"""
    scenario: str = Field(..., description="Clinical scenario description")
    patient_profile: Dict[str, Any] = Field(..., description="Complete patient profile")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario": "45-year-old female with chronic joint pain, wanting to start Panchakarma",
                "patient_profile": {
                    "age": 45,
                    "gender": "F",
                    "prakriti": "vata",
                    "conditions": ["rheumatoid arthritis", "thyroid disorder"],
                    "current_medications": ["levothyroxine", "methotrexate"],
                    "bala": "madhyama",
                    "agni": "vishama"
                }
            }
        }


@app.post("/api/v1/decision-support/interactions", tags=["Clinical Decision Support"], response_model=APIResponse)
async def check_drug_interactions(request: DrugInteractionRequest):
    """
    ## Herb-Drug Interaction Checker
    
    Checks for interactions between Ayurvedic herbs and modern medicines.
    
    ### Returns:
    - **Interactions Found**: List of potential interactions
    - **Severity Levels**: Critical, Major, Moderate, Minor
    - **Mechanism**: How the interaction occurs
    - **Recommendations**: Clinical guidance
    """
    try:
        response = api.check_drug_interactions(
            herbs_medicines=request.herbs_medicines,
            output_format='dict'
        )
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/decision-support/contraindications", tags=["Clinical Decision Support"], response_model=APIResponse)
async def check_contraindications(request: ContraindicationRequest):
    """
    ## Treatment Contraindication Checker
    
    Checks if a treatment is contraindicated for patient's conditions.
    
    ### Returns:
    - **Is Contraindicated**: Boolean
    - **Reasons**: Why contraindicated
    - **Alternatives**: Safe alternative treatments
    """
    try:
        response = api.check_contraindications(
            treatment=request.treatment,
            patient_conditions=request.patient_conditions,
            output_format='dict'
        )
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/decision-support", tags=["Clinical Decision Support"], response_model=APIResponse)
async def get_decision_support(request: DecisionSupportRequest):
    """
    ## Comprehensive Clinical Decision Support
    
    Provides full clinical decision support for treatment scenarios.
    
    ### Returns:
    - **Treatment Options**: Ranked options with pros/cons
    - **Contraindication Warnings**: Safety alerts
    - **Drug Interaction Alerts**: Herb-drug concerns
    - **Dosage Recommendations**: Personalized doses
    - **Monitoring Parameters**: What to track
    - **Follow-up Protocol**: Review schedule
    - **Decision Tree**: Step-by-step guidance
    """
    try:
        response = api.get_decision_support(
            scenario=request.scenario,
            patient_profile=request.patient_profile,
            output_format='dict'
        )
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# DISEASE PROGRESSION MODELING MODULE
# ─────────────────────────────────────────────────────────────────────────────

class ProgressionModelRequest(BaseModel):
    """Request for disease progression modeling"""
    disease: str = Field(..., description="Disease or condition name")
    current_symptoms: List[str] = Field(..., description="Current symptoms")
    duration_days: int = Field(..., ge=1, description="How long symptoms have been present")
    patient_profile: Optional[Dict[str, Any]] = Field(default=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "disease": "Prameha (Diabetes)",
                "current_symptoms": ["increased thirst", "frequent urination", "fatigue", "slow wound healing"],
                "duration_days": 180,
                "patient_profile": {
                    "age": 50,
                    "gender": "M",
                    "prakriti": "kapha",
                    "bmi": 29.5
                }
            }
        }


class InterventionRequest(BaseModel):
    """Request for stage-specific intervention recommendations"""
    disease: str = Field(..., description="Disease name")
    current_stage: int = Field(..., ge=1, le=6, description="Current Kriyakala stage (1-6)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "disease": "Prameha (Diabetes)",
                "current_stage": 4
            }
        }


@app.post("/api/v1/progression", tags=["Disease Progression Module"], response_model=APIResponse)
async def model_disease_progression(request: ProgressionModelRequest):
    """
    ## Disease Progression Modeling (Shat Kriyakala)
    
    Models disease progression using Ayurveda's 6-stage pathogenesis:
    
    ### Stages:
    1. **Sanchaya (Accumulation)**: Dosha accumulates at its seat
    2. **Prakopa (Aggravation)**: Dosha becomes excited
    3. **Prasara (Spread)**: Dosha spreads from its seat
    4. **Sthanasamshraya (Localization)**: Settles in weak tissues
    5. **Vyakti (Manifestation)**: Disease becomes apparent
    6. **Bheda (Complication)**: Structural damage occurs
    
    ### Returns:
    - **Current Stage**: Where patient is in progression
    - **Stage Details**: Description and characteristics
    - **Prognosis**: Sadhya (curable), Yapya (manageable), etc.
    - **Intervention Window**: Optimal treatment timing
    - **Trajectory**: If untreated progression forecast
    - **Reversal Potential**: Likelihood of reversal at current stage
    """
    try:
        response = api.model_disease_progression(
            disease=request.disease,
            current_symptoms=request.current_symptoms,
            duration_days=request.duration_days,
            patient_profile=request.patient_profile,
            output_format='dict'
        )
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/progression/intervention", tags=["Disease Progression Module"], response_model=APIResponse)
async def get_intervention_recommendation(request: InterventionRequest):
    """
    ## Stage-Specific Intervention Recommendations
    
    Get targeted intervention recommendations based on disease stage.
    
    ### Returns:
    - **Intervention Type**: Shodhana, Shamana, Rasayana, etc.
    - **Urgency Level**: Immediate, Moderate, Routine
    - **Specific Therapies**: Stage-appropriate treatments
    - **Expected Outcome**: What to expect with treatment
    """
    try:
        response = api.get_intervention_recommendation(
            disease=request.disease,
            current_stage=request.current_stage,
            output_format='dict'
        )
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# COMBINED ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/v1/query-all", tags=["Combined"], response_model=APIResponse)
async def query_all_modes(request: QueryRequest):
    """
    ## Query All Modes Simultaneously
    
    Returns responses from Doctor, Patient, and AYUSH modules for the same query.
    Useful for comprehensive analysis or comparison.
    """
    try:
        response = api.query_all_modes(request.question)
        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/batch/doctor", tags=["Batch Processing"], response_model=APIResponse)
async def batch_doctor_queries(request: BatchQueryRequest):
    """
    ## Batch Processing for Clinical Queries
    
    Process multiple clinical queries in a single request.
    Maximum 10 queries per batch.
    """
    try:
        responses = api.batch_doctor_queries(request.questions)
        return APIResponse(success=True, data=responses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/v1/doshas", tags=["Reference"])
async def list_doshas():
    """List all dosha types and their descriptions"""
    return {
        "doshas": {
            "vata": {
                "elements": ["Air", "Space"],
                "qualities": ["Light", "Dry", "Cold", "Rough", "Mobile"],
                "governs": ["Movement", "Breathing", "Circulation", "Nervous system"]
            },
            "pitta": {
                "elements": ["Fire", "Water"],
                "qualities": ["Hot", "Sharp", "Light", "Oily", "Liquid"],
                "governs": ["Digestion", "Metabolism", "Intelligence", "Vision"]
            },
            "kapha": {
                "elements": ["Earth", "Water"],
                "qualities": ["Heavy", "Slow", "Cool", "Oily", "Smooth"],
                "governs": ["Structure", "Lubrication", "Immunity", "Stability"]
            }
        }
    }


@app.get("/api/v1/dhatus", tags=["Reference"])
async def list_dhatus():
    """List all seven dhatus (tissues) and their functions"""
    return {
        "dhatus": {
            "rasa": {"english": "Plasma/Lymph", "function": "Nourishment, hydration"},
            "rakta": {"english": "Blood", "function": "Oxygenation, vitality"},
            "mamsa": {"english": "Muscle", "function": "Strength, movement"},
            "meda": {"english": "Fat/Adipose", "function": "Lubrication, energy storage"},
            "asthi": {"english": "Bone", "function": "Structure, support"},
            "majja": {"english": "Marrow/Nerve", "function": "Nervous system, cognition"},
            "shukra": {"english": "Reproductive", "function": "Vitality, immunity, reproduction"}
        }
    }


@app.get("/api/v1/agni-types", tags=["Reference"])
async def list_agni_types():
    """List agni (digestive fire) types"""
    return {
        "agni_types": {
            "sama": {"description": "Balanced digestion", "dosha": "Balanced"},
            "vishama": {"description": "Irregular digestion", "dosha": "Vata"},
            "tikshna": {"description": "Hyperactive digestion", "dosha": "Pitta"},
            "manda": {"description": "Sluggish digestion", "dosha": "Kapha"}
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# RUN SERVER
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    print("═" * 60)
    print("🌿 AYURVEDA API SERVER")
    print("═" * 60)
    print("Starting server on http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    print("═" * 60)
    
    uvicorn.run(
        "ayurveda_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
