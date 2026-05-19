// /media/yagaven_25/coding/Projects/codeNames/src/components/layout/Sidebar.jsx
import { NavLink } from 'react-router-dom';
import { Gauge, Settings, Trophy, UserRound } from 'lucide-react';
import { Badge } from '../ui/Badge.jsx';
import { useAuth } from '../../hooks/useAuth.js';
import { cn, formatNumber } from '../../utils/helpers.js';

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: Gauge },
  { label: 'Leaderboard', path: '/leaderboard', icon: Trophy },
  { label: 'Profile', path: '/profile', icon: UserRound },
  { label: 'Settings', path: '/settings', icon: Settings }
];

export const Sidebar = () => {
  const { user } = useAuth();

  return (
    <aside className="hidden w-72 shrink-0 border-r border-white/10 bg-white/[0.03] p-5 backdrop-blur-xl lg:block">
      <div className="glass-panel rounded-2xl p-4">
        <p className="font-label text-xs uppercase tracking-[0.18em] text-cream/50 light:text-slate-500">Player Card</p>
        <h2 className="mt-2 font-heading text-2xl font-bold text-cream light:text-slate-950">{user?.name}</h2>
        <p className="text-sm text-cream/60 light:text-slate-600">{user?.city} adda captain</p>
        <div className="mt-4 grid grid-cols-2 gap-2">
          <Badge tone="saffron">Lv {user?.level}</Badge>
          <Badge tone="emerald">{formatNumber(user?.xp || 0)} XP</Badge>
        </div>
      </div>

      <nav className="mt-6 space-y-2" aria-label="Dashboard sections">
        {navItems.map(({ label, path, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-xl px-4 py-3 font-label font-semibold text-cream/70 transition hover:bg-white/10 hover:text-cream light:text-slate-600 light:hover:text-slate-950',
                isActive && 'bg-gradient-to-r from-saffron/20 to-emerald/10 text-cream ring-1 ring-saffron/25 light:text-slate-950'
              )
            }
          >
            <Icon className="h-5 w-5" aria-hidden="true" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};
