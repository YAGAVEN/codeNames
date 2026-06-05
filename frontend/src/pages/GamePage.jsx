// /media/yagaven_25/coding/Projects/codeNames/src/pages/GamePage.jsx
import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Crown, Eye, MessageCircle, Volume2, VolumeX, Zap } from 'lucide-react';
import { Button } from '../components/ui/Button.jsx';
import { Badge } from '../components/ui/Badge.jsx';
import { Modal } from '../components/ui/Modal.jsx';
import { ChatPanel } from '../components/lobby/ChatPanel.jsx';
import { ClueInput } from '../components/game/ClueInput.jsx';
import { ReactionRail } from '../components/game/ReactionRail.jsx';
import { Scoreboard } from '../components/game/Scoreboard.jsx';
import { TeamPanel } from '../components/game/TeamPanel.jsx';
import { Timer } from '../components/game/Timer.jsx';
import { WordGrid } from '../components/game/WordGrid.jsx';
import { useToast } from '../components/ui/Toast.jsx';
import { useAuth } from '../hooks/useAuth.js';
import { useGame } from '../hooks/useGame.js';
import { useSocket } from '../hooks/useSocket.js';
import { SOCKET_EVENTS } from '../services/socket.js';
import { cn } from '../utils/helpers.js';

const GamePage = () => {
  const { roomCode } = useParams();
  const { soundEnabled, setSoundEnabled, user } = useAuth();
  const { board, score, currentTurn, clue, players, timerSeconds, roomSettings, setTimer, winner } = useGame();
  const { emit, lastEvent, setRoomCode } = useSocket();
  const { showToast } = useToast();
  const [chatOpen, setChatOpen] = useState(false);

  /** The authenticated user's record inside the room's player list. */
  const currentPlayer = useMemo(
    () => players.find((player) => String(player.id) === String(user?.id)) || null,
    [players, user?.id]
  );

  const isSpymaster = currentPlayer?.role === 'Spymaster';
  const isCurrentTeam = currentPlayer?.team === currentTurn;

  /**
   * Action banner text describing who should do what right now.
   * e.g. "🔴 Red Spymaster — Give your clue!"  or  "🔵 Blue Operatives — Choose a card!"
   */
  const actionBanner = useMemo(() => {
    if (winner) return null;
    const teamLabel = currentTurn === 'red' ? '🔴 Red' : '🔵 Blue';
    const hasClue = Boolean(clue?.word);

    if (!hasClue) {
      return {
        text: `${teamLabel} Spymaster — Give your clue now!`,
        tone: currentTurn,
        icon: Crown
      };
    }
    return {
      text: `${teamLabel} Field Operatives — Choose a card!`,
      tone: currentTurn,
      icon: Zap
    };
  }, [winner, currentTurn, clue]);

  // Register room code so the socket connects to the correct room.
  useEffect(() => {
    setRoomCode(roomCode || '');
  }, [roomCode, setRoomCode]);

  useEffect(() => {
    if (winner) {
      showToast({
        type: 'success',
        title: `${winner === 'red' ? '🔴 Red' : '🔵 Blue'} team wins!`,
        message: 'View the result screen for match stats.'
      });
    }
  }, [showToast, winner]);

  useEffect(() => {
    if (lastEvent?.event === SOCKET_EVENTS.ERROR_MESSAGE) {
      showToast({
        type: 'error',
        title: 'Game error',
        message: lastEvent.message || 'That move could not be played.'
      });
    }
  }, [lastEvent, showToast]);

  const handleReveal = async (cardId) => {
    if (!user?.id || !currentPlayer) {
      showToast({ type: 'warning', title: 'Join the room', message: 'Only room players can choose cards.' });
      return;
    }
    if (isSpymaster) {
      showToast({ type: 'warning', title: 'Spymasters watch', message: 'Only Field Operatives can choose cards.' });
      return;
    }
    if (!isCurrentTeam) {
      showToast({
        type: 'warning',
        title: 'Wait your turn',
        message: `${currentTurn === 'red' ? '🔴 Red' : '🔵 Blue'} team is choosing now.`
      });
      return;
    }
    if (!clue?.word) {
      showToast({ type: 'warning', title: 'Awaiting clue', message: 'Wait for your Spymaster to give a clue first.' });
      return;
    }

    try {
      await emit(SOCKET_EVENTS.MAKE_GUESS, { cardId });
    } catch (error) {
      showToast({ type: 'error', title: 'Guess failed', message: error.message });
    }
  };

  return (
    <div className="space-y-4">
      <section className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <Badge tone={currentTurn === 'red' ? 'red' : 'blue'}>{roomCode || 'Game'}</Badge>
          <h1 className="mt-2 font-heading text-4xl font-bold text-cream light:text-slate-900">Main Game Screen</h1>
          <p className="text-cream/65 light:text-slate-600">Operatives guess carefully. One assassin card can end the night.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="secondary"
            icon={soundEnabled ? Volume2 : VolumeX}
            onClick={() => setSoundEnabled(!soundEnabled)}
            aria-label="Toggle sound effects"
          >
            SFX {soundEnabled ? 'On' : 'Off'}
          </Button>
          <Button className="xl:hidden" variant="secondary" icon={MessageCircle} onClick={() => setChatOpen(true)} aria-label="Open chat panel">
            Chat
          </Button>
          <Button as={Link} to={roomCode ? `/spymaster/${roomCode}` : '/spymaster'} variant="secondary" icon={Eye} aria-label="Open spymaster view">
            Spymaster
          </Button>
        </div>
      </section>

      {/* ── Action banner ───────────────────────────────────────────────────── */}
      {actionBanner ? (
        <div
          className={cn(
            'flex items-center gap-3 rounded-2xl border px-4 py-3 text-sm font-semibold',
            actionBanner.tone === 'red'
              ? 'border-red-400/40 bg-red-500/15 text-red-100'
              : 'border-blue-400/40 bg-blue-500/15 text-blue-100'
          )}
          role="status"
          aria-live="polite"
        >
          <actionBanner.icon className="h-4 w-4 shrink-0" aria-hidden="true" />
          <span>{actionBanner.text}</span>
          {currentPlayer ? (
            <span
              className={cn(
                'ml-auto rounded-full px-2 py-0.5 text-xs font-bold',
                isCurrentTeam
                  ? isSpymaster
                    ? 'bg-saffron/20 text-saffron'
                    : 'bg-emerald-500/20 text-emerald-300'
                  : 'bg-white/10 text-cream/50'
              )}
            >
              You: {isSpymaster ? 'Spymaster' : 'Operative'} · {currentPlayer.team === 'red' ? '🔴 Red' : currentPlayer.team === 'blue' ? '🔵 Blue' : 'Spectator'}
            </span>
          ) : null}
        </div>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-[18rem_1fr_23rem]">
        <aside className="space-y-4">
          <Timer seconds={timerSeconds} total={roomSettings.timerLength} onTick={setTimer} onExpire={() => setTimer(roomSettings.timerLength)} />
          <TeamPanel players={players} currentTurn={currentTurn} />
        </aside>

        <section className="space-y-4">
          <Scoreboard score={score} currentTurn={currentTurn} clue={clue} />
          <WordGrid board={board} onReveal={handleReveal} disabled={Boolean(winner)} />
          {winner ? (
            <Button as={Link} to="/results" className="w-full" aria-label="Open game result screen">
              View Match Results
            </Button>
          ) : null}
        </section>

        <aside className="hidden space-y-4 xl:block">
          <ClueInput compact />
          <ChatPanel compact />
        </aside>
      </div>

      <ReactionRail />
      <Modal open={chatOpen} onClose={() => setChatOpen(false)} title="Room Chat" className="sm:max-w-xl">
        <ChatPanel />
      </Modal>
    </div>
  );
};

export default GamePage;
