import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './StructuredOutput.css';

// Type definitions based on backend PatientResponse
interface HomeRemedy {
  remedy: string;
  how_to_use: string;
  caution?: string;
}

interface DietaryAdvice {
  do: string;
  dont: string;
}

interface PatientStructuredResponse {
  query_id: string;
  timestamp: string;
  query: string;
  understanding_your_condition: {
    summary: string;
    ayurvedic_perspective: string;
  };
  actionable_advice: {
    dietary_advice: DietaryAdvice[];
    lifestyle_tips: string[];
    home_remedies: HomeRemedy[];
    yoga_recommendations: string[];
  };
  safety: {
    when_to_see_doctor: string[];
    disclaimer: string;
  };
  metadata: {
    reading_time_minutes: number;
  };
}

export default function PatientStructured() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<PatientStructuredResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/patient', {
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

  return (
    <div className="structured-container">
      {/* Header */}
      <header className="structured-header patient-theme">
        <button className="back-btn" onClick={() => navigate('/')}>
          ← Back
        </button>
        <h1>
          💜 Patient Guidance <span className="badge">Easy to Understand</span>
        </h1>
      </header>

      <main className="structured-main">
        {/* Query Input */}
        <section className="query-section patient-theme">
          <h2>🔍 What would you like to know?</h2>
          <form className="query-form" onSubmit={handleSubmit}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., I have headaches and fatigue, what can help?"
              disabled={loading}
            />
            <button type="submit" disabled={loading || !query.trim()}>
              {loading ? '⏳ Loading...' : '💡 Get Advice'}
            </button>
          </form>
        </section>

        {/* Loading State */}
        {loading && (
          <div className="loading-container">
            <div className="loading-spinner" style={{ borderTopColor: '#6b46c1' }}></div>
            <p>Finding personalized guidance for you...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="error-container">
            <div className="icon">❌</div>
            <h3>Something went wrong</h3>
            <p>{error}</p>
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <div className="results-container">
            {/* Reading Time Badge */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '-0.5rem' }}>
              <span className="status-badge info">
                📖 {data.metadata.reading_time_minutes} min read
              </span>
            </div>

            {/* Understanding Your Condition */}
            <div className="section-card">
              <div className="section-header">
                <div className="section-icon" style={{ background: 'linear-gradient(135deg, #6b46c1, #4c1d95)' }}>📋</div>
                <h3>Understanding Your Condition</h3>
              </div>
              <div className="section-content">
                <div className="mini-card" style={{ marginBottom: '1rem' }}>
                  <h4>📝 Summary</h4>
                  <p>{data.understanding_your_condition.summary}</p>
                </div>
                <div className="mini-card">
                  <h4>🌿 Ayurvedic Perspective</h4>
                  <p>{data.understanding_your_condition.ayurvedic_perspective}</p>
                </div>
              </div>
            </div>

            {/* Dietary Advice */}
            {data.actionable_advice.dietary_advice.length > 0 && (
              <div className="section-card">
                <div className="section-header">
                  <div className="section-icon" style={{ background: 'linear-gradient(135deg, #6b46c1, #4c1d95)' }}>🥗</div>
                  <h3>What to Eat & Avoid</h3>
                </div>
                <div className="section-content">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>✅ Recommended</th>
                        <th>❌ Avoid</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.actionable_advice.dietary_advice.map((advice, idx) => (
                        <tr key={idx}>
                          <td style={{ color: '#166534' }}>{advice.do}</td>
                          <td style={{ color: '#991b1b' }}>{advice.dont}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Lifestyle Tips */}
            {data.actionable_advice.lifestyle_tips.length > 0 && (
              <div className="section-card">
                <div className="section-header">
                  <div className="section-icon" style={{ background: 'linear-gradient(135deg, #6b46c1, #4c1d95)' }}>💪</div>
                  <h3>Lifestyle Tips</h3>
                </div>
                <div className="section-content">
                  <ul className="tips-list">
                    {data.actionable_advice.lifestyle_tips.map((tip, idx) => (
                      <li key={idx}>
                        <span className="bullet" style={{ background: 'linear-gradient(135deg, #6b46c1, #4c1d95)' }}>{idx + 1}</span>
                        <span className="text">{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Home Remedies */}
            {data.actionable_advice.home_remedies.length > 0 && (
              <div className="section-card">
                <div className="section-header">
                  <div className="section-icon" style={{ background: 'linear-gradient(135deg, #6b46c1, #4c1d95)' }}>🏠</div>
                  <h3>Home Remedies</h3>
                </div>
                <div className="section-content">
                  <div className="cards-grid">
                    {data.actionable_advice.home_remedies.map((remedy, idx) => (
                      <div key={idx} className="remedy-card">
                        <div className="name">🌿 {remedy.remedy}</div>
                        <div className="how-to">
                          <strong>How to use:</strong> {remedy.how_to_use}
                        </div>
                        {remedy.caution && (
                          <div className="caution">
                            <span>⚠️</span>
                            <span>{remedy.caution}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Yoga Recommendations */}
            {data.actionable_advice.yoga_recommendations.length > 0 && (
              <div className="section-card">
                <div className="section-header">
                  <div className="section-icon" style={{ background: 'linear-gradient(135deg, #6b46c1, #4c1d95)' }}>🧘</div>
                  <h3>Yoga & Exercise</h3>
                </div>
                <div className="section-content">
                  <div className="tags-container">
                    {data.actionable_advice.yoga_recommendations.map((yoga, idx) => (
                      <span key={idx} className="tag" style={{ background: '#f3e8ff', color: '#6b21a8' }}>
                        🧘 {yoga}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Safety Section */}
            <div className="section-card">
              <div className="section-header">
                <div className="section-icon" style={{ background: 'linear-gradient(135deg, #dc2626, #991b1b)' }}>⚠️</div>
                <h3>Safety Information</h3>
              </div>
              <div className="section-content">
                {data.safety.when_to_see_doctor.length > 0 && (
                  <div className="safety-box">
                    <h4>🏥 When to See a Doctor</h4>
                    <ul>
                      {data.safety.when_to_see_doctor.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="disclaimer-box">
                  <strong>⚖️ Disclaimer:</strong> {data.safety.disclaimer}
                </div>
              </div>
            </div>

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
                <span className="icon">📖</span>
                Reading time: ~{data.metadata.reading_time_minutes} minutes
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && !data && (
          <div className="empty-state">
            <div className="icon">💜</div>
            <h3>Ask Your Health Question</h3>
            <p>Get easy-to-understand Ayurvedic guidance personalized for you</p>
          </div>
        )}
      </main>
    </div>
  );
}
