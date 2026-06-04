// /media/yagaven_25/coding/Projects/codeNames/src/context/GameContext.jsx
import { createContext, useCallback, useContext, useEffect, useMemo, useReducer, useRef } from 'react';
import { calculateScore, revealCardById } from '../services/gameLogic.js';
import { useSocket } from '../hooks/useSocket.js';
import { SOCKET_EVENTS } from '../services/socket.js';
import { DEFAULT_ROOM_SETTINGS, EMOJI_REACTIONS, TEAM_TYPES } from '../utils/constants.js';

const GameContext = createContext(null);

const emptyScore = {
  red: 0,
  blue: 0,
  neutral: 0,
  assassinRevealed: false,
  redTotal: 9,
  blueTotal: 8
};

const initialState = {
  room: null,
  players: [],
  board: [],
  spymasterBoard: [],
  serverScore: emptyScore,
  currentTurn: TEAM_TYPES.RED,
  clue: { word: '', count: 0, from: null },
  chatMessages: [],
  reactions: [],
  readyPlayers: [],
  roomSettings: DEFAULT_ROOM_SETTINGS,
  winner: null,
  timerSeconds: DEFAULT_ROOM_SETTINGS.timerLength,
  // gameStarted is true once the server broadcasts game_started.
  // Pages listen to this flag to trigger navigation.
  gameStarted: false
};

const normalizeClue = (clue = {}) => ({
  word: clue.word || '',
  count: Number(clue.count ?? clue.number ?? 0),
  remaining: Number(clue.remaining ?? clue.count ?? clue.number ?? 0),
  from: clue.from || null
});

const stripGeneratedSuffix = (value = '') => String(value).replace(/_[a-f0-9]{6}$/i, '');

const displayNameFromUsername = (value = '') =>
  stripGeneratedSuffix(value)
    .replace(/[^a-zA-Z0-9]+/g, ' ')
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
    .join(' ') || 'Player';

const displayHandleFromUsername = (value = '') => {
  const username = stripGeneratedSuffix(value)
    .toLowerCase()
    .replace(/[^a-z0-9_]+/g, '_')
    .replace(/^_+|_+$/g, '');
  return username ? `@${username}` : '';
};

/**
 * Build a normalised player object from a WebSocket event payload.
 * Prefers `username` and `name` fields (set by the updated backend join_room handler)
 * over the old UUID-based fallback.
 */
const playerFromEvent = (payload = {}) => {
  const id = String(payload.user_id || payload.playerId || payload.id || '');
  if (!id) {
    return null;
  }

  // The updated backend sends username and name in player_joined / team_changed events.
  const rawName = payload.name || payload.username || `Player ${id.slice(0, 6)}`;
  const displayName = displayNameFromUsername(rawName);

  return {
    id,
    name: displayName,
    handle: payload.username ? displayHandleFromUsername(payload.username) : '',
    team: payload.team || TEAM_TYPES.SPECTATOR,
    role:
      payload.role === 'spymaster'
        ? 'Spymaster'
        : payload.role === 'operative'
          ? 'Operative'
          : payload.role || 'Operative',
    status: 'online',
    level: Number(payload.level ?? 1),
    winRate: Number(payload.winRate ?? payload.win_rate ?? 0)
  };
};

const gameReducer = (state, action) => {
  switch (action.type) {
    case 'SET_ROOM_STATE': {
      const room = action.payload || {};
      const settings = room.settings || {};
      const roomInGame = room.status === 'In Game' || room.status === 'in_progress';
      return {
        ...state,
        room,
        players: room.players || state.players,
        readyPlayers: room.readyPlayers || state.readyPlayers,
        roomSettings: { ...state.roomSettings, ...settings },
        timerSeconds: Number(settings.timerLength || state.timerSeconds),
        gameStarted: roomInGame ? state.gameStarted : false
      };
    }
    case 'SET_BOARD':
      return {
        ...state,
        board: action.payload.board || [],
        serverScore: action.payload.score || state.serverScore
      };
    case 'SET_SPYMASTER_BOARD':
      return { ...state, spymasterBoard: action.payload || [] };
    case 'SET_SCORE':
      return { ...state, serverScore: { ...state.serverScore, ...action.payload } };
    case 'SET_TURN':
      return {
        ...state,
        currentTurn: action.payload || TEAM_TYPES.RED,
        clue: action.payload && action.payload === state.currentTurn ? state.clue : { word: '', count: 0, from: null }
      };
    case 'RESET_TURN':
      return { ...state, currentTurn: action.payload || TEAM_TYPES.RED, clue: { word: '', count: 0, from: null } };
    case 'SET_WINNER':
      return { ...state, winner: action.payload || null };
    case 'UPSERT_PLAYER': {
      const player = playerFromEvent(action.payload);
      if (!player) {
        return state;
      }
      const exists = state.players.some((item) => item.id === player.id);
      return {
        ...state,
        players: exists
          ? state.players.map((item) =>
              item.id === player.id
                ? {
                    // Preserve existing name if the new event has a UUID-based fallback
                    // (e.g. older ready_up events that don't include username).
                    ...item,
                    ...player,
                    name:
                      player.name && !player.name.startsWith('Player ')
                        ? player.name
                        : item.name || player.name
                  }
                : item
            )
          : [...state.players, player]
      };
    }
    case 'REMOVE_PLAYER': {
      const removeId = String(action.payload || '');
      return {
        ...state,
        players: state.players.filter((p) => p.id !== removeId),
        readyPlayers: state.readyPlayers.filter((id) => id !== removeId)
      };
    }
    case 'SET_READY': {
      const playerId = String(action.payload.playerId || action.payload.user_id || '');
      if (!playerId) {
        return state;
      }
      return {
        ...state,
        readyPlayers: action.payload.ready
          ? [...new Set([...state.readyPlayers, playerId])]
          : state.readyPlayers.filter((id) => id !== playerId)
      };
    }
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
    case 'APPLY_CARD': {
      const card = action.payload;
      const board = state.board.map((item) => (item.boardId === card.boardId ? { ...item, ...card } : item));
      const spymasterBoard = state.spymasterBoard.map((item) => (item.boardId === card.boardId ? { ...item, ...card } : item));
      return {
        ...state,
        board,
        spymasterBoard
      };
    }
    case 'GIVE_CLUE':
      return { ...state, clue: normalizeClue(action.payload), timerSeconds: state.roomSettings.timerLength };
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
        board: [],
        spymasterBoard: [],
        serverScore: emptyScore,
        currentTurn: TEAM_TYPES.RED,
        clue: { word: '', count: 0, from: null },
        winner: null,
        gameStarted: false,
        timerSeconds: state.roomSettings.timerLength
      };
    case 'GAME_STARTED_FROM_SERVER':
      return {
        ...state,
        gameStarted: true
      };
    case 'SET_TIMER':
      return { ...state, timerSeconds: action.payload };
    default:
      return state;
  }
};

