"""
Disease Risk Mapper
====================
Pre-processes the AyurGenixAI dataset into structured risk mappings for 
efficient disease prediction based on user health profiles.

This module creates:
1. Disease-to-Dosha mappings
2. Symptom-to-Disease mappings
3. Risk factor correlations
4. Age/Gender specific risk profiles
5. Lifestyle-to-Disease correlations
"""

import os
import csv
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DiseaseProfile:
    """Complete disease profile from AyurGenixAI dataset"""
    name: str
    hindi_name: str
    marathi_name: str
    
    # Symptoms & Diagnosis
    symptoms: List[str]
    diagnosis_tests: List[str]
    severity: str
    duration: str
    
    # Risk Factors
    risk_factors: List[str]
    environmental_factors: List[str]
    family_history_relevant: bool
    family_history_conditions: List[str]
    
    # Dosha Information
    doshas_involved: List[str]
    prakriti_association: str
    
    # Demographics
    age_group: str
    gender_preference: str
    occupation_lifestyle: str
    
    # Lifestyle Factors
    dietary_triggers: List[str]
    sleep_pattern_impact: str
    stress_impact: str
    physical_activity_level: str
    
    # Seasonal
    seasonal_variation: List[str]
    
    # Allergies
    allergies_related: List[str]
    
    # Ayurvedic Treatment
    ayurvedic_herbs: List[str]
    formulation: str
    diet_lifestyle_recommendations: str
    yoga_therapy: List[str]
    
    # Medical
    medical_intervention: str
    prevention: str
    prognosis: str
    complications: List[str]
    patient_recommendations: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class RiskProfile:
    """Risk profile for a specific condition"""
    disease_name: str
    base_risk_score: float  # 0.0 - 1.0
    
    # Contributing factors
    dosha_factors: Dict[str, float]  # dosha -> contribution weight
    age_factor: float
    gender_factor: float
    bmi_factor: float
    lifestyle_factor: float
    family_history_factor: float
    symptom_match_factor: float
    
    # Time-based probabilities
    probability_6_months: float = 0.0
    probability_1_year: float = 0.0
    probability_5_years: float = 0.0
    
    # Prevention info
    preventive_measures: List[str] = field(default_factory=list)
    early_warning_signs: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# DISEASE RISK MAPPER
# ═══════════════════════════════════════════════════════════════════════════════

