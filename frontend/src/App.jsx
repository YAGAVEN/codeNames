// /media/yagaven_25/coding/Projects/codeNames/src/App.jsx
import { AnimatePresence, MotionConfig, motion } from 'framer-motion';
import { Route, Routes, useLocation } from 'react-router-dom';
import { ErrorBoundary } from './components/shared/ErrorBoundary.jsx';
import { AuthLayout } from './layouts/AuthLayout.jsx';
import { GameLayout } from './layouts/GameLayout.jsx';
import { MainLayout } from './layouts/MainLayout.jsx';
import AuthCallbackPage from './pages/AuthCallbackPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import ForgotPasswordPage from './pages/ForgotPasswordPage.jsx';
import GamePage from './pages/GamePage.jsx';
import LandingPage from './pages/LandingPage.jsx';
import LeaderboardPage from './pages/LeaderboardPage.jsx';
import LobbyPage from './pages/LobbyPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import ProfilePage from './pages/ProfilePage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import ResultPage from './pages/ResultPage.jsx';
import SettingsPage from './pages/SettingsPage.jsx';
import SpymasterPage from './pages/SpymasterPage.jsx';
import { pageTransition } from './utils/animations.js';

const PageFrame = ({ children }) => (
  <motion.div
    variants={pageTransition}
    initial="initial"
    animate="animate"
    exit="exit"
    className="min-h-screen"
  >
    {children}
  </motion.div>
);

export const App = () => {
  const location = useLocation();

  return (
    <MotionConfig reducedMotion="user">
      <ErrorBoundary>
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route
              path="/"
              element={
                <PageFrame>
                  <LandingPage />
                </PageFrame>
              }
            />
            <Route element={<AuthLayout />}>
              <Route
                path="/login"
                element={
                  <PageFrame>
                    <LoginPage />
                  </PageFrame>
                }
              />
              <Route
                path="/register"
                element={
                  <PageFrame>
                    <RegisterPage />
                  </PageFrame>
                }
              />
              <Route
                path="/forgot-password"
                element={
                  <PageFrame>
                    <ForgotPasswordPage />
                  </PageFrame>
                }
              />
              <Route
                path="/auth/callback"
                element={
                  <PageFrame>
                    <AuthCallbackPage />
                  </PageFrame>
                }
              />
            </Route>
            <Route element={<MainLayout />}>
              <Route
                path="/dashboard"
                element={
                  <PageFrame>
                    <DashboardPage />
                  </PageFrame>
                }
              />
              <Route
                path="/leaderboard"
                element={
                  <PageFrame>
                    <LeaderboardPage />
                  </PageFrame>
                }
              />
              <Route
                path="/profile"
                element={
                  <PageFrame>
                    <ProfilePage />
                  </PageFrame>
                }
              />
              <Route
                path="/settings"
                element={
                  <PageFrame>
                    <SettingsPage />
                  </PageFrame>
                }
              />
            </Route>
            <Route element={<GameLayout />}>
              <Route
                path="/lobby/:roomCode?"
                element={
                  <PageFrame>
                    <LobbyPage />
                  </PageFrame>
                }
              />
              <Route
                path="/game/:roomCode?"
                element={
                  <PageFrame>
                    <GamePage />
                  </PageFrame>
                }
              />
              <Route
                path="/spymaster/:roomCode?"
                element={
                  <PageFrame>
                    <SpymasterPage />
                  </PageFrame>
                }
              />
              <Route
                path="/results"
                element={
                  <PageFrame>
                    <ResultPage />
                  </PageFrame>
                }
              />
            </Route>
          </Routes>
        </AnimatePresence>
      </ErrorBoundary>
    </MotionConfig>
  );
};
