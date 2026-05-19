// /media/yagaven_25/coding/Projects/codeNames/src/components/layout/BottomNav.jsx
import { NavLink } from 'react-router-dom';
import { Gamepad2, Gauge, Settings, Trophy, UserRound } from 'lucide-react';
import { cn } from '../../utils/helpers.js';

const mobileItems = [
  { label: 'Home', path: '/dashboard', icon: Gauge },
  { label: 'Game', path: '/game/IND-2048', icon: Gamepad2 },
  { label: 'Ranks', path: '/leaderboard', icon: Trophy },
  { label: 'Profile', path: '/profile', icon: UserRound },
  { label: 'Settings', path: '/settings', icon: Settings }
];

export const BottomNav = () => (
  <nav
    className="safe-bottom fixed inset-x-0 bottom-0 z-40 border-t border-white/10 bg-night/90 px-2 pt-2 backdrop-blur-xl light:bg-cream/90 md:hidden"
    aria-label="Mobile navigation"
  >
    <div className="mx-auto grid max-w-md grid-cols-5 gap-1">
      {mobileItems.map(({ label, path, icon: Icon }) => (
        <NavLink
          key={path}
          to={path}
          className={({ isActive }) =>
            cn(
              'flex min-h-14 flex-col items-center justify-center gap-1 rounded-lg text-[11px] font-semibold text-cream/60 transition light:text-slate-500',
              isActive && 'bg-white/10 text-saffron light:bg-slate-900/10'
            )
          }
        >
          <Icon className="h-5 w-5" aria-hidden="true" />
          {label}
        </NavLink>
      ))}
    </div>
  </nav>
);
