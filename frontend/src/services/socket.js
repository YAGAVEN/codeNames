import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { getStoredToken } from './api.js';
import { createRoomCode } from '../utils/helpers.js';

export const SOCKET_EVENTS = {
  JOIN_ROOM: 'join-room',
  LEAVE_ROOM: 'leave-room',
  GIVE_CLUE: 'give-clue',
  MAKE_GUESS: 'make-guess',
  PLAYER_JOINED: 'player-joined',
  GAME_STARTED: 'game-started',
  CARD_REVEALED: 'card-revealed',
  BOARD_UPDATED: 'board-updated',
  SPYMASTER_BOARD_UPDATED: 'spymaster-board-updated',
  SCORE_UPDATED: 'score-updated',
  TURN_CHANGED: 'turn-changed',
  CLUE_RECEIVED: 'clue-received',
  GAME_OVER: 'game-over',
  ERROR_MESSAGE: 'error-message',
  CHAT_MESSAGE: 'chat-message',
  EMOJI_REACTION: 'emoji-reaction',
  PLAYER_READY: 'player-ready'
};

const buildWsFallback = () => {
  if (import.meta.env.PROD) {
    if (typeof window !== 'undefined') {
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
      return `${protocol}://${window.location.host}/ws`;
    }
    return '/ws';
  }
  return 'ws://localhost:8000/ws';
};

export const WS_BASE_URL = (import.meta.env.VITE_WS_URL || buildWsFallback()).replace(/\/+$/, '');
const backendEvents = {
  [SOCKET_EVENTS.JOIN_ROOM]: 'join_room',
  [SOCKET_EVENTS.LEAVE_ROOM]: 'leave_room',
  [SOCKET_EVENTS.GIVE_CLUE]: 'give_clue',
  [SOCKET_EVENTS.MAKE_GUESS]: 'select_card',
  [SOCKET_EVENTS.GAME_STARTED]: 'start_game',
  [SOCKET_EVENTS.CHAT_MESSAGE]: 'send_chat',
  [SOCKET_EVENTS.EMOJI_REACTION]: 'reaction',
  [SOCKET_EVENTS.PLAYER_READY]: 'ready_up'
};

const frontendEvents = {
  player_joined: SOCKET_EVENTS.PLAYER_JOINED,
  game_started: SOCKET_EVENTS.GAME_STARTED,
  card_revealed: SOCKET_EVENTS.CARD_REVEALED,
  board_updated: SOCKET_EVENTS.BOARD_UPDATED,
  spymaster_board_updated: SOCKET_EVENTS.SPYMASTER_BOARD_UPDATED,
  score_updated: SOCKET_EVENTS.SCORE_UPDATED,
  turn_changed: SOCKET_EVENTS.TURN_CHANGED,
  clue_received: SOCKET_EVENTS.CLUE_RECEIVED,
  game_over: SOCKET_EVENTS.GAME_OVER,
  error_message: SOCKET_EVENTS.ERROR_MESSAGE,
  chat_message: SOCKET_EVENTS.CHAT_MESSAGE
};

const acknowledgementFor = (event, payload = {}) => {
  const base = {
    ok: true,
    event,
    receivedAt: new Date().toISOString()
  };

  const responses = {
    [SOCKET_EVENTS.JOIN_ROOM]: {
      ...base,
      roomCode: payload.roomCode || createRoomCode(),
      message: 'Joined the room adda.'
    },
    [SOCKET_EVENTS.LEAVE_ROOM]: {
      ...base,
      message: 'Left the room.'
    },
    [SOCKET_EVENTS.GIVE_CLUE]: {
      ...base,
      clue: payload.clue
    },
    [SOCKET_EVENTS.MAKE_GUESS]: {
      ...base,
      cardId: payload.cardId
    },
    [SOCKET_EVENTS.CARD_REVEALED]: {
      ...base,
      cardId: payload.cardId
    },
    [SOCKET_EVENTS.CHAT_MESSAGE]: {
      ...base,
      message: payload.message
    },
    [SOCKET_EVENTS.EMOJI_REACTION]: {
      ...base,
      emoji: payload.emoji
    },
    [SOCKET_EVENTS.PLAYER_READY]: {
      ...base,
      ready: payload.ready
    },
    [SOCKET_EVENTS.GAME_STARTED]: {
      ...base,
      roomCode: payload.roomCode
    }
  };

  return responses[event] || { ...base, payload };
};

const cardIndexFromId = (cardId) => {
  const raw = String(cardId ?? '').replace('card-', '');
  const index = Number(raw);
  return Number.isFinite(index) ? index : 0;
};

const normalizeCard = (card = {}) => {
  const index = Number(card.index ?? card.card_index ?? card.id ?? 0);
  const type = card.type || card.team || 'hidden';

  return {
    boardId: `card-${index}`,
    index,
    word: card.word || '',
    category: card.category || card.word_pack || '',
    type,
    revealed: Boolean(card.revealed),
    revealedBy: card.revealed_by || card.revealedBy || null
  };
};

