import { createBrowserRouter, Navigate } from 'react-router-dom';

// Layouts
import { DoctorLayout, PatientLayout } from '../components/layout';

// Auth Pages
import { LandingPage, LoginPage, RegisterPage } from '../pages/auth';

// Doctor Pages
import {
  DoctorDashboard,
  DiagnosisPage,
  TreatmentPage,
  DecisionSupportPage,
  ProgressionPage,
  PatientsPage,
} from '../pages/doctor';

// Patient Pages
import {
  PatientDashboard,
  PatientProfile,
  SymptomChecker,
  HealthPredictions,
  AskAIChat,
  MyTreatments,
  LearnAyurveda,
} from '../pages/patient';

// Assessment Pages
import { PrakritiQuiz } from '../pages/assessment';

export const router = createBrowserRouter([
  // Public Routes
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },

  // Doctor Routes
  {
    path: '/doctor',
    element: <DoctorLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/doctor/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <DoctorDashboard />,
      },
      {
        path: 'diagnosis',
        element: <DiagnosisPage />,
      },
      {
        path: 'treatment',
        element: <TreatmentPage />,
      },
      {
        path: 'decision-support',
        element: <DecisionSupportPage />,
      },
      {
        path: 'progression',
        element: <ProgressionPage />,
      },
      {
        path: 'patients',
        element: <PatientsPage />,
      },
    ],
  },

  // Patient Routes
  {
    path: '/patient',
    element: <PatientLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/patient/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <PatientDashboard />,
      },
      {
        path: 'profile',
        element: <PatientProfile />,
      },
      {
        path: 'symptoms',
        element: <SymptomChecker />,
      },
      {
        path: 'predictions',
        element: <HealthPredictions />,
      },
      {
        path: 'chat',
        element: <AskAIChat />,
      },
      {
        path: 'treatments',
        element: <MyTreatments />,
      },
      {
        path: 'learn',
        element: <LearnAyurveda />,
      },
    ],
  },

  // Assessment Routes (shared)
  {
    path: '/assessment',
    element: <PatientLayout />,
    children: [
      {
        path: 'prakriti',
        element: <PrakritiQuiz />,
      },
    ],
  },

  // Catch-all redirect
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);
