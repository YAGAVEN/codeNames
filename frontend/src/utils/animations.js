// /media/yagaven_25/coding/Projects/codeNames/src/utils/animations.js
export const pageTransition = {
  initial: { opacity: 0, y: 18 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.32, ease: [0.2, 0.8, 0.2, 1] } },
  exit: { opacity: 0, y: -12, transition: { duration: 0.22 } }
};

export const staggerContainer = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.06
    }
  }
};

export const popIn = {
  initial: { opacity: 0, scale: 0.96, y: 12 },
  animate: { opacity: 1, scale: 1, y: 0, transition: { duration: 0.28 } }
};

export const lobbyAvatarDrop = {
  initial: { opacity: 0, y: -24, scale: 0.88 },
  animate: { opacity: 1, y: 0, scale: 1, transition: { type: 'spring', stiffness: 360, damping: 24 } }
};

export const floatingReaction = {
  initial: { opacity: 0, y: 14, scale: 0.9 },
  animate: { opacity: [0, 1, 1, 0], y: [14, -18, -62, -96], scale: [0.9, 1.08, 1.2, 1.15] },
  transition: { duration: 1.8, ease: 'easeOut' }
};

export const modalTransition = {
  initial: { opacity: 0, scale: 0.96, y: 20 },
  animate: { opacity: 1, scale: 1, y: 0, transition: { duration: 0.22 } },
  exit: { opacity: 0, scale: 0.96, y: 16, transition: { duration: 0.18 } }
};
