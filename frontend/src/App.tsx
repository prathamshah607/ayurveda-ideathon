import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import './App.css'
import DoctorChat from './pages/DoctorChat'
import PatientChat from './pages/PatientChat'
import AyushChat from './pages/AyushChat'
import DoctorStructured from './pages/DoctorStructured'
import PatientStructured from './pages/PatientStructured'
import AyushStructured from './pages/AyushStructured'
import FutureTrends from './pages/FutureTrends'

function HomePage() {
  return (
    <div className="app">
      <header className="header">
        <h1>🌿 Ayurveda AYUSH</h1>
        <p>Your Ayurvedic Health Companion</p>
      </header>

      <main className="main">
        <section className="hero">
          <h2>Welcome to Ayurveda AYUSH</h2>
          <p>
            Discover the ancient wisdom of Ayurveda combined with modern technology.
            Get personalized health insights and recommendations.
          </p>
        </section>

        <section className="features">
          <h3>💬 Chat Interfaces</h3>
          <p className="section-subtitle">Conversational AI for flexible, detailed responses</p>
          <div className="feature-cards">
            <Link to="/doctor-chat" className="feature-card">
              <span className="feature-icon">🩺</span>
              <h4>Doctor Chat</h4>
              <p>Clinical consultation for Ayurvedic practitioners with detailed treatment protocols.</p>
            </Link>
            
            <Link to="/patient-chat" className="feature-card">
              <span className="feature-icon">🧘</span>
              <h4>Patient Chat</h4>
              <p>Easy-to-understand health guidance for wellness seekers.</p>
            </Link>
            
            <Link to="/ayush-chat" className="feature-card ayush-card">
              <span className="feature-icon">🏛️</span>
              <h4>AYUSH Chat</h4>
              <p>Comprehensive framework analysis: Panchamahabhuta, Tridosha, Saptadhatu & more.</p>
            </Link>
          </div>
        </section>

        <section className="features structured-section">
          <h3>📊 Structured Analysis</h3>
          <p className="section-subtitle">Tabular outputs with organized, parseable data</p>
          <div className="feature-cards">
            <Link to="/doctor-structured" className="feature-card structured-card">
              <span className="feature-icon">🏥</span>
              <h4>Clinical Analysis</h4>
              <p>Structured Samprapti, Dosha assessment, treatment protocols & prognosis.</p>
            </Link>
            
            <Link to="/patient-structured" className="feature-card structured-card patient-card">
              <span className="feature-icon">💜</span>
              <h4>Patient Guidance</h4>
              <p>Organized dietary advice, home remedies, lifestyle tips & safety info.</p>
            </Link>
            
            <Link to="/ayush-structured" className="feature-card structured-card ayush-card">
              <span className="feature-icon">🏛️</span>
              <h4>AYUSH Framework</h4>
              <p>Five elements, seven tissues, digestive fire & complete interventions.</p>
            </Link>
            
            <Link to="/future-trends" className="feature-card structured-card trends-card">
              <span className="feature-icon">📈</span>
              <h4>Future Trends</h4>
              <p>Predict health risks, get personalized prevention plans & seasonal guidance.</p>
            </Link>
          </div>
        </section>
      </main>

      <footer className="footer">
        <p>© 2026 Ayurveda AYUSH. All rights reserved.</p>
      </footer>
    </div>
  )
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/doctor-chat" element={<DoctorChat />} />
        <Route path="/patient-chat" element={<PatientChat />} />
        <Route path="/ayush-chat" element={<AyushChat />} />
        <Route path="/doctor-structured" element={<DoctorStructured />} />
        <Route path="/patient-structured" element={<PatientStructured />} />
        <Route path="/ayush-structured" element={<AyushStructured />} />
        <Route path="/future-trends" element={<FutureTrends />} />
      </Routes>
    </Router>
  )
}

export default App
