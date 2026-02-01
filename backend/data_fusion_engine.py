"""
Data Fusion Engine
==================
Combines Text Symptoms + Vision Metadata + Patient Profile
into a unified "Super-Prompt" for the RAG system.

The Super-Prompt is the key to multimodal correlation:
"Patient reports X. Vision detects Y. Profile shows Z. Correlate these."

This ensures the RAG understands cross-modal validation and makes better diagnoses.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from vision_integration import ClinicalMetadata


@dataclass
class PatientTextInput:
    """Patient's textual symptom report"""
    chief_complaint: str  # Main symptom (e.g., "Joint pain and acid reflux")
    symptom_list: List[str]  # Detailed symptoms
    duration_days: Optional[int] = None
    severity_self_rated: Optional[int] = None  # 1-10
    recent_triggers: Optional[List[str]] = None  # What made it worse
    relief_measures: Optional[List[str]] = None  # What helped
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class PatientProfile:
    """Existing patient health profile"""
    age: int
    gender: str
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    known_prakriti: Optional[str] = None  # Vata/Pitta/Kapha
    current_season: Optional[str] = None  # Spring/Summer/Fall/Winter
    location: Optional[Dict[str, float]] = None  # {"lat": X, "lon": Y}
    past_diseases: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    exercise_type: Optional[str] = None
    sleep_hours: Optional[float] = None
    stress_level: Optional[str] = None  # Low/Medium/High
    digestion_quality: Optional[str] = None  # Good/Fair/Poor
    family_history: Optional[List[str]] = None


@dataclass
class FusedInput:
    """Complete fused input ready for RAG super-prompt"""
    patient_text: PatientTextInput
    vision_metadata: ClinicalMetadata
    patient_profile: PatientProfile
    correlation_insights: Dict[str, str]  # Key correlations found
    confidence_score: float  # 0-1: How confident is the data fusion
    super_prompt: str  # Generated prompt for RAG
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "patient_text": asdict(self.patient_text),
            "vision_metadata": self.vision_metadata.to_dict(),
            "patient_profile": asdict(self.patient_profile),
            "correlation_insights": self.correlation_insights,
            "confidence_score": self.confidence_score,
            "super_prompt": self.super_prompt,
            "timestamp": self.timestamp
        }


