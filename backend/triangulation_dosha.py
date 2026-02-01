"""
Triangulation Dosha Inference
==============================
Auto-detect patient's Dosha WITHOUT a 50-question quiz.
Uses three modalities: Visual (Akriti), Semantic (Shabda), Biological (Jivha).

Result: Probabilistic Dosha (e.g., "60% Pitta, 40% Vata")
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List
import re
from enum import Enum


class TypingStyle(str, Enum):
    """Inferred from patient's text input"""
    SHORT_URGENT = "short_urgent"  # Pitta: Quick, action-focused, typos from haste
    WANDERING_ANXIOUS = "wandering_anxious"  # Vata: Long, scattered, anxious language
    SLOW_POLITE = "slow_polite"  # Kapha: Methodical, repetitive, overly polite


class BodyFrame(str, Enum):
    """Body type classification"""
    THIN_LANKY = "thin_lanky"  # Vata
    MEDIUM_MUSCULAR = "medium_muscular"  # Pitta
    BROAD_HEAVY = "broad_heavy"  # Kapha


@dataclass
class TriangulationResult:
    """Output: Probabilistic Dosha assessment"""
    visual_dosha: Dict[str, float]  # From body frame
    semantic_dosha: Dict[str, float]  # From text style
    biological_dosha: Dict[str, float]  # From tongue/nails
    final_dosha: Dict[str, float]  # Weighted average
    dominant_dosha: str  # Vata/Pitta/Kapha
    secondary_dosha: Optional[str]  # If > 30%
    confidence: float  # How certain (0-1)
    reasoning: str  # Explanation for user


