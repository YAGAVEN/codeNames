// /media/yagaven_25/coding/Projects/codeNames/src/components/game/WordGrid.jsx
import { motion } from 'framer-motion';
import { GameCard } from './GameCard.jsx';
import { staggerContainer } from '../../utils/animations.js';

export const WordGrid = ({ board, spymaster = false, onReveal, disabled }) => (
  <motion.section
    variants={staggerContainer}
    initial="initial"
    animate="animate"
    className="grid w-full grid-cols-5 gap-1.5 sm:gap-2 lg:gap-3"
    aria-label={spymaster ? 'Spymaster word grid with hidden map' : 'Operative word grid'}
  >
    {board.map((card, index) => (
      <GameCard key={card.boardId} card={card} index={index} spymaster={spymaster} disabled={disabled} onReveal={onReveal} />
    ))}
  </motion.section>
);
