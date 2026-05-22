// /media/yagaven_25/coding/Projects/codeNames/src/components/game/ReactionRail.jsx
import { AnimatePresence, motion } from 'framer-motion';
import { useAuth } from '../../hooks/useAuth.js';
import { useGame } from '../../hooks/useGame.js';
import { useSocket } from '../../hooks/useSocket.js';
import { SOCKET_EVENTS } from '../../services/socket.js';
import { floatingReaction } from '../../utils/animations.js';
import { useToast } from '../ui/Toast.jsx';

export const ReactionRail = () => {
  const { user } = useAuth();
  const { reactions, emojiOptions } = useGame();
  const { emit, connected } = useSocket();
  const { showToast } = useToast();

  const sendReaction = async (emoji) => {
    if (!user?.id) {
      showToast({ type: 'warning', title: 'Sign in to react', message: 'Log in to send reactions.' });
      return;
    }
    if (!connected) {
      showToast({ type: 'warning', title: 'Socket offline', message: 'Reconnect to send reactions.' });
      return;
    }

    try {
      await emit(SOCKET_EVENTS.EMOJI_REACTION, { emoji, playerId: user.id });
    } catch (error) {
      showToast({ type: 'error', title: 'Reaction failed', message: error.message });
    }
  };

  return (
    <div className="pointer-events-none fixed bottom-24 right-3 z-30 flex flex-col items-center gap-2 sm:right-6">
      <div className="relative h-28 w-14">
        <AnimatePresence>
          {reactions.slice(-5).map((reaction, index) => (
            <motion.span
              key={reaction.id}
              variants={floatingReaction}
              initial="initial"
              animate="animate"
              exit={{ opacity: 0 }}
              className="absolute bottom-0 text-3xl drop-shadow-lg"
              style={{ left: `${(index % 2) * 18}px` }}
            >
              {reaction.emoji}
            </motion.span>
          ))}
        </AnimatePresence>
      </div>
      <div className="pointer-events-auto grid grid-cols-2 gap-1 rounded-xl border border-white/10 bg-night/70 p-1.5 backdrop-blur-xl">
        {emojiOptions.slice(0, 4).map((emoji) => (
          <button
            key={emoji}
            type="button"
            aria-label={`React with ${emoji}`}
            onClick={() => sendReaction(emoji)}
            className="touch-target rounded-lg bg-white/10 text-lg transition hover:bg-white/20"
          >
            {emoji}
          </button>
        ))}
      </div>
    </div>
  );
};
