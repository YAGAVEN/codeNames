// /media/yagaven_25/coding/Projects/codeNames/src/layouts/GameLayout.jsx
import { Outlet } from 'react-router-dom';
import { BottomNav } from '../components/layout/BottomNav.jsx';
import { Navbar } from '../components/layout/Navbar.jsx';
import { ErrorBoundary } from '../components/shared/ErrorBoundary.jsx';

export const GameLayout = () => (
  <div className="min-h-screen text-cream light:text-slate-950">
    <Navbar compact />
    <main className="mx-auto min-h-[calc(100vh-4rem)] max-w-[1700px] px-3 pb-28 pt-4 sm:px-5 lg:px-8">
      <ErrorBoundary>
        <Outlet />
      </ErrorBoundary>
    </main>
    <BottomNav />
  </div>
);
