// /media/yagaven_25/coding/Projects/codeNames/src/pages/GamePage.jsx
import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Eye, MessageCircle, Volume2, VolumeX } from 'lucide-react';
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

const GamePage = () => {
  const { roomCode } = useParams();
  const navigate = useNavigate();
  const { soundEnabled, setSoundEnabled } = useAuth();
  const { board, score, currentTurn, clue, players, timerSeconds, roomSettings, setTimer, winner } = useGame();
  const { emit, lastEvent, setRoomCode } = useSocket();
  const { showToast } = useToast();
  const [chatOpen, setChatOpen] = useState(false);

  // Register room code so the socket connects to the correct room.
  // This covers players who navigate directly to /game/:roomCode (e.g. late joins,
  // page refresh) — the socket will send join_room on open.
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
    try {
      // card_index is the numeric index extracted from boardId by socket.js
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
