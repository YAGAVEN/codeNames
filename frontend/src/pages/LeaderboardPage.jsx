// /media/yagaven_25/coding/Projects/codeNames/src/pages/LeaderboardPage.jsx
import { useEffect, useMemo, useState } from 'react';
import { Filter, Flame, Trophy } from 'lucide-react';
import { Button } from '../components/ui/Button.jsx';
import { Badge } from '../components/ui/Badge.jsx';
import { Skeleton } from '../components/shared/Skeleton.jsx';
import { fetchLeaderboard } from '../services/api.js';
import { formatNumber } from '../utils/helpers.js';

const filters = ['Global', 'Friends', 'This Week'];

const LeaderboardPage = () => {
  const [entries, setEntries] = useState([]);
  const [filter, setFilter] = useState('Global');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard().then((data) => {
      setEntries(data);
      setLoading(false);
    });
  }, []);

  const visibleEntries = useMemo(() => {
    if (filter === 'Friends') {
      return entries.filter((entry) => entry.rank % 2 === 0);
    }
    if (filter === 'This Week') {
      return entries.filter((entry) => entry.streak >= 3);
    }
    return entries;
  }, [entries, filter]);

  if (loading) {
    return <Skeleton className="h-[38rem]" />;
  }

  return (
    <div className="space-y-5">
      <section className="glass-panel rangoli-border rounded-2xl p-5">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <Badge tone="saffron">
              <Trophy className="h-3.5 w-3.5" aria-hidden="true" />
              Ranked Season: Monsoon Masters
            </Badge>
            <h1 className="mt-3 font-heading text-4xl font-bold text-cream light:text-slate-900">Leaderboard</h1>
            <p className="text-cream/65 light:text-slate-600">Global, friends, streaks, XP, badges, and country ranks.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {filters.map((item) => (
              <Button key={item} variant={filter === item ? 'primary' : 'secondary'} onClick={() => setFilter(item)} aria-label={`Filter leaderboard by ${item}`}>
                {item}
              </Button>
            ))}
          </div>
        </div>
      </section>

      <section className="glass-panel rounded-2xl p-4 sm:p-5">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="font-heading text-3xl font-bold text-cream light:text-slate-900">{filter} Rankings</h2>
          <Badge tone="emerald">
            <Filter className="h-3.5 w-3.5" aria-hidden="true" />
            {visibleEntries.length} players
          </Badge>
        </div>
        <div className="space-y-2">
          {visibleEntries.map((entry) => (
            <article
              key={entry.id}
              className={`grid grid-cols-[3.5rem_1fr_auto] items-center gap-3 rounded-xl border p-3 ${
                entry.rank <= 3 ? 'border-saffron/35 bg-saffron/10' : 'border-white/10 bg-white/5'
              }`}
            >
              <div className="grid h-11 w-11 place-items-center rounded-lg bg-white/10 font-heading text-xl font-bold text-cream light:text-slate-900">
                {entry.rank}
              </div>
              <div className="min-w-0">
                <h3 className="truncate font-semibold text-cream light:text-slate-900">{entry.name}</h3>
                <p className="text-sm text-cream/55 light:text-slate-500">{entry.country} • {entry.badge} • {entry.winRate}% wins</p>
              </div>
              <div className="text-right">
                <p className="font-heading text-2xl font-bold text-saffron">{formatNumber(entry.xp)}</p>
                <p className="flex items-center justify-end gap-1 text-xs text-emerald">
                  <Flame className="h-3.5 w-3.5" aria-hidden="true" />
                  {entry.streak} streak
                </p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
};

export default LeaderboardPage;
