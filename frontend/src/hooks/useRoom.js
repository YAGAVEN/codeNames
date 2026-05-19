// /media/yagaven_25/coding/Projects/codeNames/src/hooks/useRoom.js
import { useCallback, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSocket } from './useSocket.js';
import { SOCKET_EVENTS } from '../services/socket.js';
import { copyToClipboard, createRoomCode } from '../utils/helpers.js';

/**
 * Coordinates room creation, joining, and invite-link copying.
 */
export const useRoom = () => {
  const navigate = useNavigate();
  const { emit, setRoomCode } = useSocket();
  const [busy, setBusy] = useState(false);
  const [lastRoomCode, setLastRoomCode] = useState('IND-2048');

  const joinRoom = useCallback(
    async (roomCode) => {
      setBusy(true);
      const response = await emit(SOCKET_EVENTS.JOIN_ROOM, { roomCode });
      setRoomCode(response.roomCode);
      setLastRoomCode(response.roomCode);
      setBusy(false);
      navigate(`/lobby/${response.roomCode}`);
      return response;
    },
    [emit, navigate, setRoomCode]
  );

  const createRoom = useCallback(async () => {
    const roomCode = createRoomCode();
    return joinRoom(roomCode);
  }, [joinRoom]);

  const copyInvite = useCallback(async (roomCode = lastRoomCode) => {
    const url = `${window.location.origin}/lobby/${roomCode}`;
    return copyToClipboard(url);
  }, [lastRoomCode]);

  return useMemo(
    () => ({
      busy,
      lastRoomCode,
      joinRoom,
      createRoom,
      copyInvite
    }),
    [busy, copyInvite, createRoom, joinRoom, lastRoomCode]
  );
};
