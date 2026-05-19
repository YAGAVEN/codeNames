// /media/yagaven_25/coding/Projects/codeNames/src/layouts/MainLayout.jsx
import { Outlet } from 'react-router-dom';
import { BottomNav } from '../components/layout/BottomNav.jsx';
import { Footer } from '../components/layout/Footer.jsx';
import { Navbar } from '../components/layout/Navbar.jsx';
import { Sidebar } from '../components/layout/Sidebar.jsx';

export const MainLayout = () => (
  <div className="min-h-screen text-cream light:text-slate-950">
    <Navbar />
    <div className="mx-auto flex max-w-[1600px]">
      <Sidebar />
      <main className="min-w-0 flex-1 px-4 pb-28 pt-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
    <Footer />
    <BottomNav />
  </div>
);
