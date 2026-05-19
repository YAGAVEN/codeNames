// /media/yagaven_25/coding/Projects/codeNames/src/components/layout/Footer.jsx
import { Link } from 'react-router-dom';

export const Footer = () => (
  <footer className="border-t border-white/10 px-4 py-8 text-sm text-cream/55 light:text-slate-500">
    <div className="mx-auto flex max-w-7xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <p>Codenames India • multiplayer word strategy for every adda.</p>
      <div className="flex gap-4">
        <Link className="hover:text-saffron" to="/settings">
          Audio
        </Link>
        <Link className="hover:text-saffron" to="/leaderboard">
          Leaderboard
        </Link>
        <Link className="hover:text-saffron" to="/lobby/IND-2048">
          Join lobby
        </Link>
      </div>
    </div>
  </footer>
);
