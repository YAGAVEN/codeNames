// /media/yagaven_25/coding/Projects/codeNames/src/services/gameLogic.js
import { indianWords } from '../data/indianWords.js';
import { CARD_TYPES } from '../utils/constants.js';

const shuffle = (items) => [...items].sort(() => Math.random() - 0.5);

/**
 * Builds a 25-card Codenames board with a classic 9/8/7/1 distribution.
 * TODO: Move board generation server-side before enabling ranked games.
 */
export const generateGameBoard = (categories = []) => {
  const pool = categories.length
    ? indianWords.filter((word) => categories.includes(word.category))
    : indianWords;
  const selectedWords = shuffle(pool.length >= 25 ? pool : indianWords).slice(0, 25);
  const cardTypes = shuffle([
    ...Array(9).fill(CARD_TYPES.RED),
    ...Array(8).fill(CARD_TYPES.BLUE),
    ...Array(7).fill(CARD_TYPES.NEUTRAL),
    CARD_TYPES.ASSASSIN
  ]);

  return selectedWords.map((word, index) => ({
    ...word,
    boardId: `card-${index}`,
    type: cardTypes[index],
    revealed: false
  }));
};

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