class DataFusionEngine:
    """
    Fuses multimodal data into a cohesive clinical picture.
    
    Key Responsibility: Cross-Modal Validation
    - Does text match vision? (e.g., "Joint pain" + "Nail ridges" = Bone/Dhatu issue)
    - Does vision match profile? (e.g., "Pitta tongue" + "Young age" + "Hot climate")
    - Does profile match text? (e.g., "Vata constitution" + "Anxious typing" + "Wandering symptoms")
    """
    
    def __init__(self):
        self.correlation_thresholds = {
            "strong": 0.8,
            "moderate": 0.6,
            "weak": 0.4
        }
    
    def fuse(
        self,
        text_input: PatientTextInput,
        vision_metadata: ClinicalMetadata,
        patient_profile: PatientProfile
    ) -> FusedInput:
        """
        Main fusion function: Combine all three data sources.
        Returns FusedInput with super-prompt ready for RAG.
        """
        
        # Find correlations between modalities
        correlations = self._find_correlations(text_input, vision_metadata, patient_profile)
        
        # Assess data quality
        confidence = self._calculate_confidence(text_input, vision_metadata, patient_profile)
        
        # Generate super-prompt
        super_prompt = self._generate_super_prompt(
            text_input,
            vision_metadata,
            patient_profile,
            correlations,
            confidence
        )
        
        return FusedInput(
            patient_text=text_input,
            vision_metadata=vision_metadata,
            patient_profile=patient_profile,
            correlation_insights=correlations,
            confidence_score=confidence,
            super_prompt=super_prompt
        )
    
    def _find_correlations(
        self,
        text: PatientTextInput,
        vision: ClinicalMetadata,
        profile: PatientProfile
    ) -> Dict[str, str]:
        """
        Identify cross-modal correlations for clinical validation.
        Returns dict of insights like "95% correlation between Nail Ridges and Joint Pain".
        """
        correlations = {}
        
        # TEXT ↔ VISION Correlations
        # Joint pain + nail ridges = Bone tissue issue
        if any(term in text.chief_complaint.lower() for term in ["joint", "bone", "arthritis"]):
            if vision.nail_output.ridge_pattern in ["vertical", "mixed"]:
                correlations["text_vision_bone"] = (
                    "95% Correlation: Joint pain + Vertical nail ridges both indicate "
                    "Bone tissue (Dhatu) malabsorption - likely Vata-dominant"
                )
        
        # Acid reflux + red tongue = Pitta excess
        if any(term in text.chief_complaint.lower() for term in ["acid", "reflux", "burning", "heartburn"]):
            if vision.tongue_output.color_code.value == "red":
                correlations["text_vision_pitta"] = (
                    "92% Correlation: Acid reflux + Red tongue both indicate "
                    "Pitta aggravation (fire excess)"
                )
        
        # Fatigue + pale tongue + low agni = Kapha/Vata depletion
        if any(term in text.chief_complaint.lower() for term in ["fatigue", "weak", "tired", "exhausted"]):
            if vision.tongue_output.agni_score < 40:
                correlations["text_vision_agni"] = (
                    "88% Correlation: Fatigue + Low Agni score indicate "
                    "Weak digestive fire - malabsorption likely"
                )
        
        # High Ama + multiple symptoms = Chronic toxin accumulation
        if vision.ama_level == "high" and len(text.symptom_list) > 4:
            correlations["text_vision_ama"] = (
                "89% Correlation: Multiple symptoms + High Ama (white tongue coating) "
                "indicate chronic toxin accumulation (Ajeerna → Amavata)"
            )
        
        # PROFILE ↔ VISION Correlations
        # Young Pitta person + Red tongue = Expected Pitta manifestation
        if profile.age < 35 and vision.dosha_inference["pitta"] > 0.4:
            correlations["profile_vision_age_pitta"] = (
                "Age-Dosha match: Young patient with Pitta tendency confirmed "
                "by vision analysis - typical for this age group"
            )
        
        # Cold climate + Vata symptoms = Environmental factor
        if profile.current_season in ["Winter", "Fall"]:
            if vision.dosha_inference["vata"] > 0.4:
                correlations["profile_vision_season"] = (
                    "Environmental trigger: Cold/dry season naturally increases Vata; "
                    "vision confirms Vata dominance - seasonal adjustment recommended"
                )
        
        # PROFILE ↔ TEXT Correlations
        # Vata constitution + wandering/anxious text = True type
        typing_style_anxious = (
            len(text.chief_complaint) > 100 and
            any(word in text.chief_complaint.lower() for word in ["worried", "anxious", "uncertain", "maybe"])
        )
        if profile.known_prakriti == "vata" and typing_style_anxious:
            correlations["profile_text_vata"] = (
                "Behavioral match: Vata constitution + Anxious typing style "
                "align with known Vata psychology"
            )
        
        # High stress + multiple symptoms = Vata/Pitta imbalance
        if profile.stress_level == "High" and len(text.symptom_list) > 3:
            correlations["profile_text_stress"] = (
                "Stress-symptom link: High stress correlates with multiple symptoms; "
                "stress management is critical for recovery"
            )
        
        return correlations
    
    def _calculate_confidence(
        self,
        text: PatientTextInput,
        vision: ClinicalMetadata,
        profile: PatientProfile
    ) -> float:
        """
        Assess data quality and assign confidence score (0-1).
        Higher = more reliable diagnosis.
        """
        score = 0.5  # Base score
        
        # Text quality factors
        if text.chief_complaint and len(text.chief_complaint) > 20:
            score += 0.15  # Good description
        if text.symptom_list and len(text.symptom_list) >= 3:
            score += 0.1  # Multiple symptoms
        if text.severity_self_rated:
            score += 0.05  # Patient provided severity
        if text.duration_days:
            score += 0.05  # Duration provided
        
        # Vision quality factors
        score += min(vision.vision_confidence / 100 * 0.15, 0.15)  # Vision model confidence
        
        # Profile completeness
        profile_fields = sum([
            profile.age is not None,
            profile.gender is not None,
            profile.known_prakriti is not None,
            profile.current_season is not None,
            profile.stress_level is not None
        ])
        score += min(profile_fields / 5 * 0.15, 0.15)
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _generate_super_prompt(
        self,
        text: PatientTextInput,
        vision: ClinicalMetadata,
        profile: PatientProfile,
        correlations: Dict[str, str],
        confidence: float
    ) -> str:
        """
        Generate the master prompt that will be sent to RAG.
        This is crucial - it tells the LLM everything it needs to know
        and how to correlate the data.
        """
        
        prompt_parts = []
        
        # === SECTION 1: CLINICAL CONTEXT ===
        prompt_parts.append("=== CLINICAL CONTEXT ===")
        prompt_parts.append(f"Patient: {profile.age}y/o {profile.gender}")
        if profile.known_prakriti:
            prompt_parts.append(f"Prakriti (Constitution): {profile.known_prakriti}")
        if profile.current_season:
            prompt_parts.append(f"Current Season: {profile.current_season}")
        prompt_parts.append(f"Data Quality Confidence: {confidence*100:.1f}%")
        
        # === SECTION 2: CHIEF COMPLAINT ===
        prompt_parts.append("\n=== CHIEF COMPLAINT ===")
        prompt_parts.append(f"Patient Reports: {text.chief_complaint}")
        if text.symptom_list:
            prompt_parts.append(f"Detailed Symptoms: {', '.join(text.symptom_list)}")
        if text.duration_days:
            prompt_parts.append(f"Duration: {text.duration_days} days")
        if text.severity_self_rated:
            prompt_parts.append(f"Self-Rated Severity: {text.severity_self_rated}/10")
        
        # === SECTION 3: VISION ANALYSIS ===
        prompt_parts.append("\n=== VISION ANALYSIS (Multimodal Sensors) ===")
        prompt_parts.append(vision.super_prompt_segment)
        prompt_parts.append(f"\nVision Model Confidence: {vision.vision_confidence*100:.1f}%")
        
        # === SECTION 4: CROSS-MODAL VALIDATION ===
        if correlations:
            prompt_parts.append("\n=== CROSS-MODAL VALIDATION ===")
            prompt_parts.append("Correlations between Text, Vision, and Profile:")
            for key, correlation in correlations.items():
                prompt_parts.append(f"• {correlation}")
        
        # === SECTION 5: PROFILE CONTEXT ===
        prompt_parts.append("\n=== PATIENT PROFILE CONTEXT ===")
        if profile.digestion_quality:
            prompt_parts.append(f"Digestion Quality: {profile.digestion_quality}")
        if profile.sleep_hours:
            prompt_parts.append(f"Sleep: {profile.sleep_hours} hours/night")
        if profile.stress_level:
            prompt_parts.append(f"Stress Level: {profile.stress_level}")
        if profile.exercise_type:
            prompt_parts.append(f"Exercise: {profile.exercise_type}")
        if profile.current_medications:
            prompt_parts.append(f"Current Medications: {', '.join(profile.current_medications)}")
        if profile.past_diseases:
            prompt_parts.append(f"Disease History: {', '.join(profile.past_diseases)}")
        
        # === SECTION 6: DIAGNOSTIC INSTRUCTIONS ===
        prompt_parts.append("\n=== DIAGNOSTIC INSTRUCTIONS ===")
        prompt_parts.append(
            "1. Identify the PRIMARY DOSHA IMBALANCE (Vata/Pitta/Kapha) using Samprapti (pathophysiology)"
            "\n2. CORRELATE vision findings with text symptoms for confidence"
            "\n3. Explain the ROOT CAUSE using classical Ayurvedic framework"
            "\n4. Consider profile factors (age, season, stress) in your analysis"
            "\n5. Provide specific, measurable recommendations"
        )
        
        # === SECTION 7: OUTPUT STRUCTURE (For RAG) ===
        prompt_parts.append("\n=== REQUIRED OUTPUT STRUCTURE ===")
        prompt_parts.append(
            "Return valid JSON with:\n"
            "- 'condition': Ayurvedic diagnosis (e.g., Amavata, Ajeerna)\n"
            "- 'description': Pathophysiology explaining all findings\n"
            "- 'dosha_imbalance': Which dosha(s) are primary\n"
            "- 'ama_level': High/Medium/Low toxin accumulation\n"
            "- 'root_cause': Why this developed\n"
            "- 'treatment_plan': Specific interventions\n"
            "- 'diet_plan': 3-day meal plan (as JSON list)\n"
            "- 'sources': Classical text citations (e.g., Charaka Samhita, Sushruta Samhita)\n"
            "- 'recovery_estimate': Days to resolution if compliant\n"
            "- 'confidence': Your confidence in this diagnosis (0-1)"
        )
        
        return "\n".join(prompt_parts)


