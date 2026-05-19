// /media/yagaven_25/coding/Projects/codeNames/src/pages/ProfilePage.jsx
import { Edit3, History, Medal, UsersRound } from 'lucide-react';
import { Button } from '../components/ui/Button.jsx';
import { Badge } from '../components/ui/Badge.jsx';
import { PlayerAvatar } from '../components/lobby/PlayerAvatar.jsx';
import { useAuth } from '../hooks/useAuth.js';
import { mockPlayers } from '../data/mockPlayers.js';
import { formatNumber, relativeTime } from '../utils/helpers.js';

const ProfilePage = () => {
  const { user } = useAuth();
  const friends = mockPlayers.filter((player) => player.id !== user.id).slice(0, 6);

  return (
    <div className="grid gap-5 xl:grid-cols-[1fr_22rem]">
      <section className="glass-panel rangoli-border rounded-2xl p-5 sm:p-6">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <PlayerAvatar player={user} size="lg" />
            <div>
              <Badge tone="saffron">Level {user.level}</Badge>
              <h1 className="mt-2 font-heading text-4xl font-bold text-cream light:text-slate-900">{user.name}</h1>
              <p className="text-cream/65 light:text-slate-600">{user.handle} • {user.city}</p>
            </div>
          </div>
          <Button variant="secondary" icon={Edit3} aria-label="Edit profile mock">
            Edit Profile
          </Button>
        </div>
        <div className="mt-6 grid gap-3 sm:grid-cols-4">
          {[
            ['XP', formatNumber(user.xp)],
            ['Win Rate', `${user.winRate}%`],
            ['Streak', user.streak],
            ['Badges', user.badges.length]
          ].map(([label, value]) => (
            <div key={label} className="rounded-xl border border-white/10 bg-white/5 p-4">
              <p className="font-heading text-3xl font-bold text-cream light:text-slate-900">{value}</p>
              <p className="text-sm text-cream/55 light:text-slate-500">{label}</p>
            </div>
          ))}
        </div>
      </section>

      <aside className="glass-panel rounded-2xl p-5">
        <div className="flex items-center gap-2">
          <UsersRound className="h-5 w-5 text-saffron" aria-hidden="true" />
          <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Friends</h2>
        </div>
        <div className="mt-4 space-y-2">
          {friends.map((friend) => (
            <div key={friend.id} className="flex items-center gap-3 rounded-xl bg-white/5 p-2">
              <PlayerAvatar player={friend} size="sm" showLevel={false} />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-cream light:text-slate-900">{friend.name}</p>
                <p className="text-xs text-cream/50 light:text-slate-500">{friend.status}</p>
              </div>
              <Badge tone="emerald">{friend.winRate}%</Badge>
            </div>
          ))}
        </div>
      </aside>

      <section className="glass-panel rounded-2xl p-5 xl:col-span-2">
        <div className="flex items-center gap-2">
          <Medal className="h-5 w-5 text-saffron" aria-hidden="true" />
          <h2 className="font-heading text-3xl font-bold text-cream light:text-slate-900">Badge Showcase</h2>
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {user.badges.map((badge) => (
            <article key={badge.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
              <span className="text-3xl" aria-hidden="true">{badge.icon}</span>
              <h3 className="mt-2 font-heading text-xl font-bold text-cream light:text-slate-900">{badge.name}</h3>
              <p className="text-sm text-cream/55 light:text-slate-500">{badge.description}</p>
              <Badge className="mt-3" tone="saffron">{badge.rarity}</Badge>
            </article>
          ))}
        </div>
      </section>

      <section className="glass-panel rounded-2xl p-5 xl:col-span-2">
        <div className="flex items-center gap-2">
          <History className="h-5 w-5 text-saffron" aria-hidden="true" />
          <h2 className="font-heading text-3xl font-bold text-cream light:text-slate-900">Match History</h2>
        </div>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[42rem] text-left text-sm">
            <thead className="text-cream/50 light:text-slate-500">
              <tr>
                <th className="py-3">Room</th>
                <th>Result</th>
                <th>Role</th>
                <th>Team</th>
                <th>Score</th>
                <th>Played</th>
              </tr>
            </thead>
            <tbody>
              {user.matchHistory.map((match) => (
                <tr key={match.id} className="border-t border-white/10">
                  <td className="py-3 font-semibold text-cream light:text-slate-900">{match.room}</td>
                  <td><Badge tone={match.result === 'Win' ? 'emerald' : 'red'}>{match.result}</Badge></td>
                  <td className="text-cream/70 light:text-slate-600">{match.role}</td>
                  <td className="capitalize text-cream/70 light:text-slate-600">{match.team}</td>
                  <td className="text-cream/70 light:text-slate-600">{match.score}</td>
                  <td className="text-cream/50 light:text-slate-500">{relativeTime(match.playedAt)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default ProfilePage;
