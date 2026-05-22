// /media/yagaven_25/coding/Projects/codeNames/src/pages/SpymasterPage.jsx
import { useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, Eye, ShieldAlert } from 'lucide-react';
import { Badge } from '../components/ui/Badge.jsx';
import { Button } from '../components/ui/Button.jsx';
import { ClueInput } from '../components/game/ClueInput.jsx';
import { Scoreboard } from '../components/game/Scoreboard.jsx';
import { TeamPanel } from '../components/game/TeamPanel.jsx';
import { WordGrid } from '../components/game/WordGrid.jsx';
import { useGame } from '../hooks/useGame.js';
import { useSocket } from '../hooks/useSocket.js';

const SpymasterPage = () => {
  const { roomCode } = useParams();
  const { board, spymasterBoard, score, currentTurn, clue, players } = useGame();
  const { setRoomCode } = useSocket();
  const visibleBoard = spymasterBoard.length ? spymasterBoard : board;

  useEffect(() => {
    setRoomCode(roomCode || '');
  }, [roomCode, setRoomCode]);

  return (
    <div className="space-y-4">
      <section className="glass-panel rangoli-border rounded-2xl p-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <Badge tone="saffron">
              <Eye className="h-3.5 w-3.5" aria-hidden="true" />
              Hidden map active
            </Badge>
            <h1 className="mt-3 font-heading text-4xl font-bold text-cream light:text-slate-900">Spymaster View</h1>
            <p className="text-cream/65 light:text-slate-600">
              {roomCode ? `Room ${roomCode}` : 'Room'} map is visible. Keep clues legal and team-safe.
            </p>
          </div>
          <Button as={Link} to={roomCode ? `/game/${roomCode}` : '/game'} variant="secondary" icon={ArrowLeft} aria-label="Return to operative game view">
            Back to Game
          </Button>
        </div>
      </section>

      <div className="grid gap-4 xl:grid-cols-[19rem_1fr]">
        <aside className="space-y-4">
          <ClueInput />
          <TeamPanel players={players} currentTurn={currentTurn} />
          <section className="rounded-2xl border border-danger/25 bg-danger/10 p-4">
            <div className="flex items-center gap-2">
              <ShieldAlert className="h-5 w-5 text-danger" aria-hidden="true" />
              <h2 className="font-heading text-2xl font-bold text-red-100">Map Discipline</h2>
            </div>
            <p className="mt-2 text-sm text-red-100/70">
              Do not describe card colors, positions, or category counts in chat. The validator only checks clue text.
            </p>
          </section>
        </aside>

        <section className="space-y-4">
          <Scoreboard score={score} currentTurn={currentTurn} clue={clue} />
          <WordGrid board={visibleBoard} spymaster disabled />
        </section>
      </div>
    </div>
  );
};

export default SpymasterPage;
