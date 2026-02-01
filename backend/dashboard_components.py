"""
Dashboard Components & Calculations
====================================
Home panel features:
1. News Portal (RSS feed for Ayurveda research)
2. Geo-Dosha (Weather-adjusted dosha imbalance)
3. Future Risks Alert (Predictive disease risk)
4. Dosha Clock (Time-based dosha guidance)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime, time
import requests
from enum import Enum
import math


class DoshaTime(str, Enum):
    """6-hour windows for dosha dominance"""
    KAPHA_MORNING = "kapha_morning"  # 6-10 AM
    PITTA_MIDDAY = "pitta_midday"  # 10 AM - 2 PM
    VATA_EVENING = "vata_evening"  # 2-6 PM
    KAPHA_EVENING = "kapha_evening"  # 6-10 PM
    PITTA_NIGHT = "pitta_night"  # 10 PM - 2 AM
    VATA_NIGHT = "vata_night"  # 2-6 AM


@dataclass
class NewsArticle:
    """Ayurveda research/news item"""
    title: str
    source: str
    url: str
    published_date: str
    snippet: str
    category: str  # Research/News/Clinical Trial


@dataclass
class WeatherData:
    """Local weather for geo-dosha calculation"""
    temperature_c: float
    humidity_percent: float
    wind_speed_kmh: float
    precipitation_mm: float


@dataclass
class GeoDosha:
    """Weather-adjusted dosha imbalance"""
    base_dosha: Dict[str, float]  # Patient's natural dosha
    weather_adjusted_dosha: Dict[str, float]  # After weather adjustment
    environmental_factor: str  # Description of adjustment
    recommendations: List[str]
    adjustment_percentages: Dict[str, float]  # How much each dosha shifted


@dataclass
class FutureRisk:
    """Predicted disease risk based on current state"""
    disease: str
    risk_percentage: float
    timeframe_days: int  # When it might develop
    risk_factors: List[str]  # Why this risk
    prevention_measures: List[str]
    alert_level: str  # Low/Medium/High/Critical


@dataclass
class DoshaClockAdvice:
    """Time-based dosha guidance"""
    current_time: str
    current_dosha_period: DoshaTime
    dosha_description: str
    recommended_activities: List[str]
    foods_to_eat: List[str]
    foods_to_avoid: List[str]
    yoga_asanas: List[str]
    ayurveda_principle: str


class GeoDoshaCalculator:
    """
    Calculates weather-adjusted dosha imbalance.
    
    Logic: If Weather = Cold/Wet → +10% Kapha
    """
    
    @staticmethod
    def calculate(
        base_dosha: Dict[str, float],
        weather: WeatherData
    ) -> GeoDosha:
        """Adjust dosha based on weather conditions"""
        
        adjusted = base_dosha.copy()
        adjustments = {"vata": 0.0, "pitta": 0.0, "kapha": 0.0}
        
        # Temperature impact
        if weather.temperature_c < 10:  # Cold
            adjustments["vata"] += 0.05
            adjustments["kapha"] += 0.05
        elif weather.temperature_c > 35:  # Hot
            adjustments["pitta"] += 0.10
        
        # Humidity impact
        if weather.humidity_percent > 70:  # Wet
            adjustments["kapha"] += 0.10
            adjustments["pitta"] -= 0.05
        elif weather.humidity_percent < 30:  # Dry
            adjustments["vata"] += 0.10
        
        # Wind impact
        if weather.wind_speed_kmh > 25:  # Windy
            adjustments["vata"] += 0.08
        
        # Precipitation impact
        if weather.precipitation_mm > 5:  # Rainy
            adjustments["kapha"] += 0.05
            adjustments["vata"] += 0.05
        
        # Apply adjustments
        for dosha, adj in adjustments.items():
            adjusted[dosha] = min(adjusted[dosha] + adj, 1.0)
        
        # Renormalize
        total = sum(adjusted.values())
        if total > 0:
            adjusted = {k: v/total for k, v in adjusted.items()}
        
        # Environmental description
        env_factors = []
        if weather.temperature_c < 10:
            env_factors.append("Cold temperature increases Vata and Kapha")
        elif weather.temperature_c > 35:
            env_factors.append("Hot weather increases Pitta")
        
        if weather.humidity_percent > 70:
            env_factors.append("High humidity increases Kapha")
        elif weather.humidity_percent < 30:
            env_factors.append("Dry air increases Vata")
        
        if weather.wind_speed_kmh > 25:
            env_factors.append("Strong winds increase Vata")
        
        env_description = "; ".join(env_factors) if env_factors else "Neutral weather conditions"
        
        # Recommendations
        recommendations = []
        if adjusted["vata"] > 0.4:
            recommendations.append("Increase warm, oily foods to balance Vata")
        if adjusted["pitta"] > 0.4:
            recommendations.append("Favor cooling foods and avoid excess sun")
        if adjusted["kapha"] > 0.4:
            recommendations.append("Increase warm, light foods and vigorous exercise")
        
        return GeoDosha(
            base_dosha=base_dosha,
            weather_adjusted_dosha=adjusted,
            environmental_factor=env_description,
            recommendations=recommendations,
            adjustment_percentages=adjustments
        )


class FutureRiskPredictor:
    """
    Algorithmic look-ahead for disease risks.
    
    Logic: If Current_State = "High Ama" AND History = "Joint Pain"
    → Risk = "Rheumatoid Arthritis (80% Probability)"
    """
    
    RISK_PATTERNS = [
        {
            "condition": "High Ama + Joint Pain",
            "disease": "Amavata (Rheumatoid Arthritis)",
            "base_risk": 0.80,
            "factors": ["ama_high", "joint_pain"],
            "timeframe": 30,
            "prevention": ["Digestive support", "Anti-Ama diet", "Gentle exercise"]
        },
        {
            "condition": "High Pitta + Stress",
            "disease": "Hypertension",
            "base_risk": 0.65,
            "factors": ["pitta_high", "stress_high"],
            "timeframe": 60,
            "prevention": ["Cooling diet", "Stress management", "Regular yoga"]
        },
        {
            "condition": "High Kapha + Sedentary",
            "disease": "Type 2 Diabetes",
            "base_risk": 0.70,
            "factors": ["kapha_high", "sedentary"],
            "timeframe": 90,
            "prevention": ["Vigorous exercise", "Light diet", "Warming spices"]
        },
        {
            "condition": "High Vata + Anxiety",
            "disease": "Neurological Disorder",
            "base_risk": 0.55,
            "factors": ["vata_high", "anxiety_high"],
            "timeframe": 45,
            "prevention": ["Grounding herbs", "Oil massage", "Meditation"]
        },
        {
            "condition": "High Ama + Indigestion",
            "disease": "Autoimmune Disease",
            "base_risk": 0.60,
            "factors": ["ama_high", "digestion_poor"],
            "timeframe": 180,
            "prevention": ["Panchakarma", "Probiotic herbs", "Healing foods"]
        }
    ]
    
    @staticmethod
    def predict(
        current_state: Dict[str, any],
        history: List[str],
        dosha_profile: Dict[str, float]
    ) -> List[FutureRisk]:
        """
        Predict future disease risks based on current state.
        
        Args:
            current_state: {"ama": "high", "stress": "high", ...}
            history: ["Joint Pain", "Acid Reflux", ...]
            dosha_profile: {"vata": 0.3, "pitta": 0.6, "kapha": 0.1}
        
        Returns:
            Sorted list of FutureRisk, highest risk first
        """
        
        risks = []
        
        for pattern in FutureRiskPredictor.RISK_PATTERNS:
            # Check if factors match
            matching_factors = 0
            for factor in pattern["factors"]:
                if factor == "ama_high" and current_state.get("ama_level") == "high":
                    matching_factors += 1
                elif factor == "stress_high" and current_state.get("stress_level") == "High":
                    matching_factors += 1
                elif factor == "pitta_high" and dosha_profile.get("pitta", 0) > 0.4:
                    matching_factors += 1
                elif factor == "kapha_high" and dosha_profile.get("kapha", 0) > 0.4:
                    matching_factors += 1
                elif factor == "vata_high" and dosha_profile.get("vata", 0) > 0.4:
                    matching_factors += 1
                elif factor == "joint_pain" and "Joint Pain" in history:
                    matching_factors += 1
                elif factor == "digestion_poor" and current_state.get("digestion_quality") == "Poor":
                    matching_factors += 1
                elif factor == "sedentary" and current_state.get("exercise_frequency", 0) < 2:
                    matching_factors += 1
                elif factor == "anxiety_high" and current_state.get("anxiety_level", "Low") == "High":
                    matching_factors += 1
            
            # Calculate risk based on factor matches
            if matching_factors > 0:
                risk_percentage = pattern["base_risk"] * (matching_factors / len(pattern["factors"]))
                
                alert_level = "Critical" if risk_percentage > 0.75 else \
                              "High" if risk_percentage > 0.60 else \
                              "Medium" if risk_percentage > 0.40 else "Low"
                
                risks.append(FutureRisk(
                    disease=pattern["disease"],
                    risk_percentage=risk_percentage * 100,
                    timeframe_days=pattern["timeframe"],
                    risk_factors=[f.replace("_", " ").title() for f in pattern["factors"] if matching_factors > 0],
                    prevention_measures=pattern["prevention"],
                    alert_level=alert_level
                ))
        
        # Sort by risk percentage
        risks.sort(key=lambda x: x.risk_percentage, reverse=True)
        
        return risks[:3]  # Top 3 risks


class DoshaClockCalculator:
    """
    Time-based dosha guidance (Dosha Clock).
    Different doshas dominate different times of day.
    """
    
    DOSHA_PERIODS = [
        {
            "period": DoshaTime.KAPHA_MORNING,
            "hours": (6, 10),
            "dosha": "Kapha",
            "description": "Earth energy - Heavy, slow, grounding time",
            "activities": ["Vigorous exercise", "Cold water bath", "Dynamic work"],
            "foods": ["Warm spices", "Light grains", "Honey"],
            "avoid": ["Heavy foods", "Sleeping in", "Cold items"],
            "asanas": ["Surya Namaskar", "Warrior poses", "Jump squats"],
            "principle": "Combat Kapha heaviness with activity"
        },
        {
            "period": DoshaTime.PITTA_MIDDAY,
            "hours": (10, 14),
            "dosha": "Pitta",
            "description": "Fire energy - Bright, hot, transformative time",
            "activities": ["Main meal", "Important work", "Study"],
            "foods": ["Cooling herbs", "Ghee", "Sweet/bitter tastes"],
            "avoid": ["Spicy foods", "Excessive sun", "Stimulating drinks"],
            "asanas": ["Moon poses", "Cooling twists", "Seated forward folds"],
            "principle": "Eat your largest meal now - Pitta fires digestion"
        },
        {
            "period": DoshaTime.VATA_EVENING,
            "hours": (14, 18),
            "dosha": "Vata",
            "description": "Wind/Air energy - Mobile, light, creative time",
            "activities": ["Creative work", "Walking", "Social time"],
            "foods": ["Warm, grounding foods", "Sesame", "Roots"],
            "avoid": ["Cold foods", "Rushing", "Caffeine"],
            "asanas": ["Grounding poses", "Child's pose", "Hip openers"],
            "principle": "Ground Vata with warm, nourishing foods"
        },
        {
            "period": DoshaTime.KAPHA_EVENING,
            "hours": (18, 22),
            "dosha": "Kapha",
            "description": "Earth energy (evening) - Settling, calming",
            "activities": ["Light dinner", "Reflection", "Family time"],
            "foods": ["Warm spices", "Light dinner", "Herbal tea"],
            "avoid": ["Heavy meals", "Sugar", "TV before bed"],
            "asanas": ["Gentle stretches", "Meditation", "Relaxation"],
            "principle": "Light dinner and early sleep"
        },
        {
            "period": DoshaTime.PITTA_NIGHT,
            "hours": (22, 2),
            "dosha": "Pitta",
            "description": "Fire energy (night) - Cellular metabolism, healing",
            "activities": ["Sleep", "Recovery", "Repair"],
            "foods": ["Deep sleep - fasting"],
            "avoid": ["Eating", "Stimulation", "Work"],
            "asanas": ["Sleep"],
            "principle": "Sleep for cellular rejuvenation"
        },
        {
            "period": DoshaTime.VATA_NIGHT,
            "hours": (2, 6),
            "dosha": "Vata",
            "description": "Wind/Air energy (night) - Subtle, creative dreams",
            "activities": ["Deep sleep", "Dreams", "Intuition"],
            "foods": ["Fasting"],
            "avoid": ["Waking", "Disturbance"],
            "asanas": ["Sleep"],
            "principle": "Complete sleep for rest"
        }
    ]
    
    @staticmethod
    def get_current_advice(user_dosha: Dict[str, float]) -> DoshaClockAdvice:
        """Get dosha guidance for current hour"""
        
        now = datetime.now()
        current_hour = now.hour
        
        # Find current period
        current_period = None
        for period in DoshaClockCalculator.DOSHA_PERIODS:
            start, end = period["hours"]
            if start <= current_hour < end or (end == 6 and current_hour >= start):
                current_period = period
                break
        
        if not current_period:
            current_period = DoshaClockCalculator.DOSHA_PERIODS[0]
        
        return DoshaClockAdvice(
            current_time=now.strftime("%H:%M"),
            current_dosha_period=current_period["period"],
            dosha_description=current_period["description"],
            recommended_activities=current_period["activities"],
            foods_to_eat=current_period["foods"],
            foods_to_avoid=current_period["avoid"],
            yoga_asanas=current_period["asanas"],
            ayurveda_principle=current_period["principle"]
        )


class NewsPortalFetcher:
    """Fetch Ayurveda research news"""
    
    @staticmethod
    def fetch_news(keywords: List[str] = None) -> List[NewsArticle]:
        """
        Fetch Ayurveda news from various sources.
        In production, this would query RSS feeds or APIs.
        For now, returns sample data.
        """
        
        if keywords is None:
            keywords = ["Ayurveda", "Herbal medicine", "Ayurvedic research", "Traditional medicine"]
        
        # Sample news items (in production, these come from RSS/APIs)
        sample_news = [
            {
                "title": "New Study: Turmeric Shows Promise in Joint Inflammation",
                "source": "Ayurveda Today",
                "url": "https://example.com/turmeric-study",
                "published_date": "2026-01-28",
                "snippet": "Recent clinical trials demonstrate curcumin's effectiveness in reducing rheumatoid arthritis symptoms...",
                "category": "Research"
            },
            {
                "title": "Ayurvedic Approach to Winter Wellness Gaining Popularity",
                "source": "Global Health News",
                "url": "https://example.com/winter-wellness",
                "published_date": "2026-01-27",
                "snippet": "Seasonal Ayurvedic practices show measurable health benefits in cold climates...",
                "category": "News"
            },
            {
                "title": "Clinical Trial: Ashwagandha for Stress Management",
                "source": "Medical Research Weekly",
                "url": "https://example.com/ashwagandha-trial",
                "published_date": "2026-01-25",
                "snippet": "Double-blind study confirms adaptogenic properties of Withania somnifera...",
                "category": "Clinical Trial"
            }
        ]
        
        return [NewsArticle(**item) for item in sample_news]


# Example usage
if __name__ == "__main__":
    # Test Geo-Dosha
    base_dosha = {"vata": 0.3, "pitta": 0.4, "kapha": 0.3}
    weather = WeatherData(
        temperature_c=8,
        humidity_percent=75,
        wind_speed_kmh=30,
        precipitation_mm=10
    )
    
    geo_dosha = GeoDoshaCalculator.calculate(base_dosha, weather)
    print("Geo-Dosha Result:")
    print(f"  Base: {base_dosha}")
    print(f"  Adjusted: {geo_dosha.weather_adjusted_dosha}")
    print(f"  Factor: {geo_dosha.environmental_factor}")
    print()
    
    # Test Future Risk
    current_state = {"ama_level": "high", "stress_level": "High"}
    history = ["Joint Pain"]
    risks = FutureRiskPredictor.predict(current_state, history, base_dosha)
    print("Future Risks:")
    for risk in risks:
        print(f"  {risk.disease}: {risk.risk_percentage:.1f}% ({risk.alert_level})")
    print()
    
    # Test Dosha Clock
    advice = DoshaClockCalculator.get_current_advice(base_dosha)
    print(f"Dosha Clock at {advice.current_time}:")
    print(f"  Period: {advice.dosha_description}")
    print(f"  Activities: {', '.join(advice.recommended_activities)}")
    print()
    
    # Test News
    news = NewsPortalFetcher.fetch_news()
    print(f"Latest Ayurveda News ({len(news)} items):")
    for article in news:
        print(f"  [{article.category}] {article.title}")