class TriangulationInference:
    """
    Three-point inference system for Dosha determination.
    No quiz required - uses actual clinical data.
    """
    
    def __init__(self):
        self.weights = {
            "visual": 0.35,  # Body frame
            "semantic": 0.25,  # Text analysis
            "biological": 0.40  # Vision models (tongue/nails)
        }
    
    def infer(
        self,
        height_cm: float,
        weight_kg: float,
        text_input: str,
        vision_dosha: Dict[str, float]  # From VisionProcessor
    ) -> TriangulationResult:
        """
        Main inference method.
        Combines all three modalities for dosha determination.
        """
        
        # Point 1: Visual (Akriti) - Body Frame
        visual_dosha = self._analyze_body_frame(height_cm, weight_kg)
        
        # Point 2: Semantic (Shabda) - Text Style
        semantic_dosha = self._analyze_typing_style(text_input)
        
        # Point 3: Biological (Jivha) - Vision Models
        biological_dosha = vision_dosha
        
        # Weighted average
        final_dosha = self._weighted_average(
            visual_dosha,
            semantic_dosha,
            biological_dosha
        )
        
        # Determine dominant and secondary
        sorted_doshas = sorted(final_dosha.items(), key=lambda x: x[1], reverse=True)
        dominant = sorted_doshas[0][0]
        secondary = sorted_doshas[1][0] if sorted_doshas[1][1] > 0.25 else None
        
        # Calculate confidence
        confidence = self._calculate_confidence(visual_dosha, semantic_dosha, biological_dosha)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            visual_dosha, semantic_dosha, biological_dosha,
            TypingStyle(self._classify_typing_style(text_input)),
            BodyFrame(self._classify_body_frame(height_cm, weight_kg))
        )
        
        return TriangulationResult(
            visual_dosha=visual_dosha,
            semantic_dosha=semantic_dosha,
            biological_dosha=biological_dosha,
            final_dosha=final_dosha,
            dominant_dosha=dominant,
            secondary_dosha=secondary,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _analyze_body_frame(self, height_cm: float, weight_kg: float) -> Dict[str, float]:
        """
        Analyze body frame for Dosha.
        Vata: Thin, light, irregular features
        Pitta: Medium, muscular, proportional
        Kapha: Broad, heavy, rounded
        """
        
        # Calculate BMI
        bmi = weight_kg / ((height_cm / 100) ** 2)
        
        # Classify frame
        if bmi < 19:
            frame = BodyFrame.THIN_LANKY
            return {"vata": 0.6, "pitta": 0.25, "kapha": 0.15}
        elif bmi < 25:
            frame = BodyFrame.MEDIUM_MUSCULAR
            return {"vata": 0.2, "pitta": 0.6, "kapha": 0.2}
        else:
            frame = BodyFrame.BROAD_HEAVY
            return {"vata": 0.15, "pitta": 0.25, "kapha": 0.6}
    
    def _analyze_typing_style(self, text_input: str) -> Dict[str, float]:
        """
        Analyze patient's text for Dosha tendencies.
        
        Pitta: Short, urgent, action-oriented, typos/incomplete words
        Vata: Long, wandering, anxious, repetitive, uncertain language
        Kapha: Slow, methodical, polite, detailed but structured
        """
        
        style = self._classify_typing_style(text_input)
        
        if style == TypingStyle.SHORT_URGENT:
            return {"vata": 0.1, "pitta": 0.7, "kapha": 0.2}
        elif style == TypingStyle.WANDERING_ANXIOUS:
            return {"vata": 0.65, "pitta": 0.15, "kapha": 0.2}
        else:  # SLOW_POLITE
            return {"vata": 0.2, "pitta": 0.2, "kapha": 0.6}
    
    def _classify_typing_style(self, text: str) -> str:
        """Classify text into one of three styles"""
        
        # Normalize
        text_lower = text.lower()
        word_count = len(text.split())
        
        # Count indicators
        pitta_indicators = 0
        vata_indicators = 0
        kapha_indicators = 0
        
        # PITTA indicators: Short, urgent, direct
        if word_count < 50:
            pitta_indicators += 2
        if any(word in text_lower for word in ["urgent", "hurry", "quick", "need", "must", "asap"]):
            pitta_indicators += 2
        if text.count("!") > 2:  # Exclamation marks
            pitta_indicators += 1
        if sum(1 for c in text if c.isupper()) > word_count * 0.15:  # Many caps
            pitta_indicators += 1
        typo_count = self._estimate_typos(text)
        if typo_count > 3:
            pitta_indicators += 1
        
        # VATA indicators: Long, wandering, anxious
        if word_count > 100:
            vata_indicators += 2
        if any(word in text_lower for word in ["worried", "anxious", "uncertain", "maybe", "perhaps", "might", "could", "confused"]):
            vata_indicators += 2
        if text.count("...") > 1 or text.count("?") > 3:  # Uncertainty markers
            vata_indicators += 1
        if len([word for word in text.split() if len(word) > 15]) > 2:  # Long, complex words
            vata_indicators += 1
        if text.count(",") > word_count / 10:  # Many commas (scattered thoughts)
            vata_indicators += 1
        
        # KAPHA indicators: Slow, methodical, polite
        if any(word in text_lower for word in ["please", "kindly", "thank you", "appreciate", "humble"]):
            kapha_indicators += 2
        if text.count(";") > 0:  # Structured writing
            kapha_indicators += 1
        if word_count > 80 and text.count("\n") > 2:  # Organized sections
            kapha_indicators += 1
        if len([word for word in text.split() if len(word) > 12]) > 3:  # Formal vocabulary
            kapha_indicators += 1
        
        # Determine style
        if pitta_indicators >= vata_indicators and pitta_indicators >= kapha_indicators:
            return TypingStyle.SHORT_URGENT
        elif vata_indicators >= kapha_indicators:
            return TypingStyle.WANDERING_ANXIOUS
        else:
            return TypingStyle.SLOW_POLITE
    
    def _classify_body_frame(self, height_cm: float, weight_kg: float) -> str:
        """Classify body frame"""
        bmi = weight_kg / ((height_cm / 100) ** 2)
        if bmi < 19:
            return BodyFrame.THIN_LANKY
        elif bmi < 25:
            return BodyFrame.MEDIUM_MUSCULAR
        else:
            return BodyFrame.BROAD_HEAVY
    
    def _estimate_typos(self, text: str) -> int:
        """Rough typo estimation"""
        # Look for incomplete words or obvious spelling errors
        typo_pattern = r'\b[a-z]+[A-Z]|[A-Z]{2,}\b|[a-z]*[A-Z][a-z]*[A-Z]'
        typos = len(re.findall(typo_pattern, text))
        return typos
    
    def _weighted_average(
        self,
        visual: Dict[str, float],
        semantic: Dict[str, float],
        biological: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate weighted average of three dosha scores"""
        
        result = {
            "vata": (
                visual["vata"] * self.weights["visual"] +
                semantic["vata"] * self.weights["semantic"] +
                biological["vata"] * self.weights["biological"]
            ),
            "pitta": (
                visual["pitta"] * self.weights["visual"] +
                semantic["pitta"] * self.weights["semantic"] +
                biological["pitta"] * self.weights["biological"]
            ),
            "kapha": (
                visual["kapha"] * self.weights["visual"] +
                semantic["kapha"] * self.weights["semantic"] +
                biological["kapha"] * self.weights["biological"]
            )
        }
        
        # Normalize
        total = sum(result.values())
        if total > 0:
            result = {k: v/total for k, v in result.items()}
        
        return result
    
    def _calculate_confidence(
        self,
        visual: Dict[str, float],
        semantic: Dict[str, float],
        biological: Dict[str, float]
    ) -> float:
        """
        Confidence is HIGH when all three modalities agree.
        Confidence is LOW when they disagree.
        """
        
        # Get dominant for each
        visual_dom = max(visual, key=visual.get)
        semantic_dom = max(semantic, key=semantic.get)
        biological_dom = max(biological, key=biological.get)
        
        # Check agreement
        agreements = sum([
            visual_dom == semantic_dom,
            visual_dom == biological_dom,
            semantic_dom == biological_dom
        ])
        
        # Base confidence on agreement
        confidence_base = 0.5 + (agreements / 3) * 0.35
        
        # Boost if dominant is strong (>50%)
        all_doms = [visual[visual_dom], semantic[semantic_dom], biological[biological_dom]]
        avg_strength = sum(all_doms) / 3
        confidence_base += min(max(avg_strength - 0.5, 0) * 0.15, 0.15)
        
        return min(confidence_base, 1.0)
    
    def _generate_reasoning(
        self,
        visual: Dict[str, float],
        semantic: Dict[str, float],
        biological: Dict[str, float],
        typing_style: TypingStyle,
        body_frame: BodyFrame
    ) -> str:
        """Generate explanation for the user"""
        
        reasons = []
        
        # Visual explanation
        reasons.append(f"Body Frame: Your {body_frame.value} frame suggests {max(visual, key=visual.get).title()} tendency.")
        
        # Semantic explanation
        style_descriptions = {
            TypingStyle.SHORT_URGENT: "Your direct, action-oriented communication style indicates Pitta quality",
            TypingStyle.WANDERING_ANXIOUS: "Your wandering, uncertain communication style indicates Vata quality",
            TypingStyle.SLOW_POLITE: "Your methodical, polite communication style indicates Kapha quality"
        }
        reasons.append(style_descriptions[typing_style])
        
        # Biological explanation
        bio_dom = max(biological, key=biological.get)
        reasons.append(f"Vision Analysis: Tongue and nail findings confirm {bio_dom.title()} dominance.")
        
        # Consensus
        final_dom = max({
            "vata": visual["vata"] + semantic["vata"] + biological["vata"],
            "pitta": visual["pitta"] + semantic["pitta"] + biological["pitta"],
            "kapha": visual["kapha"] + semantic["kapha"] + biological["kapha"]
        }, key=lambda x: {
            "vata": visual["vata"] + semantic["vata"] + biological["vata"],
            "pitta": visual["pitta"] + semantic["pitta"] + biological["pitta"],
            "kapha": visual["kapha"] + semantic["kapha"] + biological["kapha"]
        }[x])
        
        reasons.append(f"Consensus: Your constitution is predominantly {final_dom.title()} with balanced influences.")
        
        return " ".join(reasons)


# Example usage
if __name__ == "__main__":
    inference = TriangulationInference()
    
    text_input = (
        "Hi, I'm very worried and confused about my joint pain. "
        "It's been happening for a while now, and I'm not sure what's causing it. "
        "Sometimes it gets better, sometimes worse. Maybe it's the weather? "
        "I'm also concerned about other symptoms..."
    )
    
    vision_dosha = {"vata": 0.5, "pitta": 0.2, "kapha": 0.3}  # From VisionProcessor
    
    result = inference.infer(
        height_cm=165,
        weight_kg=55,
        text_input=text_input,
        vision_dosha=vision_dosha
    )
    
    print("=== TRIANGULATION DOSHA RESULT ===\n")
    print(f"Visual (Body Frame): {result.visual_dosha}")
    print(f"Semantic (Typing Style): {result.semantic_dosha}")
    print(f"Biological (Vision): {result.biological_dosha}")
    print(f"\nFinal Dosha Distribution: {result.final_dosha}")
    print(f"\nDominant: {result.dominant_dosha.upper()}")
    if result.secondary_dosha:
        print(f"Secondary: {result.secondary_dosha.upper()}")
    print(f"Confidence: {result.confidence*100:.1f}%")
    print(f"\nReasoning:\n{result.reasoning}")
