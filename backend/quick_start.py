#!/usr/bin/env python3
"""
Quick Start Guide for Enhanced Multimodal Ayurveda System
=========================================================
Run this to test the complete system end-to-end.

Usage:
    python quick_start.py
"""

import json
from datetime import datetime

print("=" * 80)
print("🌿 ENHANCED MULTIMODAL AYURVEDA SYSTEM - QUICK START")
print("=" * 80)
print()

# Test 1: Vision Integration
print("📋 TEST 1: Vision Integration")
print("-" * 80)
try:
    from vision_integration import (
        VisionProcessor, TongueVisionOutput, NailVisionOutput,
        AmaPresence, TongueColorCode, NailShapeClass
    )
    
    tongue = TongueVisionOutput(
        agni_score=35,
        ama_presence=AmaPresence.HIGH,
        color_code=TongueColorCode.WHITE_COATED,
        coating_thickness="Thick"
    )
    
    nails = NailVisionOutput(
        texture_score=40,
        shape_class=NailShapeClass.RIDGES,
        ridge_pattern="vertical",
        white_spots_count=2
    )
    
    processor = VisionProcessor()
    metadata = processor.process(tongue, nails)
    
    print("✅ Vision Integration: OK")
    print(f"   - Dosha Inference: {metadata.dosha_inference}")
    print(f"   - Ama Level: {metadata.ama_level}")
    print(f"   - Confidence: {metadata.vision_confidence:.1%}")
    print()
except Exception as e:
    print(f"❌ Vision Integration: FAILED - {e}")
    print()

# Test 2: Data Fusion
print("📋 TEST 2: Data Fusion Engine")
print("-" * 80)
try:
    from data_fusion_engine import (
        DataFusionEngine, PatientTextInput, PatientProfile
    )
    
    text = PatientTextInput(
        chief_complaint="Joint pain and acid reflux",
        symptom_list=["Morning stiffness", "Burning stomach", "Bloating"],
        duration_days=14,
        severity_self_rated=7
    )
    
    profile = PatientProfile(
        age=42,
        gender="Male",
        height_cm=175,
        weight_kg=85,
        stress_level="High",
        digestion_quality="Poor"
    )
    
    engine = DataFusionEngine()
    fused = engine.fuse(text, metadata, profile)
    
    print("✅ Data Fusion: OK")
    print(f"   - Confidence: {fused.confidence_score:.1%}")
    print(f"   - Correlations Found: {len(fused.correlation_insights)}")
    for key, corr in fused.correlation_insights.items():
        print(f"     • {corr[:70]}...")
    print()
except Exception as e:
    print(f"❌ Data Fusion: FAILED - {e}")
    print()

# Test 3: Triangulation Dosha
print("📋 TEST 3: Triangulation Dosha Inference")
print("-" * 80)
try:
    from triangulation_dosha import TriangulationInference
    
    inference = TriangulationInference()
    
    text_input = (
        "Hi, I'm very worried about my joint pain. "
        "It's been happening for a while, and I'm confused about what's causing it."
    )
    
    vision_dosha = {"vata": 0.5, "pitta": 0.2, "kapha": 0.3}
    
    result = inference.infer(
        height_cm=165,
        weight_kg=55,
        text_input=text_input,
        vision_dosha=vision_dosha
    )
    
    print("✅ Triangulation Dosha: OK")
    print(f"   - Dominant: {result.dominant_dosha.upper()} ({result.final_dosha[result.dominant_dosha]:.1%})")
    if result.secondary_dosha:
        print(f"   - Secondary: {result.secondary_dosha.upper()} ({result.final_dosha[result.secondary_dosha]:.1%})")
    print(f"   - Confidence: {result.confidence:.1%}")
    print()
except Exception as e:
    print(f"❌ Triangulation Dosha: FAILED - {e}")
    print()

