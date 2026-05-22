// /media/yagaven_25/coding/Projects/codeNames/src/components/game/Scoreboard.jsx
import { Badge } from '../ui/Badge.jsx';

export const Scoreboard = ({ score, currentTurn, clue }) => {
  const hasClue = Boolean(clue?.word);
  const clueCount = clue?.count ?? clue?.number ?? 0;

  return (
    <section className="glass-panel rounded-2xl p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Scoreboard</h2>
          <p className="text-sm text-cream/60 light:text-slate-600">
            {hasClue ? (
              <>
                Current clue: <span className="font-semibold text-saffron">{clue.word}</span> for {clueCount}
              </>
            ) : (
              'Awaiting the next clue.'
            )}
          </p>
        </div>
        <Badge tone={currentTurn === 'red' ? 'red' : 'blue'}>{currentTurn === 'red' ? 'Red' : 'Blue'} turn</Badge>
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
