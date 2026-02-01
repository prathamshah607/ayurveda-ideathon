"""
API Testing Script for Ayurveda Modular API v2.0
=================================================
Tests all 20+ endpoints including the new AI clinical modules.

Usage:
    python test_api.py
"""

import requests
import json
from typing import Dict, Any
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_section(title: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")


def print_response(response: Dict[Any, Any], limit_length: bool = True):
    """Pretty print API response"""
    response_str = json.dumps(response, indent=2, ensure_ascii=False)
    if limit_length and len(response_str) > 500:
        response_str = response_str[:500] + f"\n... (truncated, total length: {len(response_str)} chars)"
    print(f"{Colors.YELLOW}{response_str}{Colors.RESET}")


def test_endpoint(method: str, endpoint: str, data: Dict = None, description: str = ""):
    """Test a single endpoint"""
    url = f"{API_V1}{endpoint}"
    print(f"\n{Colors.MAGENTA}Testing: {method} {endpoint}{Colors.RESET}")
    if description:
        print(f"{Colors.BLUE}{description}{Colors.RESET}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=data, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            print_error(f"Unsupported method: {method}")
            return False
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Status: {response.status_code}")
            print_response(result, limit_length=True)
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Make sure the server is running on http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print_error("Request timed out")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'*' * 70}")
    print(f"🌿 AYURVEDA API TESTING SUITE")
    print(f"{'*' * 70}{Colors.RESET}")
    print(f"{Colors.YELLOW}Testing Server: {BASE_URL}{Colors.RESET}")
    print(f"{Colors.YELLOW}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    results = []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # HEALTH CHECK
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("1. HEALTH CHECK")
    results.append(test_endpoint("GET", "/health", description="Check API health and modules"))
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CORE MODULES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("2. CORE MODULES - Doctor/Patient/AYUSH")
    
    # Doctor Module
    results.append(test_endpoint(
        "POST", "/doctor",
        data={"question": "What is the Ayurvedic treatment for diabetes?"},
        description="Clinical analysis for practitioners"
    ))
    
    # Patient Module
    results.append(test_endpoint(
        "POST", "/patient",
        data={"question": "I have frequent headaches, what should I do?"},
        description="User-friendly health guidance"
    ))
    
    # AYUSH Module
    results.append(test_endpoint(
        "POST", "/ayush",
        data={"question": "Explain joint pain from Ayurvedic perspective"},
        description="AYUSH framework analysis"
    ))
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # FUTURE TRENDS MODULE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("3. FUTURE TRENDS - Risk Prediction")
    
    results.append(test_endpoint(
        "POST", "/trends",
        data={
            "age": 45,
            "gender": "M",
            "height_cm": 175,
            "weight_kg": 85,
            "known_prakriti": "vata_pitta",
            "current_symptoms": ["fatigue", "joint pain", "digestive issues"],
            "lifestyle": {
                "diet": "mixed",
                "exercise": "sedentary",
                "stress_level": "high",
                "sleep_hours": 6
            },
            "medical_history": ["hypertension"],
            "family_history": ["diabetes", "heart disease"],
            "current_season": "hemanta"
        },
        description="Comprehensive health risk prediction"
    ))
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AI DIAGNOSIS MODULE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("4. AI DIAGNOSIS - Nidana Panchaka Framework")
    
    # Main diagnosis
    results.append(test_endpoint(
        "POST", "/diagnose",
        data={
            "symptoms": ["fatigue", "joint pain", "dry skin", "constipation", "anxiety"],
            "profile": {
                "age": 42,
                "gender": "F",
                "prakriti": "vata",
                "medical_history": ["thyroid disorder"]
            }
        },
        description="AI-assisted diagnosis with confidence scores"
    ))
    
    # Prakriti assessment
    results.append(test_endpoint(
        "POST", "/diagnose/prakriti",
        data={
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
        },
        description="Constitutional assessment"
    ))
    
    # Red flags check
    results.append(test_endpoint(
        "POST", "/diagnose/red-flags",
        data={
            "symptoms": ["severe chest pain", "difficulty breathing", "sudden weakness"]
        },
        description="Emergency warning signs check"
    ))
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PERSONALIZED TREATMENT MODULE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("5. PERSONALIZED TREATMENT - Multi-Phase Algorithms")
    
    results.append(test_endpoint(
        "POST", "/treatment-plan",
        data={
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
        },
        description="Generate personalized treatment protocol"
    ))
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CLINICAL DECISION SUPPORT MODULE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("6. CLINICAL DECISION SUPPORT")
    
    # Drug interactions
    results.append(test_endpoint(
        "POST", "/decision-support/interactions",
        data={
            "herbs_medicines": ["ashwagandha", "brahmi", "warfarin", "metformin"]
        },
        description="Check herb-drug interactions"
    ))
    
    # Contraindications
    results.append(test_endpoint(
        "POST", "/decision-support/contraindications",
        data={
            "treatment": "virechana",
            "patient_conditions": ["pregnancy", "debilitated", "hemorrhoids"]
        },
        description="Check treatment contraindications"
    ))
    
    # Full decision support
    results.append(test_endpoint(
        "POST", "/decision-support",
        data={
            "scenario": "45-year-old female with chronic joint pain, wanting to start Panchakarma therapy",
            "patient_profile": {
                "age": 45,
                "gender": "F",
                "prakriti": "vata",
                "conditions": ["rheumatoid arthritis", "thyroid disorder"],
                "current_medications": ["levothyroxine", "methotrexate"],
                "bala": "madhyama",
                "agni": "vishama"
            }
        },
        description="Comprehensive clinical decision support"
    ))
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DISEASE PROGRESSION MODELING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("7. DISEASE PROGRESSION - Shat Kriyakala")
    
    # Model progression
    results.append(test_endpoint(
        "POST", "/progression",
        data={
            "disease": "Prameha (Diabetes)",
            "current_symptoms": ["increased thirst", "frequent urination", "fatigue", "slow wound healing"],
            "duration_days": 180,
            "patient_profile": {
                "age": 50,
                "gender": "M",
                "prakriti": "kapha",
                "bmi": 29.5
            }
        },
        description="Model disease progression through 6 stages"
    ))
    
    # Intervention recommendation
    results.append(test_endpoint(
        "POST", "/progression/intervention",
        data={
            "disease": "Prameha (Diabetes)",
            "current_stage": 4
        },
        description="Get stage-specific intervention recommendations"
    ))
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # COMBINED & REFERENCE ENDPOINTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("8. COMBINED & REFERENCE ENDPOINTS")
    
    # Query all modes
    results.append(test_endpoint(
        "POST", "/query-all",
        data={"question": "What is the treatment for insomnia?"},
        description="Query Doctor, Patient, and AYUSH simultaneously"
    ))
    
    # Reference data
    results.append(test_endpoint(
        "GET", "/doshas",
        description="Get dosha reference data"
    ))
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SUMMARY
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_section("TEST SUMMARY")
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"{Colors.BOLD}Total Tests: {total}{Colors.RESET}")
    print(f"{Colors.GREEN}Passed: {passed} ✅{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed} ❌{Colors.RESET}")
    
    if failed == 0:
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 ALL TESTS PASSED!{Colors.RESET}\n")
    else:
        print(f"\n{Colors.BOLD}{Colors.RED}⚠️  Some tests failed. Check errors above.{Colors.RESET}\n")
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Tests interrupted by user{Colors.RESET}\n")
        exit(1)
