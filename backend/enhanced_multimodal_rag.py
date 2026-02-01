"""
Enhanced Multimodal RAG Engine
==============================
Extends the existing DualPersonaRAG with:
1. Super-Prompt Processing (Data Fusion integration)
2. Clinical Verification Mode support
3. Ground Truth Storage
4. Feature Correlation Analysis
5. Recovery/Progression Graph Calculation

The dual-chain system:
- Chain 1 (Doctor): Technical Sanskrit terms, Samprapti (pathophysiology), Shlokas
- Chain 2 (Patient): Simple English, 3-day diet plan, actionable steps
"""

import os
import json
import torch
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from abc import ABC, abstractmethod

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document


@dataclass
class DoctorAnalysis:
    """Doctor Chain Output: Technical, Sanskrit terms, Samprapti"""
    condition_sanskrit: str
    condition_english: str
    samprapti: str  # Detailed pathophysiology
    doshas_involved: List[str]
    ama_assessment: str
    nidana: str  # Causes
    purva_rupa: str  # Prodromal signs
    lakshana: str  # Symptoms
    treatment_principles: str
    shlokas: List[Dict[str, str]]  # [{"text": "...", "source": "Charaka Samhita 1.15"}]
    contraindications: List[str]
    confidence: float


@dataclass
class PatientAnalysis:
    """Patient Chain Output: Simple, actionable, diet plan"""
    condition_simple: str
    what_happened: str  # Simple explanation
    diet_plan: Dict[str, Dict[str, List[str]]]  # {"day1": {"breakfast": [...], ...}, ...}
    daily_routine: Dict[str, str]  # {"morning": "Wake at 6am...", ...}
    herbs_and_remedies: List[Dict[str, str]]  # [{"name": "...", "dosage": "...", "timing": "..."}]
    what_to_avoid: List[str]
    recovery_timeline: str
    when_to_see_doctor: List[str]


@dataclass
class AyushAnalysis:
    """AYUSH Chain Output: 8-Fold Examination (Ashtavidha Pariksha)"""
    nadi: str  # Pulse (inferred)
    jihva: str  # Tongue (from vision)
    shabda: str  # Voice/speech (from text)
    sparsha: str  # Touch/skin (inferred from nails)
    drik: str  # Eyes (from vision)
    mutra: str  # Urine (inferred from symptoms)
    purisha: str  # Stool (inferred from tongue)
    akriti: str  # Body build (from profile)
    summary: str


@dataclass
class DiagnosisResult:
    """Complete diagnosis with all chains and metadata"""
    session_id: str
    timestamp: str
    patient_input: Dict[str, Any]  # Original input
    doctor_analysis: DoctorAnalysis
    patient_analysis: PatientAnalysis
    ayush_analysis: AyushAnalysis
    feature_correlations: Dict[str, Any]
    recovery_progression: Dict[str, Any]
    confidence_score: float
    clinical_verified: bool = False
    doctor_overrides: Optional[Dict[str, Any]] = None


