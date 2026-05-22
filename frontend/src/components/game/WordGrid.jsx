// /media/yagaven_25/coding/Projects/codeNames/src/components/game/WordGrid.jsx
import { motion } from 'framer-motion';
import { GameCard } from './GameCard.jsx';
import { staggerContainer } from '../../utils/animations.js';

export const WordGrid = ({ board = [], spymaster = false, onReveal, disabled }) => {
  if (!board.length) {
    return (
      <section className="glass-panel grid min-h-80 place-items-center rounded-2xl p-6 text-center" aria-label="Waiting for server board">
        <div>
          <h2 className="font-heading text-3xl font-bold text-cream light:text-slate-900">Waiting for the game board</h2>
          <p className="mt-2 text-sm text-cream/60 light:text-slate-600">Start the room to load server cards.</p>
        </div>
      </section>
    );
  }

  return (
    <motion.section
      variants={staggerContainer}
      initial="initial"
      animate="animate"
      className="grid w-full grid-cols-5 gap-1.5 sm:gap-2 lg:gap-3"
      aria-label={spymaster ? 'Spymaster word grid with hidden map' : 'Operative word grid'}
    >
      {board.map((card, index) => (
        <GameCard key={card.boardId || card.index} card={card} index={index} spymaster={spymaster} disabled={disabled} onReveal={onReveal} />
      ))}
    </motion.section>
  );
};