const toBackendMessage = (event, payload = {}) => {
  if (event === SOCKET_EVENTS.CARD_REVEALED) {
    return null;
  }

  const backendEvent = backendEvents[event];
  if (!backendEvent) {
    return null;
  }

  const dataByEvent = {
    [SOCKET_EVENTS.JOIN_ROOM]: {},
    [SOCKET_EVENTS.LEAVE_ROOM]: {},
    [SOCKET_EVENTS.GIVE_CLUE]: {
      word: payload.clue?.word || payload.word,
      number: Number(payload.clue?.count || payload.number || payload.count || 1)
    },
    [SOCKET_EVENTS.MAKE_GUESS]: {
      card_index: cardIndexFromId(payload.cardId)
    },
    [SOCKET_EVENTS.GAME_STARTED]: {
      word_pack: payload.wordPack || 'india',
      seed: payload.seed || payload.roomCode || createRoomCode()
    },
    [SOCKET_EVENTS.CHAT_MESSAGE]: {
      message: payload.message || String(payload)
    },
    [SOCKET_EVENTS.EMOJI_REACTION]: {
      reaction: payload.emoji
    },
    [SOCKET_EVENTS.PLAYER_READY]: {
      is_ready: Boolean(payload.ready)
    }
  };

  return {
    event: backendEvent,
    data: dataByEvent[event] || payload
  };
};

const fromBackendMessage = (message) => {
  let event = frontendEvents[message.event] || message.event;
  const data = message.data || {};

  if (message.event === 'chat_message' && data.reaction) {
    event = SOCKET_EVENTS.EMOJI_REACTION;
  }

  return {
    ok: true,
    event,
    ...data,
    board: Array.isArray(data.board) ? data.board.map(normalizeCard) : undefined,
    card: data.card ? normalizeCard(data.card) : undefined,
    payload: data,
    receivedAt: new Date().toISOString()
  };
};

export const createSocketClient = (url, options = {}) => {
  const listeners = new Map();
  const queued = [];
  const websocket = new WebSocket(url);
  const client = {
    connected: false,
    id: `ws-${Date.now()}`,
    on(event, callback) {
      const current = listeners.get(event) || new Set();
      current.add(callback);
      listeners.set(event, current);
    },
    off(event, callback) {
      listeners.get(event)?.delete(callback);
    },
    async emit(event, payload = {}, acknowledgement) {
      const response = acknowledgementFor(event, payload);
      const message = toBackendMessage(event, payload);

      if (message) {
        if (websocket.readyState === WebSocket.OPEN) {
          websocket.send(JSON.stringify(message));
        } else {
          queued.push(message);
        }
      }

      acknowledgement?.(response);
      return response;
    },
    disconnect() {
      listeners.clear();
      websocket.close();
      this.connected = false;
    }
  };

  websocket.addEventListener('open', () => {
    client.connected = true;
    while (queued.length > 0) {
      websocket.send(JSON.stringify(queued.shift()));
    }
    options.onOpen?.();
  });

  websocket.addEventListener('message', (event) => {
    let parsed;
    try {
      parsed = JSON.parse(event.data);
    } catch {
      return;
    }
    const response = fromBackendMessage(parsed);
    listeners.get(response.event)?.forEach((callback) => callback(response));
    options.onMessage?.(response);
  });

  websocket.addEventListener('close', () => {
    client.connected = false;
    options.onClose?.();
  });

  websocket.addEventListener('error', () => {
    options.onError?.();
  });

  return client;
};

export const useSocket = (roomCode) => {
  const socketRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState(null);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      socketRef.current?.disconnect?.();
      socketRef.current = null;
      setConnected(false);
      setLastEvent(null);
      return undefined;
    }

    const url = `${WS_BASE_URL}/${encodeURIComponent(roomCode || 'lobby')}?token=${encodeURIComponent(token)}`;
    socketRef.current = createSocketClient(url, {
      onOpen: () => {
        setConnected(true);
        if (roomCode) {
          socketRef.current?.emit(SOCKET_EVENTS.JOIN_ROOM, { roomCode }).then(setLastEvent);
        }
      },
      onMessage: setLastEvent,
      onClose: () => setConnected(false),
      onError: () => setConnected(false)
    });

    return () => {
      if (roomCode) {
        socketRef.current?.emit(SOCKET_EVENTS.LEAVE_ROOM, { roomCode });
      }
      socketRef.current?.disconnect();
      setConnected(false);
    };
  }, [roomCode]);

  const emit = useCallback(async (event, payload) => {
    if (!socketRef.current) {
      throw new Error('Socket connection is not available.');
    }

    const response = await socketRef.current.emit(event, payload);
    setLastEvent(response);
    return response;
  }, []);

  return useMemo(
    () => ({
      socket: socketRef.current,
      connected,
      lastEvent,
      emit
    }),
    [connected, emit, lastEvent]
  );
};
