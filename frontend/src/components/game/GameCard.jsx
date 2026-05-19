// /media/yagaven_25/coding/Projects/codeNames/src/components/game/GameCard.jsx
import { motion } from 'framer-motion';
import { Eye, Skull } from 'lucide-react';
import { CARD_TYPES } from '../../utils/constants.js';
import { cn } from '../../utils/helpers.js';

const revealedStyles = {
  [CARD_TYPES.RED]: 'border-red-300/55 bg-red-500/30 text-red-50 shadow-[0_0_28px_rgba(239,68,68,0.28)]',
  [CARD_TYPES.BLUE]: 'border-blue-300/55 bg-blue-500/30 text-blue-50 shadow-[0_0_28px_rgba(37,99,235,0.28)]',
  [CARD_TYPES.NEUTRAL]: 'border-stone-200/35 bg-stone-400/20 text-stone-100',
  [CARD_TYPES.ASSASSIN]: 'border-white/25 bg-black/70 text-white shadow-[0_0_34px_rgba(0,0,0,0.5)]'
};

const spymasterPips = {
  [CARD_TYPES.RED]: 'bg-red-400',
  [CARD_TYPES.BLUE]: 'bg-blue-400',
  [CARD_TYPES.NEUTRAL]: 'bg-stone-300',
  [CARD_TYPES.ASSASSIN]: 'bg-black ring-1 ring-white/40'
};

export const GameCard = ({ card, index, spymaster = false, disabled = false, onReveal }) => {
  const revealed = card.revealed || spymaster;
  const label = `${card.word}, ${card.category}${card.revealed ? ', revealed' : ''}`;

  return (
    <button
      type="button"
      aria-label={label}
      disabled={disabled || card.revealed}
      onClick={() => onReveal?.(card.boardId)}
      className="perspective-1200 touch-target aspect-[1.12/1] min-h-14 w-full rounded-xl outline-none focus:ring-2 focus:ring-saffron/70 disabled:cursor-not-allowed sm:min-h-20"
    >
      <motion.div
        className="preserve-3d relative h-full w-full"
        initial={false}
        animate={{ rotateY: revealed ? 180 : 0 }}
        transition={{ duration: 0.6, ease: [0.2, 0.8, 0.2, 1] }}
      >
        <div className="backface-hidden glass-panel absolute inset-0 flex flex-col justify-between rounded-xl border border-white/12 p-2.5 text-left transition hover:border-saffron/50 hover:shadow-saffron sm:p-3">
          <div className="flex items-center justify-between gap-2">
            <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] font-bold text-cream/60">{String(index + 1).padStart(2, '0')}</span>
            {spymaster ? <span className={cn('h-3 w-3 rounded-full', spymasterPips[card.type])} /> : <Eye className="h-3.5 w-3.5 text-saffron" aria-hidden="true" />}
          </div>
          <span className="break-words text-center font-heading text-[clamp(0.78rem,2.6vw,1.25rem)] font-bold leading-tight text-cream light:text-slate-900">
            {card.word}
          </span>
          <span className="truncate text-center text-[10px] font-semibold uppercase tracking-normal text-cream/40 light:text-slate-500">
            {card.category}
          </span>
        </div>

        <div
          className={cn(
            'backface-hidden absolute inset-0 flex rotate-y-180 flex-col items-center justify-center rounded-xl border p-2 text-center',
            revealedStyles[card.type]
          )}
        >
          {card.type === CARD_TYPES.ASSASSIN ? <Skull className="mb-1 h-5 w-5" aria-hidden="true" /> : null}
          <span className="break-words font-heading text-[clamp(0.78rem,2.6vw,1.22rem)] font-bold leading-tight">{card.word}</span>
          <span className="mt-1 text-[10px] font-bold uppercase tracking-normal opacity-70">
            {card.type === CARD_TYPES.ASSASSIN ? 'Assassin' : `${card.type} card`}
          </span>
        </div>
      </motion.div>
    </button>
  );
};
