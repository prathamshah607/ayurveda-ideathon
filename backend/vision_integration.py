"""
Vision Integration Module
==========================
Wraps vision models (Tongue & Nail sensors) and processes their binary classification outputs.

Vision Model Architecture:
- Two EfficientNet binary classifiers (Class 0: Healthy, Class 1: Sick)
- Each outputs: severity_score (0-1) = confidence that image is Class 1 (sick)

Inputs from Vision Models:
- Tongue Model: tongue_severity_score (0-1)
- Nail Model: nail_severity_score (0-1)

Processing:
- VisionProcessor INFERS clinical metadata from severity scores using heuristics
- Converts scores → dosha tendencies, ama levels, tissue issues

Outputs:
- Clinical Metadata with inferred agni_score, color_code, ama_presence, etc.
- Used by Data Fusion Engine to create Super-Prompts
"""

from dataclasses import dataclass, asdict
from typing import Dict, Optional, List, Literal
from enum import Enum
import json
from datetime import datetime


class AmaPresence(str, Enum):
    """Toxin/Ama levels detected by tongue vision model"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TongueColorCode(str, Enum):
    """Tongue color classification indicating dosha imbalance"""
    RED = "red"  # Pitta
    YELLOW = "yellow"  # Mixed
    PALE = "pale"  # Vata
    WHITE_COATED = "white_coated"  # High Ama/Kapha
    PURPLE = "purple"  # Vata/Blood stagnation


class NailShapeClass(str, Enum):
    """Nail shape abnormalities indicating tissue issues"""
    NORMAL = "normal"
    CLUBBING = "clubbing"  # Heart/Lung/Liver disease
    PITTING = "pitting"  # Psoriasis, alopecia, autoimmune
    RIDGES = "ridges"  # Mineral deficiency, bone tissue issue
    BRITTLENESS = "brittleness"  # Vata aggravation


@dataclass
class TongueVisionOutput:
    """Output from Tongue Binary Classifier (EfficientNet Model)
    
    INPUT: Raw model output = severity_score (0-1)
           where 0.0 = definitely healthy (Class 0)
                 1.0 = definitely sick (Class 1)
    
    INFERENCE: All clinical fields are computed from severity_score
    """
    severity_score: float  # 0-1: Model confidence that tongue is Class 1 (sick)
    
    # INFERRED FIELDS (computed from severity_score using heuristics)
    agni_score: Optional[float] = None  # 0-100: Computed as (100 - severity_score*100)
    ama_presence: Optional[AmaPresence] = None  # High/Medium/Low: From agni_score bands
    color_code: Optional[TongueColorCode] = None  # Inferred from severity bands
    coating_thickness: Optional[str] = None  # thin/moderate/thick
    temperature_estimate: Optional[str] = None  # cool/warm/hot
    confidence: Optional[float] = None  # Will be set to severity_score
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """Infer all clinical metadata from severity_score"""
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        
        # Set confidence = severity_score
        if self.confidence is None:
            self.confidence = self.severity_score
        
        # INFER agni_score (inverse relationship)
        # severity 0.0 (healthy) → agni 100 (strong)
        # severity 1.0 (sick) → agni 0 (weak)
        if self.agni_score is None:
            self.agni_score = max(0, min(100, 100 - (self.severity_score * 100)))
        
        # INFER ama_presence from agni score bands
        if self.ama_presence is None:
            if self.agni_score < 30:
                self.ama_presence = AmaPresence.HIGH
            elif self.agni_score < 60:
                self.ama_presence = AmaPresence.MEDIUM
            else:
                self.ama_presence = AmaPresence.LOW
        
        # INFER color_code from severity percentile bands
        if self.color_code is None:
            if self.severity_score < 0.2:
                self.color_code = TongueColorCode.PALE  # Minimal sickness signature
            elif self.severity_score < 0.4:
                self.color_code = TongueColorCode.YELLOW  # Mild inflammation
            elif self.severity_score < 0.7:
                self.color_code = TongueColorCode.WHITE_COATED  # Moderate ama
            else:
                self.color_code = TongueColorCode.RED  # Strong heat/pitta signature
        
        # INFER coating_thickness
        if self.coating_thickness is None:
            if self.ama_presence == AmaPresence.HIGH:
                self.coating_thickness = "thick"
            elif self.ama_presence == AmaPresence.MEDIUM:
                self.coating_thickness = "moderate"
            else:
                self.coating_thickness = "thin"
        
        # INFER temperature_estimate
        if self.temperature_estimate is None:
            if self.severity_score > 0.6:
                self.temperature_estimate = "hot"
            elif self.severity_score > 0.3:
                self.temperature_estimate = "warm"
            else:
                self.temperature_estimate = "cool"
    
    def infer_dosha_tendency(self) -> Dict[str, float]:
        """
        Infer dosha imbalance from tongue characteristics.
        Returns probabilistic distribution.
        """
        dosha_scores = {"vata": 0.0, "pitta": 0.0, "kapha": 0.0}
        
        # Color-based inference
        if self.color_code == TongueColorCode.RED:
            dosha_scores["pitta"] += 0.4
            dosha_scores["vata"] += 0.1
        elif self.color_code == TongueColorCode.PALE:
            dosha_scores["vata"] += 0.4
            dosha_scores["kapha"] += 0.2
        elif self.color_code == TongueColorCode.WHITE_COATED:
            dosha_scores["kapha"] += 0.4
            dosha_scores["vata"] += 0.1
        
        # Ama presence (toxins = Kapha/Vata blockage)
        if self.ama_presence == AmaPresence.HIGH:
            dosha_scores["kapha"] += 0.3
            dosha_scores["vata"] += 0.2
        elif self.ama_presence == AmaPresence.MEDIUM:
            dosha_scores["kapha"] += 0.15
        
        # Agni score (low agni = Kapha/Vata, high agni = Pitta)
        if self.agni_score < 30:
            dosha_scores["kapha"] += 0.2
            dosha_scores["vata"] += 0.1
        elif self.agni_score > 70:
            dosha_scores["pitta"] += 0.2
        
        # Normalize to probabilities
        total = sum(dosha_scores.values())
        if total > 0:
            dosha_scores = {k: v/total for k, v in dosha_scores.items()}
        
        return dosha_scores


@dataclass
class NailVisionOutput:
    """Output from Nail Dhatu Sensor (Vision Model)"""
    texture_score: float  # 0-100: Tissue health
    shape_class: NailShapeClass  # Normal/Clubbing/Pitting etc.
    color_assessment: Optional[str] = None  # Pink/Pale/Yellow
    ridge_pattern: Optional[str] = None  # Smooth/Vertical/Horizontal/Mixed
    white_spots_count: int = 0  # Zinc deficiency markers
    confidence: float = 0.85
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def infer_tissue_issues(self) -> Dict[str, str]:
        """
        Infer tissue (Dhatu) and bone health issues from nails.
        Returns diagnosis suggestions.
        """
        issues = {}
        
        if self.shape_class == NailShapeClass.CLUBBING:
            issues["cardiac_respiratory"] = "Possible heart/lung/liver issue"
        elif self.shape_class == NailShapeClass.PITTING:
            issues["autoimmune"] = "Possible autoimmune/psoriasis condition"
        
        if self.ridge_pattern == "vertical":
            issues["bone_health"] = "Vertical ridges indicate bone tissue malabsorption"
            issues["mineral_deficiency"] = "Low calcium/magnesium"
        elif self.ridge_pattern == "horizontal":
            issues["stress_indicator"] = "Horizontal ridges suggest past systemic stress"
        
        if self.white_spots_count > 3:
            issues["zinc_deficiency"] = f"Multiple white spots ({self.white_spots_count}) suggest zinc deficiency"
        
        if self.texture_score < 30:
            issues["severe_tissue_depletion"] = "Low texture score indicates poor tissue development"
        
        return issues
    
    def infer_dosha_tendency(self) -> Dict[str, float]:
        """Infer dosha from nail characteristics"""
        dosha_scores = {"vata": 0.0, "pitta": 0.0, "kapha": 0.0}
        
        # Ridge patterns indicate Vata (dryness)
        if self.ridge_pattern in ["vertical", "mixed"]:
            dosha_scores["vata"] += 0.3
        
        # Color assessment
        if self.color_assessment == "pale":
            dosha_scores["vata"] += 0.2
        elif self.color_assessment == "yellow":
            dosha_scores["pitta"] += 0.2
        
        # Shape abnormalities often Vata-related
        if self.shape_class in [NailShapeClass.PITTING, NailShapeClass.RIDGES]:
            dosha_scores["vata"] += 0.2
        
        # Low texture = Vata/Kapha depletion
        if self.texture_score < 40:
            dosha_scores["vata"] += 0.15
            dosha_scores["kapha"] += 0.1
        
        # Normalize
        total = sum(dosha_scores.values())
        if total > 0:
            dosha_scores = {k: v/total for k, v in dosha_scores.items()}
        
        return dosha_scores


@dataclass
class ClinicalMetadata:
    """Standardized output combining both vision model results"""
    tongue_output: TongueVisionOutput
    nail_output: NailVisionOutput
    dosha_inference: Dict[str, float]  # Combined probabilistic dosha
    ama_level: str  # High/Medium/Low - key indicator
    tissue_issues: Dict[str, str]
    vision_confidence: float  # Average confidence of both models
    super_prompt_segment: str  # Generated text for RAG super-prompt
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "tongue": asdict(self.tongue_output),
            "nails": asdict(self.nail_output),
            "dosha_inference": self.dosha_inference,
            "ama_level": self.ama_level,
            "tissue_issues": self.tissue_issues,
            "vision_confidence": self.vision_confidence,
            "super_prompt_segment": self.super_prompt_segment,
            "timestamp": self.timestamp
        }


class VisionProcessor:
    """
    Processes raw vision model outputs and creates clinical metadata.
    
    Usage:
        processor = VisionProcessor()
        tongue_data = TongueVisionOutput(agni_score=35, ama_presence="high", color_code="white_coated")
        nail_data = NailVisionOutput(texture_score=40, shape_class="ridges", ridge_pattern="vertical")
        metadata = processor.process(tongue_data, nail_data)
    """
    
    def __init__(self):
        self.ama_thresholds = {
            "high": 70,  # Ama detected + agni < 40
            "medium": 40,
            "low": 0
        }
    
    def process(
        self,
        tongue_output: TongueVisionOutput,
        nail_output: NailVisionOutput
    ) -> ClinicalMetadata:
        """
        Fuse tongue and nail vision outputs into clinical metadata.
        """
        
        # Combine dosha inferences
        tongue_dosha = tongue_output.infer_dosha_tendency()
        nail_dosha = nail_output.infer_dosha_tendency()
        
        combined_dosha = {
            "vata": (tongue_dosha["vata"] + nail_dosha["vata"]) / 2,
            "pitta": (tongue_dosha["pitta"] + nail_dosha["pitta"]) / 2,
            "kapha": (tongue_dosha["kapha"] + nail_dosha["kapha"]) / 2
        }
        
        # Normalize
        total = sum(combined_dosha.values())
        if total > 0:
            combined_dosha = {k: v/total for k, v in combined_dosha.items()}
        
        # Determine Ama level
        ama_level = self._assess_ama_level(tongue_output)
        
        # Get tissue issues
        tissue_issues = nail_output.infer_tissue_issues()
        
        # Generate super-prompt segment
        super_prompt = self._generate_super_prompt(tongue_output, nail_output, ama_level, tissue_issues)
        
        # Average confidence
        avg_confidence = (tongue_output.confidence + nail_output.confidence) / 2
        
        return ClinicalMetadata(
            tongue_output=tongue_output,
            nail_output=nail_output,
            dosha_inference=combined_dosha,
            ama_level=ama_level,
            tissue_issues=tissue_issues,
            vision_confidence=avg_confidence,
            super_prompt_segment=super_prompt
        )
    
    def _assess_ama_level(self, tongue: TongueVisionOutput) -> str:
        """Determine overall Ama (toxin) level"""
        if tongue.ama_presence == AmaPresence.HIGH or tongue.agni_score < 30:
            return "high"
        elif tongue.ama_presence == AmaPresence.MEDIUM or tongue.agni_score < 50:
            return "medium"
        else:
            return "low"
    
    def _generate_super_prompt(
        self,
        tongue: TongueVisionOutput,
        nails: NailVisionOutput,
        ama_level: str,
        tissue_issues: Dict
    ) -> str:
        """Generate the vision findings segment for RAG super-prompt"""
        
        segments = []
        
        # Tongue findings
        segments.append(
            f"Vision Analysis - Tongue: {tongue.color_code.value} color, "
            f"Agni Score {tongue.agni_score}/100 ({self._interpret_agni(tongue.agni_score)}), "
            f"Ama presence: {tongue.ama_presence.value}."
        )
        
        # Nail findings
        nail_finding = f"Nails: {nails.shape_class.value}"
        if nails.ridge_pattern:
            nail_finding += f", {nails.ridge_pattern} ridge pattern"
        nail_finding += f", tissue health score {nails.texture_score}/100."
        segments.append(nail_finding)
        
        # Ama assessment
        segments.append(f"Overall Ama/Toxin Level: {ama_level}")
        
        # Tissue issues
        if tissue_issues:
            issues_str = "; ".join([f"{k}: {v}" for k, v in tissue_issues.items()])
            segments.append(f"Tissue Concerns: {issues_str}")
        
        # Clinical correlation note
        segments.append(
            "IMPORTANT: Correlate these vision findings with patient's text symptoms. "
            "Cross-modal validation required for diagnosis confidence."
        )
        
        return " ".join(segments)
    
    @staticmethod
    def _interpret_agni(score: float) -> str:
        """Interpret Agni score"""
        if score < 25:
            return "Very Weak (Manda)"
        elif score < 50:
            return "Weak (Vishama)"
        elif score < 75:
            return "Normal (Sama)"
        else:
            return "Strong (Tikshna)"


# Example usage and testing
if __name__ == "__main__":
    # Simulate vision model outputs
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
    
    print("Clinical Metadata Generated:")
    print(json.dumps(metadata.to_dict(), indent=2))