export const GameProvider = ({ children }) => {
  const [state, dispatch] = useReducer(gameReducer, initialState);
  const processedEventSequenceRef = useRef(0);
  const { eventQueue } = useSocket();
  const setRoomState = useCallback((room) => dispatch({ type: 'SET_ROOM_STATE', payload: room }), []);

  useEffect(() => {
    if (!eventQueue.length) {
      processedEventSequenceRef.current = 0;
      return;
    }

    const pendingEvents = eventQueue.filter((event) => event.sequence > processedEventSequenceRef.current);
    if (!pendingEvents.length) {
      return;
    }

    for (const socketEvent of pendingEvents) {
      switch (socketEvent.event) {
        case SOCKET_EVENTS.GAME_STARTED:
          dispatch({
            type: 'SET_BOARD',
            payload: {
              board: socketEvent.board || [],
              score: socketEvent.scores
            }
          });
          dispatch({ type: 'RESET_TURN', payload: socketEvent.current_team });
          dispatch({ type: 'GIVE_CLUE', payload: socketEvent.current_clue || {} });
          dispatch({ type: 'SET_WINNER', payload: socketEvent.winner_team });
          dispatch({ type: 'GAME_STARTED_FROM_SERVER' });
          break;

        case SOCKET_EVENTS.BOARD_UPDATED:
          dispatch({ type: 'SET_BOARD', payload: { board: socketEvent.board || [], score: socketEvent.scores } });
          break;

        case SOCKET_EVENTS.SPYMASTER_BOARD_UPDATED:
          dispatch({ type: 'SET_SPYMASTER_BOARD', payload: socketEvent.board || [] });
          break;

        case SOCKET_EVENTS.CARD_REVEALED:
          if (socketEvent.card) {
            dispatch({ type: 'APPLY_CARD', payload: socketEvent.card });
          }
          break;

        case SOCKET_EVENTS.SCORE_UPDATED:
          dispatch({ type: 'SET_SCORE', payload: socketEvent.scores || {} });
          break;

        case SOCKET_EVENTS.TURN_CHANGED:
          dispatch({ type: 'SET_TURN', payload: socketEvent.current_team });
          break;

        case SOCKET_EVENTS.CLUE_RECEIVED:
          dispatch({ type: 'GIVE_CLUE', payload: socketEvent.clue || {} });
          break;

        case SOCKET_EVENTS.GAME_OVER:
          dispatch({ type: 'SET_WINNER', payload: socketEvent.winner_team });
          break;

        case SOCKET_EVENTS.PLAYER_JOINED:
          if (socketEvent.is_ready !== undefined) {
            dispatch({ type: 'SET_READY', payload: { playerId: socketEvent.user_id, ready: Boolean(socketEvent.is_ready) } });
          } else {
            dispatch({ type: 'UPSERT_PLAYER', payload: socketEvent });
          }
          break;

        case SOCKET_EVENTS.PLAYER_LEFT:
          dispatch({ type: 'REMOVE_PLAYER', payload: socketEvent.user_id });
          break;

        case SOCKET_EVENTS.TEAM_CHANGED:
          dispatch({ type: 'UPSERT_PLAYER', payload: socketEvent });
          break;

        case SOCKET_EVENTS.CHAT_MESSAGE:
          if (socketEvent.message) {
            dispatch({
              type: 'ADD_CHAT_MESSAGE',
              payload: {
                id: `${socketEvent.sender_id}-${socketEvent.receivedAt}`,
                author: playerFromEvent({ user_id: socketEvent.sender_id }),
                message: socketEvent.message,
                createdAt: socketEvent.receivedAt
              }
            });
          }
          break;

        case SOCKET_EVENTS.EMOJI_REACTION:
          if (socketEvent.reaction) {
            dispatch({ type: 'ADD_REACTION', payload: { emoji: socketEvent.reaction, player: playerFromEvent({ user_id: socketEvent.sender_id }) } });
          }
          break;

        default:
          break;
      }
    }
    processedEventSequenceRef.current = pendingEvents[pendingEvents.length - 1].sequence;
  }, [eventQueue]);

  const value = useMemo(
    () => ({
      ...state,
      score: state.board.length ? { ...calculateScore(state.board), ...state.serverScore } : state.serverScore,
      emojiOptions: EMOJI_REACTIONS,
      setRoomState,
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
    [setRoomState, state]
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
