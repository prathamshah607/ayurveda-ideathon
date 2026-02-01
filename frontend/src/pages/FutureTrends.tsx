import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './StructuredOutput.css';
import './FutureTrends.css';

// Type definitions for Future Trends
interface RiskFactor {
  risk_name: string;
  category: string;
  current_severity: string;
  probability_6_months: number;
  probability_1_year: number;
  probability_5_years: number;
  contributing_factors: string[];
  preventive_measures: string[];
  early_warning_signs: string[];
}

interface HerbalFormulation {
  name: string;
  sanskrit_name: string | null;
  dosage: string | null;
  anupana: string | null;
  timing: string | null;
  duration: string | null;
  contraindications: string[];
}

interface FutureTrendsResponse {
  query_id: string;
  timestamp: string;
  user_profile: Record<string, any>;
  constitution: {
    prakriti: string;
    vikriti: {
      primary_dosha: string;
      state: string;
      secondary_dosha: string | null;
      vikriti_description: string;
    } | null;
  };
  health_scores: {
    overall: number;
    dosha_balance: number;
    agni: number;
    ojas: number;
  };
  risk_factors: RiskFactor[];
  seasonal_vulnerabilities: Record<string, string[]>;
  age_related_risks: Array<Record<string, any>>;
  prevention_plan: Record<string, string[]>;
  lifestyle_optimization: {
    optimal_routine: Record<string, string>;
    recommended_rasayanas: HerbalFormulation[];
  };
}

interface QuickRiskItem {
  disease: string;
  risk_score: number;
  // Fields from actual API response (flat structure)
  probability_6_months?: number;
  probability_1_year?: number;
  probability_5_years?: number;
  preventive_measures?: string[];
  warning_signs?: string[];
  // Optional fields that may or may not be present
  category?: string;
  severity?: string;
}

interface QuickRiskData {
  quick_risks: QuickRiskItem[];
  profile_summary: Record<string, any>;
}

