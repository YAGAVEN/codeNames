// /media/yagaven_25/coding/Projects/codeNames/src/hooks/useSocket.js
import { useSocketContext } from '../context/SocketContext.jsx';

/**
 * Provides global mock Socket.io connection state and emit helpers.
 */
export const useSocket = () => useSocketContext();