class DiseaseRiskMapper:
    """
    Maps diseases to risk factors and creates lookup structures for
    efficient risk prediction.
    """
    
    def __init__(self, csv_path: str = None):
        self.csv_path = csv_path or self._find_csv_path()
        self.diseases: Dict[str, DiseaseProfile] = {}
        
        # Lookup indices
        self.symptom_to_diseases: Dict[str, List[str]] = defaultdict(list)
        self.dosha_to_diseases: Dict[str, List[str]] = defaultdict(list)
        self.risk_factor_to_diseases: Dict[str, List[str]] = defaultdict(list)
        self.age_group_diseases: Dict[str, List[str]] = defaultdict(list)
        self.lifestyle_to_diseases: Dict[str, List[str]] = defaultdict(list)
        self.family_history_diseases: Dict[str, List[str]] = defaultdict(list)
        
        # BMI correlations
        self.obesity_related_diseases: List[str] = []
        self.underweight_related_diseases: List[str] = []
        
        # Chronic vs Acute
        self.chronic_diseases: List[str] = []
        self.acute_diseases: List[str] = []
        
        # Severity mapping
        self.severe_diseases: List[str] = []
        self.mild_diseases: List[str] = []
        
        # Load and index
        if self.csv_path and os.path.exists(self.csv_path):
            self._load_from_csv()
            self._build_indices()
    
    def _find_csv_path(self) -> Optional[str]:
        """Find the AyurGenixAI dataset"""
        possible_paths = [
            "./databases&embeddings/AyurGenixAI_Dataset.csv",
            "../databases&embeddings/AyurGenixAI_Dataset.csv",
            "AyurGenixAI_Dataset.csv"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _parse_list(self, value: str) -> List[str]:
        """Parse comma-separated values into list"""
        if not value or value.strip() == "":
            return []
        # Split by comma and clean
        items = [item.strip() for item in value.split(",")]
        return [item for item in items if item]
    
    def _load_from_csv(self):
        """Load disease profiles from CSV"""
        print(f"📊 Loading disease data from {self.csv_path}...")
        
        # Use newline='' for proper CSV handling and utf-8-sig to handle BOM
        with open(self.csv_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    disease_name = row.get('Disease', '').strip()
                    if not disease_name:
                        continue
                    
                    # Parse family history
                    family_hist = row.get('Family History', '')
                    has_family_history = bool(family_hist and family_hist.strip())
                    
                    profile = DiseaseProfile(
                        name=disease_name,
                        hindi_name=row.get('Hindi Name', ''),
                        marathi_name=row.get('Marathi Name', ''),
                        symptoms=self._parse_list(row.get('Symptoms', '')),
                        diagnosis_tests=self._parse_list(row.get('Diagnosis & Tests', '')),
                        severity=row.get('Symptom Severity', 'Moderate'),
                        duration=row.get('Duration of Treatment', ''),
                        risk_factors=self._parse_list(row.get('Risk Factors', '')),
                        environmental_factors=self._parse_list(row.get('Environmental Factors', '')),
                        family_history_relevant=has_family_history,
                        family_history_conditions=self._parse_list(family_hist),
                        doshas_involved=self._parse_list(row.get('Doshas', '')),
                        prakriti_association=row.get('Constitution/Prakriti', ''),
                        age_group=row.get('Age Group', 'All ages'),
                        gender_preference=row.get('Gender', 'Both genders'),
                        occupation_lifestyle=row.get('Occupation and Lifestyle', ''),
                        dietary_triggers=self._parse_list(row.get('Dietary Habits', '')),
                        sleep_pattern_impact=row.get('Sleep Patterns', ''),
                        stress_impact=row.get('Stress Levels', ''),
                        physical_activity_level=row.get('Physical Activity Levels', ''),
                        seasonal_variation=self._parse_list(row.get('Seasonal Variation', '')),
                        allergies_related=self._parse_list(row.get('Allergies (Food/Env)', '')),
                        ayurvedic_herbs=self._parse_list(row.get('Ayurvedic Herbs', '')),
                        formulation=row.get('Formulation', ''),
                        diet_lifestyle_recommendations=row.get('Diet and Lifestyle Recommendations', ''),
                        yoga_therapy=self._parse_list(row.get('Yoga & Physical Therapy', '')),
                        medical_intervention=row.get('Medical Intervention', ''),
                        prevention=row.get('Prevention', ''),
                        prognosis=row.get('Prognosis', ''),
                        complications=self._parse_list(row.get('Complications', '')),
                        patient_recommendations=row.get('Patient Recommendations', '')
                    )
                    
                    self.diseases[disease_name.lower()] = profile
                    
                except Exception as e:
                    print(f"   ⚠ Error parsing row: {e}")
                    continue
        
        print(f"   ✓ Loaded {len(self.diseases)} disease profiles")
    
    def _build_indices(self):
        """Build lookup indices for fast querying"""
        print("📇 Building risk indices...")
        
        for disease_name, profile in self.diseases.items():
            # Symptom index
            for symptom in profile.symptoms:
                symptom_lower = symptom.lower().strip()
                self.symptom_to_diseases[symptom_lower].append(disease_name)
            
            # Dosha index
            for dosha in profile.doshas_involved:
                dosha_lower = dosha.lower().strip()
                self.dosha_to_diseases[dosha_lower].append(disease_name)
            
            # Risk factor index
            for rf in profile.risk_factors:
                rf_lower = rf.lower().strip()
                self.risk_factor_to_diseases[rf_lower].append(disease_name)
            
            # Age group index
            age_group = profile.age_group.lower()
            self.age_group_diseases[age_group].append(disease_name)
            
            # Lifestyle index
            lifestyle = profile.occupation_lifestyle.lower()
            if 'sedentary' in lifestyle:
                self.lifestyle_to_diseases['sedentary'].append(disease_name)
            if 'stress' in lifestyle or 'high stress' in profile.stress_impact.lower():
                self.lifestyle_to_diseases['high_stress'].append(disease_name)
            if 'active' in lifestyle:
                self.lifestyle_to_diseases['active'].append(disease_name)
            
            # Family history index
            if profile.family_history_relevant:
                for condition in profile.family_history_conditions:
                    cond_lower = condition.lower().strip()
                    self.family_history_diseases[cond_lower].append(disease_name)
            
            # BMI-related classification
            risk_factors_lower = ' '.join(profile.risk_factors).lower()
            if 'obesity' in risk_factors_lower or 'overweight' in risk_factors_lower:
                self.obesity_related_diseases.append(disease_name)
            if 'underweight' in risk_factors_lower or 'malnutrition' in risk_factors_lower:
                self.underweight_related_diseases.append(disease_name)
            
            # Duration-based classification
            duration_lower = profile.duration.lower()
            if 'lifelong' in duration_lower or 'lifetime' in duration_lower or 'chronic' in duration_lower:
                self.chronic_diseases.append(disease_name)
            else:
                self.acute_diseases.append(disease_name)
            
            # Severity classification
            severity_lower = profile.severity.lower()
            if 'severe' in severity_lower:
                self.severe_diseases.append(disease_name)
            elif 'mild' in severity_lower:
                self.mild_diseases.append(disease_name)
        
        print(f"   ✓ Indexed {len(self.symptom_to_diseases)} symptom mappings")
        print(f"   ✓ Indexed {len(self.dosha_to_diseases)} dosha mappings")
        print(f"   ✓ Found {len(self.chronic_diseases)} chronic conditions")
        print(f"   ✓ Found {len(self.obesity_related_diseases)} obesity-related conditions")
    
    def get_diseases_by_symptoms(self, symptoms: List[str]) -> Dict[str, int]:
        """Get diseases matching given symptoms with match count"""
        disease_scores = defaultdict(int)
        
        for symptom in symptoms:
            symptom_lower = symptom.lower().strip()
            # Direct match
            for disease in self.symptom_to_diseases.get(symptom_lower, []):
                disease_scores[disease] += 2
            # Partial match
            for indexed_symptom, diseases in self.symptom_to_diseases.items():
                if symptom_lower in indexed_symptom or indexed_symptom in symptom_lower:
                    for disease in diseases:
                        disease_scores[disease] += 1
        
        return dict(disease_scores)
    
    def get_diseases_by_dosha(self, doshas: List[str]) -> List[str]:
        """Get diseases associated with given doshas"""
        diseases = set()
        for dosha in doshas:
            dosha_lower = dosha.lower().strip()
            diseases.update(self.dosha_to_diseases.get(dosha_lower, []))
        return list(diseases)
    
    def get_diseases_by_age(self, age: int) -> List[str]:
        """Get diseases relevant to age group"""
        diseases = []
        
        # Match age to age groups
        for age_group, disease_list in self.age_group_diseases.items():
            if 'all ages' in age_group:
                diseases.extend(disease_list)
            elif '-' in age_group:
                try:
                    parts = age_group.replace(' years', '').replace('+', '-120').split('-')
                    min_age = int(parts[0])
                    max_age = int(parts[1]) if len(parts) > 1 else 120
                    if min_age <= age <= max_age:
                        diseases.extend(disease_list)
                except:
                    pass
            elif '+' in age_group:
                try:
                    min_age = int(age_group.replace('+', '').replace(' years', '').strip())
                    if age >= min_age:
                        diseases.extend(disease_list)
                except:
                    pass
        
        return list(set(diseases))
    
    def get_diseases_by_bmi(self, bmi: float) -> List[str]:
        """Get diseases based on BMI category"""
        if bmi >= 30:
            return self.obesity_related_diseases.copy()
        elif bmi < 18.5:
            return self.underweight_related_diseases.copy()
        return []
    
    def get_diseases_by_family_history(self, family_conditions: List[str]) -> List[str]:
        """Get diseases based on family history"""
        diseases = set()
        for condition in family_conditions:
            cond_lower = condition.lower().strip()
            # Direct match
            diseases.update(self.family_history_diseases.get(cond_lower, []))
            # Partial match
            for indexed_cond, disease_list in self.family_history_diseases.items():
                if cond_lower in indexed_cond or indexed_cond in cond_lower:
                    diseases.update(disease_list)
        return list(diseases)
    
    def get_diseases_by_lifestyle(self, lifestyle: Dict[str, Any]) -> List[str]:
        """Get diseases based on lifestyle factors"""
        diseases = set()
        
        # Exercise level
        exercise = lifestyle.get('exercise', '').lower()
        if exercise in ['none', 'low', 'sedentary']:
            diseases.update(self.lifestyle_to_diseases.get('sedentary', []))
        
        # Stress level
        stress = lifestyle.get('stress_level', '').lower()
        if stress in ['high', 'very high', 'severe']:
            diseases.update(self.lifestyle_to_diseases.get('high_stress', []))
        
        return list(diseases)
    
    def calculate_risk_score(self, disease_name: str, user_data: Dict[str, Any]) -> RiskProfile:
        """Calculate comprehensive risk score for a disease"""
        disease_key = disease_name.lower()
        if disease_key not in self.diseases:
            return None
        
        profile = self.diseases[disease_key]
        
        # Initialize factors
        dosha_factors = {}
        age_factor = 0.0
        gender_factor = 0.0
        bmi_factor = 0.0
        lifestyle_factor = 0.0
        family_history_factor = 0.0
        symptom_match_factor = 0.0
        
        # 1. Dosha matching
        user_prakriti = user_data.get('known_prakriti', '').lower()
        user_vikriti_doshas = user_data.get('current_dosha_symptoms', {})
        
        for dosha in profile.doshas_involved:
            dosha_lower = dosha.lower()
            if dosha_lower in user_prakriti:
                dosha_factors[dosha_lower] = 0.3
            if dosha_lower in user_vikriti_doshas:
                dosha_factors[dosha_lower] = dosha_factors.get(dosha_lower, 0) + 0.4
        
        # 2. Age matching
        user_age = user_data.get('age', 30)
        age_diseases = self.get_diseases_by_age(user_age)
        if disease_key in age_diseases:
            age_factor = 0.2
        
        # Extra weight for Vata-predominant conditions in elderly
        if user_age > 60 and 'vata' in [d.lower() for d in profile.doshas_involved]:
            age_factor += 0.15
        
        # 3. Gender matching
        user_gender = user_data.get('gender', '').lower()
        disease_gender = profile.gender_preference.lower()
        if 'both' in disease_gender or user_gender in disease_gender:
            gender_factor = 0.1
        if 'mostly' in disease_gender and user_gender in disease_gender:
            gender_factor = 0.2
        
        # 4. BMI matching
        user_bmi = user_data.get('bmi')
        if user_bmi:
            bmi_diseases = self.get_diseases_by_bmi(user_bmi)
            if disease_key in bmi_diseases:
                if user_bmi >= 35:
                    bmi_factor = 0.35
                elif user_bmi >= 30:
                    bmi_factor = 0.25
                elif user_bmi < 17:
                    bmi_factor = 0.3
                elif user_bmi < 18.5:
                    bmi_factor = 0.2
        
        # 5. Lifestyle matching
        user_lifestyle = user_data.get('lifestyle', {})
        lifestyle_diseases = self.get_diseases_by_lifestyle(user_lifestyle)
        if disease_key in lifestyle_diseases:
            lifestyle_factor = 0.2
        
        # Sleep pattern
        if 'poor' in profile.sleep_pattern_impact.lower():
            user_sleep = user_lifestyle.get('sleep_quality', '').lower()
            if user_sleep in ['poor', 'bad', 'irregular']:
                lifestyle_factor += 0.1
        
        # Stress
        if 'high' in profile.stress_impact.lower():
            user_stress = user_lifestyle.get('stress_level', '').lower()
            if user_stress in ['high', 'very high', 'severe']:
                lifestyle_factor += 0.15
        
        # 6. Family history matching
        user_family_history = user_data.get('family_history', [])
        if user_family_history:
            fh_diseases = self.get_diseases_by_family_history(user_family_history)
            if disease_key in fh_diseases:
                family_history_factor = 0.3
            # Check if specific disease is in family history
            for fh in user_family_history:
                if disease_name.lower() in fh.lower() or fh.lower() in disease_name.lower():
                    family_history_factor = 0.4
                    break
        
        # 7. Symptom matching
        user_symptoms = user_data.get('current_symptoms', [])
        if user_symptoms:
            symptom_matches = self.get_diseases_by_symptoms(user_symptoms)
            if disease_key in symptom_matches:
                match_score = symptom_matches[disease_key]
                symptom_match_factor = min(0.5, match_score * 0.15)
        
        # Calculate base risk score
        base_risk = sum([
            sum(dosha_factors.values()),
            age_factor,
            gender_factor,
            bmi_factor,
            lifestyle_factor,
            family_history_factor,
            symptom_match_factor
        ])
        
        # Normalize to 0-1
        base_risk = min(1.0, base_risk)
        
        # Calculate time-based probabilities
        # Chronic diseases have higher long-term risk
        if disease_key in self.chronic_diseases:
            prob_6m = base_risk * 0.3
            prob_1y = base_risk * 0.5
            prob_5y = base_risk * 0.8
        else:
            prob_6m = base_risk * 0.5
            prob_1y = base_risk * 0.6
            prob_5y = base_risk * 0.4  # Acute conditions less likely to persist
        
        # Build prevention measures
        preventive = []
        if profile.prevention:
            preventive.append(profile.prevention)
        if profile.diet_lifestyle_recommendations:
            preventive.append(profile.diet_lifestyle_recommendations)
        
        return RiskProfile(
            disease_name=disease_name,
            base_risk_score=base_risk,
            dosha_factors=dosha_factors,
            age_factor=age_factor,
            gender_factor=gender_factor,
            bmi_factor=bmi_factor,
            lifestyle_factor=lifestyle_factor,
            family_history_factor=family_history_factor,
            symptom_match_factor=symptom_match_factor,
            probability_6_months=round(prob_6m, 3),
            probability_1_year=round(prob_1y, 3),
            probability_5_years=round(prob_5y, 3),
            preventive_measures=preventive,
            early_warning_signs=profile.symptoms[:5]  # First 5 symptoms as early signs
        )
    
    def get_top_risks(self, user_data: Dict[str, Any], top_n: int = 10) -> List[RiskProfile]:
        """Get top N disease risks for a user"""
        risk_profiles = []
        
        for disease_name in self.diseases.keys():
            risk = self.calculate_risk_score(disease_name, user_data)
            if risk and risk.base_risk_score > 0.1:  # Filter low-risk
                risk_profiles.append(risk)
        
        # Sort by base risk score
        risk_profiles.sort(key=lambda x: x.base_risk_score, reverse=True)
        
        return risk_profiles[:top_n]
    
    def get_disease_profile(self, disease_name: str) -> Optional[DiseaseProfile]:
        """Get full disease profile"""
        return self.diseases.get(disease_name.lower())
    
    def get_dosha_disease_summary(self) -> Dict[str, List[Dict]]:
        """Get summary of diseases by dosha"""
        summary = {}
        
        for dosha in ['vata', 'pitta', 'kapha']:
            diseases = self.dosha_to_diseases.get(dosha, [])
            summary[dosha] = [
                {
                    "name": d,
                    "severity": self.diseases[d].severity if d in self.diseases else "Unknown",
                    "prognosis": self.diseases[d].prognosis if d in self.diseases else "Unknown"
                }
                for d in diseases[:20]  # Top 20 per dosha
            ]
        
        return summary
    
    def export_risk_map(self, filepath: str = "disease_risk_map.json"):
        """Export the risk map to JSON for caching"""
        export_data = {
            "diseases": {name: asdict(profile) for name, profile in self.diseases.items()},
            "symptom_index": dict(self.symptom_to_diseases),
            "dosha_index": dict(self.dosha_to_diseases),
            "risk_factor_index": dict(self.risk_factor_to_diseases),
            "obesity_related": self.obesity_related_diseases,
            "chronic_diseases": self.chronic_diseases,
            "severe_diseases": self.severe_diseases
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Exported risk map to {filepath}")
        return filepath


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_mapper_instance: Optional[DiseaseRiskMapper] = None

def get_disease_mapper() -> DiseaseRiskMapper:
    """Get singleton instance of DiseaseRiskMapper"""
    global _mapper_instance
    if _mapper_instance is None:
        _mapper_instance = DiseaseRiskMapper()
    return _mapper_instance


# ═══════════════════════════════════════════════════════════════════════════════
# CLI FOR TESTING
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("🔬 DISEASE RISK MAPPER - TEST")
    print("=" * 60)
    
    mapper = DiseaseRiskMapper()
    
    # Test with sample user data
    sample_user = {
        "age": 45,
        "gender": "M",
        "bmi": 28.5,
        "known_prakriti": "vata_pitta",
        "current_symptoms": ["fatigue", "joint pain", "frequent urination"],
        "lifestyle": {
            "exercise": "low",
            "stress_level": "high",
            "sleep_quality": "poor",
            "diet": "mixed"
        },
        "family_history": ["diabetes", "hypertension"],
        "current_dosha_symptoms": {
            "vata": ["anxiety", "dry skin"],
            "pitta": ["acidity", "irritability"]
        }
    }
    
    print("\n📊 Sample User Profile:")
    print(json.dumps(sample_user, indent=2))
    
    print("\n🎯 Top 10 Disease Risks:")
    print("-" * 60)
    
    top_risks = mapper.get_top_risks(sample_user, top_n=10)
    
    for i, risk in enumerate(top_risks, 1):
        print(f"\n{i}. {risk.disease_name.title()}")
        print(f"   Base Risk Score: {risk.base_risk_score:.2f}")
        print(f"   6-month probability: {risk.probability_6_months:.1%}")
        print(f"   1-year probability: {risk.probability_1_year:.1%}")
        print(f"   5-year probability: {risk.probability_5_years:.1%}")
        print(f"   Contributing factors:")
        if risk.dosha_factors:
            print(f"      Dosha: {risk.dosha_factors}")
        if risk.family_history_factor > 0:
            print(f"      Family History: {risk.family_history_factor:.2f}")
        if risk.symptom_match_factor > 0:
            print(f"      Symptom Match: {risk.symptom_match_factor:.2f}")
    
    # Export
    mapper.export_risk_map()
