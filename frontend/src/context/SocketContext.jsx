// /media/yagaven_25/coding/Projects/codeNames/src/context/SocketContext.jsx
import { createContext, useContext, useMemo, useState } from 'react';
import { SOCKET_EVENTS, useSocket as useSocketLifecycle } from '../services/socket.js';

const SocketContext = createContext(null);

export const SocketProvider = ({ children }) => {
  const [roomCode, setRoomCode] = useState('');
  const socketState = useSocketLifecycle(roomCode);

  const value = useMemo(
    () => ({
      ...socketState,
      roomCode,
      setRoomCode,
      events: SOCKET_EVENTS
    }),
    [roomCode, socketState]
  );

  return <SocketContext.Provider value={value}>{children}</SocketContext.Provider>;
};

export const useSocketContext = () => {
  const context = useContext(SocketContext);

  if (!context) {
    throw new Error('useSocketContext must be used inside SocketProvider');
  }

  return context;
};
