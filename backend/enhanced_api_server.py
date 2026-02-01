"""
Enhanced Multimodal API Server
===============================
Extends ayurveda_server.py with new multimodal endpoints:

Multimodal Analysis:
  POST /api/v1/multimodal/analyze

Doctor Verification:
  POST /api/v1/clinical/verify

Dashboard:
  GET /api/v1/dashboard/home
  GET /api/v1/dashboard/geo-dosha
  GET /api/v1/dashboard/future-risks
  GET /api/v1/dashboard/dosha-clock
  GET /api/v1/dashboard/news

Dosha Triangulation:
  POST /api/v1/dosha/triangulate

Role-Based Chat:
  POST /api/v1/chat/ask
"""

import os
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import new modules
from vision_integration import VisionProcessor, TongueVisionOutput, NailVisionOutput, AmaPresence, TongueColorCode, NailShapeClass
from data_fusion_engine import DataFusionEngine, PatientTextInput, PatientProfile, FusedInput
from triangulation_dosha import TriangulationInference
from enhanced_multimodal_rag import EnhancedMultimodalRAG, DiagnosisResult
from dashboard_components import (
    GeoDoshaCalculator, WeatherData, GeoDosha,
    FutureRiskPredictor, DoshaClockCalculator,
    NewsPortalFetcher
)


# ═════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═════════════════════════════════════════════════════════════════════════════

class VisionAnalysisInput(BaseModel):
    """Binary classifier outputs from EfficientNet vision models
    
    ACTUAL MODEL OUTPUT:
    - Each model (tongue, nail) outputs a single severity_score (0-1)
    - 0.0 = definitely healthy (Class 0)
    - 1.0 = definitely sick (Class 1)
    
    Clinical metadata (agni_score, color_code, ama_presence, etc.)
    is INFERRED from severity_score using heuristics in VisionProcessor
    """
    tongue_severity_score: float = Field(..., ge=0, le=1, description="Tongue model confidence for Class 1 (sick)")
    nail_severity_score: float = Field(..., ge=0, le=1, description="Nail model confidence for Class 1 (sick)")


class MultimodalAnalysisRequest(BaseModel):
    """Complete multimodal analysis request"""
    chief_complaint: str = Field(..., min_length=5, description="Main symptom")
    symptom_list: List[str] = Field(..., description="Detailed symptoms")
    symptom_duration_days: Optional[int] = Field(default=None, description="Duration")
    symptom_severity_1_10: Optional[int] = Field(default=None, ge=1, le=10)
    
    vision_analysis: VisionAnalysisInput
    
    # Patient profile
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., pattern="^(M|F|Male|Female|Other)$")
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    known_prakriti: Optional[str] = None
    current_season: Optional[str] = None
    stress_level: Optional[str] = None  # Low/Medium/High
    digestion_quality: Optional[str] = None  # Good/Fair/Poor
    sleep_hours: Optional[float] = None
    lifestyle_adherence: Optional[str] = Field(
        default="Moderate",
        description="Will you follow the diet? Strict/Moderate/Loose",
        pattern="^(Strict|Moderate|Loose)$"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "chief_complaint": "Joint pain and acid reflux",
                "symptom_list": ["Morning stiffness", "Burning stomach"],
                "symptom_duration_days": 14,
                "symptom_severity_1_10": 7,
                "vision_analysis": {
                    "tongue_agni_score": 35,
                    "tongue_ama_presence": "high",
                    "tongue_color_code": "white_coated",
                    "nail_texture_score": 40,
                    "nail_shape_class": "ridges",
                    "nail_ridge_pattern": "vertical"
                },
                "age": 42,
                "gender": "Male",
                "stress_level": "High",
                "digestion_quality": "Poor",
                "lifestyle_adherence": "Moderate"
            }
        }


class ClinicalVerificationRequest(BaseModel):
    """Doctor override for diagnosis"""
    session_id: str
    corrected_diagnosis: str
    corrected_treatment: str
    risk_unticked: Optional[List[str]] = None
    modified_prescription: Optional[Dict[str, Any]] = None
    doctor_notes: Optional[str] = None


