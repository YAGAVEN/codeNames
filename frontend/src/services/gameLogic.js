// /media/yagaven_25/coding/Projects/codeNames/src/services/gameLogic.js
import { CARD_TYPES } from '../utils/constants.js';

/**
 * Validates spymaster clues against current board words and clue count limits.
 */
export const validateClue = ({ word, count }, board) => {
  const trimmedWord = word.trim();

  if (trimmedWord.length < 2) {
    return 'Clue must be at least two letters.';
  }

  if (board.some((card) => card.word.toLowerCase() === trimmedWord.toLowerCase())) {
    return 'Clue cannot be one of the visible board words.';
  }

  if (!Number.isInteger(Number(count)) || Number(count) < 1 || Number(count) > 9) {
    return 'Pick a clue count from 1 to 9.';
  }

  return '';
};

/**
 * Reveals a card immutably and returns the updated board.
 */
export const revealCardById = (board, cardId) =>
  board.map((card) => (card.boardId === cardId ? { ...card, revealed: true } : card));

/**
 * Calculates live score counts for scoreboard panels.
 */
export const calculateScore = (board) => ({
  red: board.filter((card) => card.type === CARD_TYPES.RED && card.revealed).length,
  blue: board.filter((card) => card.type === CARD_TYPES.BLUE && card.revealed).length,
  neutral: board.filter((card) => card.type === CARD_TYPES.NEUTRAL && card.revealed).length,
  assassinRevealed: board.some((card) => card.type === CARD_TYPES.ASSASSIN && card.revealed),
  redTotal: board.filter((card) => card.type === CARD_TYPES.RED).length,
  blueTotal: board.filter((card) => card.type === CARD_TYPES.BLUE).length
});
