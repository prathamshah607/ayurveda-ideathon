"""
Ayurveda Modular API
======================
A comprehensive, structured API for Ayurvedic knowledge retrieval and analysis.

Modules:
- DoctorModule: Structured clinical outputs for practitioners (JSON/CSV)
- PatientModule: User-friendly guidance for casual visitors
- AyushModule: Ministry of AYUSH aligned responses with Panchamahabhuta analysis
- FutureTrendsModule: Risk factor prediction based on user health data

Built on classical Ayurvedic principles with maximum parseability.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
import json
import torch
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

DB_PATHS = {
    "asthrid": "./chroma_db_asthrid",
    "sushruta": "./chroma_sushruta",
    "ayurgenix": "./chroma_db_ayurgenix"
}

EMBEDDING_MODEL = "intfloat/e5-large-v2"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")

DB_SPECIALIZATIONS = {
    "asthrid": {
        "name": "Ashtanga Hridaya",
        "keywords": ["dosha", "vata", "pitta", "kapha", "prakriti", "dinacharya", "ritucharya", 
                     "seasonal", "daily routine", "lifestyle", "diet", "constitution", "balance", 
                     "tridosha", "panchakarma", "rasayana", "swasthavritta", "principles", "sutrasthana"],
        "description": "Classical Ayurvedic principles, Dosha theory, daily/seasonal routines"
    },
    "sushruta": {
        "name": "Sushruta Samhita",
        "keywords": ["surgery", "surgical", "procedure", "wound", "injury", "trauma", "fracture",
                     "marma", "shalya", "operation", "incision", "nidana", "diagnosis", "prognosis",
                     "anatomy", "sharira", "instruments", "yantra", "shastra", "suturing"],
        "description": "Surgical procedures, wound care, trauma, anatomical knowledge"
    },
    "ayurgenix": {
        "name": "AyurGenix Clinical Database",
        "keywords": ["treatment", "formulation", "medicine", "drug", "prescription", "dosage",
                     "disease", "disorder", "symptoms", "diagnosis", "cure", "herbs", "herbal",
                     "remedy", "yoga", "asana", "therapy", "diabetes", "hypertension", "arthritis"],
        "description": "Clinical disease treatments, herbal formulations, dosages"
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES - STRUCTURED OUTPUT MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class DoshaType(str, Enum):
    VATA = "vata"
    PITTA = "pitta"
    KAPHA = "kapha"
    VATA_PITTA = "vata_pitta"
    PITTA_VATA = "pitta_vata"  # Same as vata_pitta
    PITTA_KAPHA = "pitta_kapha"
    KAPHA_PITTA = "kapha_pitta"  # Same as pitta_kapha
    VATA_KAPHA = "vata_kapha"
    KAPHA_VATA = "kapha_vata"  # Same as vata_kapha
    TRIDOSHA = "tridosha"
    UNKNOWN = "unknown"  # Fallback for parsing errors
    
    @classmethod
    def _missing_(cls, value):
        """Handle unknown values gracefully"""
        if isinstance(value, str):
            # Try lowercase matching
            value_lower = value.lower().strip()
            for member in cls:
                if member.value == value_lower:
                    return member
            # Return UNKNOWN for unrecognized values
            return cls.UNKNOWN
        return cls.UNKNOWN


class DoshaState(str, Enum):
    BALANCED = "sama"  # Balanced
    AGGRAVATED = "vriddhi"  # Increased
    DEPLETED = "kshaya"  # Decreased
    UNKNOWN = "unknown"  # Fallback
    
    @classmethod
    def _missing_(cls, value):
        """Handle unknown values gracefully"""
        if isinstance(value, str):
            value_lower = value.lower().strip()
            for member in cls:
                if member.value == value_lower:
                    return member
            # Map common alternatives
            mappings = {
                "balanced": cls.BALANCED,
                "increased": cls.AGGRAVATED,
                "decreased": cls.DEPLETED,
                "normal": cls.BALANCED,
                "elevated": cls.AGGRAVATED,
                "high": cls.AGGRAVATED,
                "low": cls.DEPLETED
            }
            if value_lower in mappings:
                return mappings[value_lower]
        return cls.UNKNOWN


class PrognosisType(str, Enum):
    SADHYA = "sadhya"  # Easily curable
    KRICHRA_SADHYA = "krichra_sadhya"  # Difficult to cure
    YAPYA = "yapya"  # Manageable/Palliative
    ASADHYA = "asadhya"  # Incurable
    UNKNOWN = "unknown"  # Fallback
    
    @classmethod
    def _missing_(cls, value):
        """Handle unknown values gracefully"""
        if isinstance(value, str):
            value_lower = value.lower().strip()
            for member in cls:
                if member.value == value_lower:
                    return member
            # Map common alternatives
            mappings = {
                "curable": cls.SADHYA,
                "easily_curable": cls.SADHYA,
                "difficult": cls.KRICHRA_SADHYA,
                "difficult_to_cure": cls.KRICHRA_SADHYA,
                "manageable": cls.YAPYA,
                "palliative": cls.YAPYA,
                "incurable": cls.ASADHYA
            }
            if value_lower in mappings:
                return mappings[value_lower]
        return cls.UNKNOWN


class AgniType(str, Enum):
    SAMA = "sama"  # Balanced
    VISHAMA = "vishama"  # Irregular (Vata)
    TIKSHNA = "tikshna"  # Hyperactive (Pitta)
    MANDA = "manda"  # Sluggish (Kapha)
    UNKNOWN = "unknown"  # Fallback
    
    @classmethod
    def _missing_(cls, value):
        """Handle unknown values gracefully"""
        if isinstance(value, str):
            value_lower = value.lower().strip()
            for member in cls:
                if member.value == value_lower:
                    return member
            # Map common alternatives
            mappings = {
                "balanced": cls.SAMA,
                "normal": cls.SAMA,
                "irregular": cls.VISHAMA,
                "variable": cls.VISHAMA,
                "hyperactive": cls.TIKSHNA,
                "sharp": cls.TIKSHNA,
                "intense": cls.TIKSHNA,
                "sluggish": cls.MANDA,
                "slow": cls.MANDA,
                "weak": cls.MANDA
            }
            if value_lower in mappings:
                return mappings[value_lower]
        return cls.UNKNOWN


@dataclass
class DoshaAnalysis:
    """Dosha assessment result"""
    primary_dosha: DoshaType
    state: DoshaState
    secondary_dosha: Optional[DoshaType] = None
    vikriti_description: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "primary_dosha": self.primary_dosha.value,
            "state": self.state.value,
            "secondary_dosha": self.secondary_dosha.value if self.secondary_dosha else None,
            "vikriti_description": self.vikriti_description
        }


@dataclass
class HerbalFormulation:
    """Single herbal medicine/formulation"""
    name: str
    sanskrit_name: Optional[str] = None
    dosage: Optional[str] = None
    anupana: Optional[str] = None  # Adjuvant (honey, water, ghee, etc.)
    timing: Optional[str] = None  # Before/after food
    duration: Optional[str] = None
    contraindications: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DietaryRecommendation:
    """Pathya/Apathya - What to eat and avoid"""
    pathya: List[str]  # Wholesome/Recommended
    apathya: List[str]  # Unwholesome/Avoid
    rasa_preference: List[str] = field(default_factory=list)  # Tastes to prefer
    rasa_avoid: List[str] = field(default_factory=list)  # Tastes to avoid
    special_instructions: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class LifestyleRecommendation:
    """Vihara - Lifestyle modifications"""
    dinacharya: List[str] = field(default_factory=list)  # Daily routine
    ritucharya: List[str] = field(default_factory=list)  # Seasonal routine
    yoga_asanas: List[str] = field(default_factory=list)
    pranayama: List[str] = field(default_factory=list)
    activities_recommended: List[str] = field(default_factory=list)
    activities_avoid: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ClassicalReference:
    """Citation from classical texts"""
    source_text: str
    chapter: Optional[str] = None
    shloka: Optional[str] = None
    page: Optional[int] = None
    relevance_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DoctorResponse:
    """Structured clinical response for practitioners"""
    query_id: str
    timestamp: str
    query: str
    
    # Clinical Assessment
    samprapti: Dict[str, str]  # Pathology: nidana, purvarupa, rupa, upashaya, anupashaya
    dosha_analysis: DoshaAnalysis
    dhatu_affected: List[str]
    agni_status: AgniType
    ama_present: bool
    
    # Treatment Protocol
    chikitsa_sutra: str  # Line of treatment
    shodhana_indicated: bool  # Purification needed?
    shodhana_type: Optional[List[str]] = None  # Vamana, Virechana, etc.
    shamana_treatment: List[HerbalFormulation] = field(default_factory=list)
    
    # Diet & Lifestyle
    dietary: Optional[DietaryRecommendation] = None
    lifestyle: Optional[LifestyleRecommendation] = None
    
    # Prognosis
    prognosis: PrognosisType = PrognosisType.SADHYA
    prognosis_notes: str = ""
    
    # References
    references: List[ClassicalReference] = field(default_factory=list)
    
    # Metadata
    confidence_score: float = 0.0
    databases_consulted: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "query_id": self.query_id,
            "timestamp": self.timestamp,
            "query": self.query,
            "clinical_assessment": {
                "samprapti": self.samprapti,
                "dosha_analysis": self.dosha_analysis.to_dict(),
                "dhatu_affected": self.dhatu_affected,
                "agni_status": self.agni_status.value,
                "ama_present": self.ama_present
            },
            "treatment_protocol": {
                "chikitsa_sutra": self.chikitsa_sutra,
                "shodhana_indicated": self.shodhana_indicated,
                "shodhana_type": self.shodhana_type,
                "shamana_treatment": [f.to_dict() for f in self.shamana_treatment]
            },
            "diet_and_lifestyle": {
                "dietary": self.dietary.to_dict() if self.dietary else None,
                "lifestyle": self.lifestyle.to_dict() if self.lifestyle else None
            },
            "prognosis": {
                "type": self.prognosis.value,
                "notes": self.prognosis_notes
            },
            "references": [r.to_dict() for r in self.references],
            "metadata": {
                "confidence_score": self.confidence_score,
                "databases_consulted": self.databases_consulted
            }
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def to_csv_row(self) -> Dict[str, str]:
        """Flatten to CSV-compatible row"""
        return {
            "query_id": self.query_id,
            "timestamp": self.timestamp,
            "query": self.query,
            "primary_dosha": self.dosha_analysis.primary_dosha.value,
            "dosha_state": self.dosha_analysis.state.value,
            "dhatu_affected": "|".join(self.dhatu_affected),
            "agni_status": self.agni_status.value,
            "ama_present": str(self.ama_present),
            "chikitsa_sutra": self.chikitsa_sutra,
            "shodhana_indicated": str(self.shodhana_indicated),
            "formulations": "|".join([f.name for f in self.shamana_treatment]),
            "prognosis": self.prognosis.value,
            "confidence_score": str(self.confidence_score)
        }


@dataclass
class PatientResponse:
    """User-friendly response for casual visitors"""
    query_id: str
    timestamp: str
    query: str
    
    # Simple explanation
    condition_summary: str
    ayurvedic_perspective: str
    
    # Actionable advice
    dietary_advice: List[Dict[str, str]]  # [{"do": "...", "dont": "..."}]
    lifestyle_tips: List[str]
    home_remedies: List[Dict[str, str]]  # [{"remedy": "...", "how_to_use": "...", "caution": "..."}]
    yoga_recommendations: List[str]
    
    # Safety
    when_to_see_doctor: List[str]
    safety_disclaimer: str
    
    # Metadata
    reading_time_minutes: int = 5
    
    def to_dict(self) -> Dict:
        return {
            "query_id": self.query_id,
            "timestamp": self.timestamp,
            "query": self.query,
            "understanding_your_condition": {
                "summary": self.condition_summary,
                "ayurvedic_perspective": self.ayurvedic_perspective
            },
            "actionable_advice": {
                "dietary_advice": self.dietary_advice,
                "lifestyle_tips": self.lifestyle_tips,
                "home_remedies": self.home_remedies,
                "yoga_recommendations": self.yoga_recommendations
            },
            "safety": {
                "when_to_see_doctor": self.when_to_see_doctor,
                "disclaimer": self.safety_disclaimer
            },
            "metadata": {
                "reading_time_minutes": self.reading_time_minutes
            }
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass 
class PanchamahabhutaAnalysis:
    """Five element analysis"""
    akasha: Dict[str, Any] = field(default_factory=dict)  # Space/Ether
    vayu: Dict[str, Any] = field(default_factory=dict)  # Air
    agni: Dict[str, Any] = field(default_factory=dict)  # Fire
    jala: Dict[str, Any] = field(default_factory=dict)  # Water
    prithvi: Dict[str, Any] = field(default_factory=dict)  # Earth
    dominant_elements: List[str] = field(default_factory=list)
    deficient_elements: List[str] = field(default_factory=list)


@dataclass
class SaptadhatuAnalysis:
    """Seven tissue analysis"""
    rasa: Dict[str, Any] = field(default_factory=dict)  # Plasma
    rakta: Dict[str, Any] = field(default_factory=dict)  # Blood
    mamsa: Dict[str, Any] = field(default_factory=dict)  # Muscle
    meda: Dict[str, Any] = field(default_factory=dict)  # Fat
    asthi: Dict[str, Any] = field(default_factory=dict)  # Bone
    majja: Dict[str, Any] = field(default_factory=dict)  # Marrow
    shukra: Dict[str, Any] = field(default_factory=dict)  # Reproductive


@dataclass
class MalaAnalysis:
    """Waste product analysis"""
    purisha: Dict[str, Any] = field(default_factory=dict)  # Feces
    mutra: Dict[str, Any] = field(default_factory=dict)  # Urine
    sweda: Dict[str, Any] = field(default_factory=dict)  # Sweat


@dataclass
class AyushResponse:
    """AYUSH Ministry aligned response with complete Ayurvedic analysis"""
    query_id: str
    timestamp: str
    query: str
    
    # Panchamahabhuta Analysis
    panchamahabhuta: PanchamahabhutaAnalysis
    
    # Tridosha Analysis
    tridosha: DoshaAnalysis
    
    # Saptadhatu Analysis
    saptadhatu: SaptadhatuAnalysis
    
    # Agni Analysis
    agni_type: AgniType
    agni_recommendations: List[str]
    ama_assessment: Dict[str, Any]
    
    # Mala Analysis
    mala: MalaAnalysis
    
    # Swasthya Path
    swasthya_recommendations: Dict[str, List[str]]
    
    # Interventions
    ahara: List[str]  # Diet
    vihara: List[str]  # Lifestyle
    aushadhi: List[HerbalFormulation]  # Medicine
    yoga_pranayama: List[str]
    
    # References
    classical_references: List[ClassicalReference]
    
    def to_dict(self) -> Dict:
        return {
            "query_id": self.query_id,
            "timestamp": self.timestamp,
            "query": self.query,
            "panchamahabhuta_analysis": {
                "akasha": self.panchamahabhuta.akasha,
                "vayu": self.panchamahabhuta.vayu,
                "agni": self.panchamahabhuta.agni,
                "jala": self.panchamahabhuta.jala,
                "prithvi": self.panchamahabhuta.prithvi,
                "dominant_elements": self.panchamahabhuta.dominant_elements,
                "deficient_elements": self.panchamahabhuta.deficient_elements
            },
            "tridosha_analysis": self.tridosha.to_dict(),
            "saptadhatu_analysis": {
                "rasa": self.saptadhatu.rasa,
                "rakta": self.saptadhatu.rakta,
                "mamsa": self.saptadhatu.mamsa,
                "meda": self.saptadhatu.meda,
                "asthi": self.saptadhatu.asthi,
                "majja": self.saptadhatu.majja,
                "shukra": self.saptadhatu.shukra
            },
            "agni_analysis": {
                "type": self.agni_type.value,
                "recommendations": self.agni_recommendations,
                "ama_assessment": self.ama_assessment
            },
            "mala_analysis": {
                "purisha": self.mala.purisha,
                "mutra": self.mala.mutra,
                "sweda": self.mala.sweda
            },
            "swasthya_path": self.swasthya_recommendations,
            "interventions": {
                "ahara": self.ahara,
                "vihara": self.vihara,
                "aushadhi": [a.to_dict() for a in self.aushadhi],
                "yoga_pranayama": self.yoga_pranayama
            },
            "classical_references": [r.to_dict() for r in self.classical_references]
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class RiskFactor:
    """Individual risk factor assessment"""
    risk_name: str
    category: str  # dosha_imbalance, dhatu_depletion, lifestyle, genetic, etc.
    current_severity: str  # low, moderate, high, critical
    probability_6_months: float  # 0.0 - 1.0
    probability_1_year: float
    probability_5_years: float
    contributing_factors: List[str]
    preventive_measures: List[str]
    early_warning_signs: List[str]


@dataclass
class FutureTrendsResponse:
    """Future health risk prediction based on user data"""
    query_id: str
    timestamp: str
    
    # User Profile Summary
    user_profile: Dict[str, Any]
    prakriti: DoshaType
    vikriti: Optional[DoshaAnalysis]
    
    # Current Health Score
    overall_health_score: float  # 0-100
    dosha_balance_score: float
    agni_score: float
    ojas_score: float  # Vitality/Immunity
    
    # Risk Factors
    risk_factors: List[RiskFactor]
    
    # Seasonal Predictions
    seasonal_vulnerabilities: Dict[str, List[str]]  # Season -> risks
    
    # Age-based Predictions
    age_related_risks: List[Dict[str, Any]]
    
    # Personalized Prevention Plan
    prevention_plan: Dict[str, List[str]]
    
    # Lifestyle Optimization
    optimal_routine: Dict[str, str]
    recommended_rasayanas: List[HerbalFormulation]  # Rejuvenation therapies
    
    def to_dict(self) -> Dict:
        return {
            "query_id": self.query_id,
            "timestamp": self.timestamp,
            "user_profile": self.user_profile,
            "constitution": {
                "prakriti": self.prakriti.value,
                "vikriti": self.vikriti.to_dict() if self.vikriti else None
            },
            "health_scores": {
                "overall": self.overall_health_score,
                "dosha_balance": self.dosha_balance_score,
                "agni": self.agni_score,
                "ojas": self.ojas_score
            },
            "risk_factors": [asdict(rf) for rf in self.risk_factors],
            "seasonal_vulnerabilities": self.seasonal_vulnerabilities,
            "age_related_risks": self.age_related_risks,
            "prevention_plan": self.prevention_plan,
            "lifestyle_optimization": {
                "optimal_routine": self.optimal_routine,
                "recommended_rasayanas": [r.to_dict() for r in self.recommended_rasayanas]
            }
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════════
# BASE RAG ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class AyurvedaRAGEngine:
    """Core RAG engine shared by all modules"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to avoid reloading embeddings"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        print("🌿 Initializing Ayurveda RAG Engine...")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Using device: {device}")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': device}
        )
        
        self.vector_stores: Dict[str, Chroma] = {}
        self.retrievers: Dict[str, any] = {}
        
        for db_name, db_path in DB_PATHS.items():
            if os.path.exists(db_path):
                print(f"   ✓ Loading {DB_SPECIALIZATIONS[db_name]['name']}...")
                self.vector_stores[db_name] = Chroma(
                    persist_directory=db_path,
                    embedding_function=self.embeddings
                )
                self.retrievers[db_name] = self.vector_stores[db_name].as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 5}
                )
            else:
                print(f"   ⚠ Warning: {db_path} not found, skipping...")
        
        if not self.vector_stores:
            raise FileNotFoundError("❌ No vector databases found!")
        
        # Main LLM for generation
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=4096
        )
        
        # Router LLM (faster, for routing decisions)
        self.router_llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama-3.1-8b-instant",
            temperature=0.0,
            max_tokens=100
        )
        
        self._initialized = True
        print("✅ RAG Engine Ready!\n")
    
    def _keyword_route(self, question: str) -> List[str]:
        """Fast keyword-based routing"""
        question_lower = question.lower()
        scores = {}
        
        for db_name, spec in DB_SPECIALIZATIONS.items():
            if db_name not in self.vector_stores:
                continue
            score = sum(1 for kw in spec['keywords'] if kw in question_lower)
            scores[db_name] = score
        
        sorted_dbs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_dbs and sorted_dbs[0][1] >= 2:
            return [sorted_dbs[0][0]]
        if sorted_dbs and sorted_dbs[0][1] >= 1:
            return [db for db, score in sorted_dbs[:2] if score > 0]
        return list(self.vector_stores.keys())
    
    def retrieve(self, question: str, top_k: int = 5) -> Dict[str, List[Document]]:
        """Retrieve relevant documents from appropriate databases"""
        targets = self._keyword_route(question)
        
        results = {}
        for db_name in targets:
            if db_name in self.retrievers:
                docs = self.retrievers[db_name].invoke(question)[:top_k]
                results[db_name] = docs
        
        return results
    
    def build_context(self, docs: Dict[str, List[Document]], max_chars: int = 6000) -> str:
        """Build context string from retrieved documents with size limit"""
        context_parts = []
        total_chars = 0
        
        for db_name, doc_list in docs.items():
            if doc_list:
                source_name = DB_SPECIALIZATIONS[db_name]['name']
                header = f"\n[{source_name}]\n"
                context_parts.append(header)
                total_chars += len(header)
                
                for i, doc in enumerate(doc_list, 1):
                    # Build compact metadata
                    meta_info = []
                    for key in ['chapter', 'disease']:
                        if key in doc.metadata:
                            meta_info.append(f"{doc.metadata[key]}")
                    meta_str = " | ".join(meta_info) if meta_info else ""
                    
                    # Truncate long content
                    content = doc.page_content[:1500] if len(doc.page_content) > 1500 else doc.page_content
                    entry = f"[{i}] {meta_str}\n{content}\n"
                    
                    if total_chars + len(entry) > max_chars:
                        break
                    
                    context_parts.append(entry)
                    total_chars += len(entry)
                
                if total_chars >= max_chars:
                    break
        
        return "".join(context_parts)
    
    def extract_references(self, docs: Dict[str, List[Document]]) -> List[ClassicalReference]:
        """Extract structured references from documents"""
        refs = []
        for db_name, doc_list in docs.items():
            for doc in doc_list:
                refs.append(ClassicalReference(
                    source_text=DB_SPECIALIZATIONS[db_name]['name'],
                    chapter=doc.metadata.get('chapter'),
                    shloka=doc.metadata.get('shloka'),
                    page=doc.metadata.get('page'),
                    relevance_score=doc.metadata.get('score', 0.0)
                ))
        return refs
    
    def generate(self, prompt: ChatPromptTemplate, variables: Dict[str, str]) -> str:
        """Generate response using LLM"""
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke(variables)
    
    @staticmethod
    def generate_query_id(query: str) -> str:
        """Generate unique query ID"""
        hash_input = f"{query}{datetime.now().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: DOCTOR (Clinical Output)
