// /media/yagaven_25/coding/Projects/codeNames/src/pages/ResultPage.jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import confetti from 'canvas-confetti';
import { Crown, RotateCcw, Share2, Trophy } from 'lucide-react';
import { Button } from '../components/ui/Button.jsx';
import { Badge } from '../components/ui/Badge.jsx';
import { PlayerAvatar } from '../components/lobby/PlayerAvatar.jsx';
import { achievements } from '../data/achievements.js';
import { useGame } from '../hooks/useGame.js';
import { useAuth } from '../hooks/useAuth.js';
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
  const { score, winner, players, startGame } = useGame();
  const { user } = useAuth();
  const mvp = players[0];

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
          A smart clue chain, careful guesses, and one spectacular save near the assassin card.
        </p>
        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          {[
            ['Red cards found', score.red],
            ['Blue cards found', score.blue],
            ['XP earned', 1280]
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
          <div className="flex items-center gap-3">
            <PlayerAvatar player={mvp} size="lg" />
            <div>
              <Badge tone="emerald">
                <Crown className="h-3.5 w-3.5" aria-hidden="true" />
                Match MVP
              </Badge>
              <h2 className="mt-2 font-heading text-3xl font-bold text-cream light:text-slate-900">{mvp.name}</h2>
              <p className="text-cream/60 light:text-slate-600">Clue efficiency 82% • saved two risky guesses</p>
            </div>
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            {achievements.slice(0, 3).map((badge) => (
              <article key={badge.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
                <span className="text-3xl" aria-hidden="true">{badge.icon}</span>
                <h3 className="mt-2 font-heading text-xl font-bold text-cream light:text-slate-900">{badge.name}</h3>
                <p className="text-sm text-cream/55 light:text-slate-500">{badge.description}</p>
              </article>
            ))}
          </div>
        </section>

        <aside className="glass-panel rounded-2xl p-5">
          <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Next Move</h2>
          <p className="mt-2 text-sm text-cream/60 light:text-slate-600">Share the result, rematch the same room, or check the leaderboard climb.</p>
          <div className="mt-5 space-y-2">
            <Button className="w-full" icon={Share2} aria-label="Share match result">
              Share Result
            </Button>
            <Button as={Link} to="/game/IND-2048" className="mt-2 w-full" variant="secondary" icon={RotateCcw} onClick={startGame} aria-label="Replay room">
              Replay
            </Button>
            <Button as={Link} to="/leaderboard" className="mt-2 w-full" variant="secondary" aria-label="View leaderboard after match">
              View Leaderboard
            </Button>
          </div>
          <p className="mt-5 text-xs text-cream/45 light:text-slate-500">Signed in as {user.name}. Ranked MMR updates are mocked until backend sync.</p>
        </aside>
      </div>
    </div>
  );
};

export default ResultPage;
