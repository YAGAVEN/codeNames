// /media/yagaven_25/coding/Projects/codeNames/src/pages/DashboardPage.jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { History, Play, Plus, UsersRound } from 'lucide-react';
import { motion } from 'framer-motion';
import { Button } from '../components/ui/Button.jsx';
import { Badge } from '../components/ui/Badge.jsx';
import { Skeleton } from '../components/shared/Skeleton.jsx';
import { PlayerAvatar } from '../components/lobby/PlayerAvatar.jsx';
import { useToast } from '../components/ui/Toast.jsx';
import { fetchDashboard } from '../services/api.js';
import { useRoom } from '../hooks/useRoom.js';
import { useAuth } from '../hooks/useAuth.js';
import { formatNumber, relativeTime } from '../utils/helpers.js';

const DashboardPage = () => {
  const { user: authUser } = useAuth();
  const { createRoom, joinRoom, busy } = useRoom();
  const { showToast } = useToast();
  const [dashboard, setDashboard] = useState(null);
  const [roomCode, setRoomCode] = useState('');

  useEffect(() => {
    fetchDashboard().then(setDashboard).catch((error) => {
      showToast({ type: 'error', title: 'Dashboard load failed', message: error.message });
    });
  }, [showToast]);

  if (!dashboard) {
    return (
      <div className="grid gap-4 lg:grid-cols-[1fr_22rem]">
        <Skeleton className="h-80" />
        <Skeleton className="h-80" />
        <Skeleton className="h-52 lg:col-span-2" />
      </div>
    );
  }

  const currentUser = dashboard.currentUser || authUser;
  const recentMatches = currentUser?.matchHistory || [];
  const winsThisWeek = recentMatches.filter((match) => match.result === 'Win').length;
  const lossesThisWeek = recentMatches.filter((match) => match.result === 'Loss').length;
  const totalMatches = recentMatches.length;

  return (
    <>
      <div className="grid gap-5 xl:grid-cols-[1fr_24rem]">
        <section className="glass-panel rangoli-border rounded-2xl p-5 sm:p-6">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <PlayerAvatar player={currentUser} size="lg" />
              <div>
                <Badge tone="saffron">Streak {currentUser?.streak ?? 0} days</Badge>
                <h1 className="mt-2 font-heading text-4xl font-bold text-cream light:text-slate-900">
                  Namaste, {(currentUser?.name || 'Player').split(' ')[0]}
                </h1>
                <p className="text-cream/65 light:text-slate-600">
                  {currentUser?.city || '—'} • {formatNumber(currentUser?.xp ?? 0)} XP • {currentUser?.winRate ?? 0}% win rate
                </p>
              </div>
            </div>
            <div className="flex flex-col gap-2 sm:w-52">
              <Button icon={Plus} onClick={createRoom} loading={busy} aria-label="Create new multiplayer room">
                Create Room
              </Button>
              <Button as={Link} to="/leaderboard" className="w-full" variant="secondary" aria-label="View leaderboard">
                View Ranks
              </Button>
            </div>
          </div>

          <div className="mt-6 grid gap-3 md:grid-cols-3">
            {[
              ['Matches this week', totalMatches],
              ['Wins this week', winsThisWeek],
              ['Losses this week', lossesThisWeek]
            ].map(([label, value]) => (
              <div key={label} className="rounded-xl border border-white/10 bg-white/5 p-4">
                <p className="font-heading text-4xl font-bold text-cream light:text-slate-900">{value}</p>
                <p className="text-sm text-cream/55 light:text-slate-500">{label}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="glass-panel rounded-2xl p-5">
          <div className="flex items-center gap-2">
            <Play className="h-5 w-5 text-saffron" aria-hidden="true" />
            <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Quick Join</h2>
          </div>
          <label className="mt-4 block">
            <span className="font-label text-sm font-semibold text-cream/75 light:text-slate-700">Room code</span>
            <input
              value={roomCode}
              onChange={(event) => setRoomCode(event.target.value.toUpperCase())}
              aria-label="Room code"
              className="mt-2 w-full rounded-lg border border-white/10 bg-white/5 px-3 py-3 text-cream outline-none focus:border-saffron/60 light:text-slate-900"
            />
          </label>
          <Button className="mt-4 w-full" icon={Play} onClick={() => joinRoom(roomCode)} loading={busy} aria-label="Join room by code">
            Join Room
          </Button>
        </section>

        <section className="xl:col-span-2">
          <div className="mb-3 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <UsersRound className="h-5 w-5 text-saffron" aria-hidden="true" />
              <h2 className="font-heading text-3xl font-bold text-cream light:text-slate-900">Active Rooms</h2>
            </div>
            <Badge tone="emerald">{dashboard.rooms.length} live</Badge>
          </div>
          <div className="grid gap-4 lg:grid-cols-3">
            {dashboard.rooms.length ? dashboard.rooms.map((room) => (
              <motion.article key={room.id} whileHover={{ y: -4 }} className="glass-panel rounded-2xl p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-heading text-2xl font-bold text-cream light:text-slate-900">{room.name}</h3>
                    <p className="text-sm text-cream/55 light:text-slate-500">Hosted by {room.host?.name || 'Host'}</p>
                  </div>
                  <Badge tone={room.status === 'Waiting' ? 'emerald' : room.status === 'Private' ? 'red' : 'blue'}>{room.status}</Badge>
                </div>
                <div className="mt-4 flex items-center justify-between text-sm text-cream/65 light:text-slate-600">
                  <span>{room.playerCount}/{room.maxPlayers} players</span>
                  <span>{room.theme}</span>
                </div>
                <Button className="mt-4 w-full" variant="secondary" onClick={() => joinRoom(room.code)} aria-label={`Join ${room.name}`}>
                  Join {room.code}
                </Button>
              </motion.article>
            )) : (
              <div className="rounded-xl border border-white/10 bg-white/5 p-5 text-sm text-cream/60 light:text-slate-600 lg:col-span-3">
                No live rooms are available yet. Create one to start a real match.
              </div>
            )}
          </div>
        </section>

        <section className="glass-panel rounded-2xl p-5 xl:col-span-2">
          <div className="flex items-center gap-2">
            <History className="h-5 w-5 text-saffron" aria-hidden="true" />
            <h2 className="font-heading text-3xl font-bold text-cream light:text-slate-900">Recent Matches</h2>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
            {(currentUser?.matchHistory || []).length ? currentUser.matchHistory.map((match) => (
              <article key={match.id} className="rounded-xl border border-white/10 bg-white/5 p-3">
                <Badge tone={match.result === 'Win' ? 'emerald' : 'red'}>{match.result}</Badge>
                <h3 className="mt-3 font-semibold text-cream light:text-slate-900">{match.room}</h3>
                <p className="text-sm text-cream/55 light:text-slate-500">{match.role} • {match.score}</p>
                <p className="mt-2 text-xs text-cream/40 light:text-slate-500">{relativeTime(match.playedAt)}</p>
              </article>
            )) : (
              <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-cream/60 light:text-slate-600 md:col-span-2 xl:col-span-5">
                Match history will appear here after completed games are saved.
              </div>
            )}
          </div>
        </section>
      </div>
    </>
  );
};

export default DashboardPage;
