// /media/yagaven_25/coding/Projects/codeNames/src/services/api.js
import { achievements } from '../data/achievements.js';
import { leaderboard } from '../data/leaderboard.js';
import { mockPlayers, friendRequests } from '../data/mockPlayers.js';
import { mockRooms } from '../data/mockRooms.js';

const wait = (ms = 420) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Mock login request.
 * TODO: Replace with POST /auth/login and secure session handling.
 */
export const loginUser = async ({ email }) => {
  await wait();
  return {
    token: 'mock-token-codenames-india',
    user: {
      ...mockPlayers[0],
      email
    }
  };
};

/**
 * Mock registration request with profile bootstrap data.
 * TODO: Replace with POST /auth/register.
 */
export const registerUser = async ({ name, email }) => {
  await wait();
  return {
    token: 'mock-token-new-player',
    user: {
      ...mockPlayers[0],
      id: 'new-player',
      name,
      email,
      handle: `@${name.toLowerCase().replaceAll(' ', '_')}`,
      level: 1,
      xp: 250,
      winRate: 0,
      streak: 0,
      badges: [achievements[0]]
    }
  };
};

/**
 * Mock dashboard query combining profile, room, and social data.
 */
export const fetchDashboard = async () => {
  await wait(320);
  return {
    currentUser: mockPlayers[0],
    rooms: mockRooms,
    friends: mockPlayers.slice(1, 7),
    friendRequests,
    achievements
  };
};

/**
 * Mock leaderboard query.
 */
export const fetchLeaderboard = async () => {
  await wait(260);
  return leaderboard;
};

/**
 * Mock forgot password request.
 * TODO: Replace with POST /auth/forgot-password.
 */
export const requestPasswordReset = async (email) => {
  await wait(500);
  return {
    ok: true,
    email,
    message: 'Reset link sent. Check inbox and spam folders.'
  };
};
