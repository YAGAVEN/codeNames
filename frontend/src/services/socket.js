// /media/yagaven_25/coding/Projects/codeNames/src/services/socket.js
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { io } from 'socket.io-client';
import { createRoomCode } from '../utils/helpers.js';

export const SOCKET_EVENTS = {
  JOIN_ROOM: 'join-room',
  LEAVE_ROOM: 'leave-room',
  GIVE_CLUE: 'give-clue',
  MAKE_GUESS: 'make-guess',
  PLAYER_JOINED: 'player-joined',
  GAME_STARTED: 'game-started',
  CARD_REVEALED: 'card-revealed',
  GAME_OVER: 'game-over',
  CHAT_MESSAGE: 'chat-message',
  EMOJI_REACTION: 'emoji-reaction',
  PLAYER_READY: 'player-ready'
};

const delay = (ms = 360) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Creates a real Socket.io client for backend integration.
 * TODO: Replace mock mode in SocketContext with this once the multiplayer API is live.
 */
export const createSocketClient = (url, options = {}) =>
  io(url, {
    transports: ['websocket'],
    autoConnect: true,
    ...options
  });

/**
 * Emits mock socket events and resolves with server-shaped dummy payloads.
 */
export const mockEmit = async (event, payload = {}) => {
  await delay(280 + Math.random() * 360);

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
    }
  };

  return responses[event] || { ...base, payload };
};

/**
 * Minimal event bus that mimics Socket.io on/off/emit for local UI flows.
 */
export const createMockSocket = () => {
  const listeners = new Map();

  return {
    connected: true,
    id: `mock-${Date.now()}`,
    on(event, callback) {
      const current = listeners.get(event) || new Set();
      current.add(callback);
      listeners.set(event, current);
    },
    off(event, callback) {
      listeners.get(event)?.delete(callback);
    },
    async emit(event, payload, acknowledgement) {
      const response = await mockEmit(event, payload);
      listeners.get(event)?.forEach((callback) => callback(response));
      acknowledgement?.(response);
      return response;
    },
    disconnect() {
      listeners.clear();
      this.connected = false;
    }
  };
};

/**
 * Hook wrapping the mock Socket.io lifecycle and room connection state.
 */
export const useSocket = (roomCode) => {
  const socketRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState(null);

  useEffect(() => {
    socketRef.current = createMockSocket();
    setConnected(true);

    if (roomCode) {
      socketRef.current.emit(SOCKET_EVENTS.JOIN_ROOM, { roomCode }).then(setLastEvent);
    }

    return () => {
      if (roomCode) {
        socketRef.current?.emit(SOCKET_EVENTS.LEAVE_ROOM, { roomCode });
      }
      socketRef.current?.disconnect();
      setConnected(false);
    };
  }, [roomCode]);

  const emit = useCallback(async (event, payload) => {
    const response = await socketRef.current?.emit(event, payload);
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
