// /media/yagaven_25/coding/Projects/codeNames/src/hooks/useGame.js
import { useGameContext } from '../context/GameContext.jsx';

/**
 * Provides shared game board, teams, clue, timer, and room actions.
 */
export const useGame = () => useGameContext();
