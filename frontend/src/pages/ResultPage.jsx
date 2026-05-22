// /media/yagaven_25/coding/Projects/codeNames/src/pages/ResultPage.jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import confetti from 'canvas-confetti';
import { RotateCcw, Trophy } from 'lucide-react';
import { Button } from '../components/ui/Button.jsx';
import { Badge } from '../components/ui/Badge.jsx';
import { useGame } from '../hooks/useGame.js';
import { useAuth } from '../hooks/useAuth.js';
import { useSocket } from '../hooks/useSocket.js';
import { formatNumber } from '../utils/helpers.js';

const RollingNumber = ({ value }) => {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    const step = Math.max(1, Math.ceil(value / 24));
    const timer = window.setInterval(() => {
      setDisplay((current) => {
        const next = Math.min(value, current + step);
        if (next === value) {
          window.clearInterval(timer);
        }
        return next;
      });
    }, 32);
    return () => window.clearInterval(timer);
  }, [value]);

  return formatNumber(display);
};

const ResultPage = () => {
  const { score, winner, startGame } = useGame();
  const { user } = useAuth();
  const { roomCode } = useSocket();
  const replayPath = roomCode ? `/game/${roomCode}` : '/game';
  const totalFound = Number(score.red || 0) + Number(score.blue || 0) + Number(score.neutral || 0);
  const badges = user?.badges || [];

  useEffect(() => {
    confetti({
      particleCount: 160,
      spread: 76,
      origin: { y: 0.72 },
      colors: ['#FF9933', '#10B981', '#F59E0B', '#2563EB']
    });
  }, []);

  return (
    <div className="mx-auto max-w-6xl space-y-5">
      <section className="glass-panel rangoli-border rounded-3xl p-6 text-center sm:p-8">
        <Badge tone="saffron">
          <Trophy className="h-3.5 w-3.5" aria-hidden="true" />
          Match Complete
        </Badge>
        <h1 className="mt-4 font-heading text-5xl font-bold text-cream light:text-slate-900 sm:text-7xl">
          {winner ? `${winner === 'red' ? 'Red' : 'Blue'} Team Wins` : 'Diwali Draw'}
        </h1>
        <p className="mx-auto mt-3 max-w-2xl text-cream/70 light:text-slate-600">
          Final server score from the completed room.
        </p>
        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          {[
            ['Red cards found', score.red],
            ['Blue cards found', score.blue],
            ['Cards revealed', totalFound]
          ].map(([label, value]) => (
            <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="font-heading text-5xl font-bold text-saffron">
                <RollingNumber value={value} />
              </p>
              <p className="text-sm text-cream/55 light:text-slate-500">{label}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="grid gap-5 lg:grid-cols-[1fr_22rem]">
        <section className="glass-panel rounded-2xl p-5">
          <Badge tone="emerald">Unlocked Badges</Badge>
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            {badges.length ? badges.slice(0, 3).map((badge) => (
              <article key={badge.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
                <span className="text-3xl" aria-hidden="true">{badge.icon}</span>
                <h3 className="mt-2 font-heading text-xl font-bold text-cream light:text-slate-900">{badge.name}</h3>
                <p className="text-sm text-cream/55 light:text-slate-500">{badge.description}</p>
              </article>
            )) : (
              <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-cream/60 light:text-slate-600 sm:col-span-3">
                Badge unlocks will appear here after backend rewards are recorded.
              </div>
            )}
          </div>
        </section>

        <aside className="glass-panel rounded-2xl p-5">
          <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Next Move</h2>
          <p className="mt-2 text-sm text-cream/60 light:text-slate-600">Rematch the same room or check the leaderboard climb.</p>
          <div className="mt-5 space-y-2">
            <Button as={Link} to={replayPath} className="mt-2 w-full" variant="secondary" icon={RotateCcw} onClick={startGame} aria-label="Replay room">
              Replay
            </Button>
            <Button as={Link} to="/leaderboard" className="mt-2 w-full" variant="secondary" aria-label="View leaderboard after match">
              View Leaderboard
            </Button>
          </div>
          <p className="mt-5 text-xs text-cream/45 light:text-slate-500">
            Signed in as {user?.name || 'Player'}.
          </p>
        </aside>
      </div>
    </div>
  );
};

export default ResultPage;