export default function FutureTrends() {
  const navigate = useNavigate();
  
  // Form state
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [prakriti, setPrakriti] = useState('');
  const [symptoms, setSymptoms] = useState('');
  const [familyHistory, setFamilyHistory] = useState('');
  
  // Lifestyle form state (user-friendly dropdowns)
  const [stressLevel, setStressLevel] = useState('');
  const [exerciseLevel, setExerciseLevel] = useState('');
  const [sleepHours, setSleepHours] = useState('');
  const [dietType, setDietType] = useState('');
  const [smokingStatus, setSmokingStatus] = useState('');
  const [alcoholConsumption, setAlcoholConsumption] = useState('');
  
  // Analysis state
  const [quickLoading, setQuickLoading] = useState(false);
  const [fullLoading, setFullLoading] = useState(false);
  const [quickError, setQuickError] = useState<string | null>(null);
  const [fullError, setFullError] = useState<string | null>(null);
  const [quickData, setQuickData] = useState<QuickRiskData | null>(null);
  const [fullData, setFullData] = useState<FutureTrendsResponse | null>(null);

  const calculateBMI = () => {
    if (height && weight) {
      const h = parseFloat(height) / 100; // cm to m
      const w = parseFloat(weight);
      if (h > 0) {
        return (w / (h * h)).toFixed(1);
      }
    }
    return null;
  };

  // Build lifestyle object from form fields
  const buildLifestyleObject = () => {
    const lifestyle: Record<string, string> = {};
    if (stressLevel) lifestyle.stress_level = stressLevel;
    if (exerciseLevel) lifestyle.exercise = exerciseLevel;
    if (sleepHours) lifestyle.sleep_hours = sleepHours;
    if (dietType) lifestyle.diet = dietType;
    if (smokingStatus) lifestyle.smoking = smokingStatus;
    if (alcoholConsumption) lifestyle.alcohol = alcoholConsumption;
    return lifestyle;
  };

  const handleQuickAssessment = async () => {
    if (!age || !gender) {
      setQuickError('Age and gender are required');
      return;
    }

    setQuickLoading(true);
    setQuickError(null);

    try {
      const bmi = calculateBMI();
      const payload = {
        age: parseInt(age),
        gender,
        bmi: bmi ? parseFloat(bmi) : undefined,
        known_prakriti: prakriti || undefined,
        current_symptoms: symptoms ? symptoms.split(',').map(s => s.trim()).filter(s => s) : [],
        family_history: familyHistory ? familyHistory.split(',').map(s => s.trim()).filter(s => s) : [],
        lifestyle: buildLifestyleObject(),
      };

      const response = await fetch('/api/v1/trends/quick', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      if (result.success) {
        setQuickData(result.data);
      } else {
        throw new Error(result.error || 'Unknown error');
      }
    } catch (err) {
      console.error('Quick assessment error:', err);
      setQuickError(err instanceof Error ? err.message : 'Failed to fetch quick assessment');
    } finally {
      setQuickLoading(false);
    }
  };

  const handleFullAnalysis = async () => {
    if (!age || !gender) {
      setFullError('Age and gender are required for full analysis');
      return;
    }

    setFullLoading(true);
    setFullError(null);

    try {
      const bmi = calculateBMI();
      const payload = {
        age: parseInt(age),
        gender,
        height_cm: height ? parseFloat(height) : undefined,
        weight_kg: weight ? parseFloat(weight) : undefined,
        bmi: bmi ? parseFloat(bmi) : undefined,
        known_prakriti: prakriti || undefined,
        current_symptoms: symptoms ? symptoms.split(',').map(s => s.trim()).filter(s => s) : [],
        family_history: familyHistory ? familyHistory.split(',').map(s => s.trim()).filter(s => s) : [],
        lifestyle: buildLifestyleObject(),
      };

      const response = await fetch('/api/v1/trends', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      if (result.success) {
        setFullData(result.data);
      } else {
        throw new Error(result.error || 'Unknown error');
      }
    } catch (err) {
      console.error('Full analysis error:', err);
      setFullError(err instanceof Error ? err.message : 'Failed to fetch full analysis');
    } finally {
      setFullLoading(false);
    }
  };

  // Derive severity from risk score
  const getRiskSeverity = (riskScore: number | undefined): string => {
    if (riskScore === undefined || riskScore === null) return 'unknown';
    if (riskScore >= 0.7) return 'high';
    if (riskScore >= 0.4) return 'moderate';
    return 'low';
  };

  // Derive category from risk score
  const getRiskCategory = (riskScore: number | undefined): string => {
    if (riskScore === undefined || riskScore === null) return 'Unknown';
    if (riskScore >= 0.7) return 'High Priority';
    if (riskScore >= 0.4) return 'Moderate Concern';
    return 'Low Risk';
  };

  const getSeverityColor = (severity: string | undefined | null) => {
    if (!severity) return 'neutral';
    const s = severity.toLowerCase();
    if (s === 'critical' || s === 'high') return 'negative';
    if (s === 'moderate') return 'neutral';
    return 'positive';
  };

  const formatDosha = (dosha: string) => {
    return dosha.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('-');
  };

  return (
    <div className="structured-container trends-page">
      {/* Header */}
      <header className="structured-header trends-theme">
        <button className="back-btn" onClick={() => navigate('/')}>
          ← Back
        </button>
        <h1>
          📈 Future Health Trends <span className="badge">Predictive Analysis</span>
        </h1>
      </header>

      <main className="structured-main">
        {/* Input Form */}
        <section className="section-card">
          <div className="section-header">
            <div className="section-icon trends-icon">📋</div>
            <h3>Enter Your Health Profile</h3>
          </div>
          <div className="section-content">
            <div className="trends-form">
              <div className="form-grid">
                <div className="form-group">
                  <label>Age *</label>
                  <input
                    type="number"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    placeholder="e.g., 35"
                    min="1"
                    max="120"
                  />
                </div>
                <div className="form-group">
                  <label>Gender *</label>
                  <select value={gender} onChange={(e) => setGender(e.target.value)}>
                    <option value="">Select</option>
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Height (cm)</label>
                  <input
                    type="number"
                    value={height}
                    onChange={(e) => setHeight(e.target.value)}
                    placeholder="e.g., 170"
                  />
                </div>
                <div className="form-group">
                  <label>Weight (kg)</label>
                  <input
                    type="number"
                    value={weight}
                    onChange={(e) => setWeight(e.target.value)}
                    placeholder="e.g., 70"
                  />
                </div>
                <div className="form-group">
                  <label>Known Prakriti</label>
                  <select value={prakriti} onChange={(e) => setPrakriti(e.target.value)}>
                    <option value="">Unknown</option>
                    <option value="vata">Vata</option>
                    <option value="pitta">Pitta</option>
                    <option value="kapha">Kapha</option>
                    <option value="vata_pitta">Vata-Pitta</option>
                    <option value="pitta_kapha">Pitta-Kapha</option>
                    <option value="vata_kapha">Vata-Kapha</option>
                    <option value="tridosha">Tridosha</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>BMI</label>
                  <input
                    type="text"
                    value={calculateBMI() || ''}
                    disabled
                    placeholder="Auto-calculated"
                    className="bmi-display"
                  />
                </div>
              </div>

              <div className="form-group full-width">
                <label>Current Symptoms (comma-separated)</label>
                <input
                  type="text"
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  placeholder="e.g., fatigue, joint pain, headaches"
                />
              </div>

              <div className="form-group full-width">
                <label>Family History (comma-separated)</label>
                <input
                  type="text"
                  value={familyHistory}
                  onChange={(e) => setFamilyHistory(e.target.value)}
                  placeholder="e.g., diabetes, hypertension, heart disease"
                />
              </div>

              {/* Lifestyle Factors Section */}
              <div className="form-section-divider full-width">
                <span>🏃 Lifestyle Factors (Optional)</span>
              </div>

              <div className="form-group">
                <label>Stress Level</label>
                <select value={stressLevel} onChange={(e) => setStressLevel(e.target.value)}>
                  <option value="">-- Select --</option>
                  <option value="low">Low</option>
                  <option value="moderate">Moderate</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div className="form-group">
                <label>Exercise Level</label>
                <select value={exerciseLevel} onChange={(e) => setExerciseLevel(e.target.value)}>
                  <option value="">-- Select --</option>
                  <option value="sedentary">Sedentary</option>
                  <option value="light">Light</option>
                  <option value="moderate">Moderate</option>
                  <option value="active">Active</option>
                </select>
              </div>

              <div className="form-group">
                <label>Sleep (hours/night)</label>
                <select value={sleepHours} onChange={(e) => setSleepHours(e.target.value)}>
                  <option value="">-- Select --</option>
                  <option value="less_than_6">Less than 6</option>
                  <option value="6_to_7">6-7 hours</option>
                  <option value="7_to_8">7-8 hours</option>
                  <option value="more_than_8">More than 8</option>
                </select>
              </div>

              <div className="form-group">
                <label>Diet Type</label>
                <select value={dietType} onChange={(e) => setDietType(e.target.value)}>
                  <option value="">-- Select --</option>
                  <option value="vegetarian">Vegetarian</option>
                  <option value="non_vegetarian">Non-Vegetarian</option>
                  <option value="vegan">Vegan</option>
                  <option value="mixed">Mixed</option>
                </select>
              </div>

              <div className="form-group">
                <label>Smoking</label>
                <select value={smokingStatus} onChange={(e) => setSmokingStatus(e.target.value)}>
                  <option value="">-- Select --</option>
                  <option value="never">Never</option>
                  <option value="former">Former Smoker</option>
                  <option value="current">Current Smoker</option>
                </select>
              </div>

              <div className="form-group">
                <label>Alcohol Consumption</label>
                <select value={alcoholConsumption} onChange={(e) => setAlcoholConsumption(e.target.value)}>
                  <option value="">-- Select --</option>
                  <option value="none">None</option>
                  <option value="occasional">Occasional</option>
                  <option value="moderate">Moderate</option>
                  <option value="heavy">Heavy</option>
                </select>
              </div>

              <div className="form-actions">
                <button
                  className="btn-quick"
                  onClick={handleQuickAssessment}
                  disabled={quickLoading || !age || !gender}
                >
                  {quickLoading ? '⏳ Analyzing...' : '⚡ Quick Assessment (Fast)'}
                </button>
                <button
                  className="btn-full"
                  onClick={handleFullAnalysis}
                  disabled={fullLoading || !age || !gender}
                >
                  {fullLoading ? '⏳ Analyzing...' : '🔬 Full Analysis (Comprehensive)'}
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Risk Assessment Results */}
        {quickData && (
          <div className="results-section">
            <h2 className="results-title">⚡ Quick Risk Assessment</h2>
            
            {(quickData.quick_risks || []).map((risk, idx) => {
              const derivedSeverity = risk?.severity || getRiskSeverity(risk?.risk_score);
              const derivedCategory = risk?.category || getRiskCategory(risk?.risk_score);
              
              return (
                <div key={idx} className="section-card risk-card">
                  <div className="section-header">
                    <div className={`section-icon trends-icon severity-${getSeverityColor(derivedSeverity)}`}>
                      {idx + 1}
                    </div>
                    <div style={{ flex: 1 }}>
                      <h3>{risk?.disease || 'Unknown Risk'}</h3>
                      <span className={`status-badge ${getSeverityColor(derivedSeverity)}`}>
                        {derivedSeverity.toUpperCase()} - {derivedCategory}
                      </span>
                    </div>
                  </div>
                  <div className="section-content">
                    <div className="two-column">
                      <div className="column-card">
                        <h4>🛡️ Preventive Measures</h4>
                        <ul>
                          {(risk?.preventive_measures || []).map((measure, i) => (
                            <li key={i}>{measure}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="column-card">
                        <h4>⚠️ Warning Signs</h4>
                        <ul>
                          {(risk?.warning_signs || []).map((sign, i) => (
                            <li key={i}>{sign}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Full Trends Analysis Results */}
        {fullData && (
          <div className="results-section">
            <h2 className="results-title">🔬 Comprehensive Analysis</h2>

            {/* Health Scores Dashboard */}
            <div className="section-card">
              <div className="section-header">
                <div className="section-icon trends-icon">📊</div>
                <h3>Health Scores Dashboard</h3>
              </div>
              <div className="section-content">
                <div className="scores-grid">
                  <div className="score-card overall">
                    <div className="score-icon">🎯</div>
                    <div className="score-value">{fullData.health_scores.overall.toFixed(0)}</div>
                    <div className="score-label">Overall Health</div>
                    <div className="score-bar">
                      <div 
                        className="score-bar-fill"
                        style={{ width: `${fullData.health_scores.overall}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="score-card">
                    <div className="score-icon">☯️</div>
                    <div className="score-value">{fullData.health_scores.dosha_balance.toFixed(0)}</div>
                    <div className="score-label">Dosha Balance</div>
                    <div className="score-bar">
                      <div 
                        className="score-bar-fill"
                        style={{ width: `${fullData.health_scores.dosha_balance}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="score-card">
                    <div className="score-icon">🔥</div>
                    <div className="score-value">{fullData.health_scores.agni.toFixed(0)}</div>
                    <div className="score-label">Agni (Digestion)</div>
                    <div className="score-bar">
                      <div 
                        className="score-bar-fill"
                        style={{ width: `${fullData.health_scores.agni}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="score-card">
                    <div className="score-icon">✨</div>
                    <div className="score-value">{fullData.health_scores.ojas.toFixed(0)}</div>
                    <div className="score-label">Ojas (Vitality)</div>
                    <div className="score-bar">
                      <div 
                        className="score-bar-fill"
                        style={{ width: `${fullData.health_scores.ojas}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Constitution Analysis */}
            <div className="section-card">
              <div className="section-header">
                <div className="section-icon trends-icon">🧬</div>
                <h3>Constitution (Prakriti & Vikriti)</h3>
              </div>
              <div className="section-content">
                <div className="kv-grid">
                  <div className="kv-item">
                    <div className="key">Prakriti (Natural Constitution)</div>
                    <div className="value">{formatDosha(fullData.constitution.prakriti)}</div>
                  </div>
                  {fullData.constitution.vikriti && (
                    <>
                      <div className="kv-item">
                        <div className="key">Vikriti (Current Imbalance)</div>
                        <div className="value">{formatDosha(fullData.constitution.vikriti.primary_dosha)}</div>
                      </div>
                      <div className="kv-item">
                        <div className="key">State</div>
                        <div className="value">
                          <span className={`status-badge ${fullData.constitution.vikriti.state}`}>
                            {fullData.constitution.vikriti.state}
                          </span>
                        </div>
                      </div>
                    </>
                  )}
                </div>
                {fullData.constitution.vikriti?.vikriti_description && (
                  <div className="mini-card" style={{ marginTop: '1rem' }}>
                    <p>{fullData.constitution.vikriti.vikriti_description}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Risk Factors */}
            {(fullData.risk_factors || []).length > 0 && (
              <div className="section-card">
                <div className="section-header">
                  <div className="section-icon trends-icon">⚠️</div>
                  <h3>Identified Risk Factors</h3>
                </div>
                <div className="section-content">
                  {(fullData.risk_factors || []).map((risk, idx) => (
                    <div key={idx} className="risk-factor-card">
                      <div className="risk-header">
                        <h4>
                          <span className={`status-badge ${getSeverityColor(risk?.current_severity)}`}>
                            {(risk?.current_severity || 'Unknown').toUpperCase()}
                          </span>
                          {risk?.risk_name || 'Unknown Risk'}
                        </h4>
                        <span className="risk-category">{risk?.category || 'N/A'}</span>
                      </div>
                      
                      <div className="probability-timeline compact">
                        <div className="timeline-item">
                          <span className="timeline-label">6mo</span>
                          <div className="timeline-bar">
                            <div className="timeline-fill" style={{ width: `${(risk?.probability_6_months ?? 0) * 100}%` }}></div>
                          </div>
                          <span className="timeline-value">{((risk?.probability_6_months ?? 0) * 100).toFixed(0)}%</span>
                        </div>
                        <div className="timeline-item">
                          <span className="timeline-label">1yr</span>
                          <div className="timeline-bar">
                            <div className="timeline-fill" style={{ width: `${(risk?.probability_1_year ?? 0) * 100}%` }}></div>
                          </div>
                          <span className="timeline-value">{((risk?.probability_1_year ?? 0) * 100).toFixed(0)}%</span>
                        </div>
                        <div className="timeline-item">
                          <span className="timeline-label">5yr</span>
                          <div className="timeline-bar">
                            <div className="timeline-fill" style={{ width: `${(risk?.probability_5_years ?? 0) * 100}%` }}></div>
                          </div>
                          <span className="timeline-value">{((risk?.probability_5_years ?? 0) * 100).toFixed(0)}%</span>
                        </div>
                      </div>

                      {(risk?.contributing_factors || []).length > 0 && (
                        <div className="risk-details">
                          <strong>Contributing Factors:</strong>
                          <div className="tags-container">
                            {(risk?.contributing_factors || []).map((factor, i) => (
                              <span key={i} className="tag avoid">{factor}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {(risk?.preventive_measures || []).length > 0 && (
                        <div className="risk-details">
                          <strong>Preventive Measures:</strong>
                          <ul>
                            {(risk?.preventive_measures || []).map((measure, i) => (
                              <li key={i}>{measure}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {(risk?.early_warning_signs || []).length > 0 && (
                        <div className="risk-details warning-signs">
                          <strong>⚠️ Early Warning Signs:</strong>
                          <div className="tags-container">
                            {(risk?.early_warning_signs || []).map((sign, i) => (
                              <span key={i} className="tag" style={{ background: '#fef3c7', color: '#92400e' }}>{sign}</span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Prevention Plan */}
            {Object.keys(fullData.prevention_plan || {}).length > 0 && (
              <div className="section-card">
                <div className="section-header">
                  <div className="section-icon trends-icon">🛡️</div>
                  <h3>Personalized Prevention Plan</h3>
                </div>
                <div className="section-content">
                  <div className="cards-grid">
                    {Object.entries(fullData.prevention_plan || {}).map(([category, items]) => (
                      <div key={category} className="mini-card">
                        <h4>✨ {category.replace(/_/g, ' ').charAt(0).toUpperCase() + category.replace(/_/g, ' ').slice(1)}</h4>
                        <ul>
                          {((items as string[]) || []).map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Seasonal Vulnerabilities */}
            {Object.keys(fullData.seasonal_vulnerabilities || {}).length > 0 && (
              <div className="section-card">
                <div className="section-header">
                  <div className="section-icon trends-icon">🍂</div>
                  <h3>Seasonal Vulnerability Calendar</h3>
                </div>
                <div className="section-content">
                  <div className="seasonal-grid">
                    {Object.entries(fullData.seasonal_vulnerabilities || {}).map(([season, risks]) => (
                      <div key={season} className="seasonal-card">
                        <h4>{season.charAt(0).toUpperCase() + season.slice(1)}</h4>
                        <div className="tags-container">
                          {((risks as string[]) || []).map((risk, i) => (
                            <span key={i} className="tag avoid">{risk}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Optimal Routine */}
            {Object.keys(fullData.lifestyle_optimization?.optimal_routine || {}).length > 0 && (
              <div className="section-card">
                <div className="section-header">
                  <div className="section-icon trends-icon">⏰</div>
                  <h3>Optimal Daily Routine</h3>
                </div>
                <div className="section-content">
                  <div className="kv-grid">
                    {Object.entries(fullData.lifestyle_optimization?.optimal_routine || {}).map(([time, activity]) => (
                      <div key={time} className="kv-item">
                        <div className="key">{time.replace(/_/g, ' ')}</div>
                        <div className="value">{activity}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Recommended Rasayanas */}
            {(fullData.lifestyle_optimization?.recommended_rasayanas || []).length > 0 && (
              <div className="section-card">
                <div className="section-header">
                  <div className="section-icon trends-icon">🌿</div>
                  <h3>Recommended Rasayanas (Rejuvenation)</h3>
                </div>
                <div className="section-content">
                  <div className="cards-grid">
                    {(fullData.lifestyle_optimization?.recommended_rasayanas || []).map((rasayana, idx) => (
                      <div key={idx} className="formulation-card">
                        <div className="name">🌿 {rasayana?.name || 'Unknown'}</div>
                        {rasayana?.sanskrit_name && (
                          <div className="sanskrit">{rasayana.sanskrit_name}</div>
                        )}
                        <div className="formulation-details">
                          {rasayana?.dosage && (
                            <div className="formulation-detail">
                              <span className="label">Dosage</span>
                              <span className="value">{rasayana.dosage}</span>
                            </div>
                          )}
                          {rasayana?.timing && (
                            <div className="formulation-detail">
                              <span className="label">Timing</span>
                              <span className="value">{rasayana.timing}</span>
                            </div>
                          )}
                          {rasayana?.duration && (
                            <div className="formulation-detail">
                              <span className="label">Duration</span>
                              <span className="value">{rasayana.duration}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="metadata-footer">
              <div className="metadata-item">
                <span className="icon">🔑</span>
                Query ID: {fullData.query_id || 'N/A'}
              </div>
              <div className="metadata-item">
                <span className="icon">🕐</span>
                {fullData.timestamp ? new Date(fullData.timestamp).toLocaleString() : 'N/A'}
              </div>
            </div>
          </div>
        )}

        {/* Error States */}
        {quickError && (
          <div className="error-container">
            <div className="icon">❌</div>
            <h3>Quick Assessment Failed</h3>
            <p>{quickError}</p>
          </div>
        )}

        {fullError && (
          <div className="error-container">
            <div className="icon">❌</div>
            <h3>Full Analysis Failed</h3>
            <p>{fullError}</p>
          </div>
        )}

        {/* Empty State */}
        {!quickData && !fullData && !quickLoading && !fullLoading && (
          <div className="empty-state">
            <div className="icon">📈</div>
            <h3>Predict Your Health Future</h3>
            <p>Fill in your health profile above to get personalized risk predictions and prevention strategies</p>
          </div>
        )}
      </main>
    </div>
  );
}
