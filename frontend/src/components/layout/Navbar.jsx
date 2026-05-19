// /media/yagaven_25/coding/Projects/codeNames/src/components/layout/Navbar.jsx
import { Link, NavLink } from 'react-router-dom';
import { Bell, Moon, Sun, Wifi, WifiOff } from 'lucide-react';
import { Button } from '../ui/Button.jsx';
import { Badge } from '../ui/Badge.jsx';
import { Tooltip } from '../ui/Tooltip.jsx';
import { useAuth } from '../../hooks/useAuth.js';
import { useSocket } from '../../hooks/useSocket.js';
import { ROUTES } from '../../utils/constants.js';
import { cn } from '../../utils/helpers.js';

export const Navbar = ({ compact = false }) => {
  const { theme, setTheme, notificationsEnabled } = useAuth();
  const { connected, roomCode } = useSocket();

  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-night/70 backdrop-blur-xl light:bg-cream/80">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-3" aria-label="Codenames India home">
          <span className="grid h-10 w-10 place-items-center rounded-lg bg-gradient-to-br from-saffron to-emerald font-heading text-lg font-bold text-night shadow-saffron">
            CI
          </span>
          <span className="hidden font-heading text-2xl font-bold tracking-normal text-cream light:text-slate-950 sm:block">
            Codenames <span className="festival-text">India</span>
          </span>
        </Link>

        {!compact ? (
          <nav className="hidden items-center gap-1 md:flex" aria-label="Primary navigation">
            {ROUTES.map((route) => (
              <NavLink
                key={route.path}
                to={route.path}
                className={({ isActive }) =>
                  cn(
                    'rounded-lg px-3 py-2 text-sm font-semibold text-cream/70 transition hover:bg-white/10 hover:text-cream light:text-slate-600 light:hover:text-slate-950',
                    isActive && 'bg-white/10 text-cream light:bg-slate-900/10 light:text-slate-950'
                  )
                }
              >
                {route.label}
              </NavLink>
            ))}
          </nav>
        ) : null}

        <div className="flex items-center gap-2">
          <Badge tone={connected ? 'emerald' : 'red'} className="hidden sm:inline-flex">
            {connected ? <Wifi className="h-3.5 w-3.5" aria-hidden="true" /> : <WifiOff className="h-3.5 w-3.5" aria-hidden="true" />}
            {connected ? roomCode : 'Offline'}
          </Badge>
          <Tooltip label={notificationsEnabled ? 'Notifications on' : 'Notifications muted'}>
            <Button aria-label="Notification center" variant="icon" icon={Bell} />
          </Tooltip>
          <Tooltip label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}>
            <Button
              aria-label="Toggle color theme"
              variant="icon"
              icon={theme === 'dark' ? Sun : Moon}
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            />
          </Tooltip>
        </div>
      </div>
    </header>
  );
};