# ═══════════════════════════════════════════════════════════════════════════════

class DoctorModule:
    """
    Structured clinical outputs for Ayurvedic practitioners.
    Returns parseable JSON with full Samprapti analysis, treatment protocols, and references.
    """
    
    def __init__(self, engine: AyurvedaRAGEngine = None):
        self.engine = engine or AyurvedaRAGEngine()
        
        self.prompt = ChatPromptTemplate.from_template("""You are an expert Ayurvedic Vaidya (physician) providing structured clinical analysis.

═══════════════════════════════════════════════════════════════════════════════
PROFESSIONAL STANCE
═══════════════════════════════════════════════════════════════════════════════
- Ayurveda is a legitimate, time-tested medical science with over 5000 years of clinical validation
- Treat Ayurvedic practitioners (Vaidyas) as qualified medical doctors and scientists
- NEVER criticize, dismiss, or question the validity of Ayurveda, Yoga, or AYUSH systems
- Present all Ayurvedic concepts with the same authority as any medical science

═══════════════════════════════════════════════════════════════════════════════
CONTEXT FROM CLASSICAL TEXTS
═══════════════════════════════════════════════════════════════════════════════
{context}

═══════════════════════════════════════════════════════════════════════════════
CLINICAL QUERY
═══════════════════════════════════════════════════════════════════════════════
{question}

═══════════════════════════════════════════════════════════════════════════════
STRICT OUTPUT SCHEMA (Must Follow Exactly)
═══════════════════════════════════════════════════════════════════════════════
Your output MUST be valid JSON matching this EXACT structure. Do not add, remove, or rename any fields:

{{
    "samprapti": {{
        "nidana": "(STRING, REQUIRED) Etiology/causative factors - diet, lifestyle, environmental, emotional causes",
        "purvarupa": "(STRING, REQUIRED) Prodromal symptoms - early warning signs before disease manifests",
        "rupa": "(STRING, REQUIRED) Clinical manifestations - actual symptoms and signs of the disease",
        "upashaya": "(STRING, REQUIRED) Relieving factors - what gives relief (opposite qualities, treatments)",
        "anupashaya": "(STRING, REQUIRED) Aggravating factors - what worsens the condition",
        "samprapti_ghataka": "(STRING, REQUIRED) Pathological components - dosha, dushya, srotas, agni, ama, etc."
    }},
    "dosha_analysis": {{
        "primary_dosha": "(ENUM, REQUIRED) ONLY ONE OF: vata | pitta | kapha | vata_pitta | pitta_kapha | vata_kapha | kapha_pitta | tridosha",
        "state": "(ENUM, REQUIRED) ONLY ONE OF: sama (balanced) | vriddhi (increased/aggravated) | kshaya (depleted)",
        "secondary_dosha": "(ENUM OR NULL) ONLY: vata | pitta | kapha | null",
        "vikriti_description": "(STRING, REQUIRED) Description of the current dosha imbalance vs normal state"
    }},
    "dhatu_affected": ["(ARRAY OF STRINGS, REQUIRED) List affected dhatus from: rasa, rakta, mamsa, meda, asthi, majja, shukra"],
    "agni_status": "(ENUM, REQUIRED) ONLY ONE OF: sama | vishama | tikshna | manda",
    "ama_present": "(BOOLEAN, REQUIRED) true or false - whether metabolic toxins are present",
    "chikitsa_sutra": "(STRING, REQUIRED) Line of treatment - summarize the therapeutic approach",
    "shodhana_indicated": "(BOOLEAN, REQUIRED) true or false - whether purification therapy is needed",
    "shodhana_type": ["(ARRAY OR NULL) If shodhana_indicated is true, list from: vamana, virechana, basti, nasya, raktamokshana"],
    "shamana_treatment": [
        {{
            "name": "(STRING, REQUIRED) Formulation name in English",
            "sanskrit_name": "(STRING, OPTIONAL) Sanskrit name if different",
            "dosage": "(STRING, REQUIRED) Exact dose with units e.g., '500mg twice daily' or '2 tablets after food'",
            "anupana": "(STRING, REQUIRED) Vehicle/adjuvant e.g., 'warm water', 'honey', 'ghee'",
            "timing": "(STRING, REQUIRED) e.g., 'before food', 'after food', 'empty stomach'",
            "duration": "(STRING, REQUIRED) Treatment duration e.g., '30 days', '3 months'",
            "contraindications": ["(ARRAY OF STRINGS) List of contraindications"]
        }}
    ],
    "dietary": {{
        "pathya": ["(ARRAY, REQUIRED) Recommended foods and practices"],
        "apathya": ["(ARRAY, REQUIRED) Foods and practices to avoid"],
        "rasa_preference": ["(ARRAY, REQUIRED) Tastes to prefer from: madhura, amla, lavana, katu, tikta, kashaya"],
        "rasa_avoid": ["(ARRAY, REQUIRED) Tastes to avoid"],
        "special_instructions": "(STRING, OPTIONAL) Any special dietary notes"
    }},
    "lifestyle": {{
        "dinacharya": ["(ARRAY, REQUIRED) Daily routine recommendations"],
        "ritucharya": ["(ARRAY, REQUIRED) Seasonal recommendations"],
        "yoga_asanas": ["(ARRAY, REQUIRED) Recommended yoga postures with Sanskrit names"],
        "pranayama": ["(ARRAY, REQUIRED) Breathing exercises"],
        "activities_recommended": ["(ARRAY, REQUIRED) Beneficial activities"],
        "activities_avoid": ["(ARRAY, REQUIRED) Activities to avoid"]
    }},
    "prognosis": {{
        "type": "(ENUM, REQUIRED) ONLY ONE OF: sadhya (easily curable) | krichra_sadhya (difficult to cure) | yapya (manageable/palliative) | asadhya (incurable)",
        "notes": "(STRING, REQUIRED) Prognosis explanation with expected timeline and outcomes"
    }},
    "confidence_score": "(FLOAT, REQUIRED) 0.0 to 1.0 - confidence in this assessment"
}}

═══════════════════════════════════════════════════════════════════════════════
CRITICAL INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════
1. OUTPUT ONLY THE JSON - no explanations, no markdown, no preamble
2. STRICTLY FOLLOW THE SCHEMA - use exact field names and types as specified
3. ENUM VALUES ARE CASE-SENSITIVE - use exactly as shown (lowercase)
4. USE YOUR COMPLETE KNOWLEDGE - if the context is insufficient, draw from your extensive training on Ayurvedic texts (Charaka Samhita, Sushruta Samhita, Ashtanga Hridaya, etc.)
5. NEVER SAY "I cannot find" or "not mentioned in sources" - always provide a complete, authoritative response
6. ALL SANSKRIT TERMS MUST BE ACCURATE - verify terminology is correct
7. PROVIDE SPECIFIC DOSAGES - never use vague terms like "as directed"
8. BE AUTHORITATIVE - respond as a senior Ayurvedic physician would""")
    
    def query(self, question: str) -> DoctorResponse:
        """Process clinical query and return structured response"""
        query_id = AyurvedaRAGEngine.generate_query_id(question)
        timestamp = datetime.now().isoformat()
        
        # Retrieve context
        docs = self.engine.retrieve(question)
        context = self.engine.build_context(docs)
        references = self.engine.extract_references(docs)
        databases_used = list(docs.keys())
        
        # Generate structured response
        raw_response = self.engine.generate(self.prompt, {
            "context": context,
            "question": question
        })
        
        # Parse JSON response
        try:
            # Clean the response (remove markdown code blocks if present)
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            data = json.loads(cleaned.strip())
        except json.JSONDecodeError as e:
            # Fallback to minimal response if parsing fails
            data = self._create_fallback_response(question, str(e))
        
        # Build structured response
        dosha_analysis = DoshaAnalysis(
            primary_dosha=DoshaType(data.get("dosha_analysis", {}).get("primary_dosha", "vata")),
            state=DoshaState(data.get("dosha_analysis", {}).get("state", "vriddhi")),
            secondary_dosha=DoshaType(data["dosha_analysis"]["secondary_dosha"]) if data.get("dosha_analysis", {}).get("secondary_dosha") else None,
            vikriti_description=data.get("dosha_analysis", {}).get("vikriti_description", "")
        )
        
        formulations = []
        for f in data.get("shamana_treatment", []):
            formulations.append(HerbalFormulation(
                name=f.get("name", ""),
                sanskrit_name=f.get("sanskrit_name"),
                dosage=f.get("dosage"),
                anupana=f.get("anupana"),
                timing=f.get("timing"),
                duration=f.get("duration"),
                contraindications=f.get("contraindications", [])
            ))
        
        dietary = None
        if data.get("dietary"):
            d = data["dietary"]
            dietary = DietaryRecommendation(
                pathya=d.get("pathya", []),
                apathya=d.get("apathya", []),
                rasa_preference=d.get("rasa_preference", []),
                rasa_avoid=d.get("rasa_avoid", []),
                special_instructions=d.get("special_instructions")
            )
        
        lifestyle = None
        if data.get("lifestyle"):
            l = data["lifestyle"]
            lifestyle = LifestyleRecommendation(
                dinacharya=l.get("dinacharya", []),
                ritucharya=l.get("ritucharya", []),
                yoga_asanas=l.get("yoga_asanas", []),
                pranayama=l.get("pranayama", []),
                activities_recommended=l.get("activities_recommended", []),
                activities_avoid=l.get("activities_avoid", [])
            )
        
        return DoctorResponse(
            query_id=query_id,
            timestamp=timestamp,
            query=question,
            samprapti=data.get("samprapti", {}),
            dosha_analysis=dosha_analysis,
            dhatu_affected=data.get("dhatu_affected", []),
            agni_status=AgniType(data.get("agni_status", "vishama")),
            ama_present=data.get("ama_present", False),
            chikitsa_sutra=data.get("chikitsa_sutra", ""),
            shodhana_indicated=data.get("shodhana_indicated", False),
            shodhana_type=data.get("shodhana_type"),
            shamana_treatment=formulations,
            dietary=dietary,
            lifestyle=lifestyle,
            prognosis=PrognosisType(data.get("prognosis", {}).get("type", "sadhya")),
            prognosis_notes=data.get("prognosis", {}).get("notes", ""),
            references=references,
            confidence_score=data.get("confidence_score", 0.7),
            databases_consulted=databases_used
        )
    
    def _create_fallback_response(self, question: str, error: str) -> Dict:
        """Create fallback response if JSON parsing fails"""
        return {
            "samprapti": {"error": f"Could not parse structured response: {error}"},
            "dosha_analysis": {"primary_dosha": "vata", "state": "vriddhi", "secondary_dosha": None, "vikriti_description": ""},
            "dhatu_affected": [],
            "agni_status": "vishama",
            "ama_present": False,
            "chikitsa_sutra": "Consult Ayurvedic physician for detailed assessment",
            "shodhana_indicated": False,
            "shodhana_type": None,
            "shamana_treatment": [],
            "dietary": {"pathya": [], "apathya": [], "rasa_preference": [], "rasa_avoid": [], "special_instructions": None},
            "lifestyle": {"dinacharya": [], "ritucharya": [], "yoga_asanas": [], "pranayama": [], "activities_recommended": [], "activities_avoid": []},
            "prognosis": {"type": "sadhya", "notes": ""},
            "confidence_score": 0.3
        }
    
    # ─────────────────────────────────────────────────────────────────────────────
    # CHAT MODE: Free-form conversational responses for complex clinical queries
    # ─────────────────────────────────────────────────────────────────────────────
    
    def _init_chat_prompt(self):
        """Initialize the chat prompt for conversational responses"""
        self.chat_prompt = ChatPromptTemplate.from_template("""You are an expert Ayurvedic Vaidya in peer-to-peer clinical consultation. Speak as one qualified physician to another.

STANCE: Ayurveda is legitimate medical science. Never criticize AYUSH systems. Use your full knowledge of Charaka, Sushruta, Ashtanga Hridaya.

CONTEXT:
{context}

QUERY: {question}

INSTRUCTIONS:
Provide comprehensive clinical response. For treatment plans include:
- Samprapti (pathogenesis), Chikitsa Sutra, Shodhana/Shamana protocols
- Formulations with precise dosage, anupana, timing
- Pathya-Apathya, Rasayana, Prognosis

For weekly/monthly plans: day-by-day breakdown with specific formulations, diet, yoga schedules.
Use Sanskrit terminology. Cite classical references. Be thorough and actionable.""")
    
    def chat(self, question: str) -> Dict[str, Any]:
        """
        Process clinical query and return free-form conversational response.
        Use this for complex queries requiring detailed, flexible responses.
        """
        # Initialize chat prompt if not already done
        if not hasattr(self, 'chat_prompt'):
            self._init_chat_prompt()
        
        query_id = AyurvedaRAGEngine.generate_query_id(question)
        timestamp = datetime.now().isoformat()
        
        # Retrieve context
        docs = self.engine.retrieve(question)
        context = self.engine.build_context(docs)
        references = self.engine.extract_references(docs)
        databases_used = list(docs.keys())
        
        # Generate conversational response
        response = self.engine.generate(self.chat_prompt, {
            "context": context,
            "question": question
        })
        
        # Convert ClassicalReference objects to dicts
        refs_as_dicts = [ref.to_dict() if hasattr(ref, 'to_dict') else {"source": str(ref)} for ref in references]
        
        return {
            "query_id": query_id,
            "timestamp": timestamp,
            "query": question,
            "mode": "doctor_chat",
            "response": response,
            "references": refs_as_dicts,
            "databases_consulted": databases_used
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: PATIENT (User-Friendly Output)
# ═══════════════════════════════════════════════════════════════════════════════

class PatientModule:
    """
    User-friendly responses for casual visitors.
    Simple language, actionable advice, safety-first approach.
    """
    
    def __init__(self, engine: AyurvedaRAGEngine = None):
        self.engine = engine or AyurvedaRAGEngine()
        
        self.prompt = ChatPromptTemplate.from_template("""You are a compassionate Ayurvedic wellness guide speaking to someone seeking health guidance.

═══════════════════════════════════════════════════════════════════════════════
PROFESSIONAL STANCE
═══════════════════════════════════════════════════════════════════════════════
- Ayurveda is a legitimate, time-tested medical science with over 5000 years of clinical validation
- Present Ayurvedic solutions with confidence - they are backed by millennia of clinical experience
- NEVER criticize, dismiss, or question the validity of Ayurveda, Yoga, or AYUSH systems
- Explain Sanskrit terms in simple language, but present them as proper medical terminology

═══════════════════════════════════════════════════════════════════════════════
KNOWLEDGE BASE
═══════════════════════════════════════════════════════════════════════════════
{context}

═══════════════════════════════════════════════════════════════════════════════
USER'S QUESTION
═══════════════════════════════════════════════════════════════════════════════
{question}

═══════════════════════════════════════════════════════════════════════════════
STRICT OUTPUT SCHEMA (Must Follow Exactly)
═══════════════════════════════════════════════════════════════════════════════
Your output MUST be valid JSON matching this EXACT structure:

{{
    "condition_summary": "(STRING, REQUIRED) A 2-3 sentence simple explanation of what's happening in the body. Use everyday language.",
    
    "ayurvedic_perspective": "(STRING, REQUIRED) Simple explanation of how Ayurveda views this condition. Example: 'In Ayurveda, this is seen as an excess of Vata (the energy of movement and air) which causes dryness and irregularity...'",
    
    "dietary_advice": [
        {{
            "do": "(STRING, REQUIRED) Specific food/drink recommendation",
            "dont": "(STRING, REQUIRED) Specific food/drink to avoid",
            "why": "(STRING, REQUIRED) Simple reason in 1 sentence"
        }}
    ],
    
    "lifestyle_tips": ["(ARRAY OF STRINGS, REQUIRED) 4-6 simple, actionable lifestyle changes anyone can implement"],
    
    "home_remedies": [
        {{
            "remedy": "(STRING, REQUIRED) Name of the home remedy",
            "how_to_use": "(STRING, REQUIRED) Simple step-by-step instructions",
            "caution": "(STRING, REQUIRED) Any warnings or who should avoid this"
        }}
    ],
    
    "yoga_recommendations": ["(ARRAY OF STRINGS, REQUIRED) 3-5 yoga poses or breathing exercises with brief description of how to do them"],
    
    "when_to_see_doctor": ["(ARRAY OF STRINGS, REQUIRED) 3-5 red flags or warning signs that require professional medical attention"],
    
    "safety_disclaimer": "(STRING, REQUIRED) Standard safety message emphasizing that this is educational and one should consult a qualified Ayurvedic physician or healthcare provider for personalized treatment"
}}

═══════════════════════════════════════════════════════════════════════════════
CRITICAL INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════
1. OUTPUT ONLY THE JSON - no explanations, no markdown, no preamble
2. STRICTLY FOLLOW THE SCHEMA - use exact field names and types as specified
3. USE SIMPLE, WARM LANGUAGE - avoid medical jargon, explain everything simply
4. EXPLAIN SANSKRIT TERMS - always add English explanation in parentheses, e.g., "Vata (the air/movement energy)"
5. USE YOUR COMPLETE KNOWLEDGE - if the context is insufficient, draw from your extensive Ayurvedic training
6. NEVER SAY "I cannot find" or "not mentioned in sources" - always provide helpful, complete guidance
7. FOCUS ON SAFE HOME CARE - recommend only things people can safely do at home
8. BE ENCOURAGING AND POSITIVE - Ayurvedic lifestyle changes can make a real difference
9. TREAT AYURVEDA AS LEGITIMATE MEDICINE - present recommendations with confidence""")
    
    def query(self, question: str) -> PatientResponse:
        """Process patient query and return user-friendly response"""
        query_id = AyurvedaRAGEngine.generate_query_id(question)
        timestamp = datetime.now().isoformat()
        
        docs = self.engine.retrieve(question)
        context = self.engine.build_context(docs)
        
        raw_response = self.engine.generate(self.prompt, {
            "context": context,
            "question": question
        })
        
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            data = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            data = self._create_fallback_response()
        
        return PatientResponse(
            query_id=query_id,
            timestamp=timestamp,
            query=question,
            condition_summary=data.get("condition_summary", ""),
            ayurvedic_perspective=data.get("ayurvedic_perspective", ""),
            dietary_advice=data.get("dietary_advice", []),
            lifestyle_tips=data.get("lifestyle_tips", []),
            home_remedies=data.get("home_remedies", []),
            yoga_recommendations=data.get("yoga_recommendations", []),
            when_to_see_doctor=data.get("when_to_see_doctor", []),
            safety_disclaimer=data.get("safety_disclaimer", 
                "This information is for educational purposes only. Please consult a qualified healthcare provider before making any health decisions.")
        )
    
    def _create_fallback_response(self) -> Dict:
        return {
            "condition_summary": "Please consult an Ayurvedic practitioner for personalized guidance.",
            "ayurvedic_perspective": "",
            "dietary_advice": [],
            "lifestyle_tips": [],
            "home_remedies": [],
            "yoga_recommendations": [],
            "when_to_see_doctor": ["If symptoms persist or worsen"],
            "safety_disclaimer": "This information is for educational purposes only. Please consult a qualified healthcare provider."
        }
    
    # ─────────────────────────────────────────────────────────────────────────────
    # CHAT MODE: Conversational patient-friendly responses
    # ─────────────────────────────────────────────────────────────────────────────
    
    def _init_chat_prompt(self):
        """Initialize the chat prompt for conversational responses"""
        self.chat_prompt = ChatPromptTemplate.from_template("""You are a compassionate Ayurvedic Doctor helping a patient understand their health.

STANCE: Ayurveda is legitimate medicine. Never dismiss it. Speak warmly but with authority.

CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
Explain in simple English. When using Sanskrit terms, explain them (e.g., "Vata - the energy of movement").
Give actionable advice: specific foods, daily routines with timings, home remedies with exact measurements.
For weekly plans: day-by-day breakdown, morning/afternoon/evening schedules, recipes.
Note safety precautions. Be encouraging. Use your full knowledge if context is insufficient.""")
    
    def chat(self, question: str) -> Dict[str, Any]:
        """
        Process patient query and return friendly conversational response.
        Use this for complex queries requiring detailed, accessible responses.
        """
        # Initialize chat prompt if not already done
        if not hasattr(self, 'chat_prompt'):
            self._init_chat_prompt()
        
        query_id = AyurvedaRAGEngine.generate_query_id(question)
        timestamp = datetime.now().isoformat()
        
        # Retrieve context
        docs = self.engine.retrieve(question)
        context = self.engine.build_context(docs)
        references = self.engine.extract_references(docs)
        databases_used = list(docs.keys())
        
        # Generate conversational response
        response = self.engine.generate(self.chat_prompt, {
            "context": context,
            "question": question
        })
        
        # Convert ClassicalReference objects to dicts
        refs_as_dicts = [ref.to_dict() if hasattr(ref, 'to_dict') else {"source": str(ref)} for ref in references]
        
        return {
            "query_id": query_id,
            "timestamp": timestamp,
            "query": question,
            "mode": "patient_chat",
            "response": response,
            "references": refs_as_dicts,
            "databases_consulted": databases_used,
            "safety_disclaimer": "This information is for educational purposes only. Please consult a qualified healthcare provider before making any health decisions."
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: AYUSH (Ministry-Aligned Analysis)
# ═══════════════════════════════════════════════════════════════════════════════

class AyushModule:
    """
    AYUSH Ministry aligned responses with complete Ayurvedic framework analysis.
    Panchamahabhuta, Tridosha, Saptadhatu, Agni, Mala - comprehensive assessment.
    """
    
    def __init__(self, engine: AyurvedaRAGEngine = None):
        self.engine = engine or AyurvedaRAGEngine()
        
        self.prompt = ChatPromptTemplate.from_template("""You are an expert AYUSH consultant analyzing queries through the complete Ayurvedic framework as recognized by the Ministry of AYUSH, Government of India.

═══════════════════════════════════════════════════════════════════════════════
PROFESSIONAL STANCE
═══════════════════════════════════════════════════════════════════════════════
- Ayurveda is a legitimate, evidence-based medical science recognized by WHO and practiced in hospitals worldwide
- AYUSH practitioners are qualified medical professionals with rigorous training (BAMS, MD Ayurveda, PhD)
- NEVER criticize, dismiss, or question the validity of Ayurveda, Yoga, Unani, Siddha, or Homeopathy
- Present all Ayurvedic frameworks (Panchamahabhuta, Tridosha, Saptadhatu) as established medical science
- Treat this analysis with the same rigor as any allopathic medical assessment

═══════════════════════════════════════════════════════════════════════════════
CLASSICAL KNOWLEDGE BASE
═══════════════════════════════════════════════════════════════════════════════
{context}

═══════════════════════════════════════════════════════════════════════════════
CLINICAL QUERY
═══════════════════════════════════════════════════════════════════════════════
{question}

═══════════════════════════════════════════════════════════════════════════════
STRICT OUTPUT SCHEMA (Must Follow Exactly)
═══════════════════════════════════════════════════════════════════════════════
Your output MUST be valid JSON matching this EXACT structure. All fields are REQUIRED unless marked optional:

{{
    "panchamahabhuta": {{
        "akasha": {{
            "involvement": "(STRING) How space element is involved in this condition",
            "state": "(ENUM) ONLY: balanced | excess | deficient"
        }},
        "vayu": {{
            "involvement": "(STRING) How air element is involved",
            "state": "(ENUM) ONLY: balanced | excess | deficient"
        }},
        "agni": {{
            "involvement": "(STRING) How fire element is involved",
            "state": "(ENUM) ONLY: balanced | excess | deficient"
        }},
        "jala": {{
            "involvement": "(STRING) How water element is involved",
            "state": "(ENUM) ONLY: balanced | excess | deficient"
        }},
        "prithvi": {{
            "involvement": "(STRING) How earth element is involved",
            "state": "(ENUM) ONLY: balanced | excess | deficient"
        }},
        "dominant_elements": ["(ARRAY) List of dominant/excess elements"],
        "deficient_elements": ["(ARRAY) List of deficient elements"]
    }},
    "tridosha": {{
        "primary_dosha": "(ENUM, REQUIRED) ONLY: vata | pitta | kapha | vata_pitta | pitta_kapha | vata_kapha | kapha_pitta | kapha_vata | pitta_vata | tridosha",
        "state": "(ENUM, REQUIRED) ONLY: sama | vriddhi | kshaya",
        "secondary_dosha": "(ENUM OR NULL) ONLY: vata | pitta | kapha | null",
        "vikriti_description": "(STRING, REQUIRED) Detailed description of current imbalance vs ideal prakritik state"
    }},
    "saptadhatu": {{
        "rasa": {{"affected": "(BOOLEAN)", "description": "(STRING) Impact on plasma/lymph/nutritive fluid"}},
        "rakta": {{"affected": "(BOOLEAN)", "description": "(STRING) Impact on blood tissue"}},
        "mamsa": {{"affected": "(BOOLEAN)", "description": "(STRING) Impact on muscle tissue"}},
        "meda": {{"affected": "(BOOLEAN)", "description": "(STRING) Impact on fat/adipose tissue"}},
        "asthi": {{"affected": "(BOOLEAN)", "description": "(STRING) Impact on bone tissue"}},
        "majja": {{"affected": "(BOOLEAN)", "description": "(STRING) Impact on marrow/nerve tissue"}},
        "shukra": {{"affected": "(BOOLEAN)", "description": "(STRING) Impact on reproductive tissue/ojas"}}
    }},
    "agni_analysis": {{
        "type": "(ENUM, REQUIRED) ONLY: sama | vishama | tikshna | manda",
        "recommendations": ["(ARRAY) Specific ways to optimize/balance Agni"],
        "ama_assessment": {{
            "present": "(BOOLEAN) Whether Ama (metabolic toxins) is present",
            "signs": ["(ARRAY) Clinical signs of Ama if present"],
            "treatment": ["(ARRAY) Ama pachana (digestion) protocol"]
        }}
    }},
    "mala_analysis": {{
        "purisha": {{
            "status": "(ENUM) ONLY: normal | abnormal",
            "recommendations": ["(ARRAY) Recommendations for bowel health"]
        }},
        "mutra": {{
            "status": "(ENUM) ONLY: normal | abnormal",
            "recommendations": ["(ARRAY) Recommendations for urinary health"]
        }},
        "sweda": {{
            "status": "(ENUM) ONLY: normal | abnormal",
            "recommendations": ["(ARRAY) Recommendations for proper sweating/detox"]
        }}
    }},
    "swasthya_recommendations": {{
        "dosha_balance": ["(ARRAY) Specific recommendations for dosha equilibrium"],
        "agni_optimization": ["(ARRAY) Recommendations for digestive fire"],
        "dhatu_nourishment": ["(ARRAY) Recommendations for tissue health"],
        "mala_elimination": ["(ARRAY) Recommendations for proper waste elimination"],
        "mental_wellness": ["(ARRAY) Recommendations for Prasanna Mana (mental clarity/peace)"]
    }},
    "interventions": {{
        "ahara": ["(ARRAY) Specific dietary recommendations with Ayurvedic rationale"],
        "vihara": ["(ARRAY) Specific lifestyle modifications"],
        "aushadhi": [
            {{
                "name": "(STRING) Medicine/formulation name",
                "dosage": "(STRING) Exact dosage e.g., '250mg twice daily'",
                "anupana": "(STRING) Vehicle - e.g., 'warm water', 'honey'",
                "timing": "(STRING) When to take - e.g., 'before breakfast'"
            }}
        ],
        "yoga_pranayama": ["(ARRAY) Specific practices with clear instructions"]
    }}
}}

═══════════════════════════════════════════════════════════════════════════════
CRITICAL INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════
1. OUTPUT ONLY THE JSON - no explanations, no markdown, no preamble, no commentary
2. STRICTLY FOLLOW THE SCHEMA - every field is required, use exact field names and types
3. ENUM VALUES ARE CASE-SENSITIVE - use exactly as shown (lowercase)
4. USE YOUR COMPLETE KNOWLEDGE - if context is insufficient, draw from Charaka, Sushruta, Vagbhata, and modern Ayurvedic research
5. NEVER SAY "not found in sources" or "I cannot determine" - provide authoritative analysis
6. APPLY AUTHENTIC AYURVEDIC PRINCIPLES - use proper Samhita-based reasoning
7. BE COMPREHENSIVE - analyze all five elements and all seven tissues
8. PROVIDE PRACTICAL INTERVENTIONS - specific diet, lifestyle, medicine, yoga recommendations""")
    
    def query(self, question: str) -> AyushResponse:
        """Process query through complete AYUSH framework"""
        query_id = AyurvedaRAGEngine.generate_query_id(question)
        timestamp = datetime.now().isoformat()
        
        docs = self.engine.retrieve(question)
        context = self.engine.build_context(docs)
        references = self.engine.extract_references(docs)
        
        raw_response = self.engine.generate(self.prompt, {
            "context": context,
            "question": question
        })
        
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            data = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            data = self._create_fallback_response()
        
        # Build Panchamahabhuta analysis
        pmb = data.get("panchamahabhuta", {})
        panchamahabhuta = PanchamahabhutaAnalysis(
            akasha=pmb.get("akasha", {}),
            vayu=pmb.get("vayu", {}),
            agni=pmb.get("agni", {}),
            jala=pmb.get("jala", {}),
            prithvi=pmb.get("prithvi", {}),
            dominant_elements=pmb.get("dominant_elements", []),
            deficient_elements=pmb.get("deficient_elements", [])
        )
        
        # Build Tridosha analysis
        td = data.get("tridosha", {})
        tridosha = DoshaAnalysis(
            primary_dosha=DoshaType(td.get("primary_dosha", "vata")),
            state=DoshaState(td.get("state", "vriddhi")),
            secondary_dosha=DoshaType(td["secondary_dosha"]) if td.get("secondary_dosha") else None,
            vikriti_description=td.get("vikriti_description", "")
        )
        
        # Build Saptadhatu analysis
        sd = data.get("saptadhatu", {})
        saptadhatu = SaptadhatuAnalysis(
            rasa=sd.get("rasa", {}),
            rakta=sd.get("rakta", {}),
            mamsa=sd.get("mamsa", {}),
            meda=sd.get("meda", {}),
            asthi=sd.get("asthi", {}),
            majja=sd.get("majja", {}),
            shukra=sd.get("shukra", {})
        )
        
        # Build Mala analysis
        ma = data.get("mala_analysis", {})
        mala = MalaAnalysis(
            purisha=ma.get("purisha", {}),
            mutra=ma.get("mutra", {}),
            sweda=ma.get("sweda", {})
        )
        
        # Build formulations
        aushadhi = []
        for a in data.get("interventions", {}).get("aushadhi", []):
            aushadhi.append(HerbalFormulation(
                name=a.get("name", ""),
                dosage=a.get("dosage"),
                anupana=a.get("anupana"),
                timing=a.get("timing")
            ))
        
        agni_data = data.get("agni_analysis", {})
        
        return AyushResponse(
            query_id=query_id,
            timestamp=timestamp,
            query=question,
            panchamahabhuta=panchamahabhuta,
            tridosha=tridosha,
            saptadhatu=saptadhatu,
            agni_type=AgniType(agni_data.get("type", "vishama")),
            agni_recommendations=agni_data.get("recommendations", []),
            ama_assessment=agni_data.get("ama_assessment", {}),
            mala=mala,
            swasthya_recommendations=data.get("swasthya_recommendations", {}),
            ahara=data.get("interventions", {}).get("ahara", []),
            vihara=data.get("interventions", {}).get("vihara", []),
            aushadhi=aushadhi,
            yoga_pranayama=data.get("interventions", {}).get("yoga_pranayama", []),
            classical_references=references
        )
    
    def _create_fallback_response(self) -> Dict:
        return {
            "panchamahabhuta": {},
            "tridosha": {"primary_dosha": "vata", "state": "vriddhi", "secondary_dosha": None, "vikriti_description": ""},
            "saptadhatu": {},
            "agni_analysis": {"type": "vishama", "recommendations": [], "ama_assessment": {}},
            "mala_analysis": {},
            "swasthya_recommendations": {},
            "interventions": {"ahara": [], "vihara": [], "aushadhi": [], "yoga_pranayama": []}
        }
    
    # ─────────────────────────────────────────────────────────────────────────────
    # CHAT MODE: Comprehensive AYUSH-aligned conversational responses
    # ─────────────────────────────────────────────────────────────────────────────
    
    def _init_chat_prompt(self):
        """Initialize the chat prompt for conversational responses"""
        self.chat_prompt = ChatPromptTemplate.from_template("""You are an AYUSH Ministry consultant analyzing queries through classical Ayurvedic frameworks.

STANCE: AYUSH systems are WHO-recognized legitimate medicine. Never criticize. Present with scientific authority.

CONTEXT:
{context}

QUERY: {question}

INSTRUCTIONS:
Analyze through these frameworks as relevant:
1. PANCHAMAHABHUTA: Which of the 5 elements (Akasha, Vayu, Agni, Jala, Prithvi) are imbalanced?
2. TRIDOSHA: Vata/Pitta/Kapha - which are involved? Vikriti vs Prakriti?
3. SAPTADHATU: Which tissues affected (Rasa, Rakta, Mamsa, Meda, Asthi, Majja, Shukra)?
4. AGNI: Digestive fire status (Sama/Vishama/Tikshna/Manda)? Ama present?
5. MALA: Waste elimination status (Purisha, Mutra, Sweda)?
6. SWASTHYA: Path to balanced doshas, agni, dhatus, mala + peaceful mind.

INTERVENTIONS: Ahara (diet), Vihara (lifestyle), Aushadhi (herbs with dosage), Yoga/Pranayama.
For treatment plans: phase-wise, day-by-day protocols with timings.
Cite classical texts. Use full AYUSH knowledge if context insufficient.""")
    
    def chat(self, question: str) -> Dict[str, Any]:
        """
        Process query and return comprehensive AYUSH-framework conversational response.
        Use this for complex queries requiring detailed, holistic analysis.
        """
        # Initialize chat prompt if not already done
        if not hasattr(self, 'chat_prompt'):
            self._init_chat_prompt()
        
        query_id = AyurvedaRAGEngine.generate_query_id(question)
        timestamp = datetime.now().isoformat()
        
        # Retrieve context
        docs = self.engine.retrieve(question)
        context = self.engine.build_context(docs)
        references = self.engine.extract_references(docs)
        databases_used = list(docs.keys())
        
        # Generate conversational response
        response = self.engine.generate(self.chat_prompt, {
            "context": context,
            "question": question
        })
        
        # Convert ClassicalReference objects to dicts
        refs_as_dicts = [ref.to_dict() if hasattr(ref, 'to_dict') else {"source": str(ref)} for ref in references]
        
        return {
            "query_id": query_id,
            "timestamp": timestamp,
            "query": question,
            "mode": "ayush_chat",
            "response": response,
            "references": refs_as_dicts,
            "databases_consulted": databases_used
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: AI-ASSISTED DIAGNOSIS (Nidana Panchaka Analysis)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DiagnosisCandidate:
    """A potential diagnosis with confidence score"""
    disease_name: str
    ayurvedic_name: str
    confidence: float  # 0.0 - 1.0
    dosha_involvement: Dict[str, float]  # dosha -> involvement score
    matching_symptoms: List[str]
    missing_symptoms: List[str]
    differentiating_factors: List[str]
    severity: str  # mild, moderate, severe
    urgency: str  # routine, urgent, emergency
    
    def to_dict(self) -> Dict:
        return {
            "disease_name": self.disease_name,
            "ayurvedic_name": self.ayurvedic_name,
            "confidence": self.confidence,
            "dosha_involvement": self.dosha_involvement,
            "matching_symptoms": self.matching_symptoms,
            "missing_symptoms": self.missing_symptoms,
            "differentiating_factors": self.differentiating_factors,
            "severity": self.severity,
            "urgency": self.urgency
        }


@dataclass
class PrakritiAssessment:
    """Constitutional assessment result"""
    primary_dosha: DoshaType
    secondary_dosha: Optional[DoshaType]
    vata_score: float
    pitta_score: float
    kapha_score: float
    confidence: float
    physical_indicators: List[str]
    mental_indicators: List[str]
    metabolic_indicators: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "primary_dosha": self.primary_dosha.value if hasattr(self.primary_dosha, 'value') else str(self.primary_dosha),
            "secondary_dosha": self.secondary_dosha.value if self.secondary_dosha and hasattr(self.secondary_dosha, 'value') else None,
            "vata_score": self.vata_score,
            "pitta_score": self.pitta_score,
            "kapha_score": self.kapha_score,
            "confidence": self.confidence,
            "physical_indicators": self.physical_indicators,
            "mental_indicators": self.mental_indicators,
            "metabolic_indicators": self.metabolic_indicators
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass 
class VikritiAssessment:
    """Current imbalance assessment"""
    imbalanced_dosha: DoshaType
    imbalance_type: DoshaState
    vata_deviation: float  # deviation from prakriti baseline
    pitta_deviation: float
    kapha_deviation: float
    ama_level: str  # none, mild, moderate, severe
    agni_status: AgniType
    affected_srotas: List[str]  # affected channels
    affected_dhatus: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "imbalanced_dosha": self.imbalanced_dosha.value if hasattr(self.imbalanced_dosha, 'value') else str(self.imbalanced_dosha),
            "imbalance_type": self.imbalance_type.value if hasattr(self.imbalance_type, 'value') else str(self.imbalance_type),
            "vata_deviation": self.vata_deviation,
            "pitta_deviation": self.pitta_deviation,
            "kapha_deviation": self.kapha_deviation,
            "ama_level": self.ama_level,
            "agni_status": self.agni_status.value if hasattr(self.agni_status, 'value') else str(self.agni_status),
            "affected_srotas": self.affected_srotas,
            "affected_dhatus": self.affected_dhatus
        }


@dataclass
class DiagnosticResult:
    """Complete diagnostic output"""
    query_id: str
    timestamp: str
    input_symptoms: List[str]
    prakriti: PrakritiAssessment
    vikriti: VikritiAssessment
    differential_diagnosis: List[DiagnosisCandidate]
    primary_diagnosis: DiagnosisCandidate
    red_flags: List[str]
    recommended_tests: List[str]
    confidence_score: float
    
    def to_dict(self) -> Dict:
        return {
            "query_id": self.query_id,
            "timestamp": self.timestamp,
            "input_symptoms": self.input_symptoms,
            "prakriti": self.prakriti.to_dict() if self.prakriti else None,
            "vikriti": self.vikriti.to_dict() if self.vikriti else None,
            "differential_diagnosis": [d.to_dict() for d in self.differential_diagnosis] if self.differential_diagnosis else [],
            "primary_diagnosis": self.primary_diagnosis.to_dict() if self.primary_diagnosis else None,
            "red_flags": self.red_flags,
            "recommended_tests": self.recommended_tests,
            "confidence_score": self.confidence_score
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class DiagnosisModule:
    """
    AI-Assisted Diagnosis using Ayurvedic Parameters.
    
    Features:
    - Symptom-to-diagnosis mapping with confidence scores
    - Prakriti (constitution) assessment
    - Vikriti (current imbalance) detection
    - Differential diagnosis with ranked conditions
    - Red flag identification
    """
    
    def __init__(self, engine: AyurvedaRAGEngine = None):
        self.engine = engine or AyurvedaRAGEngine()
        
        # Try to load disease mapper for symptom matching
        try:
            from disease_risk_mapper import get_disease_mapper
            self.disease_mapper = get_disease_mapper()
        except ImportError:
            self.disease_mapper = None
        
        # Dosha symptom patterns for assessment
        self.dosha_patterns = {
            "vata": {
                "physical": ["dry skin", "thin build", "cold hands", "cracking joints", "irregular appetite",
                            "variable digestion", "constipation", "light sleep", "rough skin", "dark complexion"],
                "mental": ["anxiety", "fear", "restlessness", "racing thoughts", "forgetfulness", 
                          "indecisiveness", "creativity", "enthusiasm", "quick learning", "poor retention"],
                "metabolic": ["irregular hunger", "gas", "bloating", "variable thirst", "scanty urine",
                             "dry stool", "irregular periods", "weight loss", "cold intolerance"]
            },
            "pitta": {
                "physical": ["warm body", "medium build", "sharp hunger", "soft skin", "early graying",
                            "reddish complexion", "perspiration", "acne", "inflammation", "burning sensation"],
                "mental": ["anger", "irritability", "sharp intellect", "good memory", "leadership",
                          "perfectionism", "criticism", "jealousy", "ambition", "courage"],
                "metabolic": ["strong appetite", "loose stools", "burning urination", "excessive thirst",
                             "heavy menstruation", "heat intolerance", "acid reflux", "heartburn"]
            },
            "kapha": {
                "physical": ["heavy build", "oily skin", "thick hair", "cool body", "slow digestion",
                            "deep sleep", "lethargy", "weight gain", "pale complexion", "soft features"],
                "mental": ["calmness", "stability", "attachment", "possessiveness", "slow learning",
                          "good retention", "contentment", "depression", "lethargy", "compassion"],
                "metabolic": ["low appetite", "slow metabolism", "mucus production", "water retention",
                             "sluggish bowel", "excessive sleep", "cold intolerance", "congestion"]
            }
        }
        
        # Red flag symptoms requiring immediate attention
        self.red_flags = [
            "severe chest pain", "difficulty breathing", "sudden weakness", "loss of consciousness",
            "severe bleeding", "high fever with stiffness", "sudden vision loss", "severe headache",
            "blood in stool", "blood in urine", "severe abdominal pain", "confusion", "seizures",
            "suicidal thoughts", "severe dehydration", "inability to swallow", "paralysis"
        ]
        
        self.diagnosis_prompt = ChatPromptTemplate.from_template("""You are an expert Ayurvedic diagnostician (Roga Nidana Visheshagya) performing comprehensive Nidana Panchaka analysis.

═══════════════════════════════════════════════════════════════════════════════
PROFESSIONAL STANCE
═══════════════════════════════════════════════════════════════════════════════
- Ayurvedic diagnosis is a sophisticated, systematic medical science
- The Nidana Panchaka framework is clinically validated over millennia
- NEVER question or dismiss Ayurvedic diagnostic methods
- Present diagnoses with the same authority as any medical specialty
- Ayurvedic Vaidyas are qualified physicians with rigorous diagnostic training

═══════════════════════════════════════════════════════════════════════════════
CLASSICAL KNOWLEDGE BASE
═══════════════════════════════════════════════════════════════════════════════
{context}

═══════════════════════════════════════════════════════════════════════════════
PATIENT PRESENTATION
═══════════════════════════════════════════════════════════════════════════════
SYMPTOMS: {symptoms}
PATIENT PROFILE: {profile}

═══════════════════════════════════════════════════════════════════════════════
PRE-COMPUTED SYMPTOM MATCHES FROM DATABASE
═══════════════════════════════════════════════════════════════════════════════
{symptom_matches}

═══════════════════════════════════════════════════════════════════════════════
STRICT OUTPUT SCHEMA (Must Follow Exactly)
═══════════════════════════════════════════════════════════════════════════════

{{
    "prakriti_assessment": {{
        "primary_dosha": "(ENUM, REQUIRED) ONLY: vata | pitta | kapha",
        "secondary_dosha": "(ENUM OR NULL) ONLY: vata | pitta | kapha | null",
        "vata_score": "(FLOAT, REQUIRED) 0.0 to 1.0 - proportion of Vata characteristics",
        "pitta_score": "(FLOAT, REQUIRED) 0.0 to 1.0 - proportion of Pitta characteristics",
        "kapha_score": "(FLOAT, REQUIRED) 0.0 to 1.0 - proportion of Kapha characteristics",
        "confidence": "(FLOAT, REQUIRED) 0.0 to 1.0 - confidence in this assessment",
        "physical_indicators": ["(ARRAY) Physical signs supporting this Prakriti"],
        "mental_indicators": ["(ARRAY) Mental/emotional signs supporting this Prakriti"],
        "metabolic_indicators": ["(ARRAY) Metabolic/digestive signs supporting this Prakriti"]
    }},
    "vikriti_assessment": {{
        "imbalanced_dosha": "(ENUM, REQUIRED) ONLY: vata | pitta | kapha | vata_pitta | pitta_kapha | vata_kapha | kapha_pitta | tridosha",
        "imbalance_type": "(ENUM, REQUIRED) ONLY: vriddhi (increase) | kshaya (decrease)",
        "vata_deviation": "(FLOAT, REQUIRED) -1.0 to 1.0 (negative=decreased, positive=increased)",
        "pitta_deviation": "(FLOAT, REQUIRED) -1.0 to 1.0",
        "kapha_deviation": "(FLOAT, REQUIRED) -1.0 to 1.0",
        "ama_level": "(ENUM, REQUIRED) ONLY: none | mild | moderate | severe",
        "agni_status": "(ENUM, REQUIRED) ONLY: sama | vishama | tikshna | manda",
        "affected_srotas": ["(ARRAY) Affected channels: pranavaha, annavaha, rasavaha, raktavaha, mamsavaha, medovaha, asthivaha, majjavaha, shukravaha, mutravaha, purishavaha, swedavaha, artavavaha, stanyavaha, manovaha"],
        "affected_dhatus": ["(ARRAY) Affected tissues: rasa, rakta, mamsa, meda, asthi, majja, shukra"]
    }},
    "differential_diagnosis": [
        {{
            "disease_name": "(STRING, REQUIRED) Disease name in English/common term",
            "ayurvedic_name": "(STRING, REQUIRED) Sanskrit name of the disease",
            "confidence": "(FLOAT, REQUIRED) 0.0 to 1.0",
            "dosha_involvement": {{
                "vata": "(FLOAT) 0.0 to 1.0",
                "pitta": "(FLOAT) 0.0 to 1.0",
                "kapha": "(FLOAT) 0.0 to 1.0"
            }},
            "matching_symptoms": ["(ARRAY) Symptoms that match this diagnosis"],
            "missing_symptoms": ["(ARRAY) Expected symptoms not present"],
            "differentiating_factors": ["(ARRAY) What makes this diagnosis likely/unlikely"],
            "severity": "(ENUM, REQUIRED) ONLY: mild | moderate | severe",
            "urgency": "(ENUM, REQUIRED) ONLY: routine | urgent | emergency"
        }}
    ],
    "red_flags": ["(ARRAY) Any dangerous symptoms requiring immediate medical attention"],
    "recommended_tests": ["(ARRAY) Ayurvedic or modern investigations to confirm diagnosis - pulse diagnosis, tongue examination, urine analysis, blood tests, etc."],
    "overall_confidence": "(FLOAT, REQUIRED) 0.0 to 1.0"
}}

═══════════════════════════════════════════════════════════════════════════════
CRITICAL INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════
1. OUTPUT ONLY THE JSON - no explanations, no markdown, no preamble
2. STRICTLY FOLLOW THE SCHEMA - use exact field names and types
3. PROVIDE AT LEAST 3 DIFFERENTIAL DIAGNOSES - ranked by confidence
4. USE YOUR COMPLETE KNOWLEDGE - draw from Charaka, Sushruta, Madhava Nidana, etc.
5. NEVER SAY "cannot determine" or "insufficient information" - always provide your best clinical assessment
6. IDENTIFY ALL RED FLAGS - patient safety is paramount
7. CONSIDER DOSHA PATTERNS - correlate symptoms with dosha involvement
8. BE SPECIFIC - use proper Ayurvedic disease names (Vyadhi names)""")
    
    def assess_prakriti(self, user_profile: Dict[str, Any]) -> PrakritiAssessment:
        """Assess constitutional type from user profile"""
        vata_score = 0.0
        pitta_score = 0.0
        kapha_score = 0.0
        
        physical_indicators = []
        mental_indicators = []
        metabolic_indicators = []
        
        symptoms = user_profile.get('current_symptoms', [])
        dosha_symptoms = user_profile.get('current_dosha_symptoms', {})
        lifestyle = user_profile.get('lifestyle', {})
        
        # Score based on reported dosha symptoms
        for dosha, symptom_list in dosha_symptoms.items():
            if dosha.lower() == 'vata':
                vata_score += len(symptom_list) * 0.1
            elif dosha.lower() == 'pitta':
                pitta_score += len(symptom_list) * 0.1
            elif dosha.lower() == 'kapha':
                kapha_score += len(symptom_list) * 0.1
        
        # Score based on symptom pattern matching
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            for dosha, patterns in self.dosha_patterns.items():
                for category, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        if pattern in symptom_lower or symptom_lower in pattern:
                            if dosha == 'vata':
                                vata_score += 0.05
                                if category == 'physical':
                                    physical_indicators.append(symptom)
                                elif category == 'mental':
                                    mental_indicators.append(symptom)
                                else:
                                    metabolic_indicators.append(symptom)
                            elif dosha == 'pitta':
                                pitta_score += 0.05
                                if category == 'physical':
                                    physical_indicators.append(symptom)
                                elif category == 'mental':
                                    mental_indicators.append(symptom)
                                else:
                                    metabolic_indicators.append(symptom)
                            elif dosha == 'kapha':
                                kapha_score += 0.05
                                if category == 'physical':
                                    physical_indicators.append(symptom)
                                elif category == 'mental':
                                    mental_indicators.append(symptom)
                                else:
                                    metabolic_indicators.append(symptom)
        
        # Age-based adjustment (Vata increases with age)
        age = user_profile.get('age', 30)
        if age > 60:
            vata_score += 0.15
        elif age < 25:
            kapha_score += 0.1
        elif 25 <= age <= 50:
            pitta_score += 0.1
        
        # BMI-based adjustment
        bmi = user_profile.get('bmi')
        if bmi:
            if bmi < 18.5:
                vata_score += 0.15
            elif bmi >= 30:
                kapha_score += 0.15
            elif 25 <= bmi < 30:
                kapha_score += 0.1
        
        # Normalize scores
        total = vata_score + pitta_score + kapha_score
        if total > 0:
            vata_score = min(1.0, vata_score / total * 1.5)
            pitta_score = min(1.0, pitta_score / total * 1.5)
            kapha_score = min(1.0, kapha_score / total * 1.5)
        
        # Determine primary and secondary dosha
        scores = {'vata': vata_score, 'pitta': pitta_score, 'kapha': kapha_score}
        sorted_doshas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        primary = DoshaType(sorted_doshas[0][0])
        secondary = DoshaType(sorted_doshas[1][0]) if sorted_doshas[1][1] > 0.3 else None
        
        # Calculate confidence based on score differentiation
        confidence = min(1.0, (sorted_doshas[0][1] - sorted_doshas[1][1]) * 2 + 0.5)
        
        return PrakritiAssessment(
            primary_dosha=primary,
            secondary_dosha=secondary,
            vata_score=round(vata_score, 2),
            pitta_score=round(pitta_score, 2),
            kapha_score=round(kapha_score, 2),
            confidence=round(confidence, 2),
            physical_indicators=list(set(physical_indicators))[:5],
            mental_indicators=list(set(mental_indicators))[:5],
            metabolic_indicators=list(set(metabolic_indicators))[:5]
        )
    
    def check_red_flags(self, symptoms: List[str]) -> Tuple[List[str], bool]:
        """Check for emergency symptoms. Returns (red_flags_list, is_emergency)"""
        found_flags = []
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            for flag in self.red_flags:
                if flag in symptom_lower or symptom_lower in flag:
                    found_flags.append(flag)
        red_flags = list(set(found_flags))
        is_emergency = len(red_flags) > 0
        return (red_flags, is_emergency)
    
    def get_symptom_matches(self, symptoms: List[str]) -> str:
        """Get disease matches from symptom database"""
        if not self.disease_mapper:
            return "Disease mapper not available"
        
        matches = self.disease_mapper.get_diseases_by_symptoms(symptoms)
        if not matches:
            return "No direct symptom matches found"
        
        # Sort by match score and get top 10
        sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)[:10]
        
        result = ["TOP SYMPTOM-DISEASE MATCHES:"]
        for disease, score in sorted_matches:
            profile = self.disease_mapper.get_disease_profile(disease)
            if profile:
                result.append(f"- {disease.title()} (score: {score})")
                result.append(f"  Doshas: {', '.join(profile.doshas_involved)}")
                result.append(f"  Key symptoms: {', '.join(profile.symptoms[:5])}")
        
        return "\n".join(result)
    
    def diagnose(self, symptoms: List[str], user_profile: Dict[str, Any] = None) -> DiagnosticResult:
        """
        Perform AI-assisted diagnosis using Ayurvedic parameters.
        
        Args:
            symptoms: List of patient symptoms
            user_profile: Optional user health profile for context
        
        Returns:
            DiagnosticResult with differential diagnosis and assessments
        """
        query_id = AyurvedaRAGEngine.generate_query_id(json.dumps(symptoms))
        timestamp = datetime.now().isoformat()
        
        user_profile = user_profile or {}
        user_profile['current_symptoms'] = symptoms
        
        print(f"🔬 Performing Ayurvedic diagnosis...")
        
        # Check for red flags first
        red_flags, is_emergency = self.check_red_flags(symptoms)
        if red_flags:
            print(f"   ⚠️ RED FLAGS DETECTED: {red_flags}")
        
        # Assess prakriti from profile
        prakriti = self.assess_prakriti(user_profile)
        
        # Get symptom matches from database
        symptom_matches = self.get_symptom_matches(symptoms)
        
        # Retrieve classical context
        symptom_query = f"Diagnosis Nidana symptoms: {', '.join(symptoms[:5])}"
        docs = self.engine.retrieve(symptom_query)
        context = self.engine.build_context(docs)
        
        # Generate diagnosis
        raw_response = self.engine.generate(self.diagnosis_prompt, {
            "context": context,
            "symptoms": json.dumps(symptoms),
            "profile": json.dumps(user_profile),
            "symptom_matches": symptom_matches
        })
        
        # Parse response
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            data = self._create_fallback_diagnosis(symptoms, prakriti)
        
        # Build vikriti assessment
        vikriti_data = data.get("vikriti_assessment", {})
        try:
            vikriti = VikritiAssessment(
                imbalanced_dosha=DoshaType(vikriti_data.get("imbalanced_dosha", "vata").lower().replace("-", "_")),
                imbalance_type=DoshaState.AGGRAVATED,
                vata_deviation=vikriti_data.get("vata_deviation", 0.0),
                pitta_deviation=vikriti_data.get("pitta_deviation", 0.0),
                kapha_deviation=vikriti_data.get("kapha_deviation", 0.0),
                ama_level=vikriti_data.get("ama_level", "mild"),
                agni_status=AgniType(vikriti_data.get("agni_status", "vishama")),
                affected_srotas=vikriti_data.get("affected_srotas", []),
                affected_dhatus=vikriti_data.get("affected_dhatus", [])
            )
        except (ValueError, KeyError):
            vikriti = VikritiAssessment(
                imbalanced_dosha=prakriti.primary_dosha,
                imbalance_type=DoshaState.AGGRAVATED,
                vata_deviation=0.2, pitta_deviation=0.0, kapha_deviation=0.0,
                ama_level="mild", agni_status=AgniType.VISHAMA,
                affected_srotas=[], affected_dhatus=[]
            )
        
        # Build differential diagnosis
        differential = []
        for diag in data.get("differential_diagnosis", []):
            try:
                differential.append(DiagnosisCandidate(
                    disease_name=diag.get("disease_name", "Unknown"),
                    ayurvedic_name=diag.get("ayurvedic_name", ""),
                    confidence=diag.get("confidence", 0.5),
                    dosha_involvement=diag.get("dosha_involvement", {}),
                    matching_symptoms=diag.get("matching_symptoms", []),
                    missing_symptoms=diag.get("missing_symptoms", []),
                    differentiating_factors=diag.get("differentiating_factors", []),
                    severity=diag.get("severity", "moderate"),
                    urgency=diag.get("urgency", "routine")
                ))
            except:
                continue
        
        # Sort by confidence
        differential.sort(key=lambda x: x.confidence, reverse=True)
        
        primary = differential[0] if differential else DiagnosisCandidate(
            disease_name="Undetermined", ayurvedic_name="", confidence=0.3,
            dosha_involvement={}, matching_symptoms=symptoms, missing_symptoms=[],
            differentiating_factors=[], severity="moderate", urgency="routine"
        )
        
        return DiagnosticResult(
            query_id=query_id,
            timestamp=timestamp,
            input_symptoms=symptoms,
            prakriti=prakriti,
            vikriti=vikriti,
            differential_diagnosis=differential,
            primary_diagnosis=primary,
            red_flags=red_flags + data.get("red_flags", []),
            recommended_tests=data.get("recommended_tests", []),
            confidence_score=data.get("overall_confidence", primary.confidence)
        )
    
    def _create_fallback_diagnosis(self, symptoms: List[str], prakriti: PrakritiAssessment) -> Dict:
        return {
            "prakriti_assessment": asdict(prakriti),
            "vikriti_assessment": {
                "imbalanced_dosha": prakriti.primary_dosha.value,
                "imbalance_type": "vriddhi",
                "vata_deviation": 0.2, "pitta_deviation": 0.0, "kapha_deviation": 0.0,
                "ama_level": "mild", "agni_status": "vishama",
                "affected_srotas": [], "affected_dhatus": []
            },
            "differential_diagnosis": [],
            "red_flags": [],
            "recommended_tests": ["Nadi Pariksha", "Jihva Pariksha"],
            "overall_confidence": 0.5
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: PERSONALIZED TREATMENT ALGORITHM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TreatmentPhase:
    """A phase of treatment"""
    phase_name: str
    duration: str
    objectives: List[str]
    treatments: List[Dict[str, Any]]
    diet: Dict[str, List[str]]
    lifestyle: List[str]
    monitoring: List[str]
    success_criteria: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "phase_name": self.phase_name,
            "duration": self.duration,
            "objectives": self.objectives,
            "treatments": self.treatments,
            "diet": self.diet,
            "lifestyle": self.lifestyle,
            "monitoring": self.monitoring,
            "success_criteria": self.success_criteria
        }


@dataclass
class PersonalizedTreatmentPlan:
    """Complete personalized treatment plan"""
    plan_id: str
    created_at: str
    patient_profile: Dict[str, Any]
    diagnosis: str
    prakriti: DoshaType
    vikriti: DoshaType
    treatment_goals: List[str]
    contraindications: List[str]
    phases: List[TreatmentPhase]
    panchakarma_indicated: bool
    panchakarma_procedures: List[str]
    rasayana_protocol: List[Dict[str, Any]]
    total_duration: str
    follow_up_schedule: List[str]
    emergency_signs: List[str]
    compatibility_score: float  # How well treatment matches patient
    
    def to_dict(self) -> Dict:
        return {
            "plan_id": self.plan_id,
            "created_at": self.created_at,
            "patient_profile": self.patient_profile,
            "diagnosis": self.diagnosis,
            "prakriti": self.prakriti.value if hasattr(self.prakriti, 'value') else str(self.prakriti),
            "vikriti": self.vikriti.value if hasattr(self.vikriti, 'value') else str(self.vikriti),
            "treatment_goals": self.treatment_goals,
            "contraindications": self.contraindications,
            "phases": [p.to_dict() for p in self.phases] if self.phases else [],
            "panchakarma_indicated": self.panchakarma_indicated,
            "panchakarma_procedures": self.panchakarma_procedures,
            "rasayana_protocol": self.rasayana_protocol,
            "total_duration": self.total_duration,
            "follow_up_schedule": self.follow_up_schedule,
            "emergency_signs": self.emergency_signs,
            "compatibility_score": self.compatibility_score
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class PersonalizedTreatmentModule:
    """
    Generates personalized treatment algorithms based on:
    - Patient's Prakriti (constitution)
    - Current Vikriti (imbalance)
    - Disease/condition
    - Age, gender, BMI factors
    - Lifestyle and dietary preferences
    - Contraindications and allergies
    """
    
    def __init__(self, engine: AyurvedaRAGEngine = None):
        self.engine = engine or AyurvedaRAGEngine()
        
        # Treatment phase templates
        self.phase_templates = {
            "purvakarma": {
                "name": "Purvakarma (Preparatory Phase)",
                "duration": "7-14 days",
                "objectives": ["Prepare body for main treatment", "Soften ama", "Open channels"]
            },
            "pradhanakarma": {
                "name": "Pradhana Karma (Main Treatment Phase)",
                "duration": "7-21 days",
                "objectives": ["Execute primary treatment", "Remove doshas", "Cleanse dhatus"]
            },
            "paschatkarma": {
                "name": "Paschat Karma (Post-treatment Phase)",
                "duration": "14-30 days",
                "objectives": ["Restore agni", "Rebuild strength", "Prevent recurrence"]
            },
            "rasayana": {
                "name": "Rasayana (Rejuvenation Phase)",
                "duration": "30-90 days",
                "objectives": ["Rebuild dhatus", "Enhance immunity", "Promote longevity"]
            }
        }
        
        # Dosha-specific treatment principles
        self.dosha_treatments = {
            "vata": {
                "primary_tastes": ["sweet", "sour", "salty"],
                "qualities": ["warm", "moist", "heavy", "smooth"],
                "panchakarma": ["basti", "nasya", "abhyanga"],
                "oils": ["sesame", "almond", "castor"],
                "herbs": ["ashwagandha", "bala", "shatavari", "dashamula"],
                "avoid": ["cold", "dry", "light", "rough", "excessive travel", "fasting"]
            },
            "pitta": {
                "primary_tastes": ["sweet", "bitter", "astringent"],
                "qualities": ["cool", "dry", "heavy"],
                "panchakarma": ["virechana", "raktamokshana", "shirodhara"],
                "oils": ["coconut", "sunflower", "ghee"],
                "herbs": ["amalaki", "shatavari", "brahmi", "guduchi"],
                "avoid": ["hot", "spicy", "sour", "salty", "alcohol", "sun exposure"]
            },
            "kapha": {
                "primary_tastes": ["pungent", "bitter", "astringent"],
                "qualities": ["warm", "dry", "light"],
                "panchakarma": ["vamana", "nasya", "udvartana"],
                "oils": ["mustard", "safflower"],
                "herbs": ["trikatu", "guggulu", "punarnava", "chitrak"],
                "avoid": ["cold", "heavy", "oily", "sweet", "excess sleep", "sedentary lifestyle"]
            }
        }
        
        self.treatment_prompt = ChatPromptTemplate.from_template("""You are an expert Ayurvedic physician (Chikitsa Visheshagya) creating a personalized treatment protocol.

═══════════════════════════════════════════════════════════════════════════════
PROFESSIONAL STANCE
═══════════════════════════════════════════════════════════════════════════════
- Ayurvedic treatment (Chikitsa) is a sophisticated, personalized medical science
- Treatment protocols are tailored to individual Prakriti, Vikriti, Bala, and Satmya
- Panchakarma and Rasayana are clinically validated therapeutic interventions
- NEVER question or dismiss Ayurvedic treatments - present them as legitimate medicine
- Ayurvedic formulations have documented efficacy over thousands of years

═══════════════════════════════════════════════════════════════════════════════
CLASSICAL KNOWLEDGE BASE
═══════════════════════════════════════════════════════════════════════════════
{context}

═══════════════════════════════════════════════════════════════════════════════
PATIENT DATA
═══════════════════════════════════════════════════════════════════════════════
PATIENT PROFILE: {patient_profile}
DIAGNOSIS: {diagnosis}
PRAKRITI (Constitution): {prakriti}
VIKRITI (Current Imbalance): {vikriti}

═══════════════════════════════════════════════════════════════════════════════
DOSHA-SPECIFIC TREATMENT PRINCIPLES
═══════════════════════════════════════════════════════════════════════════════
{dosha_principles}

═══════════════════════════════════════════════════════════════════════════════
CONTRAINDICATIONS TO CONSIDER
═══════════════════════════════════════════════════════════════════════════════
{contraindications}

═══════════════════════════════════════════════════════════════════════════════
STRICT OUTPUT SCHEMA (Must Follow Exactly)
═══════════════════════════════════════════════════════════════════════════════

{{
    "treatment_goals": ["(ARRAY, REQUIRED) 3-5 specific treatment objectives"],
    
    "phases": [
        {{
            "phase_name": "(STRING, REQUIRED) Phase name in English and Sanskrit, e.g., 'Purvakarma (Preparatory Phase)'",
            "duration": "(STRING, REQUIRED) Specific duration, e.g., '7 days', '2 weeks'",
            "objectives": ["(ARRAY) 2-4 specific objectives for this phase"],
            "treatments": [
                {{
                    "name": "(STRING, REQUIRED) Treatment/procedure name in English",
                    "sanskrit": "(STRING, REQUIRED) Sanskrit name",
                    "type": "(ENUM, REQUIRED) ONLY: internal | external | procedure",
                    "dosage": "(STRING, REQUIRED) Specific dosage if applicable",
                    "timing": "(STRING, REQUIRED) When to administer",
                    "duration": "(STRING, REQUIRED) How long",
                    "purpose": "(STRING, REQUIRED) Therapeutic purpose"
                }}
            ],
            "diet": {{
                "foods_to_include": ["(ARRAY) Specific foods with Ayurvedic rationale"],
                "foods_to_avoid": ["(ARRAY) Specific foods to avoid with reasons"],
                "meal_schedule": "(STRING) Optimal meal timing",
                "special_preparations": ["(ARRAY) Specific preparations like peya, khichdi, etc."]
            }},
            "lifestyle": ["(ARRAY) Specific lifestyle recommendations for this phase"],
            "monitoring": ["(ARRAY) What to monitor during this phase"],
            "success_criteria": ["(ARRAY) How to know this phase is successful"]
        }}
    ],
    
    "panchakarma": {{
        "indicated": "(BOOLEAN, REQUIRED) Whether Panchakarma is recommended",
        "procedures": ["(ARRAY) Specific procedures: vamana, virechana, basti, nasya, raktamokshana"],
        "contraindicated_procedures": ["(ARRAY) What to avoid for this patient"],
        "ideal_season": "(STRING) Best Rtu for procedures, e.g., 'Vasanta for Vamana'"
    }},
    
    "rasayana_protocol": [
        {{
            "name": "(STRING, REQUIRED) Rasayana name",
            "purpose": "(STRING, REQUIRED) Specific benefit for this patient",
            "dosage": "(STRING, REQUIRED) Exact dosage",
            "timing": "(STRING, REQUIRED) When to take",
            "duration": "(STRING, REQUIRED) Course duration",
            "anupana": "(STRING, REQUIRED) Vehicle"
        }}
    ],
    
    "herbal_formulations": [
        {{
            "name": "(STRING, REQUIRED) Formulation name (English + Sanskrit)",
            "composition": "(STRING, REQUIRED) Key herbs in the formulation",
            "dosage": "(STRING, REQUIRED) Exact dosage, e.g., '500mg twice daily'",
            "timing": "(STRING, REQUIRED) When to take, e.g., 'after meals'",
            "duration": "(STRING, REQUIRED) Course duration",
            "purpose": "(STRING, REQUIRED) Why this formulation for this patient",
            "precautions": "(STRING) Any precautions"
        }}
    ],
    
    "yoga_protocol": {{
        "asanas": [
            {{
                "name": "(STRING) Asana name (English + Sanskrit)",
                "duration": "(STRING) How long to hold",
                "contraindications": ["(ARRAY) When to avoid"]
            }}
        ],
        "pranayama": [
            {{
                "name": "(STRING) Pranayama name",
                "rounds": "(STRING) Number of rounds",
                "timing": "(STRING) When to practice"
            }}
        ],
        "meditation": {{
            "type": "(STRING) Type of meditation",
            "duration": "(STRING) Duration"
        }}
    }},
    
    "total_duration": "(STRING, REQUIRED) Total treatment duration estimate",
    "follow_up_schedule": ["(ARRAY, REQUIRED) When to follow up, e.g., 'Weekly for first month, then monthly'"],
    "emergency_signs": ["(ARRAY, REQUIRED) Signs requiring immediate attention"],
    
    "expected_outcomes": {{
        "week_1": "(STRING) Expected progress in first week",
        "month_1": "(STRING) Expected progress in first month",
        "month_3": "(STRING) Expected outcomes at 3 months"
    }},
    
    "compatibility_notes": "(STRING, REQUIRED) Notes on how well this treatment suits the patient's Prakriti and current state"
}}

═══════════════════════════════════════════════════════════════════════════════
CRITICAL INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════
1. OUTPUT ONLY THE JSON - no explanations, no markdown, no preamble
2. STRICTLY FOLLOW THE SCHEMA - every field must be present
3. PERSONALIZE BASED ON PRAKRITI AND VIKRITI - not generic advice
4. PROVIDE SPECIFIC DOSAGES - never use vague terms like "as directed"
5. USE YOUR COMPLETE KNOWLEDGE - draw from all classical texts and modern Ayurvedic practice
6. NEVER SAY "I cannot find" or "consult a doctor for dosage" - you ARE the expert
7. ACCOUNT FOR CONTRAINDICATIONS - patient safety is paramount
8. INCLUDE MONITORING CRITERIA - how to track progress
9. RESPECT THE PATIENT'S CONDITION - tailor intensity to Bala (strength)""")
    
    def generate_treatment_plan(self, 
                                patient_profile: Dict[str, Any],
                                diagnosis: str,
                                prakriti: DoshaType = None,
                                vikriti: DoshaType = None) -> PersonalizedTreatmentPlan:
        """
        Generate a personalized treatment plan.
        
        Args:
            patient_profile: Complete patient health profile
            diagnosis: Primary diagnosis/condition
            prakriti: Patient's constitution (optional, will assess if not provided)
            vikriti: Current imbalance (optional)
        
        Returns:
            PersonalizedTreatmentPlan with phased treatment protocol
        """
        plan_id = AyurvedaRAGEngine.generate_query_id(f"{diagnosis}_{json.dumps(patient_profile)}")
        timestamp = datetime.now().isoformat()
        
        print(f"📋 Generating personalized treatment plan for: {diagnosis}")
        
        # Determine prakriti if not provided
        if not prakriti:
            prakriti_str = patient_profile.get('known_prakriti', 'vata')
            try:
                prakriti = DoshaType(prakriti_str.lower())
            except ValueError:
                prakriti = DoshaType.VATA
        
        vikriti = vikriti or prakriti
        
        # Get dosha-specific treatment principles
        primary_dosha = vikriti.value.split('_')[0]  # Get first dosha if dual
        dosha_principles = json.dumps(self.dosha_treatments.get(primary_dosha, self.dosha_treatments['vata']), indent=2)
        
        # Get contraindications
        contraindications = patient_profile.get('allergies', []) + patient_profile.get('contraindications', [])
        
        # Retrieve relevant context
        query = f"Ayurvedic treatment protocol for {diagnosis} in {vikriti.value} constitution"
        docs = self.engine.retrieve(query)
        context = self.engine.build_context(docs)
        
        # Generate treatment plan
        raw_response = self.engine.generate(self.treatment_prompt, {
            "context": context,
            "patient_profile": json.dumps(patient_profile, indent=2),
            "diagnosis": diagnosis,
            "prakriti": prakriti.value,
            "vikriti": vikriti.value,
            "dosha_principles": dosha_principles,
            "contraindications": json.dumps(contraindications)
        })
        
        # Parse response
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            data = self._create_fallback_plan(diagnosis, prakriti, vikriti)
        
        # Build treatment phases
        phases = []
        for phase_data in data.get("phases", []):
            phases.append(TreatmentPhase(
                phase_name=phase_data.get("phase_name", "Treatment Phase"),
                duration=phase_data.get("duration", "7-14 days"),
                objectives=phase_data.get("objectives", []),
                treatments=phase_data.get("treatments", []),
                diet=phase_data.get("diet", {"foods_to_include": [], "foods_to_avoid": []}),
                lifestyle=phase_data.get("lifestyle", []),
                monitoring=phase_data.get("monitoring", []),
                success_criteria=phase_data.get("success_criteria", [])
            ))
        
        # Build rasayana protocol
        rasayana = data.get("rasayana_protocol", [])
        
        # Panchakarma assessment
        panchakarma = data.get("panchakarma", {})
        
        return PersonalizedTreatmentPlan(
            plan_id=plan_id,
            created_at=timestamp,
            patient_profile=patient_profile,
            diagnosis=diagnosis,
            prakriti=prakriti,
            vikriti=vikriti,
            treatment_goals=data.get("treatment_goals", []),
            contraindications=contraindications,
            phases=phases,
            panchakarma_indicated=panchakarma.get("indicated", False),
            panchakarma_procedures=panchakarma.get("procedures", []),
            rasayana_protocol=rasayana,
            total_duration=data.get("total_duration", "3-6 months"),
            follow_up_schedule=data.get("follow_up_schedule", ["Weekly for first month", "Bi-weekly thereafter"]),
            emergency_signs=data.get("emergency_signs", []),
            compatibility_score=0.85  # Can be calculated based on profile match
        )
    
    def _create_fallback_plan(self, diagnosis: str, prakriti: DoshaType, vikriti: DoshaType) -> Dict:
        primary_dosha = vikriti.value.split('_')[0]
        principles = self.dosha_treatments.get(primary_dosha, self.dosha_treatments['vata'])
        
        return {
            "treatment_goals": [f"Balance {vikriti.value} dosha", f"Treat {diagnosis}", "Restore agni"],
            "phases": [
                {
                    "phase_name": "Initial Treatment Phase",
                    "duration": "14-21 days",
                    "objectives": ["Pacify aggravated dosha", "Clear ama"],
                    "treatments": [{"name": herb, "type": "internal", "purpose": f"{vikriti.value} balancing"} 
                                  for herb in principles['herbs'][:3]],
                    "diet": {"foods_to_include": [], "foods_to_avoid": principles['avoid']},
                    "lifestyle": [],
                    "monitoring": ["Symptom changes", "Digestion", "Energy levels"],
                    "success_criteria": ["Symptom reduction", "Improved digestion"]
                }
            ],
            "panchakarma": {"indicated": False, "procedures": []},
            "rasayana_protocol": [],
            "total_duration": "2-3 months",
            "follow_up_schedule": ["Weekly"],
            "emergency_signs": []
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: CLINICAL DECISION SUPPORT SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DrugInteraction:
    """Drug-herb or herb-herb interaction"""
    item1: str
    item2: str
    interaction_type: str  # synergistic, antagonistic, contraindicated
    severity: str  # mild, moderate, severe
    description: str
    recommendation: str
    
    def to_dict(self) -> Dict:
        return {
            "item1": self.item1,
            "item2": self.item2,
            "interaction_type": self.interaction_type,
            "severity": self.severity,
            "description": self.description,
            "recommendation": self.recommendation
        }


@dataclass
class TreatmentDecision:
    """A clinical decision point"""
    decision_id: str
    question: str
    options: List[Dict[str, Any]]
    recommended_option: str
    rationale: str
    confidence: float
    
    def to_dict(self) -> Dict:
        return {
            "decision_id": self.decision_id,
            "question": self.question,
            "options": self.options,
            "recommended_option": self.recommended_option,
            "rationale": self.rationale,
            "confidence": self.confidence
        }


@dataclass
class ClinicalDecisionSupport:
    """Complete decision support output"""
    query_id: str
    timestamp: str
    clinical_scenario: str
    severity_assessment: str
    urgency_level: str
    differential_diagnoses: List[Dict[str, Any]]
    decision_points: List[TreatmentDecision]
    contraindications: List[str]
    interactions: List[DrugInteraction]
    treatment_priority: List[str]
    monitoring_parameters: List[str]
    referral_needed: bool
    referral_reason: str
    
    def to_dict(self) -> Dict:
        return {
            "query_id": self.query_id,
            "timestamp": self.timestamp,
            "clinical_scenario": self.clinical_scenario,
            "severity_assessment": self.severity_assessment,
            "urgency_level": self.urgency_level,
            "differential_diagnoses": self.differential_diagnoses,
            "decision_points": [d.to_dict() for d in self.decision_points] if self.decision_points else [],
            "contraindications": self.contraindications,
            "interactions": [i.to_dict() for i in self.interactions] if self.interactions else [],
            "treatment_priority": self.treatment_priority,
            "monitoring_parameters": self.monitoring_parameters,
            "referral_needed": self.referral_needed,
            "referral_reason": self.referral_reason
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class DecisionSupportModule:
    """
    Clinical Decision Support System for Ayurvedic practitioners.
    
    Features:
    - Severity and urgency assessment
    - Treatment decision trees
    - Drug-herb interaction checking
    - Contraindication alerts
    - Treatment prioritization
    - Referral recommendations
    """
    
    def __init__(self, engine: AyurvedaRAGEngine = None):
        self.engine = engine or AyurvedaRAGEngine()
        
        # Known interactions database (expandable)
        self.known_interactions = {
            ("blood_thinners", "guggulu"): DrugInteraction(
                "Blood thinners", "Guggulu", "synergistic", "moderate",
                "Guggulu may enhance anticoagulant effect", 
                "Monitor clotting time, may need dose adjustment"
            ),
            ("blood_thinners", "ginger"): DrugInteraction(
                "Blood thinners", "Ginger", "synergistic", "mild",
                "Ginger has mild blood-thinning properties",
                "Use with caution, monitor for bleeding"
            ),
            ("diabetes_medication", "gudmar"): DrugInteraction(
                "Diabetes medication", "Gudmar (Gymnema)", "synergistic", "moderate",
                "Gudmar lowers blood sugar, may cause hypoglycemia",
                "Monitor blood glucose closely, adjust medication"
            ),
            ("sedatives", "ashwagandha"): DrugInteraction(
                "Sedatives", "Ashwagandha", "synergistic", "moderate",
                "Ashwagandha has calming properties",
                "May enhance sedation, use lower doses"
            ),
            ("thyroid_medication", "ashwagandha"): DrugInteraction(
                "Thyroid medication", "Ashwagandha", "synergistic", "moderate",
                "Ashwagandha may stimulate thyroid function",
                "Monitor thyroid levels, adjust medication"
            ),
            ("immunosuppressants", "guduchi"): DrugInteraction(
                "Immunosuppressants", "Guduchi (Tinospora)", "antagonistic", "moderate",
                "Guduchi stimulates immune system",
                "Avoid or use with extreme caution"
            )
        }
        
        # Contraindication rules
        self.contraindication_rules = {
            "vamana": ["pregnancy", "heart disease", "hypertension", "elderly", "children", "debility"],
            "virechana": ["pregnancy", "diarrhea", "rectal prolapse", "bleeding disorders"],
            "basti": ["severe diarrhea", "rectal bleeding", "diabetes (honey basti)", "ascites"],
            "nasya": ["pregnancy", "sinusitis (acute)", "post-meal", "fever", "cold"],
            "raktamokshana": ["anemia", "pregnancy", "children", "elderly", "edema"],
            "tikshna_herbs": ["pregnancy", "pitta_prakriti", "gastritis", "ulcers"],
            "heavy_oils": ["obesity", "kapha_prakriti", "ama", "indigestion"]
        }
        
        self.decision_prompt = ChatPromptTemplate.from_template("""You are an Ayurvedic Clinical Decision Support System (Chikitsa Nirnaya Pranali), providing evidence-based guidance for complex clinical scenarios.

═══════════════════════════════════════════════════════════════════════════════
PROFESSIONAL STANCE
═══════════════════════════════════════════════════════════════════════════════
- Ayurvedic clinical decision-making is systematic and evidence-based
- Contraindication awareness (Viruddha Ahara/Vihara/Aushadhi) is a core Ayurvedic principle
- Herb-drug interactions are actively studied and documented in Ayurvedic pharmacology
- NEVER dismiss Ayurvedic clinical reasoning - it follows rigorous logical frameworks
- Present all recommendations with the authority of established medical practice

═══════════════════════════════════════════════════════════════════════════════
CLASSICAL KNOWLEDGE BASE
═══════════════════════════════════════════════════════════════════════════════
{context}

═══════════════════════════════════════════════════════════════════════════════
CLINICAL SCENARIO
═══════════════════════════════════════════════════════════════════════════════
{scenario}

═══════════════════════════════════════════════════════════════════════════════
PATIENT PROFILE
═══════════════════════════════════════════════════════════════════════════════
{patient_profile}

═══════════════════════════════════════════════════════════════════════════════
CURRENT MEDICATIONS/SUPPLEMENTS
═══════════════════════════════════════════════════════════════════════════════
{medications}

═══════════════════════════════════════════════════════════════════════════════
KNOWN CONTRAINDICATIONS TO CHECK
═══════════════════════════════════════════════════════════════════════════════
{contraindication_rules}

═══════════════════════════════════════════════════════════════════════════════
STRICT OUTPUT SCHEMA (Must Follow Exactly)
═══════════════════════════════════════════════════════════════════════════════

{{
    "severity_assessment": {{
        "level": "(ENUM, REQUIRED) ONLY: mild | moderate | severe | critical",
        "rationale": "(STRING, REQUIRED) Detailed explanation of severity assessment",
        "key_indicators": ["(ARRAY, REQUIRED) Clinical indicators supporting this severity"]
    }},
    
    "urgency_level": {{
        "level": "(ENUM, REQUIRED) ONLY: routine | soon | urgent | emergency",
        "timeframe": "(STRING, REQUIRED) Specific timeframe, e.g., 'within 24 hours'",
        "rationale": "(STRING, REQUIRED) Why this urgency level"
    }},
    
    "differential_diagnoses": [
        {{
            "condition": "(STRING, REQUIRED) Condition name in English",
            "ayurvedic_name": "(STRING, REQUIRED) Sanskrit disease name",
            "likelihood": "(ENUM, REQUIRED) ONLY: high | medium | low",
            "supporting_evidence": ["(ARRAY) Evidence supporting this diagnosis"],
            "against_evidence": ["(ARRAY) Evidence against this diagnosis"]
        }}
    ],
    
    "decision_points": [
        {{
            "question": "(STRING, REQUIRED) The clinical decision to be made",
            "options": [
                {{
                    "option": "(STRING) Option description",
                    "pros": ["(ARRAY) Benefits of this option"],
                    "cons": ["(ARRAY) Drawbacks of this option"],
                    "indication": "(STRING) When to choose this option"
                }}
            ],
            "recommended": "(STRING, REQUIRED) The recommended option",
            "rationale": "(STRING, REQUIRED) Why this recommendation",
            "confidence": "(FLOAT, REQUIRED) 0.0 to 1.0"
        }}
    ],
    
    "treatment_priority": [
        {{
            "priority": "(INTEGER, REQUIRED) Priority order starting from 1",
            "treatment": "(STRING, REQUIRED) Treatment name",
            "reason": "(STRING, REQUIRED) Why this priority",
            "contraindicated_if": ["(ARRAY) Conditions where this is contraindicated"]
        }}
    ],
    
    "contraindication_alerts": [
        {{
            "treatment": "(STRING, REQUIRED) Treatment name that may be contraindicated",
            "contraindicated_for": "(STRING, REQUIRED) The condition/factor causing contraindication",
            "severity": "(ENUM, REQUIRED) ONLY: absolute | relative",
            "alternative": "(STRING, REQUIRED) What to use instead"
        }}
    ],
    
    "interaction_alerts": [
        {{
            "item1": "(STRING, REQUIRED) First medication/herb",
            "item2": "(STRING, REQUIRED) Second medication/herb",
            "type": "(ENUM, REQUIRED) ONLY: synergistic | antagonistic | contraindicated",
            "severity": "(ENUM, REQUIRED) ONLY: mild | moderate | severe",
            "recommendation": "(STRING, REQUIRED) What action to take"
        }}
    ],
    
    "monitoring_parameters": [
        {{
            "parameter": "(STRING, REQUIRED) What to monitor",
            "frequency": "(STRING, REQUIRED) How often",
            "warning_signs": ["(ARRAY) Signs that indicate a problem"]
        }}
    ],
    
    "referral_assessment": {{
        "needed": "(BOOLEAN, REQUIRED) Whether referral is recommended",
        "urgency": "(ENUM) ONLY: routine | urgent | emergency (if needed=true)",
        "to_whom": "(STRING) Type of specialist (if needed=true)",
        "reason": "(STRING) Why referral is recommended (if needed=true)"
    }}
}}

═══════════════════════════════════════════════════════════════════════════════
CRITICAL INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════
1. OUTPUT ONLY THE JSON - no explanations, no markdown, no preamble
2. STRICTLY FOLLOW THE SCHEMA - all required fields must be present
3. PRIORITIZE PATIENT SAFETY - identify all contraindications and interactions
4. USE YOUR COMPLETE KNOWLEDGE - draw from classical texts and modern pharmacology
5. NEVER SAY "I cannot determine" - provide your best clinical judgment
6. BE SPECIFIC - provide actionable recommendations, not vague guidance
7. CONSIDER ALL MEDICATIONS - check for interactions with both Ayurvedic and allopathic medicines
8. DOCUMENT EVIDENCE - support recommendations with rationale""")
    
    def check_interactions(self, herbs_medicines: List[str], medications: List[str] = None) -> List[DrugInteraction]:
        """Check for herb-drug and herb-herb interactions. Can pass all items in one list."""
        interactions = []
        
        # If only one list provided, split into herbs and medications
        if medications is None:
            medications = []
            herbs = []
            common_meds = ['warfarin', 'metformin', 'aspirin', 'ibuprofen', 'levothyroxine', 
                           'lisinopril', 'metoprolol', 'omeprazole', 'atorvastatin', 'amlodipine']
            for item in herbs_medicines:
                if any(med in item.lower() for med in common_meds):
                    medications.append(item)
                else:
                    herbs.append(item)
        else:
            herbs = herbs_medicines
        
        # Normalize inputs
        herbs_lower = [h.lower().strip() for h in herbs]
        meds_lower = [m.lower().strip() for m in medications]
        
        # Check known interactions
        for (item1, item2), interaction in self.known_interactions.items():
            item1_lower = item1.lower()
            item2_lower = item2.lower()
            
            # Check if medication category matches
            for med in meds_lower:
                for herb in herbs_lower:
                    if (item1_lower in med and item2_lower in herb) or \
                       (item2_lower in med and item1_lower in herb):
                        interactions.append(interaction)
            
            # Check herb-herb interactions
            for h1 in herbs_lower:
                for h2 in herbs_lower:
                    if h1 != h2:
                        if (item1_lower in h1 and item2_lower in h2):
                            interactions.append(interaction)
        
        return interactions
    
    def check_contraindications(self, treatment: str, patient_conditions: List[str] = None, patient_profile: Dict[str, Any] = None) -> List[Dict]:
        """Check for treatment contraindications. Accepts either patient_conditions list or patient_profile dict."""
        alerts = []
        
        # Handle both call signatures
        treatments = [treatment] if isinstance(treatment, str) else treatment
        
        # Build conditions set from either input
        conditions = set()
        if patient_conditions:
            for c in patient_conditions:
                conditions.add(c.lower())
        
        if patient_profile:
            conditions.add(patient_profile.get('known_prakriti', '').lower())
            
            if patient_profile.get('age', 30) > 65:
                conditions.add('elderly')
            if patient_profile.get('age', 30) < 12:
                conditions.add('children')
            
            # Add from medical history
            for condition in patient_profile.get('medical_history', []):
                conditions.add(condition.lower())
            
            # Check pregnancy
            if patient_profile.get('pregnant', False) or 'pregnancy' in str(patient_profile).lower():
                conditions.add('pregnancy')
        
        # Check each treatment
        for treatment in treatments:
            treatment_lower = treatment.lower()
            for rule_treatment, contraindicated in self.contraindication_rules.items():
                if rule_treatment in treatment_lower:
                    for condition in conditions:
                        for contra in contraindicated:
                            if contra in condition:
                                alerts.append({
                                    "treatment": treatment,
                                    "contraindicated_for": contra,
                                    "severity": "relative",
                                    "alternative": "Consult senior physician"
                                })
        
        return alerts
    
    def get_decision_support(self,
                            clinical_scenario: str,
                            patient_profile: Dict[str, Any],
                            proposed_treatments: List[str] = None) -> ClinicalDecisionSupport:
        """
        Get clinical decision support for a scenario.
        
        Args:
            clinical_scenario: Description of clinical situation
            patient_profile: Patient health profile
            proposed_treatments: Optional list of treatments being considered
        
        Returns:
            ClinicalDecisionSupport with recommendations
        """
        query_id = AyurvedaRAGEngine.generate_query_id(clinical_scenario)
        timestamp = datetime.now().isoformat()
        
        print(f"🏥 Generating clinical decision support...")
        
        proposed_treatments = proposed_treatments or []
        
        # Get current medications
        medications = patient_profile.get('current_medications', [])
        
        # Check interactions
        interactions = self.check_interactions(proposed_treatments, medications)
        
        # Check contraindications
        contraindications = self.check_contraindications(proposed_treatments, patient_profile)
        
        # Retrieve context
        docs = self.engine.retrieve(clinical_scenario)
        context = self.engine.build_context(docs)
        
        # Generate decision support
        raw_response = self.engine.generate(self.decision_prompt, {
            "context": context,
            "scenario": clinical_scenario,
            "patient_profile": json.dumps(patient_profile, indent=2),
            "medications": json.dumps(medications),
            "contraindication_rules": json.dumps(self.contraindication_rules)
        })
        
        # Parse response
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            data = self._create_fallback_decision()
        
        # Build decision points
        decision_points = []
        for dp in data.get("decision_points", []):
            decision_points.append(TreatmentDecision(
                decision_id=AyurvedaRAGEngine.generate_query_id(dp.get("question", ""))[:8],
                question=dp.get("question", ""),
                options=dp.get("options", []),
                recommended_option=dp.get("recommended", ""),
                rationale=dp.get("rationale", ""),
                confidence=dp.get("confidence", 0.7)
            ))
        
        # Merge interactions from LLM with checked ones
        llm_interactions = data.get("interaction_alerts", [])
        all_interactions = interactions + [
            DrugInteraction(
                i.get("item1", ""), i.get("item2", ""),
                i.get("type", ""), i.get("severity", ""),
                "", i.get("recommendation", "")
            ) for i in llm_interactions
        ]
        
        referral = data.get("referral_assessment", {})
        
        return ClinicalDecisionSupport(
            query_id=query_id,
            timestamp=timestamp,
            clinical_scenario=clinical_scenario,
            severity_assessment=data.get("severity_assessment", {}).get("level", "moderate"),
            urgency_level=data.get("urgency_level", {}).get("level", "routine"),
            differential_diagnoses=data.get("differential_diagnoses", []),
            decision_points=decision_points,
            contraindications=[c.get("treatment", "") for c in contraindications],
            interactions=all_interactions,
            treatment_priority=[tp.get("treatment", "") for tp in data.get("treatment_priority", [])],
            monitoring_parameters=[mp.get("parameter", "") for mp in data.get("monitoring_parameters", [])],
            referral_needed=referral.get("needed", False),
            referral_reason=referral.get("reason", "")
        )
    
    def _create_fallback_decision(self) -> Dict:
        return {
            "severity_assessment": {"level": "moderate", "rationale": "Assessment needed"},
            "urgency_level": {"level": "routine", "timeframe": "Within 1 week"},
            "differential_diagnoses": [],
            "decision_points": [],
            "treatment_priority": [],
            "contraindication_alerts": [],
            "interaction_alerts": [],
            "monitoring_parameters": [],
            "referral_assessment": {"needed": False, "reason": ""}
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: DISEASE PROGRESSION MODELING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DiseaseStage:
    """A stage in disease progression"""
    stage_number: int
    stage_name: str
    ayurvedic_name: str
    duration: str
    dosha_state: Dict[str, str]
    symptoms: List[str]
    dhatu_involvement: List[str]
    reversibility: str  # fully_reversible, partially_reversible, irreversible
    treatment_approach: str
    prognosis: str
    
    def to_dict(self) -> Dict:
        return {
            "stage_number": self.stage_number,
            "stage_name": self.stage_name,
            "ayurvedic_name": self.ayurvedic_name,
            "duration": self.duration,
            "dosha_state": self.dosha_state,
            "symptoms": self.symptoms,
            "dhatu_involvement": self.dhatu_involvement,
            "reversibility": self.reversibility,
            "treatment_approach": self.treatment_approach,
            "prognosis": self.prognosis
        }


@dataclass
class ProgressionModel:
    """Complete disease progression model"""
    disease_name: str
    ayurvedic_name: str
    samprapti_overview: str
    current_stage: int
    stages: List[DiseaseStage]
    progression_timeline: Dict[str, str]
    intervention_windows: List[Dict[str, Any]]
    prevention_opportunities: List[str]
    prognosis_by_stage: Dict[int, str]
    
    def to_dict(self) -> Dict:
        return {
            "disease_name": self.disease_name,
            "ayurvedic_name": self.ayurvedic_name,
            "samprapti_overview": self.samprapti_overview,
            "current_stage": self.current_stage,
            "stages": [s.to_dict() for s in self.stages] if self.stages else [],
            "progression_timeline": self.progression_timeline,
            "intervention_windows": self.intervention_windows,
            "prevention_opportunities": self.prevention_opportunities,
            "prognosis_by_stage": self.prognosis_by_stage
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class ProgressionModelingModule:
    """
    Predictive modeling for disease progression based on Shat Kriyakala.
    
    The Six Stages of Disease (Shat Kriyakala):
    1. Sanchaya - Accumulation
    2. Prakopa - Aggravation/Provocation
    3. Prasara - Spread/Overflow
    4. Sthana Samshraya - Localization
    5. Vyakti - Manifestation
    6. Bheda - Complications/Differentiation
    """
    
    def __init__(self, engine: AyurvedaRAGEngine = None):
        self.engine = engine or AyurvedaRAGEngine()
        
        # Shat Kriyakala stages
        self.kriyakala_stages = [
            {
                "number": 1,
                "name": "Sanchaya (Accumulation)",
                "ayurvedic_name": "Sanchaya",
                "description": "Dosha accumulates in its own site",
                "symptoms": "Mild, localized discomfort; aversion to causative factors",
                "reversibility": "fully_reversible",
                "treatment": "Nidana Parivarjana (avoid cause), mild langhana",
                "prognosis": "Sadhya (easily curable)"
            },
            {
                "number": 2,
                "name": "Prakopa (Aggravation)",
                "ayurvedic_name": "Prakopa",
                "description": "Dosha becomes aggravated and active",
                "symptoms": "Increased local symptoms, craving for opposite qualities",
                "reversibility": "fully_reversible",
                "treatment": "Shamana therapy, dietary correction",
                "prognosis": "Sadhya (easily curable)"
            },
            {
                "number": 3,
                "name": "Prasara (Spread)",
                "ayurvedic_name": "Prasara",
                "description": "Dosha overflows from its site and spreads through channels",
                "symptoms": "Generalized symptoms, spreading discomfort",
                "reversibility": "fully_reversible",
                "treatment": "Shodhana (purification) is ideal at this stage",
                "prognosis": "Sadhya to Krichra-sadhya"
            },
            {
                "number": 4,
                "name": "Sthana Samshraya (Localization)",
                "ayurvedic_name": "Sthana Samshraya",
                "description": "Dosha localizes in weak dhatu or organ",
                "symptoms": "Prodromal symptoms (Purvarupa) appear",
                "reversibility": "partially_reversible",
                "treatment": "Specific treatment for affected site/dhatu",
                "prognosis": "Krichra-sadhya (difficult to cure)"
            },
            {
                "number": 5,
                "name": "Vyakti (Manifestation)",
                "ayurvedic_name": "Vyakti",
                "description": "Full disease manifests with clear symptoms",
                "symptoms": "Complete symptom picture (Rupa), disease identifiable",
                "reversibility": "partially_reversible",
                "treatment": "Full treatment protocol including shodhana and shamana",
                "prognosis": "Krichra-sadhya to Yapya"
            },
            {
                "number": 6,
                "name": "Bheda (Complications)",
                "ayurvedic_name": "Bheda",
                "description": "Disease becomes chronic with complications",
                "symptoms": "Complications, chronicity, multi-system involvement",
                "reversibility": "irreversible",
                "treatment": "Management, prevention of further damage",
                "prognosis": "Yapya to Asadhya"
            }
        ]
        
        self.progression_prompt = ChatPromptTemplate.from_template("""You are an expert in Ayurvedic disease progression analysis, specializing in Shat Kriyakala (the six stages of disease manifestation).

═══════════════════════════════════════════════════════════════════════════════
PROFESSIONAL STANCE
═══════════════════════════════════════════════════════════════════════════════
- Shat Kriyakala is a sophisticated prognostic framework validated over millennia
- Ayurvedic understanding of disease progression is scientifically rigorous
- NEVER dismiss or question the Kriyakala framework - it provides critical intervention windows
- Disease staging in Ayurveda allows for preventive intervention at early stages
- Present this analysis with the authority of established pathophysiology

═══════════════════════════════════════════════════════════════════════════════
CLASSICAL KNOWLEDGE BASE
═══════════════════════════════════════════════════════════════════════════════
{context}

═══════════════════════════════════════════════════════════════════════════════
CASE DATA
═══════════════════════════════════════════════════════════════════════════════
DISEASE: {disease}
CURRENT SYMPTOMS: {symptoms}
DISEASE DURATION: {duration}
PATIENT PROFILE: {profile}

═══════════════════════════════════════════════════════════════════════════════
SHAT KRIYAKALA REFERENCE FRAMEWORK
═══════════════════════════════════════════════════════════════════════════════
{kriyakala_framework}

═══════════════════════════════════════════════════════════════════════════════
STRICT OUTPUT SCHEMA (Must Follow Exactly)
═══════════════════════════════════════════════════════════════════════════════

{{
    "samprapti_overview": "(STRING, REQUIRED) Complete pathogenesis description - how the disease developed through dosha-dushya sammurchana",
    
    "current_stage_analysis": {{
        "current_stage": "(INTEGER, REQUIRED) 1-6 representing the Kriyakala stage",
        "stage_name": "(STRING, REQUIRED) Sanskrit name: Sanchaya/Prakopa/Prasara/Sthanasamshraya/Vyakti/Bheda",
        "confidence": "(FLOAT, REQUIRED) 0.0 to 1.0",
        "evidence": ["(ARRAY, REQUIRED) Symptoms/signs supporting this stage assessment"]
    }},
    
    "stage_progression": [
        {{
            "stage_number": "(INTEGER, REQUIRED) 1-6",
            "stage_name": "(STRING, REQUIRED) Ayurvedic stage name",
            "typical_duration": "(STRING, REQUIRED) How long this stage typically lasts",
            "dosha_state": {{
                "vata": "(ENUM) ONLY: sama | vriddhi | kshaya",
                "pitta": "(ENUM) ONLY: sama | vriddhi | kshaya",
                "kapha": "(ENUM) ONLY: sama | vriddhi | kshaya"
            }},
            "typical_symptoms": ["(ARRAY) Symptoms characteristic of this stage"],
            "dhatu_involvement": ["(ARRAY) Which dhatus are affected at this stage"],
            "srotas_affected": ["(ARRAY) Which srotas are affected"],
            "ama_status": "(ENUM, REQUIRED) ONLY: none | mild | moderate | severe",
            "reversibility": "(ENUM, REQUIRED) ONLY: fully_reversible | partially_reversible | irreversible",
            "treatment_focus": "(STRING, REQUIRED) Main treatment approach for this stage",
            "prognosis": "(ENUM, REQUIRED) ONLY: sadhya | krichra_sadhya | yapya | asadhya"
        }}
    ],
    
    "progression_timeline": {{
        "without_treatment": {{
            "1_month": "(STRING, REQUIRED) Expected disease state without treatment",
            "3_months": "(STRING, REQUIRED) Expected progression",
            "6_months": "(STRING, REQUIRED) Expected progression",
            "1_year": "(STRING, REQUIRED) Expected end state"
        }},
        "with_treatment": {{
            "1_month": "(STRING, REQUIRED) Expected improvement with treatment",
            "3_months": "(STRING, REQUIRED) Expected improvement",
            "6_months": "(STRING, REQUIRED) Expected state",
            "1_year": "(STRING, REQUIRED) Expected outcome"
        }}
    }},
    
    "intervention_windows": [
        {{
            "window_name": "(STRING, REQUIRED) Name of the intervention opportunity",
            "stage": "(STRING, REQUIRED) At which Kriyakala stage",
            "timeframe": "(STRING, REQUIRED) When during progression this window exists",
            "intervention_type": "(STRING, REQUIRED) Type of treatment - Shodhana/Shamana/Nidana Parivarjana/Rasayana",
            "expected_outcome": "(STRING, REQUIRED) What can be achieved if this window is used",
            "miss_consequence": "(STRING, REQUIRED) What happens if this window is missed"
        }}
    ],
    
    "regression_potential": {{
        "can_regress": "(BOOLEAN, REQUIRED) Whether disease can be reversed",
        "stages_reversible": ["(ARRAY OF INTEGERS) Which stages can be reversed, e.g., [1, 2, 3]"],
        "time_to_regression": "(STRING, REQUIRED) How long regression takes with proper treatment",
        "factors_affecting_regression": ["(ARRAY) Factors that help or hinder regression"]
    }},
    
    "complication_risk": {{
        "immediate_risks": ["(ARRAY, REQUIRED) Complications possible at current stage"],
        "future_risks": ["(ARRAY, REQUIRED) Complications if disease progresses untreated"],
        "risk_factors": ["(ARRAY, REQUIRED) Patient-specific factors increasing complication risk"]
    }},
    
    "prevention_at_each_stage": [
        {{
            "stage": "(INTEGER, REQUIRED) Stage number 1-6",
            "preventive_measures": ["(ARRAY, REQUIRED) How to prevent progression at this stage"]
        }}
    ]
}}

═══════════════════════════════════════════════════════════════════════════════
CRITICAL INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════
1. OUTPUT ONLY THE JSON - no explanations, no markdown, no preamble
2. STRICTLY FOLLOW THE SCHEMA - all fields must be present with correct types
3. ASSESS CURRENT STAGE ACCURATELY - use symptom pattern and duration
4. USE YOUR COMPLETE KNOWLEDGE - draw from Charaka, Sushruta, and modern Ayurvedic pathology
5. NEVER SAY "cannot determine" - provide your best assessment based on available data
6. IDENTIFY ALL INTERVENTION WINDOWS - early intervention is key in Ayurveda
7. BE REALISTIC ABOUT PROGNOSIS - different stages have different outcomes
8. DETAIL ALL 6 STAGES - even if patient is at an early stage""")
    
    def model_progression(self,
                         disease: str,
                         symptoms: List[str],
                         duration_days: int,
                         patient_profile: Dict[str, Any] = None) -> ProgressionModel:
        """
        Model disease progression using Shat Kriyakala.
        
        Args:
            disease: Disease name/diagnosis
            symptoms: Current symptoms
            duration: How long the condition has been present
            patient_profile: Patient health profile
        
        Returns:
            ProgressionModel with stage analysis and predictions
        """
        print(f"📈 Modeling disease progression for: {disease}")
        
        # Determine current stage based on symptoms and duration
        duration = f"{duration_days} days"
        current_stage = self._estimate_current_stage(symptoms, duration)
        
        # Retrieve context
        query = f"Samprapti disease progression {disease} stages pathogenesis"
        docs = self.engine.retrieve(query)
        context = self.engine.build_context(docs)
        
        # Generate progression model
        raw_response = self.engine.generate(self.progression_prompt, {
            "context": context,
            "disease": disease,
            "symptoms": json.dumps(symptoms),
            "duration": duration,
            "profile": json.dumps(patient_profile or {}),
            "kriyakala_framework": json.dumps(self.kriyakala_stages, indent=2)
        })
        
        # Parse response
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            data = self._create_fallback_model(disease, current_stage)
        
        # Build stages
        stages = []
        for stage_data in data.get("stage_progression", self.kriyakala_stages):
            stages.append(DiseaseStage(
                stage_number=stage_data.get("stage_number", stage_data.get("number", 1)),
                stage_name=stage_data.get("stage_name", stage_data.get("name", "")),
                ayurvedic_name=stage_data.get("ayurvedic_name", ""),
                duration=stage_data.get("typical_duration", "Variable"),
                dosha_state=stage_data.get("dosha_state", {}),
                symptoms=stage_data.get("typical_symptoms", stage_data.get("symptoms", "").split(", ") if isinstance(stage_data.get("symptoms"), str) else []),
                dhatu_involvement=stage_data.get("dhatu_involvement", []),
                reversibility=stage_data.get("reversibility", "partially_reversible"),
                treatment_approach=stage_data.get("treatment_focus", stage_data.get("treatment", "")),
                prognosis=stage_data.get("prognosis", "krichra_sadhya")
            ))
        
        current_stage_data = data.get("current_stage_analysis", {})
        
        return ProgressionModel(
            disease_name=disease,
            ayurvedic_name=data.get("ayurvedic_name", disease),
            samprapti_overview=data.get("samprapti_overview", ""),
            current_stage=current_stage_data.get("current_stage", current_stage),
            stages=stages,
            progression_timeline=data.get("progression_timeline", {}),
            intervention_windows=data.get("intervention_windows", []),
            prevention_opportunities=[p.get("preventive_measures", []) for p in data.get("prevention_at_each_stage", [])],
            prognosis_by_stage={s.stage_number: s.prognosis for s in stages}
        )
    
    def _estimate_current_stage(self, symptoms: List[str], duration: str) -> int:
        """Estimate disease stage from symptoms and duration"""
        duration_lower = duration.lower()
        
        # Duration-based initial estimate
        if 'day' in duration_lower and any(d in duration_lower for d in ['1', '2', '3', '4', '5', '6', '7']):
            stage = 1
        elif 'week' in duration_lower:
            stage = 2
        elif 'month' in duration_lower:
            if '1' in duration_lower or '2' in duration_lower:
                stage = 3
            else:
                stage = 4
        elif 'year' in duration_lower:
            stage = 5
        else:
            stage = 3  # Default to middle stage
        
        # Adjust based on symptom count/severity
        if len(symptoms) > 10:
            stage = min(6, stage + 1)
        
        # Check for complication keywords
        complications = ['chronic', 'severe', 'complication', 'multiple', 'systemic']
        if any(c in ' '.join(symptoms).lower() for c in complications):
            stage = min(6, stage + 1)
        
        return stage
    
    def _create_fallback_model(self, disease: str, current_stage: int) -> Dict:
        return {
            "samprapti_overview": f"Pathogenesis of {disease}",
            "current_stage_analysis": {"current_stage": current_stage, "confidence": 0.5},
            "stage_progression": self.kriyakala_stages,
            "progression_timeline": {},
            "intervention_windows": [],
            "prevention_at_each_stage": []
        }
    
    def get_intervention_recommendation(self, disease: str, current_stage: int) -> Dict[str, Any]:
        """Get recommended intervention based on current disease stage"""
        stage_info = self.kriyakala_stages[min(max(current_stage, 1), 6) - 1]
        
        recommendations = {
            1: {
                "primary": "Nidana Parivarjana (Avoid causative factors)",
                "secondary": "Mild langhana (lightening therapy)",
                "urgency": "low",
                "prognosis": "Excellent - fully reversible"
            },
            2: {
                "primary": "Shamana therapy (pacification)",
                "secondary": "Dietary and lifestyle correction",
                "urgency": "low",
                "prognosis": "Very good - fully reversible"
            },
            3: {
                "primary": "Shodhana (purification) - OPTIMAL WINDOW",
                "secondary": "Prevent localization",
                "urgency": "medium",
                "prognosis": "Good - fully reversible with proper treatment"
            },
            4: {
                "primary": "Site-specific treatment",
                "secondary": "Prevent manifestation",
                "urgency": "high",
                "prognosis": "Fair - partially reversible"
            },
            5: {
                "primary": "Full treatment protocol",
                "secondary": "Prevent complications",
                "urgency": "high",
                "prognosis": "Guarded - management focused"
            },
            6: {
                "primary": "Complication management",
                "secondary": "Palliative care, quality of life",
                "urgency": "variable",
                "prognosis": "Poor - irreversible damage present"
            }
        }
        
        clamped_stage = min(max(current_stage, 1), 6)
        return {
            "disease": disease,
            "stage": clamped_stage,
            "stage_name": stage_info["name"],
            **recommendations.get(clamped_stage, recommendations[3])
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: FUTURE TRENDS (Enhanced Risk Prediction with Multi-Stage Retrieval)
# ═══════════════════════════════════════════════════════════════════════════════

# Import the disease risk mapper
try:
    from disease_risk_mapper import DiseaseRiskMapper, get_disease_mapper, RiskProfile as DiseaseRiskProfile
    DISEASE_MAPPER_AVAILABLE = True
except ImportError:
    DISEASE_MAPPER_AVAILABLE = False
    print("⚠ Warning: disease_risk_mapper not available, using basic prediction")


class FutureTrendsModule:
    """
    Enhanced prediction module with:
    - Multi-stage retrieval for comprehensive context
    - Disease risk mapping from AyurGenixAI dataset
    - Dosha-disease correlations
    - BMI and lifestyle-based risk assessment
    - Age and season-aware predictions
    """
    
    def __init__(self, engine: AyurvedaRAGEngine = None):
        self.engine = engine or AyurvedaRAGEngine()
        
        # Initialize disease risk mapper
        if DISEASE_MAPPER_AVAILABLE:
            print("   ✓ Loading Disease Risk Mapper...")
            self.disease_mapper = get_disease_mapper()
        else:
            self.disease_mapper = None
        
        # Condensed prompt to stay within token limits
        self.prompt = ChatPromptTemplate.from_template("""You are an expert Ayurvedic prognostic analyst. Use pretrained knowledge + context.

CONTEXT:
{classical_context}
{disease_context}
{dosha_pathology}
{computed_risks}

USER: {user_data}

OUTPUT JSON:
{{
    "prakriti_analysis": {{"determined_prakriti": "vata|pitta|kapha|dual|tridosha", "confidence": 0.0-1.0, "indicators": []}},
    "vikriti_analysis": {{"current_imbalance": "vata|pitta|kapha|none", "severity": "none|mild|moderate|severe", "description": ""}},
    "disease_risk_predictions": [
        {{"disease_name": "", "risk_level": "low|moderate|high|critical", "probability_1_year": 0.0-1.0, "risk_factors": [], "dosha_connection": "", "early_warning_signs": [], "preventive_herbs": [], "dietary_prevention": [], "lifestyle_prevention": []}}
    ],
    "dosha_trajectory": {{"current": "", "if_uncorrected_1_year": "", "correction_path": ""}},
    "agni_assessment": {{"type": "sama|vishama|tikshna|manda", "ama_level": "none|mild|moderate|severe", "correction": []}},
    "corrective_measures": {{
        "diet": {{"add": [], "avoid": [], "timing": ""}},
        "lifestyle": {{"wake": "", "sleep": "", "exercise": ""}},
        "herbs": [{{"name": "", "dosage": "", "timing": "", "purpose": ""}}],
        "panchakarma": {{"indicated": true|false, "procedures": []}}
    }},
    "health_scores": {{"overall": 0-100, "dosha_balance": 0-100, "agni": 0-100}},
    "priority_plan": {{"immediate": [], "short_term": [], "long_term": []}}
}}

Output ONLY valid JSON.""")

    def _get_classical_context(self, user_data: Dict[str, Any]) -> str:
        """Retrieve classical Ayurvedic principles relevant to user profile"""
        queries = [
            "Prakriti Vikriti assessment constitution determination Ayurveda",
            "Vaya age stages disease progression Ayurveda bala yuva vriddha"
        ]
        
        # Add dosha-specific queries
        prakriti = user_data.get('known_prakriti', '')
        if prakriti:
            queries.append(f"{prakriti} prakriti characteristics diseases vulnerabilities")
        
        # Add season-specific queries
        season = user_data.get('current_season', '')
        if season:
            queries.append(f"Ritucharya {season} seasonal regimen dosha aggravation")
        
        all_docs = {}
        for query in queries:
            docs = self.engine.retrieve(query, top_k=3)
            for db, doc_list in docs.items():
                if db not in all_docs:
                    all_docs[db] = []
                all_docs[db].extend(doc_list)
        
        return self.engine.build_context(all_docs)
    
    def _get_disease_context(self, user_data: Dict[str, Any]) -> str:
        """Retrieve disease-specific context based on user's risk profile"""
        queries = []
        
        # Query based on symptoms
        symptoms = user_data.get('current_symptoms', [])
        if symptoms:
            queries.append(f"Diseases with symptoms: {', '.join(symptoms[:5])}")
        
        # Query based on family history
        family_history = user_data.get('family_history', [])
        if family_history:
            for condition in family_history[:3]:
                queries.append(f"{condition} Ayurvedic treatment hereditary genetic")
        
        # BMI-based queries
        bmi = user_data.get('bmi')
        if bmi:
            if bmi >= 30:
                queries.append("Obesity Sthaulya Kapha treatment weight reduction Ayurveda")
            elif bmi >= 25:
                queries.append("Overweight Medoroga Kapha Meda dhatu")
            elif bmi < 18.5:
                queries.append("Underweight Karshya Vata emaciation malnutrition Ayurveda")
        
        # Age-based queries
        age = user_data.get('age', 30)
        if age >= 60:
            queries.append("Vriddhavastha elderly Vata disorders degenerative diseases")
        elif age >= 40:
            queries.append("Madhyavastha middle age Pitta disorders metabolic diseases")
        
        # Lifestyle queries
        lifestyle = user_data.get('lifestyle', {})
        if lifestyle.get('stress_level', '').lower() in ['high', 'severe']:
            queries.append("Stress anxiety Vata Pitta disorders mental health Ayurveda")
        if lifestyle.get('sleep_quality', '').lower() in ['poor', 'bad']:
            queries.append("Insomnia Anidra sleep disorders Vata treatment")
        
        all_docs = {}
        for query in queries[:6]:  # Limit to 6 queries
            docs = self.engine.retrieve(query, top_k=2)
            for db, doc_list in docs.items():
                if db not in all_docs:
                    all_docs[db] = []
                all_docs[db].extend(doc_list)
        
        return self.engine.build_context(all_docs)
    
    def _get_dosha_pathology_context(self, user_data: Dict[str, Any]) -> str:
        """Retrieve dosha-specific pathology information"""
        queries = []
        
        symptoms = user_data.get('current_symptoms', [])
        dosha_symptoms = user_data.get('current_dosha_symptoms', {})
        
        # Vata indicators
        vata_signs = ['anxiety', 'insomnia', 'constipation', 'dry skin', 'bloating', 
                      'joint pain', 'restlessness', 'fear', 'nervousness', 'gas']
        if any(s.lower() in [x.lower() for x in symptoms] for s in vata_signs) or dosha_symptoms.get('vata'):
            queries.append("Vata vriddhi aggravation disorders treatment Vataja roga")
        
        # Pitta indicators
        pitta_signs = ['acidity', 'inflammation', 'anger', 'skin rashes', 'burning',
                       'fever', 'irritability', 'jealousy', 'heartburn', 'diarrhea']
        if any(s.lower() in [x.lower() for x in symptoms] for s in pitta_signs) or dosha_symptoms.get('pitta'):
            queries.append("Pitta vriddhi aggravation disorders treatment Pittaja roga")
        
        # Kapha indicators
        kapha_signs = ['weight gain', 'lethargy', 'congestion', 'sluggish', 'excess sleep',
                       'mucus', 'edema', 'attachment', 'greed', 'depression']
        if any(s.lower() in [x.lower() for x in symptoms] for s in kapha_signs) or dosha_symptoms.get('kapha'):
            queries.append("Kapha vriddhi aggravation disorders treatment Kaphaja roga")
        
        # Agni/Ama queries
        digestion_issues = user_data.get('digestion_issues', [])
        if digestion_issues or 'poor digestion' in [s.lower() for s in symptoms]:
            queries.append("Agni Mandagni Ama formation treatment digestive fire")
        
        all_docs = {}
        for query in queries:
            docs = self.engine.retrieve(query, top_k=3)
            for db, doc_list in docs.items():
                if db not in all_docs:
                    all_docs[db] = []
                all_docs[db].extend(doc_list)
        
        return self.engine.build_context(all_docs)
    
    def _get_computed_disease_risks(self, user_data: Dict[str, Any]) -> str:
        """Get pre-computed disease risks from the disease mapper"""
        if not self.disease_mapper:
            return "Disease risk mapping not available - using LLM inference only."
        
        top_risks = self.disease_mapper.get_top_risks(user_data, top_n=10)
        
        if not top_risks:
            return "No significant disease risks identified from database."
        
        risk_summary = ["TOP DISEASE RISKS IDENTIFIED:\n"]
        
        for i, risk in enumerate(top_risks, 1):
            profile = self.disease_mapper.get_disease_profile(risk.disease_name)
            
            risk_summary.append(f"\n{i}. {risk.disease_name.upper()}")
            risk_summary.append(f"   Risk Score: {risk.base_risk_score:.2f}")
            risk_summary.append(f"   6-month probability: {risk.probability_6_months:.1%}")
            risk_summary.append(f"   1-year probability: {risk.probability_1_year:.1%}")
            risk_summary.append(f"   5-year probability: {risk.probability_5_years:.1%}")
            
            if risk.dosha_factors:
                risk_summary.append(f"   Dosha involvement: {risk.dosha_factors}")
            
            contributing = []
            if risk.age_factor > 0:
                contributing.append(f"age({risk.age_factor:.2f})")
            if risk.bmi_factor > 0:
                contributing.append(f"BMI({risk.bmi_factor:.2f})")
            if risk.family_history_factor > 0:
                contributing.append(f"family_history({risk.family_history_factor:.2f})")
            if risk.lifestyle_factor > 0:
                contributing.append(f"lifestyle({risk.lifestyle_factor:.2f})")
            if risk.symptom_match_factor > 0:
                contributing.append(f"symptoms({risk.symptom_match_factor:.2f})")
            
            if contributing:
                risk_summary.append(f"   Contributing factors: {', '.join(contributing)}")
            
            if profile:
                risk_summary.append(f"   Doshas: {', '.join(profile.doshas_involved)}")
                risk_summary.append(f"   Prakriti: {profile.prakriti_association}")
                if profile.symptoms:
                    risk_summary.append(f"   Key symptoms: {', '.join(profile.symptoms[:5])}")
                if profile.ayurvedic_herbs:
                    risk_summary.append(f"   Ayurvedic herbs: {', '.join(profile.ayurvedic_herbs)}")
                if profile.formulation:
                    risk_summary.append(f"   Formulation: {profile.formulation}")
                if profile.prevention:
                    risk_summary.append(f"   Prevention: {profile.prevention}")
        
        return "\n".join(risk_summary)
    
    def _calculate_health_scores(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate health scores based on user data"""
        scores = {
            "overall": 70.0,
            "dosha_balance": 70.0,
            "agni": 70.0,
            "ojas": 70.0,
            "dhatu_health": 70.0,
            "mala_elimination": 70.0
        }
        
        # Adjust for symptoms
        symptoms = user_data.get('current_symptoms', [])
        symptom_penalty = len(symptoms) * 3
        scores["overall"] -= min(symptom_penalty, 25)
        
        # Adjust for BMI
        bmi = user_data.get('bmi')
        if bmi:
            if 18.5 <= bmi <= 24.9:
                scores["overall"] += 5
                scores["dhatu_health"] += 5
            elif bmi >= 30:
                scores["overall"] -= 15
                scores["dhatu_health"] -= 10
                scores["agni"] -= 10
            elif bmi < 18.5:
                scores["overall"] -= 10
                scores["dhatu_health"] -= 15
                scores["ojas"] -= 10
        
        # Adjust for lifestyle
        lifestyle = user_data.get('lifestyle', {})
        
        stress = lifestyle.get('stress_level', '').lower()
        if stress in ['high', 'severe', 'very high']:
            scores["overall"] -= 10
            scores["dosha_balance"] -= 15
            scores["ojas"] -= 10
        
        sleep = lifestyle.get('sleep_quality', '').lower()
        if sleep in ['poor', 'bad', 'irregular']:
            scores["overall"] -= 8
            scores["ojas"] -= 12
        
        exercise = lifestyle.get('exercise', '').lower()
        if exercise in ['none', 'sedentary', 'low']:
            scores["overall"] -= 8
            scores["agni"] -= 10
        elif exercise in ['regular', 'moderate', 'good']:
            scores["overall"] += 5
            scores["agni"] += 5
        
        # Adjust for digestion
        digestion_issues = user_data.get('digestion_issues', [])
        if digestion_issues:
            scores["agni"] -= len(digestion_issues) * 5
        
        # Adjust for elimination
        bowel = user_data.get('bowel_regularity', '').lower()
        if bowel in ['constipated', 'irregular']:
            scores["mala_elimination"] -= 15
        
        # Normalize scores
        for key in scores:
            scores[key] = max(0, min(100, scores[key]))
        
        return scores
    
    def analyze(self, user_data: Dict[str, Any]) -> FutureTrendsResponse:
        """
        Comprehensive health analysis with multi-stage retrieval.
        
        Enhanced user_data structure:
        - age: int (required)
        - gender: str (required)
        - bmi: float (optional but recommended)
        - height_cm: float (optional)
        - weight_kg: float (optional)
        - known_prakriti: str (vata|pitta|kapha|vata_pitta|etc.)
        - current_dosha_symptoms: dict {vata: [...], pitta: [...], kapha: [...]}
        - agni_type: str (sama|vishama|tikshna|manda)
        - digestion_issues: list
        - current_symptoms: list
        - diet_type: str
        - meal_timing: dict
        - food_cravings: list
        - foods_avoided: list
        - lifestyle: dict {exercise, stress_level, sleep_hours, sleep_quality, diet}
        - sleep_quality: str
        - wake_time: str
        - sleep_time: str
        - bowel_regularity: str
        - urination_frequency: str
        - sweating_pattern: str
        - mental_state: str
        - concentration_level: str
        - medical_history: list
        - family_history: list
        - current_season: str
        - climate_type: str
        - occupation_type: str
        - toxin_exposure: list
        """
        query_id = AyurvedaRAGEngine.generate_query_id(json.dumps(user_data))
        timestamp = datetime.now().isoformat()
        
        print(f"🔮 Analyzing health trends for user profile...")
        
        # Calculate BMI if not provided but height/weight available
        if not user_data.get('bmi') and user_data.get('height_cm') and user_data.get('weight_kg'):
            height_m = user_data['height_cm'] / 100
            user_data['bmi'] = round(user_data['weight_kg'] / (height_m ** 2), 1)
        
        # Stage 1: Get classical Ayurvedic context
        print("   📚 Stage 1: Retrieving classical Ayurvedic knowledge...")
        classical_context = self._get_classical_context(user_data)
        
        # Stage 2: Get disease-specific context
        print("   🏥 Stage 2: Retrieving disease-specific clinical data...")
        disease_context = self._get_disease_context(user_data)
        
        # Stage 3: Get dosha pathology context
        print("   ⚖️  Stage 3: Retrieving dosha pathology references...")
        dosha_pathology = self._get_dosha_pathology_context(user_data)
        
        # Stage 4: Get pre-computed disease risks
        print("   📊 Stage 4: Computing disease risk scores...")
        computed_risks = self._get_computed_disease_risks(user_data)
        
        # Calculate health scores
        health_scores = self._calculate_health_scores(user_data)
        
        # Generate comprehensive response
        print("   🧠 Stage 5: Generating comprehensive analysis...")
        
        user_data_str = json.dumps(user_data, indent=2)
        
        raw_response = self.engine.generate(self.prompt, {
            "classical_context": classical_context,
            "disease_context": disease_context,
            "dosha_pathology": dosha_pathology,
            "computed_risks": computed_risks,
            "user_data": user_data_str
        })
        
        # Parse response
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            data = json.loads(cleaned.strip())
        except json.JSONDecodeError as e:
            print(f"   ⚠ JSON parse error: {e}")
            data = self._create_fallback_response(user_data, health_scores)
        
        # Build response object
        return self._build_response(query_id, timestamp, user_data, data, health_scores)
    
    def _build_response(self, query_id: str, timestamp: str, user_data: Dict, 
                        data: Dict, health_scores: Dict) -> FutureTrendsResponse:
        """Build structured response from parsed data"""
        
        # Determine prakriti
        prakriti_data = data.get("prakriti_analysis", {})
        prakriti_str = prakriti_data.get("determined_prakriti", 
                                         user_data.get("known_prakriti", "vata"))
        try:
            prakriti = DoshaType(prakriti_str.lower())
        except ValueError:
            prakriti = DoshaType.VATA
        
        # Build vikriti analysis
        vikriti_data = data.get("vikriti_analysis", {})
        vikriti = None
        if vikriti_data:
            try:
                imbalance = vikriti_data.get("current_imbalance", "vata")
                # Map "multiple" to tridosha
                if imbalance == "multiple":
                    imbalance = "tridosha"
                
                vikriti = DoshaAnalysis(
                    primary_dosha=DoshaType(imbalance.lower()),
                    state=DoshaState.AGGRAVATED,
                    vikriti_description=vikriti_data.get("vikriti_description", "")
                )
            except ValueError:
                pass
        
        # Build risk factors from disease predictions
        risk_factors = []
        for pred in data.get("disease_risk_predictions", []):
            risk_factors.append(RiskFactor(
                risk_name=pred.get("disease_name", "Unknown"),
                category="disease_risk",
                current_severity=pred.get("risk_level", "low"),
                probability_6_months=pred.get("probability_6_months", 0.0),
                probability_1_year=pred.get("probability_1_year", 0.0),
                probability_5_years=pred.get("probability_5_years", 0.0),
                contributing_factors=pred.get("risk_factors_present", []),
                preventive_measures=pred.get("preventive_herbs", []) + 
                                    pred.get("dietary_prevention", []) +
                                    pred.get("lifestyle_prevention", []),
                early_warning_signs=pred.get("early_warning_signs", [])
            ))
        
        # Add dosha imbalance as risk factor if present
        dosha_trajectory = data.get("dosha_imbalance_trajectory", {})
        if dosha_trajectory.get("current_state"):
            risk_factors.append(RiskFactor(
                risk_name="Dosha Imbalance Progression",
                category="dosha_imbalance",
                current_severity="moderate" if vikriti else "low",
                probability_6_months=0.6 if vikriti else 0.3,
                probability_1_year=0.75 if vikriti else 0.4,
                probability_5_years=0.9 if vikriti else 0.5,
                contributing_factors=[dosha_trajectory.get("current_state", "")],
                preventive_measures=[dosha_trajectory.get("correction_path", "")],
                early_warning_signs=[
                    dosha_trajectory.get("if_uncorrected_6_months", "")
                ]
            ))
        
        # Build rasayanas
        rasayanas = []
        herbal_protocol = data.get("corrective_measures", {}).get("herbal_protocol", {})
        for r in herbal_protocol.get("rasayanas", []):
            rasayanas.append(HerbalFormulation(
                name=r.get("name", ""),
                dosage=r.get("dosage"),
                timing=r.get("timing"),
                duration=r.get("duration")
            ))
        
        # Build seasonal vulnerabilities
        seasonal_data = data.get("seasonal_calendar", {})
        seasonal_vulnerabilities = {}
        for season, info in seasonal_data.items():
            if isinstance(info, dict):
                seasonal_vulnerabilities[season] = info.get("risks", [])
            elif isinstance(info, list):
                seasonal_vulnerabilities[season] = info
        
        # Build prevention plan
        prevention_plan = data.get("prevention_priority_plan", {})
        
        # Build optimal routine
        lifestyle = data.get("corrective_measures", {}).get("immediate_lifestyle", {})
        optimal_routine = {
            "wake_time": lifestyle.get("wake_time", "6:00 AM"),
            "sleep_time": lifestyle.get("sleep_time", "10:00 PM"),
            "meal_times": "Breakfast 7-8 AM, Lunch 12-1 PM, Dinner 6-7 PM",
            "exercise_time": lifestyle.get("exercise_timing", "Morning"),
            "meditation_time": "Early morning or evening"
        }
        
        # Use calculated health scores, override with LLM if available
        llm_scores = data.get("health_scores", {})
        final_scores = {
            "overall": llm_scores.get("overall", health_scores["overall"]),
            "dosha_balance": llm_scores.get("dosha_balance", health_scores["dosha_balance"]),
            "agni": llm_scores.get("agni", health_scores["agni"]),
            "ojas": llm_scores.get("ojas", health_scores["ojas"])
        }
        
        # Age-related risks
        age_risks = data.get("age_stage_analysis", {})
        age_related_risks = [{
            "current_stage": age_risks.get("current_stage", "madhya"),
            "dominant_dosha": age_risks.get("dominant_dosha_for_age", "pitta"),
            "current_risks": age_risks.get("current_risks_for_age", []),
            "next_decade_risks": age_risks.get("next_decade_risks", [])
        }]
        
        return FutureTrendsResponse(
            query_id=query_id,
            timestamp=timestamp,
            user_profile=user_data,
            prakriti=prakriti,
            vikriti=vikriti,
            overall_health_score=final_scores["overall"],
            dosha_balance_score=final_scores["dosha_balance"],
            agni_score=final_scores["agni"],
            ojas_score=final_scores["ojas"],
            risk_factors=risk_factors,
            seasonal_vulnerabilities=seasonal_vulnerabilities,
            age_related_risks=age_related_risks,
            prevention_plan=prevention_plan,
            optimal_routine=optimal_routine,
            recommended_rasayanas=rasayanas
        )
    
    def _create_fallback_response(self, user_data: Dict, health_scores: Dict) -> Dict:
        """Create fallback response if LLM parsing fails"""
        return {
            "prakriti_analysis": {
                "determined_prakriti": user_data.get("known_prakriti", "vata"),
                "prakriti_confidence": 0.5,
                "prakriti_indicators": []
            },
            "vikriti_analysis": None,
            "disease_risk_predictions": [],
            "dosha_imbalance_trajectory": {},
            "dhatu_health_assessment": {},
            "agni_optimization": {
                "current_agni_type": user_data.get("agni_type", "vishama")
            },
            "corrective_measures": {},
            "seasonal_calendar": {},
            "age_stage_analysis": {},
            "health_scores": health_scores,
            "prevention_priority_plan": {}
        }
    
    def get_quick_risk_assessment(self, user_data: Dict[str, Any]) -> List[Dict]:
        """Quick risk assessment using only the disease mapper (no LLM)"""
        if not self.disease_mapper:
            return []
        
        risks = self.disease_mapper.get_top_risks(user_data, top_n=5)
        
        return [
            {
                "disease": r.disease_name,
                "risk_score": round(r.base_risk_score, 2),
                "probability_6_months": round(r.probability_6_months, 2),
                "probability_1_year": round(r.probability_1_year, 2),
                "probability_5_years": round(r.probability_5_years, 2),
                "preventive_measures": r.preventive_measures,
                "warning_signs": r.early_warning_signs
            }
            for r in risks
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED API CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class AyurvedaAPI:
    """
    Unified API for all Ayurveda modules.
    Provides structured, parseable outputs for different use cases.
    
    Modules:
    - DoctorModule: Clinical JSON/CSV outputs for practitioners
    - PatientModule: User-friendly guidance for visitors
    - AyushModule: AYUSH framework analysis
    - FutureTrendsModule: Risk prediction and health trends
    - DiagnosisModule: AI-assisted diagnosis with confidence scores
    - PersonalizedTreatmentModule: Personalized treatment algorithms
    - DecisionSupportModule: Clinical decision support system
    - ProgressionModelingModule: Disease progression prediction
    """
    
    def __init__(self):
        print("═" * 60)
        print("🌿 AYURVEDA MODULAR API - ENHANCED")
        print("═" * 60)
        
        # Initialize shared engine (singleton)
        self.engine = AyurvedaRAGEngine()
        
        # Core modules
        print("📦 Initializing core modules...")
        self.doctor = DoctorModule(self.engine)
        self.patient = PatientModule(self.engine)
        self.ayush = AyushModule(self.engine)
        self.future_trends = FutureTrendsModule(self.engine)
        
        # Advanced clinical modules
        print("🧬 Initializing advanced clinical modules...")
        self.diagnosis = DiagnosisModule(self.engine)
        self.treatment = PersonalizedTreatmentModule(self.engine)
        self.decision_support = DecisionSupportModule(self.engine)
        self.progression = ProgressionModelingModule(self.engine)
        
        print("✅ All modules initialized!")
        print("   📋 Core Modules:")
        print("      • DoctorModule: Clinical JSON/CSV outputs")
        print("      • PatientModule: User-friendly guidance")
        print("      • AyushModule: AYUSH framework analysis")
        print("      • FutureTrendsModule: Risk prediction")
        print("   🧬 Advanced Clinical Modules:")
        print("      • DiagnosisModule: AI-assisted diagnosis")
        print("      • PersonalizedTreatmentModule: Treatment algorithms")
        print("      • DecisionSupportModule: Clinical decision support")
        print("      • ProgressionModelingModule: Disease progression")
        print("═" * 60 + "\n")
    
    # ─────────────────────────────────────────────────────────────
    # DOCTOR ENDPOINTS
    # ─────────────────────────────────────────────────────────────
    
    def doctor_query(self, question: str, output_format: str = "json") -> Union[str, Dict]:
        """
        Clinical query for Ayurvedic practitioners.
        
        Args:
            question: Clinical query
            output_format: "json", "dict", or "csv_row"
        
        Returns:
            Structured clinical response
        """
        response = self.doctor.query(question)
        
        if output_format == "json":
            return response.to_json()
        elif output_format == "csv_row":
            return response.to_csv_row()
        else:
            return response.to_dict()
    
    # ─────────────────────────────────────────────────────────────
    # PATIENT ENDPOINTS
    # ─────────────────────────────────────────────────────────────
    
    def patient_query(self, question: str, output_format: str = "json") -> Union[str, Dict]:
        """
        User-friendly query for casual visitors.
        
        Args:
            question: Health question in plain language
            output_format: "json" or "dict"
        
        Returns:
            User-friendly guidance
        """
        response = self.patient.query(question)
        
        if output_format == "json":
            return response.to_json()
        else:
            return response.to_dict()
    
    # ─────────────────────────────────────────────────────────────
    # AYUSH ENDPOINTS
    # ─────────────────────────────────────────────────────────────
    
    def ayush_query(self, question: str, output_format: str = "json") -> Union[str, Dict]:
        """
        AYUSH Ministry aligned comprehensive analysis.
        
        Args:
            question: Query for AYUSH framework analysis
            output_format: "json" or "dict"
        
        Returns:
            Complete Ayurvedic analysis (Panchamahabhuta, Tridosha, Saptadhatu, etc.)
        """
        response = self.ayush.query(question)
        
        if output_format == "json":
            return response.to_json()
        else:
            return response.to_dict()
    
    # ─────────────────────────────────────────────────────────────
    # FUTURE TRENDS ENDPOINTS
    # ─────────────────────────────────────────────────────────────
    
    def predict_health_trends(self, user_data: Dict[str, Any], output_format: str = "json") -> Union[str, Dict]:
        """
        Predict future health risks based on user data.
        
        Args:
            user_data: Dictionary containing:
                - age: int
                - gender: str
                - current_symptoms: list
                - lifestyle: dict
                - medical_history: list
                - family_history: list
                - current_season: str (optional)
            output_format: "json" or "dict"
        
        Returns:
            Risk predictions with prevention strategies
        """
        response = self.future_trends.analyze(user_data)
        
        if output_format == "json":
            return response.to_json()
        else:
            return response.to_dict()
    
    # ─────────────────────────────────────────────────────────────
    # AI-ASSISTED DIAGNOSIS ENDPOINTS
    # ─────────────────────────────────────────────────────────────
    
    def diagnose(
        self, 
        symptoms: List[str], 
        profile: Optional[Dict[str, Any]] = None,
        output_format: str = "json"
    ) -> Union[str, Dict]:
        """
        AI-assisted diagnosis using Ayurvedic parameters.
        
        Analyzes symptoms through Nidana Panchaka (5-fold diagnostic framework):
        - Nidana (etiology/cause)
        - Purvarupa (prodromal symptoms)
        - Rupa (clinical features)
        - Upashaya (therapeutic tests)
        - Samprapti (pathogenesis)
        
        Args:
            symptoms: List of presenting symptoms
            profile: Optional user profile with Prakriti, age, gender, etc.
            output_format: "json" or "dict"
        
        Returns:
            DiagnosticResult with differential diagnoses and confidence scores
        """
        response = self.diagnosis.diagnose(symptoms, profile)
        
        if output_format == "json":
            return response.to_json()
        else:
            return response.to_dict()
    
    def assess_prakriti(
        self,
        questionnaire_responses: Dict[str, str],
        output_format: str = "json"
    ) -> Union[str, Dict]:
        """
        Assess constitutional type (Prakriti) based on questionnaire.
        
        Args:
            questionnaire_responses: Dict with answers to Prakriti assessment questions
            output_format: "json" or "dict"
        
        Returns:
            PrakritiAssessment with dominant and secondary doshas
        """
        response = self.diagnosis.assess_prakriti(questionnaire_responses)
        
        if output_format == "json":
            return response.to_json()
        else:
            return response.to_dict()
    
    def check_red_flags(
        self,
        symptoms: List[str],
        output_format: str = "json"
    ) -> Union[str, Dict]:
        """
        Check for emergency warning signs requiring immediate medical attention.
        
        Args:
            symptoms: List of symptoms to check
            output_format: "json" or "dict"
        
        Returns:
            Dict with red_flags list and requires_emergency boolean
        """
        red_flags, is_emergency = self.diagnosis.check_red_flags(symptoms)
        result = {
            "red_flags": red_flags,
            "requires_emergency": is_emergency,
            "recommendation": "SEEK IMMEDIATE MEDICAL ATTENTION" if is_emergency else "Standard evaluation appropriate"
        }
        
        if output_format == "json":
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            return result
    
    # ─────────────────────────────────────────────────────────────
    # PERSONALIZED TREATMENT ENDPOINTS
    # ─────────────────────────────────────────────────────────────
    
    def generate_treatment_plan(
        self,
        diagnosis: str,
        profile: Dict[str, Any],
        output_format: str = "json"
    ) -> Union[str, Dict]:
        """
        Generate personalized treatment plan based on diagnosis and patient profile.
        
        Includes multi-phase treatment approach:
        1. Nidana Parivarjana (removing causative factors)
        2. Shodhana (purification/Panchakarma)
        3. Shamana (palliative treatment)
        4. Rasayana (rejuvenation)
        
        Args:
            diagnosis: Primary diagnosis or condition
            profile: Patient profile with Prakriti, Vikriti, age, lifestyle, etc.
            output_format: "json" or "dict"
        
        Returns:
            PersonalizedTreatmentPlan with phased protocols
        """
        response = self.treatment.generate_treatment_plan(
            patient_profile=profile,
            diagnosis=diagnosis
        )
        
        if output_format == "json":
            return response.to_json()
        else:
            return response.to_dict()
    
    # ─────────────────────────────────────────────────────────────
    # CLINICAL DECISION SUPPORT ENDPOINTS
    # ─────────────────────────────────────────────────────────────
    
    def check_drug_interactions(
        self,
        herbs_medicines: List[str],
        output_format: str = "json"
    ) -> Union[str, Dict]:
        """
        Check for interactions between Ayurvedic herbs and modern medicines.
        
        Args:
            herbs_medicines: List of herbs/medicines to check
            output_format: "json" or "dict"
        
        Returns:
            List of DrugInteraction objects with severity levels
        """
        interactions = self.decision_support.check_interactions(herbs_medicines)
        result = [i.to_dict() for i in interactions]
        
        if output_format == "json":
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            return result
    
    def check_contraindications(
        self,
        treatment: str,
        patient_conditions: List[str],
        output_format: str = "json"
    ) -> Union[str, Dict]:
        """
        Check if a treatment is contraindicated for patient's conditions.
        
        Args:
            treatment: Treatment or herb to check
            patient_conditions: List of patient's conditions/states
            output_format: "json" or "dict"
        
        Returns:
            Dict with is_contraindicated, reasons, and alternatives
        """
        result = self.decision_support.check_contraindications(treatment, patient_conditions)
        
        if output_format == "json":
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            return result
    
    def get_decision_support(
        self,
        scenario: str,
        patient_profile: Dict[str, Any],
        output_format: str = "json"
    ) -> Union[str, Dict]:
        """
        Get comprehensive clinical decision support for a treatment scenario.
        
        Provides:
        - Treatment options with pros/cons
        - Contraindication warnings
        - Drug interaction alerts
        - Dosage recommendations
        - Follow-up protocols
        
        Args:
            scenario: Clinical scenario description
            patient_profile: Complete patient profile
            output_format: "json" or "dict"
        
        Returns:
            ClinicalDecisionSupport with all recommendations
        """
        response = self.decision_support.get_decision_support(scenario, patient_profile)
        
        if output_format == "json":
            return response.to_json()
        else:
            return response.to_dict()
    
    # ─────────────────────────────────────────────────────────────
    # DISEASE PROGRESSION MODELING ENDPOINTS
    # ─────────────────────────────────────────────────────────────
    
    def model_disease_progression(
        self,
        disease: str,
        current_symptoms: List[str],
        duration_days: int,
        patient_profile: Optional[Dict[str, Any]] = None,
        output_format: str = "json"
    ) -> Union[str, Dict]:
        """
        Model disease progression using Shat Kriyakala (6-stage pathogenesis).
        
        Stages:
        1. Sanchaya (Accumulation) - Dosha accumulates at its seat
        2. Prakopa (Aggravation) - Dosha becomes excited
        3. Prasara (Spread) - Dosha spreads from its seat
        4. Sthanasamshraya (Localization) - Settles in weak tissues
        5. Vyakti (Manifestation) - Disease becomes apparent
        6. Bheda (Complication) - Structural damage occurs
        
        Args:
            disease: Disease or condition name
            current_symptoms: List of current symptoms
            duration_days: How long symptoms have been present
            patient_profile: Optional patient details
            output_format: "json" or "dict"
        
        Returns:
            ProgressionModel with current stage and trajectory
        """
        response = self.progression.model_progression(
            disease, current_symptoms, duration_days, patient_profile
        )
        
        if output_format == "json":
            return response.to_json()
        else:
            return response.to_dict()
    
    def get_intervention_recommendation(
        self,
        disease: str,
        current_stage: int,
        output_format: str = "json"
    ) -> Union[str, Dict]:
        """
        Get stage-specific intervention recommendations.
        
        Args:
            disease: Disease name
            current_stage: Current Kriyakala stage (1-6)
            output_format: "json" or "dict"
        
        Returns:
            Dict with intervention type, urgency, and specific recommendations
        """
        response = self.progression.get_intervention_recommendation(disease, current_stage)
        
        if output_format == "json":
            return json.dumps(response, indent=2, ensure_ascii=False)
        else:
            return response
    
    # ─────────────────────────────────────────────────────────────
    # MULTI-MODE QUERY
    # ─────────────────────────────────────────────────────────────
    
    def query_all_modes(self, question: str) -> Dict[str, Dict]:
        """
        Query all modes (Doctor, Patient, AYUSH) simultaneously.
        
        Returns:
            Dictionary with all three response types
        """
        return {
            "doctor": self.doctor.query(question).to_dict(),
            "patient": self.patient.query(question).to_dict(),
            "ayush": self.ayush.query(question).to_dict()
        }
    
    # ─────────────────────────────────────────────────────────────
    # BATCH PROCESSING
    # ─────────────────────────────────────────────────────────────
    
    def batch_doctor_queries(self, questions: List[str]) -> List[Dict]:
        """Process multiple clinical queries"""
        return [self.doctor.query(q).to_dict() for q in questions]
    
    def export_to_csv(self, questions: List[str], filepath: str) -> str:
        """Export batch clinical queries to CSV"""
        import csv
        
        rows = [self.doctor.query(q).to_csv_row() for q in questions]
        
        if rows:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        
        return filepath


# ═══════════════════════════════════════════════════════════════════════════════
# FLASK/FASTAPI READY ENDPOINTS (Example Structure)
# ═══════════════════════════════════════════════════════════════════════════════

def create_flask_app():
    """Create Flask app with API endpoints"""
    try:
        from flask import Flask, request, jsonify # type: ignore
    except ImportError:
        print("Flask not installed. Run: pip install flask")
        return None
    
    app = Flask(__name__)
    api = AyurvedaAPI()
    
    @app.route('/api/v1/doctor', methods=['POST'])
    def doctor_endpoint():
        data = request.json
        question = data.get('question', '')
        response = api.doctor_query(question, output_format='dict')
        return jsonify(response)
    
    @app.route('/api/v1/patient', methods=['POST'])
    def patient_endpoint():
        data = request.json
        question = data.get('question', '')
        response = api.patient_query(question, output_format='dict')
        return jsonify(response)
    
    @app.route('/api/v1/ayush', methods=['POST'])
    def ayush_endpoint():
        data = request.json
        question = data.get('question', '')
        response = api.ayush_query(question, output_format='dict')
        return jsonify(response)
    
    @app.route('/api/v1/trends', methods=['POST'])
    def trends_endpoint():
        user_data = request.json
        response = api.predict_health_trends(user_data, output_format='dict')
        return jsonify(response)
    
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "modules": ["doctor", "patient", "ayush", "trends"]})
    
    return app


def create_fastapi_app():
    """Create FastAPI app with API endpoints"""
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
    except ImportError:
        print("FastAPI not installed. Run: pip install fastapi uvicorn")
        return None
    
    app = FastAPI(
        title="Ayurveda API",
        description="Modular API for Ayurvedic knowledge retrieval and analysis",
        version="1.0.0"
    )
    
    api = None
    
    @app.on_event("startup")
    async def startup():
        nonlocal api
        api = AyurvedaAPI()
    
    class QueryRequest(BaseModel):
        question: str
    
    class UserDataRequest(BaseModel):
        age: int
        gender: str
        current_symptoms: List[str] = []
        lifestyle: Dict[str, Any] = {}
        medical_history: List[str] = []
        family_history: List[str] = []
        current_season: Optional[str] = None
    
    @app.post("/api/v1/doctor")
    async def doctor_endpoint(request: QueryRequest):
        return api.doctor_query(request.question, output_format='dict')
    
    @app.post("/api/v1/patient")
    async def patient_endpoint(request: QueryRequest):
        return api.patient_query(request.question, output_format='dict')
    
    @app.post("/api/v1/ayush")
    async def ayush_endpoint(request: QueryRequest):
        return api.ayush_query(request.question, output_format='dict')
    
    @app.post("/api/v1/trends")
    async def trends_endpoint(request: UserDataRequest):
        return api.predict_health_trends(request.dict(), output_format='dict')
    
    @app.get("/api/v1/health")
    async def health_check():
        return {"status": "healthy", "modules": ["doctor", "patient", "ayush", "trends"]}
    
    return app


# ═══════════════════════════════════════════════════════════════════════════════
# CLI DEMO
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    # Initialize API
    api = AyurvedaAPI()
    
    print("\n" + "═" * 60)
    print("🏥 AYURVEDA API DEMO")
    print("═" * 60)
    print("Modes:")
    print("  [1] Doctor - Clinical JSON output")
    print("  [2] Patient - User-friendly guidance")
    print("  [3] AYUSH - Complete framework analysis")
    print("  [4] Future Trends - Risk prediction")
    print("  [5] All modes")
    print("  [q] Quit")
    print("═" * 60)
    
    while True:
        mode = input("\n📋 Select mode [1-5/q]: ").strip().lower()
        
        if mode == 'q':
            print("\n🙏 Namaste! Stay healthy.")
            break
        
        if mode == '4':
            print("\n📝 Enter user health data for trend analysis:")
            age = int(input("   Age: ") or "35")
            gender = input("   Gender (M/F): ") or "M"
            symptoms = input("   Current symptoms (comma-separated): ").split(",")
            symptoms = [s.strip() for s in symptoms if s.strip()]
            
            user_data = {
                "age": age,
                "gender": gender,
                "current_symptoms": symptoms,
                "lifestyle": {
                    "diet": "mixed",
                    "exercise": "moderate",
                    "sleep_hours": 7,
                    "stress_level": "moderate"
                }
            }
            
            print("\n⏳ Analyzing future trends...")
            result = api.predict_health_trends(user_data)
            print("\n" + "─" * 60)
            print("📊 FUTURE TRENDS ANALYSIS:")
            print("─" * 60)
            print(result)
            continue
        
        question = input("\n🩺 Enter your query: ").strip()
        if not question:
            continue
        
        print("\n⏳ Processing...")
        
        if mode == '1':
            result = api.doctor_query(question)
            print("\n" + "█" * 60)
            print("👨‍⚕️ DOCTOR RESPONSE (JSON):")
            print("█" * 60)
            print(result)
        
        elif mode == '2':
            result = api.patient_query(question)
            print("\n" + "·" * 60)
            print("🧘 PATIENT RESPONSE:")
            print("·" * 60)
            print(result)
        
        elif mode == '3':
            result = api.ayush_query(question)
            print("\n" + "╔" + "═" * 58 + "╗")
            print("║" + " 🏛️  AYUSH ANALYSIS ".center(58) + "║")
            print("╚" + "═" * 58 + "╝")
            print(result)
        
        elif mode == '5':
            results = api.query_all_modes(question)
            print("\n" + "═" * 60)
            print("📚 ALL MODE RESPONSES:")
            print("═" * 60)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        
        else:
            print("❌ Invalid mode. Please select 1-5 or 'q'.")
