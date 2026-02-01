import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './StructuredOutput.css';

// Type definitions based on backend AyushResponse
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

interface ClassicalReference {
  source_text: string;
  chapter: string | null;
  shloka: string | null;
  page: number | null;
  relevance_score: number;
}

interface AyushStructuredResponse {
  query_id: string;
  timestamp: string;
  query: string;
  panchamahabhuta_analysis: {
    akasha: Record<string, any>;
    vayu: Record<string, any>;
    agni: Record<string, any>;
    jala: Record<string, any>;
    prithvi: Record<string, any>;
    dominant_elements: string[];
    deficient_elements: string[];
  };
  tridosha_analysis: DoshaAnalysis;
  saptadhatu_analysis: {
    rasa: Record<string, any>;
    rakta: Record<string, any>;
    mamsa: Record<string, any>;
    meda: Record<string, any>;
    asthi: Record<string, any>;
    majja: Record<string, any>;
    shukra: Record<string, any>;
  };
  agni_analysis: {
    type: string;
    recommendations: string[];
    ama_assessment: Record<string, any>;
  };
  mala_analysis: {
    purisha: Record<string, any>;
    mutra: Record<string, any>;
    sweda: Record<string, any>;
  };
  swasthya_path: Record<string, string[]>;
  interventions: {
    ahara: string[];
    vihara: string[];
    aushadhi: HerbalFormulation[];
    yoga_pranayama: string[];
  };
  classical_references: ClassicalReference[];
}

// Panchamahabhuta (Five Elements) configuration
const elementConfig: Record<string, { emoji: string; english: string; color: string }> = {
  akasha: { emoji: '🌌', english: 'Space/Ether', color: 'akasha' },
  vayu: { emoji: '💨', english: 'Air', color: 'vayu' },
  agni: { emoji: '🔥', english: 'Fire', color: 'agni' },
  jala: { emoji: '💧', english: 'Water', color: 'jala' },
  prithvi: { emoji: '🌍', english: 'Earth', color: 'prithvi' },
};

// Dosha configuration
const doshaConfig: Record<string, { emoji: string; elements: string }> = {
  vata: { emoji: '💨', elements: 'Space + Air' },
  pitta: { emoji: '🔥', elements: 'Fire + Water' },
  kapha: { emoji: '🌊', elements: 'Water + Earth' },
  vata_pitta: { emoji: '💨🔥', elements: 'Space + Air + Fire' },
  pitta_kapha: { emoji: '🔥🌊', elements: 'Fire + Water + Earth' },
  vata_kapha: { emoji: '💨🌊', elements: 'Space + Air + Earth' },
  tridosha: { emoji: '☯️', elements: 'All Elements' },
};

// Saptadhatu (Seven Tissues) configuration
const dhatuConfig: Record<string, { emoji: string; english: string; function: string }> = {
  rasa: { emoji: '💧', english: 'Plasma', function: 'Nourishment' },
  rakta: { emoji: '🩸', english: 'Blood', function: 'Oxygenation' },
  mamsa: { emoji: '💪', english: 'Muscle', function: 'Movement' },
  meda: { emoji: '🧈', english: 'Fat', function: 'Lubrication' },
  asthi: { emoji: '🦴', english: 'Bone', function: 'Support' },
  majja: { emoji: '🧠', english: 'Marrow', function: 'Filling' },
  shukra: { emoji: '✨', english: 'Reproductive', function: 'Creation' },
};

// Agni types
const agniTypes: Record<string, { description: string; emoji: string }> = {
  sama: { description: 'Balanced digestive fire - optimal digestion', emoji: '⚖️' },
  vishama: { description: 'Irregular/Variable fire (Vata type) - inconsistent digestion', emoji: '🌀' },
  tikshna: { description: 'Sharp/Intense fire (Pitta type) - hyperactive digestion', emoji: '🔥' },
  manda: { description: 'Sluggish/Slow fire (Kapha type) - weak digestion', emoji: '🐢' },
};

// Mala configuration
const malaConfig: Record<string, { emoji: string; english: string }> = {
  purisha: { emoji: '💩', english: 'Feces' },
  mutra: { emoji: '💧', english: 'Urine' },
  sweda: { emoji: '💦', english: 'Sweat' },
};

// Dosha state labels
const stateLabels: Record<string, { label: string; icon: string }> = {
  vriddhi: { label: 'Aggravated (Vriddhi)', icon: '⬆️' },
  kshaya: { label: 'Depleted (Kshaya)', icon: '⬇️' },
  sama: { label: 'Balanced (Sama)', icon: '⚖️' },
};

