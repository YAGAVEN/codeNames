import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { getStoredToken } from './api.js';
import { createRoomCode } from '../utils/helpers.js';

const PRODUCTION_WS_URL = 'wss://codenames-india-api.onrender.com/ws';

// ── Event name constants ────────────────────────────────────────────────────
// Client-emitted (frontend → backend)
// Server-emitted (backend → frontend)
export const SOCKET_EVENTS = {
  // Client → Server
  JOIN_ROOM: 'join-room',
  LEAVE_ROOM: 'leave-room',
  CHANGE_TEAM: 'change-team',
  GIVE_CLUE: 'give-clue',
  MAKE_GUESS: 'make-guess',
  START_GAME: 'start-game',
  CHAT_MESSAGE: 'chat-message',
  EMOJI_REACTION: 'emoji-reaction',
  PLAYER_READY: 'player-ready',

  // Server → Client
  PLAYER_JOINED: 'player-joined',
  PLAYER_LEFT: 'player-left',
  TEAM_CHANGED: 'team-changed',
  GAME_STARTED: 'game-started',
  CARD_REVEALED: 'card-revealed',
  BOARD_UPDATED: 'board-updated',
  SPYMASTER_BOARD_UPDATED: 'spymaster-board-updated',
  SCORE_UPDATED: 'score-updated',
  TURN_CHANGED: 'turn-changed',
  CLUE_RECEIVED: 'clue-received',
  GAME_OVER: 'game-over',
  ERROR_MESSAGE: 'error-message',
  HEARTBEAT: 'heartbeat'
};

const buildWsFallback = () => {
  if (import.meta.env.PROD) {
    return PRODUCTION_WS_URL;
  }
  return 'ws://localhost:8000/ws';
};

export const WS_BASE_URL = (import.meta.env.VITE_WS_URL || buildWsFallback()).replace(/\/+$/, '');

// ── Client → Server event name mapping ─────────────────────────────────────
const backendEvents = {
  [SOCKET_EVENTS.JOIN_ROOM]: 'join_room',
  [SOCKET_EVENTS.LEAVE_ROOM]: 'leave_room',
  [SOCKET_EVENTS.CHANGE_TEAM]: 'change_team',
  [SOCKET_EVENTS.GIVE_CLUE]: 'give_clue',
  [SOCKET_EVENTS.MAKE_GUESS]: 'select_card',
  [SOCKET_EVENTS.START_GAME]: 'start_game',
  [SOCKET_EVENTS.CHAT_MESSAGE]: 'send_chat',
  [SOCKET_EVENTS.EMOJI_REACTION]: 'reaction',
  [SOCKET_EVENTS.PLAYER_READY]: 'ready_up'
};

// ── Server → Client event name mapping ─────────────────────────────────────
const frontendEvents = {
  player_joined: SOCKET_EVENTS.PLAYER_JOINED,
  player_left: SOCKET_EVENTS.PLAYER_LEFT,
  team_changed: SOCKET_EVENTS.TEAM_CHANGED,
  game_started: SOCKET_EVENTS.GAME_STARTED,
  card_revealed: SOCKET_EVENTS.CARD_REVEALED,
  board_updated: SOCKET_EVENTS.BOARD_UPDATED,
  spymaster_board_updated: SOCKET_EVENTS.SPYMASTER_BOARD_UPDATED,
  score_updated: SOCKET_EVENTS.SCORE_UPDATED,
  turn_changed: SOCKET_EVENTS.TURN_CHANGED,
  clue_received: SOCKET_EVENTS.CLUE_RECEIVED,
  game_over: SOCKET_EVENTS.GAME_OVER,
  error_message: SOCKET_EVENTS.ERROR_MESSAGE,
  chat_message: SOCKET_EVENTS.CHAT_MESSAGE,
  heartbeat: SOCKET_EVENTS.HEARTBEAT
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

/**
 * Map a raw client-side SOCKET_EVENTS key to the backend message format.
 * Returns null if the event should not be sent to the server.
 */
const toBackendMessage = (event, payload = {}) => {
  const backendEvent = backendEvents[event];
  if (!backendEvent) {
    return null;
  }

  const dataByEvent = {
    [SOCKET_EVENTS.JOIN_ROOM]: {},
    [SOCKET_EVENTS.LEAVE_ROOM]: {},
    [SOCKET_EVENTS.CHANGE_TEAM]: {
      team: payload.team || 'spectator'
    },
    [SOCKET_EVENTS.GIVE_CLUE]: {
      word: payload.clue?.word || payload.word,
      number: Number(payload.clue?.count || payload.number || payload.count || 1)
    },
    [SOCKET_EVENTS.MAKE_GUESS]: {
      card_index: cardIndexFromId(payload.cardId)
    },
    [SOCKET_EVENTS.START_GAME]: {
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
      is_ready: Boolean(payload.is_ready ?? payload.ready)
    }
  };

  return {
    event: backendEvent,
    data: dataByEvent[event] || payload
  };
};

/**
 * Normalize a raw server message into a flat frontend event object.
 * All data fields are promoted to top level so consumers can read
 * lastEvent.board, lastEvent.team, etc. directly.
 */
const fromBackendMessage = (message) => {
  // Ignore heartbeat pings — do not pollute lastEvent
  if (message.event === 'heartbeat') {
    return null;
  }

  let event = frontendEvents[message.event] || message.event;
  const data = message.data || {};

  // Remap chat_message with reaction field to emoji-reaction
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

/**
 * Low-level WebSocket client factory.
 * Keeps a listener registry for event-based consumption.
 */
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
    /**
     * Send a message to the server. Returns true if the message was queued/sent.
     * Does NOT return a synthetic ACK — callers should wait for the real server event.
     */
    send(event, payload = {}) {
      const message = toBackendMessage(event, payload);
      if (!message) {
        return false;
      }
      if (websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(message));
      } else {
        queued.push(message);
      }
      return true;
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

  websocket.addEventListener('message', (rawEvent) => {
    let parsed;
    try {
      parsed = JSON.parse(rawEvent.data);
    } catch {
      return;
    }
    const response = fromBackendMessage(parsed);
    if (!response) return; // heartbeat or unrecognized — skip
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

/**
 * React hook that manages a WebSocket connection for a given roomCode.
 *
 * Key design decisions:
 * - A new socket is only created when roomCode changes.
 * - `emit()` sends to the server but does NOT update lastEvent with synthetic ACKs.
 *   Only real server messages update lastEvent, preventing self-triggering loops.
 * - Heartbeat messages are suppressed so they don't clutter event consumers.
 */
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
        // Send join_room immediately so the server broadcasts our presence with
        // full username + team info to all connected clients.
        if (roomCode) {
          socketRef.current?.send(SOCKET_EVENTS.JOIN_ROOM, { roomCode });
        }
      },
      // Only real server events update lastEvent (not synthetic ACKs)
      onMessage: setLastEvent,
      onClose: () => setConnected(false),
      onError: () => setConnected(false)
    });

    return () => {
      if (roomCode) {
        socketRef.current?.send(SOCKET_EVENTS.LEAVE_ROOM, { roomCode });
      }
      socketRef.current?.disconnect();
      setConnected(false);
    };
  }, [roomCode]);

  /**
   * Send a message to the server.
   * Does NOT return a synthetic ACK — await a corresponding server event instead.
   * Returns a Promise<boolean> for backwards compatibility with callers that use await.
   */
  const emit = useCallback((event, payload) => {
    if (!socketRef.current) {
      return Promise.reject(new Error('Socket connection is not available.'));
    }
    const sent = socketRef.current.send(event, payload);
    return Promise.resolve(sent);
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
