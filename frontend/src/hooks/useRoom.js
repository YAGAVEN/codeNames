// /media/yagaven_25/coding/Projects/codeNames/src/hooks/useRoom.js
import { useCallback, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSocket } from './useSocket.js';
import { createRoomRequest, joinRoomRequest } from '../services/api.js';
import { useToast } from '../components/ui/Toast.jsx';
import { copyToClipboard } from '../utils/helpers.js';

/**
 * Coordinates room creation, joining, and invite-link copying.
 */
export const useRoom = () => {
  const navigate = useNavigate();
  const { setRoomCode } = useSocket();
  const { showToast } = useToast();
  const [busy, setBusy] = useState(false);
  const [lastRoomCode, setLastRoomCode] = useState('');

  const enterRoom = useCallback(
    async (roomCode) => {
      if (!roomCode) {
        throw new Error('Room code is required to join.');
      }

      setRoomCode(roomCode);
      setLastRoomCode(roomCode);
      navigate(`/lobby/${roomCode}`);
      return { ok: true, roomCode };
    },
    [navigate, setRoomCode]
  );

  const joinRoom = useCallback(
    async (roomCode) => {
      setBusy(true);
      try {
        if (!roomCode) {
          throw new Error('Enter a room code to join.');
        }
        const room = await joinRoomRequest({ roomCode });
        return await enterRoom(room.code || roomCode);
      } catch (error) {
        showToast({ type: 'error', title: 'Join failed', message: error.message });
        return null;
      } finally {
        setBusy(false);
      }
    },
    [enterRoom, showToast]
  );

  const createRoom = useCallback(async () => {
    setBusy(true);
    try {
      const room = await createRoomRequest({
        settings: {
          name: 'New Adda',
          theme: 'Classic',
          wordPack: 'india'
        }
      });
      if (!room.code) {
        throw new Error('Room was created without a code.');
      }
      return await enterRoom(room.code);
    } catch (error) {
      showToast({ type: 'error', title: 'Room creation failed', message: error.message });
      return null;
    } finally {
      setBusy(false);
    }
  }, [enterRoom, showToast]);

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