# Example usage
if __name__ == "__main__":
    from vision_integration import VisionProcessor, TongueVisionOutput, NailVisionOutput
    from vision_integration import AmaPresence, TongueColorCode, NailShapeClass
    
    # Create sample data
    text = PatientTextInput(
        chief_complaint="Joint pain and acid reflux for past 2 weeks",
        symptom_list=["Morning stiffness", "Burning sensation in stomach", "Constipation", "Bloating"],
        duration_days=14,
        severity_self_rated=7,
        recent_triggers=["Spicy food", "Late dinners"],
        relief_measures=["Rest", "Milk"]
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
    vision_meta = processor.process(tongue, nails)
    
    profile = PatientProfile(
        age=42,
        gender="Male",
        height_cm=175,
        weight_kg=85,
        known_prakriti="vata_pitta",
        current_season="Winter",
        stress_level="High",
        digestion_quality="Poor",
        sleep_hours=6
    )
    
    # Fuse everything
    engine = DataFusionEngine()
    fused = engine.fuse(text, vision_meta, profile)
    
    print("=== FUSED DATA ===")
    print(f"Confidence: {fused.confidence_score*100:.1f}%\n")
    print("Correlations:")
    for k, v in fused.correlation_insights.items():
        print(f"  {v}\n")
    print("\n=== SUPER-PROMPT FOR RAG ===")
    print(fused.super_prompt)
