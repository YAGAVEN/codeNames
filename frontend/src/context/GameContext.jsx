// /media/yagaven_25/coding/Projects/codeNames/src/context/GameContext.jsx
import { createContext, useContext, useMemo, useReducer } from 'react';
import { mockPlayers } from '../data/mockPlayers.js';
import { mockRooms } from '../data/mockRooms.js';
import { calculateScore, generateGameBoard, revealCardById } from '../services/gameLogic.js';
import { DEFAULT_ROOM_SETTINGS, EMOJI_REACTIONS, TEAM_TYPES } from '../utils/constants.js';

const GameContext = createContext(null);

const initialBoard = generateGameBoard(DEFAULT_ROOM_SETTINGS.categories);

const initialState = {
  room: mockRooms[0],
  players: mockPlayers,
  board: initialBoard,
  currentTurn: TEAM_TYPES.RED,
  clue: { word: 'Monsoon', count: 3, from: mockPlayers[0] },
  chatMessages: [
    {
      id: 'chat-1',
      author: mockPlayers[0],
      message: 'Red team ready? Think food streets and cricket stands.',
      createdAt: new Date(Date.now() - 720000).toISOString()
    },
    {
      id: 'chat-2',
      author: mockPlayers[1],
      message: 'Blue spy network online. No peeking at the map.',
      createdAt: new Date(Date.now() - 420000).toISOString()
    }
  ],
  reactions: [],
  readyPlayers: ['p1', 'p2', 'p3', 'p4'],
  roomSettings: DEFAULT_ROOM_SETTINGS,
  winner: null,
  timerSeconds: DEFAULT_ROOM_SETTINGS.timerLength
};

const gameReducer = (state, action) => {
  switch (action.type) {
    case 'REVEAL_CARD': {
      const board = revealCardById(state.board, action.payload);
      const score = calculateScore(board);
      const winner =
        score.assassinRevealed || score.red === score.redTotal
          ? TEAM_TYPES.BLUE
          : score.blue === score.blueTotal
            ? TEAM_TYPES.RED
            : null;

      return {
        ...state,
        board,
        winner,
        currentTurn: state.currentTurn === TEAM_TYPES.RED ? TEAM_TYPES.BLUE : TEAM_TYPES.RED
      };
    }
    case 'GIVE_CLUE':
      return { ...state, clue: action.payload, timerSeconds: state.roomSettings.timerLength };
    case 'ADD_CHAT_MESSAGE':
      return { ...state, chatMessages: [...state.chatMessages, action.payload] };
    case 'ADD_REACTION':
      return {
        ...state,
        reactions: [...state.reactions.slice(-8), { id: crypto.randomUUID(), ...action.payload }]
      };
    case 'CLEAR_REACTION':
      return { ...state, reactions: state.reactions.filter((reaction) => reaction.id !== action.payload) };
    case 'TOGGLE_READY': {
      const isReady = state.readyPlayers.includes(action.payload);
      return {
        ...state,
        readyPlayers: isReady
          ? state.readyPlayers.filter((id) => id !== action.payload)
          : [...state.readyPlayers, action.payload]
      };
    }
    case 'UPDATE_ROOM_SETTINGS':
      return {
        ...state,
        roomSettings: { ...state.roomSettings, ...action.payload },
        timerSeconds: action.payload.timerLength || state.timerSeconds
      };
    case 'START_GAME':
      return {
        ...state,
        board: generateGameBoard(state.roomSettings.categories),
        winner: null,
        timerSeconds: state.roomSettings.timerLength
      };
    case 'SET_TIMER':
      return { ...state, timerSeconds: action.payload };
    default:
      return state;
  }
};

export const GameProvider = ({ children }) => {
  const [state, dispatch] = useReducer(gameReducer, initialState);

  const value = useMemo(
    () => ({
      ...state,
      score: calculateScore(state.board),
      emojiOptions: EMOJI_REACTIONS,
      revealCard: (cardId) => dispatch({ type: 'REVEAL_CARD', payload: cardId }),
      giveClue: (clue) => dispatch({ type: 'GIVE_CLUE', payload: clue }),
      addChatMessage: (message) => dispatch({ type: 'ADD_CHAT_MESSAGE', payload: message }),
      addReaction: (reaction) => dispatch({ type: 'ADD_REACTION', payload: reaction }),
      clearReaction: (reactionId) => dispatch({ type: 'CLEAR_REACTION', payload: reactionId }),
      toggleReady: (playerId) => dispatch({ type: 'TOGGLE_READY', payload: playerId }),
      updateRoomSettings: (settings) => dispatch({ type: 'UPDATE_ROOM_SETTINGS', payload: settings }),
      startGame: () => dispatch({ type: 'START_GAME' }),
      setTimer: (seconds) => dispatch({ type: 'SET_TIMER', payload: seconds })
    }),
    [state]
  );

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
};

export const useGameContext = () => {
  const context = useContext(GameContext);

  if (!context) {
    throw new Error('useGameContext must be used inside GameProvider');
  }

  return context;
};
