import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './StructuredOutput.css';

// Type definitions based on backend DoctorResponse
interface DoshaAnalysis {
  primary_dosha: string;
  state: string;
  secondary_dosha: string | null;
  vikriti_description: string;
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

interface DietaryRecommendation {
  pathya: string[];
  apathya: string[];
  rasa_preference: string[];
  rasa_avoid: string[];
  special_instructions: string | null;
}

interface LifestyleRecommendation {
  dinacharya: string[];
  ritucharya: string[];
  yoga_asanas: string[];
  pranayama: string[];
  activities_recommended: string[];
  activities_avoid: string[];
}

interface ClassicalReference {
  source_text: string;
  chapter: string | null;
  shloka: string | null;
  page: number | null;
  relevance_score: number;
}

interface DoctorStructuredResponse {
  query_id: string;
  timestamp: string;
  query: string;
  clinical_assessment: {
    samprapti: Record<string, string>;
    dosha_analysis: DoshaAnalysis;
    dhatu_affected: string[];
    agni_status: string;
    ama_present: boolean;
  };
  treatment_protocol: {
    chikitsa_sutra: string;
    shodhana_indicated: boolean;
    shodhana_type: string[] | null;
    shamana_treatment: HerbalFormulation[];
  };
  diet_and_lifestyle: {
    dietary: DietaryRecommendation | null;
    lifestyle: LifestyleRecommendation | null;
  };
  prognosis: {
    type: string;
    notes: string;
  };
  references: ClassicalReference[];
  metadata: {
    confidence_score: number;
    databases_consulted: string[];
  };
}

// Dosha emoji and color mapping
const doshaConfig: Record<string, { emoji: string; color: string }> = {
  vata: { emoji: '💨', color: 'vata' },
  pitta: { emoji: '🔥', color: 'pitta' },
  kapha: { emoji: '🌊', color: 'kapha' },
  vata_pitta: { emoji: '💨🔥', color: 'vata' },
  pitta_kapha: { emoji: '🔥🌊', color: 'pitta' },
  vata_kapha: { emoji: '💨🌊', color: 'vata' },
  tridosha: { emoji: '☯️', color: 'vata' },
};

// Dhatu (tissue) configuration
const dhatuConfig: Record<string, { emoji: string; english: string }> = {
  rasa: { emoji: '💧', english: 'Plasma' },
  rakta: { emoji: '🩸', english: 'Blood' },
  mamsa: { emoji: '💪', english: 'Muscle' },
  meda: { emoji: '🧈', english: 'Fat' },
  asthi: { emoji: '🦴', english: 'Bone' },
  majja: { emoji: '🧠', english: 'Marrow' },
  shukra: { emoji: '✨', english: 'Reproductive' },
};

// State labels
const stateLabels: Record<string, { label: string; icon: string }> = {
  vriddhi: { label: 'Aggravated (Vriddhi)', icon: '⬆️' },
  kshaya: { label: 'Depleted (Kshaya)', icon: '⬇️' },
  sama: { label: 'Balanced (Sama)', icon: '⚖️' },
};

// Prognosis configuration
const prognosisConfig: Record<string, { label: string; description: string; icon: string; className: string }> = {
  sadhya: { label: 'Sadhya', description: 'Easily curable with proper treatment', icon: '✅', className: 'sadhya' },
  krichra_sadhya: { label: 'Krichra Sadhya', description: 'Curable with difficulty, requires sustained effort', icon: '⚠️', className: 'krichra' },
  yapya: { label: 'Yapya', description: 'Manageable/Palliative - can be controlled but not fully cured', icon: '🔄', className: 'yapya' },
  asadhya: { label: 'Asadhya', description: 'Difficult to cure, requires long-term management', icon: '⚡', className: 'asadhya' },
};

export default function DoctorStructured() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<DoctorStructuredResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/doctor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const result = await response.json();
      if (result.success) {
        setData(result.data);
      } else {
        throw new Error(result.error || 'Unknown error occurred');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const formatDoshaName = (dosha: string) => {
    return dosha
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join('-');
  };

  return (
    <div className="structured-container">
      {/* Header */}
      <header className="structured-header">
        <button className="back-btn" onClick={() => navigate('/')}>
          ← Back
        </button>
        <h1>
          🏥 Clinical Analysis <span className="badge">Structured Output</span>
        </h1>
      </header>

      <main className="structured-main">
        {/* Query Input */}
        <section className="query-section">
          <h2>🔍 Enter Clinical Query</h2>
          <form className="query-form" onSubmit={handleSubmit}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., What is the Ayurvedic treatment for diabetes mellitus?"
              disabled={loading}
            />
            <button type="submit" disabled={loading || !query.trim()}>
              {loading ? '⏳ Analyzing...' : '🔬 Analyze'}
            </button>
          </form>
        </section>

        {/* Loading State */}
        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Analyzing through classical texts...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="error-container">
            <div className="icon">❌</div>
            <h3>Analysis Failed</h3>
            <p>{error}</p>
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <div className="results-container">
            {/* Clinical Assessment Section */}
            <div className="section-card">
              <div className="section-header">
                <div className="section-icon">🩺</div>
                <h3>Clinical Assessment (Samprapti)</h3>
              </div>
              <div className="section-content">
                {/* Dosha Visualization */}
                <div className="dosha-viz">
                  <div className={`dosha-circle ${data.clinical_assessment.dosha_analysis.primary_dosha}`}>
                    <span style={{ fontSize: '1.5rem' }}>
                      {doshaConfig[data.clinical_assessment.dosha_analysis.primary_dosha]?.emoji || '☯️'}
                    </span>
                    <span>{formatDoshaName(data.clinical_assessment.dosha_analysis.primary_dosha)}</span>
                  </div>
                  <div className="dosha-info">
                    <h4>Primary Dosha: {formatDoshaName(data.clinical_assessment.dosha_analysis.primary_dosha)}</h4>
                    <div className={`state ${data.clinical_assessment.dosha_analysis.state}`}>
                      {stateLabels[data.clinical_assessment.dosha_analysis.state]?.icon || '•'}{' '}
                      {stateLabels[data.clinical_assessment.dosha_analysis.state]?.label || data.clinical_assessment.dosha_analysis.state}
                    </div>
                    {data.clinical_assessment.dosha_analysis.secondary_dosha && (
                      <p>
                        <strong>Secondary:</strong> {formatDoshaName(data.clinical_assessment.dosha_analysis.secondary_dosha)}
                      </p>
                    )}
                    {data.clinical_assessment.dosha_analysis.vikriti_description && (
                      <p>{data.clinical_assessment.dosha_analysis.vikriti_description}</p>
                    )}
                  </div>
                </div>

                {/* Samprapti Details */}
                <div className="kv-grid" style={{ marginTop: '1.5rem' }}>
                  {Object.entries(data.clinical_assessment.samprapti).map(([key, value]) => (
                    <div className="kv-item" key={key}>
                      <div className="key">{key.replace(/_/g, ' ')}</div>
                      <div className="value">{value || 'Not specified'}</div>
                    </div>
                  ))}
                </div>

                {/* Dhatu Affected */}
                <h4 style={{ margin: '1.5rem 0 1rem 0', color: '#374151' }}>Dhatu (Tissues) Affected</h4>
                <div className="dhatu-grid">
                  {Object.entries(dhatuConfig).map(([key, config]) => (
                    <div
                      key={key}
                      className={`dhatu-item ${data.clinical_assessment.dhatu_affected.some(d => d.toLowerCase().includes(key)) ? 'affected' : ''}`}
                    >
                      <div className="emoji">{config.emoji}</div>
                      <div className="name">{config.english}</div>
                      <div className="sanskrit">{key.charAt(0).toUpperCase() + key.slice(1)}</div>
                    </div>
                  ))}
                </div>

                {/* Agni & Ama Status */}
                <div className="kv-grid" style={{ marginTop: '1.5rem' }}>
                  <div className="kv-item">
                    <div className="key">Agni Status (Digestive Fire)</div>
                    <div className="value" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      🔥 {data.clinical_assessment.agni_status.charAt(0).toUpperCase() + data.clinical_assessment.agni_status.slice(1)}
                    </div>
                  </div>
                  <div className="kv-item">
                    <div className="key">Ama (Toxins) Present</div>
                    <div className="value">
                      <span className={`status-badge ${data.clinical_assessment.ama_present ? 'negative' : 'positive'}`}>
                        {data.clinical_assessment.ama_present ? '⚠️ Yes' : '✅ No'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Treatment Protocol Section */}
            <div className="section-card">
              <div className="section-header">
                <div className="section-icon">💊</div>
                <h3>Treatment Protocol (Chikitsa)</h3>
              </div>
              <div className="section-content">
                {/* Chikitsa Sutra */}
                <div className="mini-card" style={{ marginBottom: '1.5rem' }}>
                  <h4>📋 Line of Treatment (Chikitsa Sutra)</h4>
                  <p>{data.treatment_protocol.chikitsa_sutra}</p>
                </div>

                {/* Shodhana */}
                <div className="kv-grid" style={{ marginBottom: '1.5rem' }}>
                  <div className="kv-item">
                    <div className="key">Shodhana (Purification) Indicated</div>
                    <div className="value">
                      <span className={`status-badge ${data.treatment_protocol.shodhana_indicated ? 'info' : 'neutral'}`}>
                        {data.treatment_protocol.shodhana_indicated ? '✅ Yes' : '➖ No'}
                      </span>
                    </div>
                  </div>
                  {data.treatment_protocol.shodhana_type && data.treatment_protocol.shodhana_type.length > 0 && (
                    <div className="kv-item">
                      <div className="key">Shodhana Types</div>
                      <div className="value">
                        <div className="tags-container">
                          {data.treatment_protocol.shodhana_type.map((type, i) => (
                            <span key={i} className="tag dosha">{type}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Shamana Treatment - Formulations */}
                {data.treatment_protocol.shamana_treatment.length > 0 && (
                  <>
                    <h4 style={{ margin: '1.5rem 0 1rem 0', color: '#374151' }}>🌿 Shamana Treatment (Formulations)</h4>
                    <div className="cards-grid">
                      {data.treatment_protocol.shamana_treatment.map((formulation, idx) => (
                        <div key={idx} className="formulation-card">
                          <div className="name">🌿 {formulation.name}</div>
                          {formulation.sanskrit_name && (
                            <div className="sanskrit">{formulation.sanskrit_name}</div>
                          )}
                          <div className="formulation-details">
                            {formulation.dosage && (
                              <div className="formulation-detail">
                                <span className="label">Dosage</span>
                                <span className="value">{formulation.dosage}</span>
                              </div>
                            )}
                            {formulation.anupana && (
                              <div className="formulation-detail">
                                <span className="label">Anupana</span>
                                <span className="value">{formulation.anupana}</span>
                              </div>
                            )}
                            {formulation.timing && (
                              <div className="formulation-detail">
                                <span className="label">Timing</span>
                                <span className="value">{formulation.timing}</span>
                              </div>
                            )}
                            {formulation.duration && (
                              <div className="formulation-detail">
                                <span className="label">Duration</span>
                                <span className="value">{formulation.duration}</span>
                              </div>
                            )}
                          </div>
                          {formulation.contraindications.length > 0 && (
                            <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: '#b45309' }}>
                              ⚠️ Contraindications: {formulation.contraindications.join(', ')}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Diet & Lifestyle Section */}
            {(data.diet_and_lifestyle.dietary || data.diet_and_lifestyle.lifestyle) && (
              <div className="section-card">
                <div className="section-header">
                  <div className="section-icon">🥗</div>
                  <h3>Diet & Lifestyle (Pathya-Apathya)</h3>
                </div>
                <div className="section-content">
                  {/* Dietary Recommendations */}
                  {data.diet_and_lifestyle.dietary && (
                    <>
                      <div className="two-column">
                        <div className="column-card do">
                          <h4>✅ Pathya (Recommended)</h4>
                          <ul>
                            {data.diet_and_lifestyle.dietary.pathya.map((item, i) => (
                              <li key={i}>{item}</li>
                            ))}
                          </ul>
                        </div>
                        <div className="column-card dont">
                          <h4>❌ Apathya (Avoid)</h4>
                          <ul>
                            {data.diet_and_lifestyle.dietary.apathya.map((item, i) => (
                              <li key={i}>{item}</li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      {/* Rasa Preferences */}
                      {(data.diet_and_lifestyle.dietary.rasa_preference.length > 0 || data.diet_and_lifestyle.dietary.rasa_avoid.length > 0) && (
                        <div className="kv-grid" style={{ marginTop: '1.5rem' }}>
                          {data.diet_and_lifestyle.dietary.rasa_preference.length > 0 && (
                            <div className="kv-item">
                              <div className="key">Tastes to Prefer (Rasa)</div>
                              <div className="tags-container">
                                {data.diet_and_lifestyle.dietary.rasa_preference.map((rasa, i) => (
                                  <span key={i} className="tag recommended">{rasa}</span>
                                ))}
                              </div>
                            </div>
                          )}
                          {data.diet_and_lifestyle.dietary.rasa_avoid.length > 0 && (
                            <div className="kv-item">
                              <div className="key">Tastes to Avoid</div>
                              <div className="tags-container">
                                {data.diet_and_lifestyle.dietary.rasa_avoid.map((rasa, i) => (
                                  <span key={i} className="tag avoid">{rasa}</span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {data.diet_and_lifestyle.dietary.special_instructions && (
                        <div className="mini-card" style={{ marginTop: '1rem' }}>
                          <h4>📝 Special Instructions</h4>
                          <p>{data.diet_and_lifestyle.dietary.special_instructions}</p>
                        </div>
                      )}
                    </>
                  )}

                  {/* Lifestyle Recommendations */}
                  {data.diet_and_lifestyle.lifestyle && (
                    <div style={{ marginTop: '1.5rem' }}>
                      <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>🧘 Lifestyle (Vihara)</h4>
                      <div className="cards-grid">
                        {data.diet_and_lifestyle.lifestyle.dinacharya.length > 0 && (
                          <div className="mini-card">
                            <h4>🌅 Dinacharya (Daily Routine)</h4>
                            <ul>
                              {data.diet_and_lifestyle.lifestyle.dinacharya.map((item, i) => (
                                <li key={i}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {data.diet_and_lifestyle.lifestyle.ritucharya.length > 0 && (
                          <div className="mini-card">
                            <h4>🍂 Ritucharya (Seasonal Routine)</h4>
                            <ul>
                              {data.diet_and_lifestyle.lifestyle.ritucharya.map((item, i) => (
                                <li key={i}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {data.diet_and_lifestyle.lifestyle.yoga_asanas.length > 0 && (
                          <div className="mini-card">
                            <h4>🧘 Yoga Asanas</h4>
                            <div className="tags-container">
                              {data.diet_and_lifestyle.lifestyle.yoga_asanas.map((asana, i) => (
                                <span key={i} className="tag">{asana}</span>
                              ))}
                            </div>
                          </div>
                        )}
                        {data.diet_and_lifestyle.lifestyle.pranayama.length > 0 && (
                          <div className="mini-card">
                            <h4>🌬️ Pranayama</h4>
                            <div className="tags-container">
                              {data.diet_and_lifestyle.lifestyle.pranayama.map((prana, i) => (
                                <span key={i} className="tag">{prana}</span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Activities */}
                      {(data.diet_and_lifestyle.lifestyle.activities_recommended.length > 0 || 
                        data.diet_and_lifestyle.lifestyle.activities_avoid.length > 0) && (
                        <div className="two-column" style={{ marginTop: '1rem' }}>
                          {data.diet_and_lifestyle.lifestyle.activities_recommended.length > 0 && (
                            <div className="column-card do">
                              <h4>✅ Recommended Activities</h4>
                              <ul>
                                {data.diet_and_lifestyle.lifestyle.activities_recommended.map((item, i) => (
                                  <li key={i}>{item}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {data.diet_and_lifestyle.lifestyle.activities_avoid.length > 0 && (
                            <div className="column-card dont">
                              <h4>❌ Activities to Avoid</h4>
                              <ul>
                                {data.diet_and_lifestyle.lifestyle.activities_avoid.map((item, i) => (
                                  <li key={i}>{item}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Prognosis Section */}
            <div className="section-card">
              <div className="section-header">
                <div className="section-icon">📊</div>
                <h3>Prognosis</h3>
              </div>
              <div className="section-content">
                <div className={`prognosis-banner ${prognosisConfig[data.prognosis.type]?.className || 'sadhya'}`}>
                  <div className="icon">{prognosisConfig[data.prognosis.type]?.icon || '📊'}</div>
                  <div className="text">
                    <h4>{prognosisConfig[data.prognosis.type]?.label || data.prognosis.type}</h4>
                    <p>{data.prognosis.notes || prognosisConfig[data.prognosis.type]?.description}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Classical References Section */}
            {data.references.length > 0 && (
              <div className="section-card">
                <div className="section-header">
                  <div className="section-icon">📚</div>
                  <h3>Classical References</h3>
                </div>
                <div className="section-content">
                  <div className="cards-grid">
                    {data.references.map((ref, idx) => (
                      <div key={idx} className="reference-card">
                        <div className="icon">📜</div>
                        <div className="content">
                          <div className="source">{ref.source_text}</div>
                          {ref.chapter && <div className="chapter">Chapter: {ref.chapter}</div>}
                          {ref.shloka && <div className="chapter">Shloka: {ref.shloka}</div>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Metadata Footer */}
            <div className="metadata-footer">
              <div className="metadata-item">
                <span className="icon">🔑</span>
                Query ID: {data.query_id}
              </div>
              <div className="metadata-item">
                <span className="icon">🕐</span>
                {new Date(data.timestamp).toLocaleString()}
              </div>
              <div className="metadata-item">
                <span className="icon">📚</span>
                Sources: {data.metadata.databases_consulted.join(', ')}
              </div>
              <div className="confidence-bar">
                <span className="confidence-label">Confidence:</span>
                <div className="confidence-track">
                  <div 
                    className="confidence-fill" 
                    style={{ width: `${data.metadata.confidence_score * 100}%` }}
                  ></div>
                </div>
                <span className="confidence-label">{(data.metadata.confidence_score * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && !data && (
          <div className="empty-state">
            <div className="icon">🔬</div>
            <h3>No Analysis Yet</h3>
            <p>Enter a clinical query above to get structured Ayurvedic analysis</p>
          </div>
        )}
      </main>
    </div>
  );
}
