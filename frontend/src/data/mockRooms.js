// /media/yagaven_25/coding/Projects/codeNames/src/data/mockRooms.js
import { DEFAULT_ROOM_SETTINGS, ROOM_STATUSES } from '../utils/constants.js';
import { mockPlayers } from './mockPlayers.js';

export const mockRooms = [
  {
    id: 'room-1',
    code: 'IND-2048',
    name: 'Marine Drive Mind Games',
    host: mockPlayers[0],
    playerCount: 8,
    maxPlayers: 16,
    status: ROOM_STATUSES.WAITING,
    theme: 'Diwali',
    privacy: 'Public',
    settings: DEFAULT_ROOM_SETTINGS
  },
  {
    id: 'room-2',
    code: 'BOL-786',
    name: 'Bollywood Blockbuster',
    host: mockPlayers[1],
    playerCount: 10,
    maxPlayers: 16,
    status: ROOM_STATUSES.IN_GAME,
    theme: 'Holi',
    privacy: 'Public',
    settings: {
      ...DEFAULT_ROOM_SETTINGS,
      categories: ['Bollywood', 'Indian Food', 'Cities'],
      timerLength: 45
    }
  },
  {
    id: 'room-3',
    code: 'IPL-108',
    name: 'Gully Cricket Strategy',
    host: mockPlayers[3],
    playerCount: 5,
    maxPlayers: 12,
    status: ROOM_STATUSES.PRIVATE,
    theme: 'Navratri',
    privacy: 'Private',
    settings: {
      ...DEFAULT_ROOM_SETTINGS,
      categories: ['Cricket', 'Indian Tech/Startups', 'History'],
      passwordEnabled: true,
      maxTeamSize: 6
    }
  }
];
