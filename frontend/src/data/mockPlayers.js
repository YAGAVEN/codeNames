// /media/yagaven_25/coding/Projects/codeNames/src/data/mockPlayers.js
import { achievements } from './achievements.js';

const resultPattern = ['Win', 'Win', 'Loss', 'Win', 'Win'];

const createMatchHistory = (seed, favoriteTeam) =>
  resultPattern.map((result, index) => ({
    id: `match-${seed}-${index}`,
    room: ['Marine Drive', 'Eden Night', 'Jaipur Rangoli', 'Startup Adda', 'Onam Arena'][index],
    result: (seed + index) % 4 === 0 ? 'Loss' : result,
    score: `${8 + ((seed + index) % 2)}-${6 + ((seed + index) % 3)}`,
    role: index % 2 === 0 ? 'Spymaster' : 'Operative',
    team: index % 2 === 0 ? favoriteTeam : favoriteTeam === 'red' ? 'blue' : 'red',
    playedAt: new Date(Date.now() - (seed + index + 1) * 86400000).toISOString()
  }));

export const mockPlayers = [
  {
    id: 'p1',
    name: 'Anaya Rao',
    handle: '@anaya_clues',
    city: 'Bengaluru',
    level: 32,
    xp: 18450,
    winRate: 68,
    streak: 7,
    status: 'online',
    team: 'red',
    role: 'Spymaster',
    avatar: '',
    badges: [achievements[0], achievements[1], achievements[4]],
    matchHistory: createMatchHistory(1, 'red')
  },
  {
    id: 'p2',
    name: 'Kabir Mehta',
    handle: '@kabir_cover',
    city: 'Mumbai',
    level: 29,
    xp: 16880,
    winRate: 63,
    streak: 5,
    status: 'online',
    team: 'blue',
    role: 'Spymaster',
    avatar: '',
    badges: [achievements[2], achievements[3]],
    matchHistory: createMatchHistory(2, 'blue')
  },
  {
    id: 'p3',
    name: 'Meera Iyer',
    handle: '@filter_kaapi',
    city: 'Chennai',
    level: 24,
    xp: 14210,
    winRate: 59,
    streak: 3,
    status: 'online',
    team: 'red',
    role: 'Operative',
    avatar: '',
    badges: [achievements[0], achievements[2]],
    matchHistory: createMatchHistory(3, 'red')
  },
  {
    id: 'p4',
    name: 'Arjun Singh',
    handle: '@cover_drive',
    city: 'Delhi',
    level: 27,
    xp: 15300,
    winRate: 61,
    streak: 4,
    status: 'away',
    team: 'blue',
    role: 'Operative',
    avatar: '',
    badges: [achievements[2], achievements[3]],
    matchHistory: createMatchHistory(4, 'blue')
  },
  {
    id: 'p5',
    name: 'Zoya Khan',
    handle: '@zoya_zing',
    city: 'Hyderabad',
    level: 19,
    xp: 9900,
    winRate: 57,
    streak: 2,
    status: 'online',
    team: 'red',
    role: 'Operative',
    avatar: '',
    badges: [achievements[1]],
    matchHistory: createMatchHistory(5, 'red')
  },
  {
    id: 'p6',
    name: 'Rohan Das',
    handle: '@mishti_moves',
    city: 'Kolkata',
    level: 21,
    xp: 11240,
    winRate: 54,
    streak: 1,
    status: 'offline',
    team: 'blue',
    role: 'Operative',
    avatar: '',
    badges: [achievements[4]],
    matchHistory: createMatchHistory(6, 'blue')
  },
  {
    id: 'p7',
    name: 'Nisha Patel',
    handle: '@garba_grid',
    city: 'Ahmedabad',
    level: 22,
    xp: 11920,
    winRate: 60,
    streak: 6,
    status: 'online',
    team: 'red',
    role: 'Operative',
    avatar: '',
    badges: [achievements[1], achievements[3]],
    matchHistory: createMatchHistory(7, 'red')
  },
  {
    id: 'p8',
    name: 'Dev Menon',
    handle: '@kochi_code',
    city: 'Kochi',
    level: 17,
    xp: 8400,
    winRate: 51,
    streak: 1,
    status: 'online',
    team: 'blue',
    role: 'Operative',
    avatar: '',
    badges: [achievements[0]],
    matchHistory: createMatchHistory(8, 'blue')
  },
  {
    id: 'p9',
    name: 'Tara Sharma',
    handle: '@tara_tactics',
    city: 'Jaipur',
    level: 15,
    xp: 7250,
    winRate: 49,
    streak: 2,
    status: 'away',
    team: 'spectator',
    role: 'Spectator',
    avatar: '',
    badges: [achievements[4]],
    matchHistory: createMatchHistory(9, 'red')
  },
  {
    id: 'p10',
    name: 'Ishaan Gill',
    handle: '@punjabi_pivot',
    city: 'Chandigarh',
    level: 18,
    xp: 9100,
    winRate: 56,
    streak: 3,
    status: 'online',
    team: 'spectator',
    role: 'Spectator',
    avatar: '',
    badges: [achievements[3]],
    matchHistory: createMatchHistory(10, 'blue')
  }
];

export const friendRequests = [
  { id: 'fr1', player: mockPlayers[4], message: 'Wants to join your next Bollywood room.' },
  { id: 'fr2', player: mockPlayers[7], message: 'Invited you to a weekend Kochi lobby.' }
];
