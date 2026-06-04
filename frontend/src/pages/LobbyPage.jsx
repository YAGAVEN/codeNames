// /media/yagaven_25/coding/Projects/codeNames/src/pages/LobbyPage.jsx
import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle2, Play, Radio } from 'lucide-react';
import { Button } from '../components/ui/Button.jsx';
import { Badge } from '../components/ui/Badge.jsx';
import { ChatPanel } from '../components/lobby/ChatPanel.jsx';
import { InvitePanel } from '../components/lobby/InvitePanel.jsx';
import { RoomSettings } from '../components/lobby/RoomSettings.jsx';
import { TeamSlot } from '../components/lobby/TeamSlot.jsx';
import { useToast } from '../components/ui/Toast.jsx';
import { useAuth } from '../hooks/useAuth.js';
import { useGame } from '../hooks/useGame.js';
import { useSocket } from '../hooks/useSocket.js';
import { fetchRoomByCode } from '../services/api.js';
import { SOCKET_EVENTS } from '../services/socket.js';

const tabs = ['Teams', 'Chat', 'Settings'];

const LobbyPage = () => {
  const { roomCode } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { players, readyPlayers, roomSettings, room, gameStarted, toggleReady, startGame, setRoomState } = useGame();
  const { emit, connected, lastEvent, setRoomCode } = useSocket();
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState('Teams');

  // ── Determine admin status ────────────────────────────────────────────────
  // The room object (fetched via REST on load and set via SET_ROOM_STATE) contains
  // host_id. Compare against the authenticated user's id to gate the Start Game button.
  const isAdmin = useMemo(() => {
    if (!user?.id || !room) return false;
    // room.host_id comes from RoomRead schema (UUID string after normalizeRoom)
    const hostId = room.host_id || room.hostId;
    return String(hostId) === String(user.id);
  }, [user?.id, room]);

  const grouped = useMemo(
    () => ({
      red: players.filter((player) => player.team === 'red'),
      blue: players.filter((player) => player.team === 'blue'),
      spectator: players.filter((player) => player.team === 'spectator')
    }),
    [players]
  );

  const ready = user?.id ? readyPlayers.includes(user.id) : false;

  // ── Navigate to game when server broadcasts game_started ─────────────────
  // This fires for ALL players — not just the admin — so everyone transitions.
  useEffect(() => {
    if (gameStarted && roomCode) {
      navigate(`/game/${roomCode}`);
    }
  }, [gameStarted, navigate, roomCode]);

  useEffect(() => {
    if (lastEvent?.event === SOCKET_EVENTS.ERROR_MESSAGE) {
      showToast({
        type: 'error',
        title: 'Game error',
        message: lastEvent.message || 'Something went wrong in the room.'
      });
    }
  }, [lastEvent, showToast]);

  // ── Register the room code with the socket context ────────────────────────
  useEffect(() => {
    setRoomCode(roomCode || '');
    if (!roomCode) {
      return undefined;
    }

    let active = true;
    fetchRoomByCode(roomCode)
      .then((room) => {
        if (active) {
          setRoomState(room);
        }
      })
      .catch((error) => {
        if (active) {
          showToast({ type: 'error', title: 'Room load failed', message: error.message });
        }
      });

    return () => {
      active = false;
    };
  }, [roomCode, setRoomCode, setRoomState, showToast]);

  const handleReady = async () => {
    if (!user?.id) {
      showToast({
        type: 'warning',
        title: 'Sign in to ready up',
        message: 'Log in to toggle your ready status for this room.'
      });
      return;
    }
    const nextReady = !ready;
    toggleReady(user.id);
    try {
      await emit(SOCKET_EVENTS.PLAYER_READY, { is_ready: nextReady });
    } catch (error) {
      toggleReady(user.id);
      showToast({ type: 'error', title: 'Ready update failed', message: error.message });
    }
  };

  const handleStart = async () => {
    if (!isAdmin) {
      showToast({ type: 'error', title: 'Not authorised', message: 'Only the room admin can start the game.' });
      return;
    }
    // Reset local game state in context (board, score, winner)
    startGame();
    try {
      // Send start_game to server. The server will broadcast game_started to
      // all clients. The useEffect above will navigate everyone to /game/:roomCode.
      await emit(SOCKET_EVENTS.START_GAME, { roomCode, wordPack: roomSettings.wordPack || 'india' });
    } catch (error) {
      showToast({ type: 'error', title: 'Game start failed', message: error.message });
    }
  };

  const handleJoinTeam = async (team) => {
    if (!user?.id) {
      showToast({ type: 'warning', title: 'Sign in first', message: 'Log in to join a team.' });
      return;
    }
    try {
      // Emit change_team — the server will update the DB and broadcast team_changed
      // to all clients, which GameContext handles by calling UPSERT_PLAYER.
      await emit(SOCKET_EVENTS.CHANGE_TEAM, { team });
    } catch (error) {
      showToast({ type: 'error', title: 'Team change failed', message: error.message });
    }
  };

  const handleDragEnd = (_, info) => {
    if (Math.abs(info.offset.x) < 70) {
      return;
    }
    const current = tabs.indexOf(activeTab);
    const next = info.offset.x < 0 ? Math.min(tabs.length - 1, current + 1) : Math.max(0, current - 1);
    setActiveTab(tabs[next]);
  };

  return (
    <div className="space-y-5">
      <section className="glass-panel rangoli-border rounded-2xl p-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <Badge tone={connected ? 'emerald' : 'red'}>
              <Radio className="h-3.5 w-3.5" aria-hidden="true" />
              {connected ? 'Socket online' : 'Reconnecting'}
            </Badge>
            <h1 className="mt-3 font-heading text-4xl font-bold text-cream light:text-slate-900">Multiplayer Lobby</h1>
            <p className="text-cream/65 light:text-slate-600">
              {roomCode ? `Room ${roomCode}` : 'Lobby'} • {players.length} players
              {isAdmin ? (
                <span className="ml-2 rounded bg-saffron/20 px-1.5 py-0.5 text-xs font-bold text-saffron">ADMIN</span>
              ) : null}
            </p>
          </div>

          <div className="grid gap-2 sm:grid-cols-2">
            <Button
              variant={ready ? 'secondary' : 'primary'}
              icon={CheckCircle2}
              onClick={handleReady}
              aria-label="Toggle ready status"
            >
              {ready ? 'Ready ✓' : 'Mark Ready'}
            </Button>

            {/* Start Game is only rendered for the room admin */}
            {isAdmin ? (
              <Button icon={Play} onClick={handleStart} aria-label="Start game">
                Start Game
              </Button>
            ) : null}
          </div>
        </div>
      </section>

      <div className="grid gap-5 xl:grid-cols-[1fr_23rem]">
        <div className="space-y-5">
          <div className="md:hidden">
            <div className="grid grid-cols-3 gap-2 rounded-xl bg-white/5 p-1">
              {tabs.map((tab) => (
                <button
                  key={tab}
                  type="button"
                  onClick={() => setActiveTab(tab)}
                  className={`rounded-lg px-3 py-2 text-sm font-bold ${activeTab === tab ? 'bg-saffron text-night' : 'text-cream/60'}`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          <motion.div drag="x" dragConstraints={{ left: 0, right: 0 }} onDragEnd={handleDragEnd} className="md:hidden">
            {activeTab === 'Teams' ? (
              <div className="grid gap-4">
                <TeamSlot team="red" players={grouped.red} readyPlayers={readyPlayers} maxPlayers={roomSettings.maxTeamSize} onJoin={handleJoinTeam} />
                <TeamSlot team="blue" players={grouped.blue} readyPlayers={readyPlayers} maxPlayers={roomSettings.maxTeamSize} onJoin={handleJoinTeam} />
              </div>
            ) : null}
            {activeTab === 'Chat' ? <ChatPanel /> : null}
            {activeTab === 'Settings' ? <RoomSettings isAdmin={isAdmin} /> : null}
          </motion.div>

          <div className="hidden gap-4 md:grid lg:grid-cols-2">
            <TeamSlot team="red" players={grouped.red} readyPlayers={readyPlayers} maxPlayers={roomSettings.maxTeamSize} onJoin={handleJoinTeam} />
            <TeamSlot team="blue" players={grouped.blue} readyPlayers={readyPlayers} maxPlayers={roomSettings.maxTeamSize} onJoin={handleJoinTeam} />
          </div>
          <div className="hidden md:block">
            <RoomSettings isAdmin={isAdmin} />
          </div>
        </div>

        <aside className="space-y-5">
          <InvitePanel roomCode={roomCode} />
          <div className="hidden xl:block">
            <ChatPanel compact />
          </div>
        </aside>
      </div>
    </div>
  );
};

export default LobbyPage;