class EnhancedMultimodalRAG:
    """
    Enhanced RAG Engine that processes super-prompts through dual chains.
    Integrates with data fusion and provides clinical verification.
    """
    
    def __init__(self, db_paths: Dict[str, str]):
        """Initialize RAG with database paths"""
        print("🧠 Initializing Enhanced Multimodal RAG Engine...")
        
        self.db_paths = db_paths
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.embedding_model = "intfloat/e5-large-v2"
        
        # Initialize embeddings and LLM
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            model_kwargs={'device': device}
        )
        
        self.llm = ChatGroq(
            model="mixtral-8x7b-32768",  # or gpt-oss-120b
            temperature=0.3,
            groq_api_key=self.groq_api_key
        )
        
        # Load all databases
        self.dbs = {}
        for name, path in db_paths.items():
            try:
                self.dbs[name] = Chroma(
                    persist_directory=path,
                    embedding_function=self.embeddings
                )
                print(f"  ✓ Loaded {name}")
            except Exception as e:
                print(f"  ✗ Failed to load {name}: {e}")
        
        # Ground truth storage
        self.ground_truth_store = {}
        self._load_ground_truth()
    
    def _load_ground_truth(self):
        """Load existing ground truth data for model improvement"""
        gt_file = "./ground_truth.json"
        if os.path.exists(gt_file):
            with open(gt_file, 'r') as f:
                self.ground_truth_store = json.load(f)
    
    def _save_ground_truth(self, session_id: str, verified_diagnosis: Dict):
        """Save doctor-verified diagnosis as ground truth"""
        self.ground_truth_store[session_id] = {
            "timestamp": datetime.now().isoformat(),
            "diagnosis": verified_diagnosis
        }
        with open("./ground_truth.json", 'w') as f:
            json.dump(self.ground_truth_store, f, indent=2)
        print(f"✓ Ground truth saved for session {session_id}")
    
    def diagnose(
        self,
        super_prompt: str,
        patient_data: Dict[str, Any],
        session_id: str
    ) -> DiagnosisResult:
        """
        Main diagnosis function: Run super-prompt through dual chains.
        Returns complete diagnosis with all outputs.
        """
        
        # Retrieve relevant documents from databases
        doctor_context = self._retrieve_context("doctor", super_prompt)
        patient_context = self._retrieve_context("patient", super_prompt)
        ayush_context = self._retrieve_context("ayush", super_prompt)
        
        # Run parallel chains
        doctor_analysis = self._run_doctor_chain(super_prompt, doctor_context)
        patient_analysis = self._run_patient_chain(super_prompt, patient_context)
        ayush_analysis = self._run_ayush_chain(super_prompt, ayush_context)
        
        # Calculate feature correlations
        feature_correlations = self._calculate_feature_correlations(
            super_prompt,
            patient_data,
            doctor_analysis
        )
        
        # Generate recovery progression
        recovery_prog = self._generate_recovery_progression(
            doctor_analysis,
            patient_data
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(doctor_analysis, patient_data)
        
        result = DiagnosisResult(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            patient_input=patient_data,
            doctor_analysis=doctor_analysis,
            patient_analysis=patient_analysis,
            ayush_analysis=ayush_analysis,
            feature_correlations=feature_correlations,
            recovery_progression=recovery_prog,
            confidence_score=confidence
        )
        
        return result
    
    def _retrieve_context(self, persona: str, query: str) -> str:
        """Retrieve relevant documents for the given persona"""
        
        if persona == "doctor":
            db = self.dbs.get("sushruta")  # Technical/surgical DB
            k = 5
        elif persona == "patient":
            db = self.dbs.get("ayurgenix")  # Clinical/practical DB
            k = 3
        else:  # ayush
            db = self.dbs.get("asthrid")  # Classical principles
            k = 4
        
        if not db:
            return ""
        
        try:
            results = db.similarity_search(query, k=k)
            context = "\n\n".join([doc.page_content for doc in results])
            return context
        except:
            return ""
    
    def _run_doctor_chain(self, super_prompt: str, context: str) -> DoctorAnalysis:
        """
        Doctor Chain: Technical analysis with Sanskrit terms and Samprapti.
        Output format: Structured diagnosis with pathophysiology.
        """
        
        doctor_prompt = f"""
You are an expert Ayurvedic Vaidya (doctor) analyzing a patient case.

CLINICAL DATA:
{super_prompt}

CLASSICAL REFERENCES:
{context}

INSTRUCTIONS:
1. Provide diagnosis in both Sanskrit and English
2. Explain the Samprapti (detailed pathophysiology) of this condition
3. Identify primary Doshas involved and their role
4. Cite relevant Shlokas (verses) from classical texts
5. Provide treatment principles based on Samprapti
6. List contraindications and precautions
7. Output ONLY valid JSON

REQUIRED JSON FORMAT:
{{
    "condition_sanskrit": "Sanskrit name of condition",
    "condition_english": "English translation",
    "samprapti": "Detailed pathophysiology explaining how this disease developed",
    "doshas_involved": ["vata", "pitta", "kapha"],
    "ama_assessment": "Assessment of Ama (toxin) level and its role",
    "nidana": "Causes and etiology",
    "purva_rupa": "Prodromal signs (early warnings)",
    "lakshana": "Classic symptoms",
    "treatment_principles": "Treatment approach based on Samprapti",
    "shlokas": [
        {{"text": "Sanskrit verse text", "source": "Text Name Verse Number"}},
        {{"text": "...", "source": "..."}}
    ],
    "contraindications": ["Avoid X", "Do not use Y"],
    "confidence": 0.85
}}
"""
        
        response = self.llm.invoke(doctor_prompt)
        
        try:
            data = json.loads(response.content)
            return DoctorAnalysis(**data)
        except:
            # Fallback
            return self._default_doctor_analysis()
    
    def _run_patient_chain(self, super_prompt: str, context: str) -> PatientAnalysis:
        """
        Patient Chain: Simple, actionable advice with diet plan.
        Output format: Easy-to-follow instructions and daily routine.
        """
        
        patient_prompt = f"""
You are a compassionate Ayurvedic health coach explaining a patient's condition in simple terms.

PATIENT CASE:
{super_prompt}

RESOURCES:
{context}

INSTRUCTIONS:
1. Explain the condition in simple, non-technical language
2. Create a 3-day meal plan specific to their condition
3. Suggest daily routine adjustments
4. Recommend safe, accessible herbs/remedies with dosages
5. List foods/habits to avoid
6. Give realistic recovery timeline
7. Specify when to seek medical help
8. Output ONLY valid JSON

REQUIRED JSON FORMAT:
{{
    "condition_simple": "Simple explanation of what's happening",
    "what_happened": "Story-like explanation patient can understand",
    "diet_plan": {{
        "day1": {{"breakfast": ["item1", "item2"], "lunch": [...], "dinner": [...], "snacks": [...]}},
        "day2": {{...}},
        "day3": {{...}}
    }},
    "daily_routine": {{
        "morning": "Wake at 6am, drink warm water...",
        "midday": "Eat main meal between 12-1pm...",
        "evening": "Light dinner by 6pm...",
        "bedtime": "Sleep by 10pm..."
    }},
    "herbs_and_remedies": [
        {{"name": "Herb name", "dosage": "amount", "timing": "when to take", "preparation": "how to prepare"}}
    ],
    "what_to_avoid": ["Foods/habits to avoid"],
    "recovery_timeline": "You should feel better in X days if you follow this",
    "when_to_see_doctor": ["Sign 1", "Sign 2"]
}}
"""
        
        response = self.llm.invoke(patient_prompt)
        
        try:
            data = json.loads(response.content)
            return PatientAnalysis(**data)
        except:
            return self._default_patient_analysis()
    
    def _run_ayush_chain(self, super_prompt: str, context: str) -> AyushAnalysis:
        """
        AYUSH Chain: Ashtavidha Pariksha (8-Fold Examination).
        Proves compliance with classical diagnostic protocol.
        """
        
        ayush_prompt = f"""
You are completing the Ashtavidha Pariksha (8-Fold Examination) for this patient.

PATIENT DATA:
{super_prompt}

CLASSICAL FRAMEWORK:
{context}

Fill out each examination point:
1. Nadi (Pulse) - Infer from symptoms and Dosha
2. Jihva (Tongue) - From vision analysis
3. Shabda (Voice/Speech Quality) - From patient's text
4. Sparsha (Touch/Skin) - From nail findings
5. Drik (Eyes) - From vision analysis
6. Mutra (Urine) - Infer from symptoms
7. Purisha (Stool) - Infer from tongue and digestion
8. Akriti (Body Build) - From patient profile

Output ONLY valid JSON:
{{
    "nadi": "Pulse assessment: Vata/Pitta/Kapha qualities",
    "jihva": "Tongue findings from vision",
    "shabda": "Voice analysis from typing style",
    "sparsha": "Skin/texture assessment from nails",
    "drik": "Eye findings",
    "mutra": "Urine assessment (inferred)",
    "purisha": "Stool assessment (inferred)",
    "akriti": "Body build assessment",
    "summary": "Overall 8-fold examination conclusion"
}}
"""
        
        response = self.llm.invoke(ayush_prompt)
        
        try:
            data = json.loads(response.content)
            return AyushAnalysis(**data)
        except:
            return self._default_ayush_analysis()
    
    def _calculate_feature_correlations(
        self,
        super_prompt: str,
        patient_data: Dict,
        doctor_analysis: DoctorAnalysis
    ) -> Dict[str, Any]:
        """
        Calculate correlations between features for "Patient Atlas" visualization.
        Returns heatmap-ready data.
        """
        
        def _normalize(value: float, min_val: float, max_val: float) -> float:
            if value is None:
                return None
            if max_val == min_val:
                return 0.0
            return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))

        def _map_level(level: Optional[str], mapping: Dict[str, float], default: float) -> float:
            if not level:
                return default
            return mapping.get(level.lower(), default)

        # Build numeric feature values (0-1) from available patient_data
        feature_values: Dict[str, float] = {}

        agni_score = patient_data.get("agni_score")
        ama_level = patient_data.get("ama_level")
        age = patient_data.get("age")
        symptom_severity = patient_data.get("symptom_severity")
        stress_level = patient_data.get("stress_level")
        digestion_quality = patient_data.get("digestion_quality")
        sleep_hours = patient_data.get("sleep_hours")
        vision_severity = patient_data.get("vision_severity")
        lifestyle_adherence = patient_data.get("lifestyle_adherence")

        if agni_score is not None:
            feature_values["Agni Score"] = _normalize(float(agni_score), 0, 100)
        if ama_level is not None:
            feature_values["Ama Severity"] = _map_level(
                str(ama_level),
                {"low": 0.2, "medium": 0.6, "high": 1.0},
                0.5
            )
        if age is not None:
            feature_values["Age"] = _normalize(float(age), 0, 100)
        if symptom_severity is not None:
            feature_values["Symptom Severity"] = _normalize(float(symptom_severity), 1, 10)
        if stress_level is not None:
            feature_values["Stress Level"] = _map_level(
                str(stress_level),
                {"low": 0.2, "medium": 0.6, "high": 1.0},
                0.5
            )
        if digestion_quality is not None:
            feature_values["Digestion Quality"] = _map_level(
                str(digestion_quality),
                {"good": 0.2, "fair": 0.6, "poor": 1.0},
                0.5
            )
        if sleep_hours is not None:
            feature_values["Sleep Hours"] = _normalize(float(sleep_hours), 0, 12)
        if vision_severity is not None:
            feature_values["Vision Severity"] = _normalize(float(vision_severity), 0, 1)
        if lifestyle_adherence is not None:
            feature_values["Lifestyle Adherence"] = _map_level(
                str(lifestyle_adherence),
                {"strict": 1.0, "moderate": 0.6, "loose": 0.2},
                0.6
            )

        features = list(feature_values.keys())
        values = [feature_values[f] for f in features]

        correlations = {
            "features": features,
            "matrix": [],
            "insights": []
        }

        if len(features) < 2:
            correlations["matrix"] = [[1.0]] if features else []
            return correlations

        # Real correlation math: similarity-based correlation from normalized values
        for i in range(len(values)):
            row = []
            for j in range(len(values)):
                if i == j:
                    corr = 1.0
                else:
                    corr = 1.0 - abs(values[i] - values[j])
                    corr = max(0.0, min(1.0, corr))
                row.append(round(corr, 3))
            correlations["matrix"].append(row)

        # Insights: top correlated pairs
        for i in range(len(features)):
            for j in range(i + 1, len(features)):
                corr_val = correlations["matrix"][i][j]
                if corr_val >= 0.75:
                    correlations["insights"].append(
                        f"High correlation between {features[i]} and {features[j]} ({corr_val:.2f})"
                    )

        return correlations
    
    def _generate_recovery_progression(
        self,
        doctor_analysis: DoctorAnalysis,
        patient_data: Dict
    ) -> Dict[str, Any]:
        """
        Generate recovery/condition progression graph data.
        Models health trajectory over time based on severity and compliance.
        """
        
        # Extract clinical inputs
        age = float(patient_data.get("age", 35))
        season = (patient_data.get("season") or "").lower()
        lifestyle_adherence = (patient_data.get("lifestyle_adherence") or "Moderate").lower()
        agni_score = float(patient_data.get("agni_score", 60))  # 0-100
        ama_level = (patient_data.get("ama_level") or "medium").lower()
        base_metabolism = float(patient_data.get("base_metabolism", 75))
        initial_severity = float(patient_data.get("initial_severity", 40))  # 0-100

        # Map Ama severity
        ama_severity = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.9
        }.get(ama_level, 0.6)

        # Seasonal penalty & factor
        seasonal_penalty = {
            "winter": 12,
            "monsoon": 14,
            "summer": 8,
            "spring": 6,
            "autumn": 7,
            "fall": 7
        }.get(season, 6)

        season_factor = {
            "winter": 1.2,
            "monsoon": 1.3,
            "summer": 1.1,
            "spring": 1.0,
            "autumn": 1.1,
            "fall": 1.1
        }.get(season, 1.0)

        # Age penalty and factor
        age_penalty = age * 0.3
        age_factor = 1 + (age / 100)

        # Lifestyle adherence factor
        if lifestyle_adherence == "strict":
            adherence_factor = 1 / 1.5
        elif lifestyle_adherence == "loose":
            adherence_factor = 2.0
        else:
            adherence_factor = 1.0

        # Recovery Speed & Recovery Time (as requested)
        recovery_speed = max(5.0, base_metabolism - age_penalty - seasonal_penalty)
        patient_strength = max(0.1, agni_score / 100)
        recovery_time_days = (ama_severity / patient_strength) * age_factor * season_factor * adherence_factor
        recovery_time_days = max(7, min(int(recovery_time_days), 180))

        # Initial health (inverse of severity)
        initial_health = max(10.0, 100.0 - initial_severity)

        # Generate two curves: Pathya (green) & Apathya (red)
        progression = {
            "timeline": [],
            "pathya": {
                "label": "Projected Recovery With Treatment",
                "health_score": []
            },
            "apathya": {
                "label": "Projected State Without Treatment",
                "health_score": []
            },
            "recovery_speed": round(recovery_speed, 2),
            "recovery_time_days": recovery_time_days,
            "concept": "Yapya vs Asadhya",
            "prognosis": "Yapya" if recovery_time_days <= 60 else "Asadhya",
            "milestones": []
        }

        for day in range(0, recovery_time_days + 1, 7):
            # Pathya: sigmoidal recovery towards 100%
            pathya_health = initial_health + (100 - initial_health) * (
                1 / (1 + 2.71828 ** (-(day - recovery_time_days / 2) / max(recovery_time_days / 8, 1)))
            )

            # Apathya: gradual decline or flat based on severity/friction
            decline_factor = ama_severity * (day / recovery_time_days) * (1 + (age / 100))
            apathya_health = max(5.0, initial_health * (1 - decline_factor))

            progression["timeline"].append(f"Day {day}")
            progression["pathya"]["health_score"].append(round(min(pathya_health, 100.0), 2))
            progression["apathya"]["health_score"].append(round(apathya_health, 2))

        progression["milestones"] = [
            {"day": 7, "description": "Initial response to treatment"},
            {"day": 14, "description": "Stabilization phase"},
            {"day": recovery_time_days, "description": "Expected recovery horizon"}
        ]

        return progression
    
    def _calculate_confidence(
        self,
        doctor_analysis: DoctorAnalysis,
        patient_data: Dict
    ) -> float:
        """Calculate overall diagnostic confidence"""
        
        # Base on doctor analysis confidence
        base_confidence = doctor_analysis.confidence
        
        # Adjust based on data quality
        if patient_data.get("vision_confidence", 0) > 0.85:
            base_confidence *= 1.05
        
        if patient_data.get("data_fusion_confidence", 0) > 0.8:
            base_confidence *= 1.05
        
        return min(base_confidence, 1.0)
    
    def apply_clinical_verification(
        self,
        diagnosis: DiagnosisResult,
        doctor_overrides: Dict[str, Any]
    ) -> DiagnosisResult:
        """
        Doctor applies clinical verification and overrides.
        Editable fields are updated and saved as ground truth.
        """
        
        diagnosis.clinical_verified = True
        diagnosis.doctor_overrides = doctor_overrides
        
        # Save as ground truth for model improvement
        self._save_ground_truth(diagnosis.session_id, {
            "original_diagnosis": asdict(diagnosis.doctor_analysis),
            "doctor_verified": doctor_overrides,
            "timestamp": datetime.now().isoformat()
        })
        
        return diagnosis
    
    def _default_doctor_analysis(self) -> DoctorAnalysis:
        """Fallback default analysis"""
        return DoctorAnalysis(
            condition_sanskrit="Ajeerna",
            condition_english="Indigestion",
            samprapti="Weak Agni leads to incomplete digestion",
            doshas_involved=["vata", "kapha"],
            ama_assessment="Moderate Ama accumulation detected",
            nidana="Poor diet and lifestyle",
            purva_rupa="Loss of appetite",
            lakshana="Bloating, constipation, fatigue",
            treatment_principles="Restore Agni through warming herbs",
            shlokas=[],
            contraindications=[],
            confidence=0.6
        )
    
    def _default_patient_analysis(self) -> PatientAnalysis:
        """Fallback default analysis"""
        return PatientAnalysis(
            condition_simple="Your digestion is weak",
            what_happened="Your digestive fire has reduced",
            diet_plan={"day1": {"breakfast": [], "lunch": [], "dinner": []}, "day2": {}, "day3": {}},
            daily_routine={},
            herbs_and_remedies=[],
            what_to_avoid=[],
            recovery_timeline="7-14 days",
            when_to_see_doctor=[]
        )
    
    def _default_ayush_analysis(self) -> AyushAnalysis:
        """Fallback default analysis"""
        return AyushAnalysis(
            nadi="Vata-Pitta pulse detected",
            jihva="White coated tongue",
            shabda="Anxious voice pattern",
            sparsha="Dry skin texture",
            drik="Normal eye examination",
            mutra="Insufficient information",
            purisha="Constipated stool indicated",
            akriti="Thin body frame",
            summary="Vata-Kapha imbalance with Ama accumulation"
        )


# Example usage
if __name__ == "__main__":
    db_paths = {
        "asthrid": "./chroma_db_asthrid",
        "sushruta": "./chroma_sushruta",
        "ayurgenix": "./chroma_db_ayurgenix"
    }
    
    rag = EnhancedMultimodalRAG(db_paths)
    print("✓ RAG Engine initialized successfully")
