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
import { VoiceChat } from '../components/game/VoiceChat.jsx';
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
  const { players, readyPlayers, roomSettings, toggleReady, startGame, setRoomState } = useGame();
  const { emit, connected, setRoomCode } = useSocket();
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState('Teams');

  const grouped = useMemo(
    () => ({
      red: players.filter((player) => player.team === 'red'),
      blue: players.filter((player) => player.team === 'blue'),
      spectator: players.filter((player) => player.team === 'spectator')
    }),
    [players]
  );

  const ready = user?.id ? readyPlayers.includes(user.id) : false;

  const handleReady = async () => {
    if (!user?.id) {
      showToast({
        type: 'warning',
        title: 'Sign in to ready up',
        message: 'Log in to toggle your ready status for this room.'
      });
      return;
    }

    try {
      toggleReady(user.id);
      await emit(SOCKET_EVENTS.PLAYER_READY, { playerId: user.id, ready: !ready });
    } catch (error) {
      showToast({ type: 'error', title: 'Ready update failed', message: error.message });
    }
  };

  const handleStart = async () => {
    try {
      startGame();
      await emit(SOCKET_EVENTS.GAME_STARTED, { roomCode, wordPack: roomSettings.wordPack || 'india' });
      navigate(roomCode ? `/game/${roomCode}` : '/game');
    } catch (error) {
      showToast({ type: 'error', title: 'Game start failed', message: error.message });
    }
  };

  const handleJoinTeam = (team) => {
    showToast({
      type: 'info',
      title: 'Team selection locked',
      message: `Team assignments are handled by the room host for ${team}.`
    });
  };

  const handleDragEnd = (_, info) => {
    if (Math.abs(info.offset.x) < 70) {
      return;
    }
    const current = tabs.indexOf(activeTab);
    const next = info.offset.x < 0 ? Math.min(tabs.length - 1, current + 1) : Math.max(0, current - 1);
    setActiveTab(tabs[next]);
  };

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
              {roomCode ? `Room ${roomCode}` : 'Lobby'} • {players.length} players • timer {roomSettings.timerLength}s
            </p>
          </div>
          <div className="grid gap-2 sm:grid-cols-2">
            <Button variant={ready ? 'secondary' : 'primary'} icon={CheckCircle2} onClick={handleReady} aria-label="Toggle ready status">
              {ready ? 'Ready' : 'Mark Ready'}
            </Button>
            <Button icon={Play} onClick={handleStart} aria-label="Start game">
              Start Game
            </Button>
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
            {activeTab === 'Settings' ? <RoomSettings /> : null}
          </motion.div>

          <div className="hidden gap-4 md:grid lg:grid-cols-2">
            <TeamSlot team="red" players={grouped.red} readyPlayers={readyPlayers} maxPlayers={roomSettings.maxTeamSize} onJoin={handleJoinTeam} />
            <TeamSlot team="blue" players={grouped.blue} readyPlayers={readyPlayers} maxPlayers={roomSettings.maxTeamSize} onJoin={handleJoinTeam} />
          </div>
          <div className="hidden md:block">
            <RoomSettings />
          </div>
          <VoiceChat players={players} />
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
