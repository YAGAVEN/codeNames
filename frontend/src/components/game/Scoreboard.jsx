// /media/yagaven_25/coding/Projects/codeNames/src/components/game/Scoreboard.jsx
import { Crown, Zap } from 'lucide-react';
import { Badge } from '../ui/Badge.jsx';

export const Scoreboard = ({ score, currentTurn, clue }) => {
  const hasClue = Boolean(clue?.word);
  const clueCount = clue?.count ?? clue?.number ?? 0;
  const teamLabel = currentTurn === 'red' ? 'Red' : 'Blue';

  // Describe what should happen next
  const actionLabel = hasClue
    ? `${teamLabel} Operatives — pick a card`
    : `${teamLabel} Spymaster — give a clue`;
  const ActionIcon = hasClue ? Zap : Crown;

  return (
    <section className="glass-panel rounded-2xl p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Scoreboard</h2>
          <p className="mt-0.5 flex items-center gap-1.5 text-sm text-cream/60 light:text-slate-600">
            <ActionIcon className="h-3.5 w-3.5 shrink-0 text-saffron" aria-hidden="true" />
            {hasClue ? (
              <>
                Clue: <span className="font-semibold text-saffron">{clue.word}</span> for {clueCount}
              </>
            ) : (
              actionLabel
            )}
          </p>
        </div>
        <Badge tone={currentTurn === 'red' ? 'red' : 'blue'}>{teamLabel} turn</Badge>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-xl border border-red-400/25 bg-red-500/10 p-3">
          <p className="text-sm text-red-100/70">Red found</p>
          <strong className="font-heading text-4xl text-red-100">
            {score.red}/{score.redTotal}
          </strong>
        </div>
        <div className="rounded-xl border border-blue-400/25 bg-blue-500/10 p-3">
          <p className="text-sm text-blue-100/70">Blue found</p>
          <strong className="font-heading text-4xl text-blue-100">
            {score.blue}/{score.blueTotal}
          </strong>
        </div>
      </div>
    </section>
  );
};