export default function AyushStructured() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AyushStructuredResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/ayush', {
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

  const renderObjectAsKeyValue = (obj: Record<string, any>, title: string) => {
    const entries = Object.entries(obj).filter(([_, v]) => v !== null && v !== undefined && v !== '');
    if (entries.length === 0) return null;
    
    return (
      <div className="mini-card">
        <h4>{title}</h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {entries.map(([key, value]) => (
            <div key={key} style={{ display: 'flex', gap: '0.5rem' }}>
              <span style={{ fontWeight: 500, color: '#6b7280', textTransform: 'capitalize' }}>
                {key.replace(/_/g, ' ')}:
              </span>
              <span style={{ color: '#374151' }}>
                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="structured-container">
      {/* Header */}
      <header className="structured-header ayush-theme">
        <button className="back-btn" onClick={() => navigate('/')}>
          ← Back
        </button>
        <h1>
          🏛️ AYUSH Framework <span className="badge">Comprehensive Analysis</span>
        </h1>
      </header>

      <main className="structured-main">
        {/* Query Input */}
        <section className="query-section ayush-theme">
          <h2>🔍 Enter Query for AYUSH Analysis</h2>
          <form className="query-form" onSubmit={handleSubmit}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Analyze the condition of chronic fatigue from AYUSH perspective"
              disabled={loading}
            />
            <button type="submit" disabled={loading || !query.trim()}>
              {loading ? '⏳ Analyzing...' : '🏛️ Analyze'}
            </button>
          </form>
        </section>

        {/* Loading State */}
        {loading && (
          <div className="loading-container">
            <div className="loading-spinner" style={{ borderTopColor: '#b45309' }}></div>
            <p>Performing comprehensive AYUSH framework analysis...</p>
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
            {/* Panchamahabhuta Analysis */}
            <div className="section-card">
              <div className="section-header">
                <div className="section-icon" style={{ background: 'linear-gradient(135deg, #b45309, #92400e)' }}>🌍</div>
                <h3>Panchamahabhuta (Five Elements)</h3>
              </div>
              <div className="section-content">
                <div className="element-grid">
                  {Object.entries(elementConfig).map(([key, config]) => {
                    const isDominant = data.panchamahabhuta_analysis.dominant_elements.some(
                      e => e.toLowerCase().includes(key)
                    );
                    const isDeficient = data.panchamahabhuta_analysis.deficient_elements.some(
                      e => e.toLowerCase().includes(key)
                    );
                    return (
                      <div 
                        key={key} 
                        className={`element-card ${config.color} ${isDominant ? 'dominant' : ''} ${isDeficient ? 'deficient' : ''}`}
                      >
                        <div className="emoji">{config.emoji}</div>
                        <div className="name">{config.english}</div>
                        <div className="sanskrit">{key.charAt(0).toUpperCase() + key.slice(1)}</div>
                        {isDominant && <span className="status-badge positive" style={{ marginTop: '0.5rem', fontSize: '0.7rem' }}>⬆️ Dominant</span>}
                        {isDeficient && <span className="status-badge negative" style={{ marginTop: '0.5rem', fontSize: '0.7rem' }}>⬇️ Deficient</span>}
                      </div>
                    );
                  })}
                </div>

                {/* Element details if available */}
                <div className="cards-grid" style={{ marginTop: '1.5rem' }}>
                  {Object.entries(elementConfig).map(([key, config]) => {
                    const elementData = data.panchamahabhuta_analysis[key as keyof typeof data.panchamahabhuta_analysis];
                    if (typeof elementData === 'object' && Object.keys(elementData).length > 0) {
                      return renderObjectAsKeyValue(elementData as Record<string, any>, `${config.emoji} ${config.english}`);
                    }
                    return null;
                  })}
                </div>
              </div>
            </div>

            {/* Tridosha Analysis */}
            <div className="section-card">
              <div className="section-header">
                <div className="section-icon" style={{ background: 'linear-gradient(135deg, #b45309, #92400e)' }}>☯️</div>
                <h3>Tridosha Analysis</h3>
              </div>
              <div className="section-content">
                <div className="dosha-viz">
                  <div className={`dosha-circle ${data.tridosha_analysis.primary_dosha}`}>
                    <span style={{ fontSize: '1.5rem' }}>
                      {doshaConfig[data.tridosha_analysis.primary_dosha]?.emoji || '☯️'}
                    </span>
                    <span>{formatDoshaName(data.tridosha_analysis.primary_dosha)}</span>
                  </div>
                  <div className="dosha-info">
                    <h4>Primary Dosha: {formatDoshaName(data.tridosha_analysis.primary_dosha)}</h4>
                    <p style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '0.5rem' }}>
                      Elements: {doshaConfig[data.tridosha_analysis.primary_dosha]?.elements || 'Various'}
                    </p>
                    <div className={`state ${data.tridosha_analysis.state}`}>
                      {stateLabels[data.tridosha_analysis.state]?.icon || '•'}{' '}
                      {stateLabels[data.tridosha_analysis.state]?.label || data.tridosha_analysis.state}
                    </div>
                    {data.tridosha_analysis.secondary_dosha && (
                      <p style={{ marginTop: '0.5rem' }}>
                        <strong>Secondary:</strong> {formatDoshaName(data.tridosha_analysis.secondary_dosha)}
                      </p>
                    )}
                    {data.tridosha_analysis.vikriti_description && (
                      <p style={{ marginTop: '0.5rem' }}>{data.tridosha_analysis.vikriti_description}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Saptadhatu Analysis */}
            <div className="section-card">
              <div className="section-header">
                <div className="section-icon" style={{ background: 'linear-gradient(135deg, #b45309, #92400e)' }}>🧬</div>
                <h3>Saptadhatu (Seven Tissues)</h3>
              </div>
              <div className="section-content">
                <div className="dhatu-grid">
                  {Object.entries(dhatuConfig).map(([key, config]) => {
                    const dhatuData = data.saptadhatu_analysis[key as keyof typeof data.saptadhatu_analysis];
                    const hasData = dhatuData && Object.keys(dhatuData).length > 0;
                    return (
                      <div key={key} className={`dhatu-item ${hasData ? 'affected' : ''}`}>
                        <div className="emoji">{config.emoji}</div>
                        <div className="name">{config.english}</div>
                        <div className="sanskrit">{key.charAt(0).toUpperCase() + key.slice(1)}</div>
                        <div style={{ fontSize: '0.65rem', color: '#9ca3af' }}>{config.function}</div>
                      </div>
                    );
                  })}
                </div>

                {/* Dhatu details if available */}
                <div className="cards-grid" style={{ marginTop: '1.5rem' }}>
                  {Object.entries(dhatuConfig).map(([key, config]) => {
                    const dhatuData = data.saptadhatu_analysis[key as keyof typeof data.saptadhatu_analysis];
                    if (dhatuData && Object.keys(dhatuData).length > 0) {
                      return renderObjectAsKeyValue(dhatuData, `${config.emoji} ${config.english} (${key.charAt(0).toUpperCase() + key.slice(1)})`);
                    }
                    return null;
                  })}
                </div>
              </div>
            </div>

            {/* Agni Analysis */}
            <div className="section-card">
              <div className="section-header">
                <div className="section-icon" style={{ background: 'linear-gradient(135deg, #b45309, #92400e)' }}>🔥</div>
                <h3>Agni Analysis (Digestive Fire)</h3>
              </div>
              <div className="section-content">
                <div className="kv-grid">
                  <div className="kv-item" style={{ borderLeftColor: '#b45309' }}>
                    <div className="key">Agni Type</div>
                    <div className="value" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {agniTypes[data.agni_analysis.type]?.emoji || '🔥'}{' '}
                      {data.agni_analysis.type.charAt(0).toUpperCase() + data.agni_analysis.type.slice(1)}
                    </div>
                    <p style={{ fontSize: '0.85rem', color: '#6b7280', marginTop: '0.5rem' }}>
                      {agniTypes[data.agni_analysis.type]?.description || ''}
                    </p>
                  </div>
                </div>

                {/* Agni Recommendations */}
                {data.agni_analysis.recommendations.length > 0 && (
                  <div style={{ marginTop: '1.5rem' }}>
                    <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>📋 Recommendations</h4>
                    <ul className="tips-list">
                      {data.agni_analysis.recommendations.map((rec, idx) => (
                        <li key={idx}>
                          <span className="bullet" style={{ background: 'linear-gradient(135deg, #b45309, #92400e)' }}>{idx + 1}</span>
                          <span className="text">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Ama Assessment */}
                {data.agni_analysis.ama_assessment && Object.keys(data.agni_analysis.ama_assessment).length > 0 && (
                  <div style={{ marginTop: '1.5rem' }}>
                    {renderObjectAsKeyValue(data.agni_analysis.ama_assessment, '🦠 Ama (Toxins) Assessment')}
                  </div>
                )}
              </div>
            </div>

            {/* Mala Analysis */}
            <div className="section-card">
              <div className="section-header">
                <div className="section-icon" style={{ background: 'linear-gradient(135deg, #b45309, #92400e)' }}>🔄</div>
                <h3>Mala Analysis (Waste Products)</h3>
              </div>
              <div className="section-content">
                <div className="cards-grid">
                  {Object.entries(malaConfig).map(([key, config]) => {
                    const malaData = data.mala_analysis[key as keyof typeof data.mala_analysis];
                    if (malaData && Object.keys(malaData).length > 0) {
                      return renderObjectAsKeyValue(malaData, `${config.emoji} ${config.english} (${key.charAt(0).toUpperCase() + key.slice(1)})`);
                    }
                    return (
                      <div key={key} className="mini-card">
                        <h4>{config.emoji} {config.english}</h4>
                        <p style={{ color: '#9ca3af' }}>No specific data available</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Swasthya Path */}
            {data.swasthya_path && Object.keys(data.swasthya_path).length > 0 && (
              <div className="section-card">
                <div className="section-header">
                  <div className="section-icon" style={{ background: 'linear-gradient(135deg, #b45309, #92400e)' }}>🌟</div>
                  <h3>Swasthya Path (Holistic Health)</h3>
                </div>
                <div className="section-content">
                  <div className="cards-grid">
                    {Object.entries(data.swasthya_path).map(([category, items]) => (
                      <div key={category} className="mini-card">
                        <h4>✨ {category.replace(/_/g, ' ').charAt(0).toUpperCase() + category.replace(/_/g, ' ').slice(1)}</h4>
                        <ul>
                          {(items as string[]).map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Interventions */}
            <div className="section-card">
              <div className="section-header">
                <div className="section-icon" style={{ background: 'linear-gradient(135deg, #b45309, #92400e)' }}>💊</div>
                <h3>Interventions</h3>
              </div>
              <div className="section-content">
                {/* Ahara (Diet) */}
                {data.interventions.ahara.length > 0 && (
                  <div style={{ marginBottom: '1.5rem' }}>
                    <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>🥗 Ahara (Diet)</h4>
                    <div className="tags-container">
                      {data.interventions.ahara.map((item, idx) => (
                        <span key={idx} className="tag recommended">{item}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Vihara (Lifestyle) */}
                {data.interventions.vihara.length > 0 && (
                  <div style={{ marginBottom: '1.5rem' }}>
                    <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>🏃 Vihara (Lifestyle)</h4>
                    <ul className="tips-list">
                      {data.interventions.vihara.map((item, idx) => (
                        <li key={idx}>
                          <span className="bullet" style={{ background: 'linear-gradient(135deg, #b45309, #92400e)' }}>{idx + 1}</span>
                          <span className="text">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Aushadhi (Medicines) */}
                {data.interventions.aushadhi.length > 0 && (
                  <div style={{ marginBottom: '1.5rem' }}>
                    <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>💊 Aushadhi (Medicines)</h4>
                    <div className="cards-grid">
                      {data.interventions.aushadhi.map((formulation, idx) => (
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
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Yoga & Pranayama */}
                {data.interventions.yoga_pranayama.length > 0 && (
                  <div>
                    <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>🧘 Yoga & Pranayama</h4>
                    <div className="tags-container">
                      {data.interventions.yoga_pranayama.map((item, idx) => (
                        <span key={idx} className="tag" style={{ background: '#fef3c7', color: '#92400e' }}>
                          🧘 {item}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Classical References */}
            {data.classical_references.length > 0 && (
              <div className="section-card">
                <div className="section-header">
                  <div className="section-icon" style={{ background: 'linear-gradient(135deg, #b45309, #92400e)' }}>📚</div>
                  <h3>Classical References</h3>
                </div>
                <div className="section-content">
                  <div className="cards-grid">
                    {data.classical_references.map((ref, idx) => (
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
                <span className="icon">🏛️</span>
                AYUSH Framework Analysis
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && !data && (
          <div className="empty-state">
            <div className="icon">🏛️</div>
            <h3>AYUSH Framework Analysis</h3>
            <p>Enter a query to receive comprehensive analysis through Panchamahabhuta, Tridosha, Saptadhatu, and more</p>
          </div>
        )}
      </main>
    </div>
  );
}