class TriangulationRequest(BaseModel):
    """Request for dosha triangulation (no quiz needed)"""
    height_cm: float = Field(..., ge=100, le=250)
    weight_kg: float = Field(..., ge=20, le=300)
    text_input: str = Field(..., min_length=20, description="Patient's description of symptoms")
    vision_dosha: Optional[Dict[str, float]] = None  # From vision models


class ChatMessageRequest(BaseModel):
    """Role-based chat query"""
    user_role: str = Field(..., pattern="^(doctor|patient)$", description="doctor or patient")
    message: str = Field(..., min_length=3)
    session_id: Optional[str] = None
    session_context: Optional[Dict[str, Any]] = None


class GeoLocationInput(BaseModel):
    """Location for geo-dosha calculation"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


# ═════════════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═════════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """App startup/shutdown"""
    # Startup
    print("🌿 Initializing Enhanced Multimodal API Server...")
    global rag_engine, vision_processor, data_fusion, dosha_inference
    
    db_paths = {
        "asthrid": "./chroma_db_asthrid",
        "sushruta": "./chroma_sushruta",
        "ayurgenix": "./chroma_db_ayurgenix"
    }
    
    rag_engine = EnhancedMultimodalRAG(db_paths)
    vision_processor = VisionProcessor()
    data_fusion = DataFusionEngine()
    dosha_inference = TriangulationInference()
    
    print("✓ All systems initialized")
    
    yield
    
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="Enhanced Multimodal Ayurveda API",
    description="Vision + Text + RAG integration for clinical Ayurvedic diagnosis",
    version="3.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═════════════════════════════════════════════════════════════════════════════
# HEALTH & SYSTEM
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0",
        "components": {
            "rag_engine": "active",
            "vision_processor": "active",
            "data_fusion": "active",
            "dosha_inference": "active"
        }
    }


# ═════════════════════════════════════════════════════════════════════════════
# CORE MULTIMODAL ENDPOINT
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/multimodal/analyze")
async def multimodal_analysis(request: MultimodalAnalysisRequest):
    """
    Complete multimodal analysis combining:
    - Vision model outputs (tongue + nail)
    - Patient text symptoms
    - Health profile
    
    Returns: Doctor + Patient + AYUSH analysis with recovery graph
    """
    
    try:
        session_id = str(uuid.uuid4())
        
        # 1. Process vision outputs (severity scores → clinical metadata)
        # The severity_score is passed directly; TongueVisionOutput.__post_init__ 
        # infers all clinical fields (agni_score, ama_presence, color_code, etc.)
        tongue = TongueVisionOutput(
            severity_score=request.vision_analysis.tongue_severity_score
            # All other fields will be inferred in __post_init__
        )
        
        nails = NailVisionOutput(
            severity_score=request.vision_analysis.nail_severity_score
            # All other fields will be inferred in __post_init__
        )
        
        # 2. Create clinical metadata from vision
        vision_meta = vision_processor.process(tongue, nails)
        
        # 3. Create patient text input
        text_input = PatientTextInput(
            chief_complaint=request.chief_complaint,
            symptom_list=request.symptom_list,
            duration_days=request.symptom_duration_days,
            severity_self_rated=request.symptom_severity_1_10
        )
        
        # 4. Create patient profile
        profile = PatientProfile(
            age=request.age,
            gender=request.gender,
            height_cm=request.height_cm,
            weight_kg=request.weight_kg,
            known_prakriti=request.known_prakriti,
            current_season=request.current_season,
            stress_level=request.stress_level,
            digestion_quality=request.digestion_quality,
            sleep_hours=request.sleep_hours
        )
        
        # 5. Fuse all data
        fused_input = data_fusion.fuse(text_input, vision_meta, profile)
        
        # 6. Run RAG diagnosis
        diagnosis = rag_engine.diagnose(
            super_prompt=fused_input.super_prompt,
            patient_data={
                "vision_confidence": vision_meta.vision_confidence,
                "data_fusion_confidence": fused_input.confidence_score,
                "initial_severity": 100 - fused_input.confidence_score * 50,
                "recovery_estimate_days": 21,
                "agni_score": vision_meta.tongue_output.agni_score,
                "ama_level": vision_meta.ama_level,
                "age": request.age,
                "season": request.current_season,
                "symptom_severity": request.symptom_severity_1_10,
                "stress_level": request.stress_level,
                "digestion_quality": request.digestion_quality,
                "sleep_hours": request.sleep_hours,
                "lifestyle_adherence": request.lifestyle_adherence,
                "vision_severity": 1 - (vision_meta.tongue_output.agni_score / 100)
            },
            session_id=session_id
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "doctor_analysis": {
                "condition_sanskrit": diagnosis.doctor_analysis.condition_sanskrit,
                "condition_english": diagnosis.doctor_analysis.condition_english,
                "samprapti": diagnosis.doctor_analysis.samprapti,
                "doshas_involved": diagnosis.doctor_analysis.doshas_involved,
                "ama_assessment": diagnosis.doctor_analysis.ama_assessment,
                "treatment_principles": diagnosis.doctor_analysis.treatment_principles,
                "confidence": diagnosis.doctor_analysis.confidence
            },
            "patient_analysis": {
                "condition_simple": diagnosis.patient_analysis.condition_simple,
                "what_happened": diagnosis.patient_analysis.what_happened,
                "diet_plan": diagnosis.patient_analysis.diet_plan,
                "daily_routine": diagnosis.patient_analysis.daily_routine,
                "herbs_and_remedies": diagnosis.patient_analysis.herbs_and_remedies,
                "what_to_avoid": diagnosis.patient_analysis.what_to_avoid,
                "recovery_timeline": diagnosis.patient_analysis.recovery_timeline
            },
            "ayush_analysis": {
                "nadi": diagnosis.ayush_analysis.nadi,
                "jihva": diagnosis.ayush_analysis.jihva,
                "shabda": diagnosis.ayush_analysis.shabda,
                "sparsha": diagnosis.ayush_analysis.sparsha,
                "drik": diagnosis.ayush_analysis.drik,
                "summary": diagnosis.ayush_analysis.summary
            },
            "recovery_graph": diagnosis.recovery_progression,
            "feature_correlations": diagnosis.feature_correlations,
            "overall_confidence": diagnosis.confidence_score,
            "cross_modal_validation": fused_input.correlation_insights
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═════════════════════════════════════════════════════════════════════════════
# CLINICAL VERIFICATION (Doctor Override)
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/clinical/verify")
async def clinical_verification(request: ClinicalVerificationRequest):
    """
    Doctor applies clinical verification and overrides.
    Saves as ground truth for model improvement.
    """
    
    try:
        overrides = {
            "corrected_diagnosis": request.corrected_diagnosis,
            "corrected_treatment": request.corrected_treatment,
            "risk_unticked": request.risk_unticked,
            "modified_prescription": request.modified_prescription,
            "doctor_notes": request.doctor_notes,
            "verified_timestamp": datetime.now().isoformat()
        }
        
        # Save to ground truth
        rag_engine._save_ground_truth(request.session_id, overrides)
        
        return {
            "status": "verified",
            "session_id": request.session_id,
            "message": "Clinical verification saved and will improve future diagnoses",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═════════════════════════════════════════════════════════════════════════════
# DOSHA TRIANGULATION (No Quiz)
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/dosha/triangulate")
async def triangulate_dosha(request: TriangulationRequest):
    """
    Auto-detect dosha using three modalities:
    - Visual (Akriti): Body frame
    - Semantic (Shabda): Text analysis
    - Biological (Jivha): Vision models
    
    No 50-question quiz needed!
    """
    
    try:
        vision_dosha = request.vision_dosha or {"vata": 0.33, "pitta": 0.33, "kapha": 0.34}
        
        result = dosha_inference.infer(
            height_cm=request.height_cm,
            weight_kg=request.weight_kg,
            text_input=request.text_input,
            vision_dosha=vision_dosha
        )
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "analysis": {
                "visual": result.visual_dosha,
                "semantic": result.semantic_dosha,
                "biological": result.biological_dosha,
                "final_dosha": result.final_dosha,
                "dominant_dosha": result.dominant_dosha,
                "secondary_dosha": result.secondary_dosha,
                "confidence": f"{result.confidence*100:.1f}%",
                "reasoning": result.reasoning
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═════════════════════════════════════════════════════════════════════════════
# DASHBOARD ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/dashboard/geo-dosha")
async def get_geo_dosha(
    base_dosha: Dict[str, float],
    location: GeoLocationInput
):
    """Weather-adjusted dosha based on geolocation"""
    
    try:
        # In production, fetch real weather data from API
        weather = WeatherData(
            temperature_c=15,
            humidity_percent=65,
            wind_speed_kmh=15,
            precipitation_mm=2
        )
        
        geo_dosha = GeoDoshaCalculator.calculate(base_dosha, weather)
        
        return {
            "base_dosha": geo_dosha.base_dosha,
            "weather_adjusted": geo_dosha.weather_adjusted_dosha,
            "environmental_factor": geo_dosha.environmental_factor,
            "adjustment_percentages": geo_dosha.adjustment_percentages,
            "recommendations": geo_dosha.recommendations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/dashboard/future-risks")
async def predict_future_risks(
    current_state: Dict[str, Any],
    history: List[str],
    dosha_profile: Dict[str, float]
):
    """Predict future disease risks"""
    
    try:
        risks = FutureRiskPredictor.predict(current_state, history, dosha_profile)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "risks": [
                {
                    "disease": r.disease,
                    "risk_percentage": f"{r.risk_percentage:.1f}%",
                    "alert_level": r.alert_level,
                    "timeframe_days": r.timeframe_days,
                    "prevention_measures": r.prevention_measures
                }
                for r in risks
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/dashboard/dosha-clock")
async def get_dosha_clock(dosha_profile: Optional[Dict[str, float]] = None):
    """Current time-based dosha guidance (Dosha Clock)"""
    
    try:
        if not dosha_profile:
            dosha_profile = {"vata": 0.33, "pitta": 0.33, "kapha": 0.34}
        
        advice = DoshaClockCalculator.get_current_advice(dosha_profile)
        
        return {
            "current_time": advice.current_time,
            "dosha_period": advice.current_dosha_period.value,
            "description": advice.dosha_description,
            "principle": advice.ayurveda_principle,
            "activities": advice.recommended_activities,
            "foods_to_eat": advice.foods_to_eat,
            "foods_to_avoid": advice.foods_to_avoid,
            "yoga_asanas": advice.yoga_asanas
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/dashboard/news")
async def get_ayurveda_news(keywords: Optional[List[str]] = Query(None)):
    """Latest Ayurveda research and news"""
    
    try:
        news = NewsPortalFetcher.fetch_news(keywords)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "articles_count": len(news),
            "articles": [
                {
                    "title": article.title,
                    "source": article.source,
                    "category": article.category,
                    "published_date": article.published_date,
                    "snippet": article.snippet,
                    "url": article.url
                }
                for article in news
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═════════════════════════════════════════════════════════════════════════════
# ROLE-BASED CHAT
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/chat/ask")
async def role_based_chat(request: ChatMessageRequest):
    """
    Role-based chat with context-specific knowledge.
    Doctor: Access to Sushruta DB (technical)
    Patient: Access to home remedies DB
    """
    
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Route to appropriate database based on role
        if request.user_role == "doctor":
            context = rag_engine._retrieve_context("doctor", request.message)
            system_role = "You are an expert Ayurvedic Vaidya answering technical questions."
        else:
            context = rag_engine._retrieve_context("patient", request.message)
            system_role = "You are a friendly health coach answering practical health questions."
        
        # Generate response
        prompt = f"""
{system_role}

Patient/Doctor Question: {request.message}

Relevant Knowledge: {context}

Provide a helpful, accurate response:
"""
        
        # For now, return placeholder
        return {
            "session_id": session_id,
            "role": request.user_role,
            "question": request.message,
            "response": "This is a placeholder response. In production, LLM generates dynamic answers.",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═════════════════════════════════════════════════════════════════════════════
# RUN SERVER
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