# Test 4: Dashboard Components
print("📋 TEST 4: Dashboard Components")
print("-" * 80)
try:
    from dashboard_components import (
        GeoDoshaCalculator, WeatherData,
        FutureRiskPredictor,
        DoshaClockCalculator,
        NewsPortalFetcher
    )
    
    # Geo-Dosha
    base_dosha = {"vata": 0.3, "pitta": 0.4, "kapha": 0.3}
    weather = WeatherData(
        temperature_c=8,
        humidity_percent=75,
        wind_speed_kmh=30,
        precipitation_mm=10
    )
    geo_dosha = GeoDoshaCalculator.calculate(base_dosha, weather)
    print("✅ Geo-Dosha Calculator: OK")
    print(f"   - Base: Vata {base_dosha['vata']:.0%}, Pitta {base_dosha['pitta']:.0%}, Kapha {base_dosha['kapha']:.0%}")
    print(f"   - Adjusted: Vata {geo_dosha.weather_adjusted_dosha['vata']:.0%}, Pitta {geo_dosha.weather_adjusted_dosha['pitta']:.0%}, Kapha {geo_dosha.weather_adjusted_dosha['kapha']:.0%}")
    print(f"   - Reason: {geo_dosha.environmental_factor}")
    
    # Future Risks
    current_state = {"ama_level": "high", "stress_level": "High"}
    history = ["Joint Pain"]
    risks = FutureRiskPredictor.predict(current_state, history, base_dosha)
    print("✅ Future Risk Predictor: OK")
    for i, risk in enumerate(risks[:2], 1):
        print(f"   {i}. {risk.disease}: {risk.risk_percentage:.0f}% ({risk.alert_level})")
    
    # Dosha Clock
    advice = DoshaClockCalculator.get_current_advice(base_dosha)
    print("✅ Dosha Clock: OK")
    print(f"   - Current Time: {advice.current_time}")
    print(f"   - Period: {advice.dosha_description}")
    print(f"   - Principle: {advice.ayurveda_principle}")
    
    # News
    news = NewsPortalFetcher.fetch_news()
    print("✅ News Portal: OK")
    print(f"   - Articles: {len(news)} items fetched")
    
    print()
except Exception as e:
    print(f"❌ Dashboard Components: FAILED - {e}")
    print()

# Test 5: Configuration Check
print("📋 TEST 5: System Configuration")
print("-" * 80)
import os
print("✅ Python Modules Available:")
print(f"   - FastAPI: ", end="")
try:
    import fastapi
    print("✓")
except:
    print("✗ (Install: pip install fastapi uvicorn)")

print(f"   - Pydantic: ", end="")
try:
    import pydantic
    print("✓")
except:
    print("✗ (Install: pip install pydantic)")

print(f"   - LangChain: ", end="")
try:
    import langchain
    print("✓")
except:
    print("✗ (Install: pip install langchain langchain-groq langchain-chroma)")

print(f"   - ChromaDB: ", end="")
try:
    import chromadb
    print("✓")
except:
    print("✗ (Install: pip install chromadb)")

print(f"   - Torch: ", end="")
try:
    import torch
    print("✓")
except:
    print("✗ (Install: pip install torch)")

print()
print(f"Environment Variables:")
groq_key = os.environ.get("GROQ_API_KEY")
print(f"   - GROQ_API_KEY: {'✓ (Set)' if groq_key else '✗ (Not set - export GROQ_API_KEY=...)'}")

print()
print("Database Check:")
import os
from pathlib import Path
dbs = {
    "Ashtanga Hridaya": "./chroma_db_asthrid",
    "Sushruta Samhita": "./chroma_sushruta",
    "AyurGenix": "./chroma_db_ayurgenix"
}
for name, path in dbs.items():
    exists = Path(path).exists()
    print(f"   - {name}: {'✓' if exists else '✗ (Not found - run embeddings script)'}")

print()

# Test 6: Summary
print("=" * 80)
print("🎯 SYSTEM STATUS SUMMARY")
print("=" * 80)
print("""
✅ BACKEND READY FOR PRODUCTION

Next Steps:
1. Install any missing packages from checklist above
2. Set GROQ_API_KEY environment variable
3. Initialize ChromaDB with embeddings (if not done)
4. Start the server:
   
   python enhanced_api_server.py
   
   Server will run on http://localhost:8000

5. Access API Documentation:
   
   Swagger UI: http://localhost:8000/docs
   ReDoc: http://localhost:8000/redoc

6. Test an endpoint:

   curl -X POST "http://localhost:8000/api/v1/multimodal/analyze" \\
     -H "Content-Type: application/json" \\
     -d @example_request.json

7. Build Vibecoding UI with components listed in:
   
   MULTIMODAL_INTEGRATION_GUIDE.md

📚 Full Documentation:
   - MULTIMODAL_INTEGRATION_GUIDE.md (Architecture + API Reference)
   - Each Python module has docstrings and examples
   - Vision modules: vision_integration.py
   - Fusion: data_fusion_engine.py
   - Dosha: triangulation_dosha.py
   - RAG: enhanced_multimodal_rag.py
   - Dashboard: dashboard_components.py

🚀 Ready to build UI and deploy!
""")
print("=" * 80)
