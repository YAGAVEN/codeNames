const PRODUCTION_API_URL = 'https://codenames-india-api.onrender.com/api';

const buildApiFallback = () => {
  if (import.meta.env.PROD) {
    return PRODUCTION_API_URL;
  }
  return 'http://localhost:8000/api';
};

export const API_BASE_URL = (import.meta.env.VITE_API_URL || buildApiFallback()).replace(/\/+$/, '');

const TOKEN_STORAGE_KEY = 'codenames-india-token';
const canUseStorage = () => typeof window !== 'undefined' && window.localStorage;

export const getStoredToken = () => {
  if (!canUseStorage()) {
    return null;
  }

  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
};

export const setStoredToken = (token) => {
  if (canUseStorage() && token) {
    window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
  }
};

export const clearStoredToken = () => {
  if (canUseStorage()) {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  }
};

const request = async (path, { method = 'GET', body, auth = true } = {}) => {
  const headers = {
    Accept: 'application/json'
  };
  const token = auth ? getStoredToken() : null;

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    credentials: 'include',
    body: body === undefined ? undefined : JSON.stringify(body)
  });
  const payload = await response.json().catch(() => ({}));

  if (!response.ok || payload.success === false) {
    const message = payload.error?.message || payload.detail || `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return payload.data ?? payload;
};

const titleCase = (value = '') =>
  value
    .replace(/[^a-zA-Z0-9]+/g, ' ')
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
    .join(' ');

const stripGeneratedSuffix = (value = '') => String(value).replace(/_[a-f0-9]{6}$/i, '');

const cleanUsername = (value = '') =>
  stripGeneratedSuffix(value)
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9_]+/g, '_')
    .replace(/^_+|_+$/g, '');

const displayNameFromUsername = (value = '') => titleCase(cleanUsername(value) || stripGeneratedSuffix(value) || 'player');

const displayHandleFromUsername = (value = '') => {
  const username = cleanUsername(value);
  return username ? `@${username}` : '';
};

const toUsername = ({ name, email }) => {
  const source = name || email?.split('@')[0] || 'player';
  const username = source
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9_]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 24);

  return username.length >= 3 ? username : `${username}player`.slice(0, 24);
};

export const normalizeUser = (user = {}) => {
  const id = String(user.id || user.user_id || '');
  const rawUsername = user.username || user.handle?.replace(/^@/, '') || user.name || 'player';
  const username = cleanUsername(rawUsername) || 'player';
  const wins = Number(user.win_count ?? user.wins ?? 0);
  const losses = Number(user.lose_count ?? user.losses ?? 0);
  const winRate = user.winRate ?? user.win_rate ?? (wins + losses > 0 ? Math.round((wins / (wins + losses)) * 100) : 0);
  const team = user.team || 'spectator';
  const matchHistory = user.matchHistory || user.match_history || [];

  return {
    id,
    name: displayNameFromUsername(user.name || rawUsername),
    handle: displayHandleFromUsername(user.handle?.replace(/^@/, '') || rawUsername),
    email: user.email,
    city: user.city || '',
    level: Number(user.level ?? 1),
    xp: Number(user.xp ?? 0),
    winRate,
    streak: Number(user.streak ?? 0),
    status: user.status || user.online_status || 'offline',
    team,
    role: user.role === 'player' ? 'Operative' : user.role || 'Operative',
    isReady: Boolean(user.isReady ?? user.is_ready),
    avatar: user.avatar || user.avatar_url || '',
    badges: Array.isArray(user.badges) ? user.badges : [],
    matchHistory: Array.isArray(matchHistory) ? matchHistory : []
  };
};

const normalizeRoomPlayer = (player = {}) => {
  const username = player.username || player.name || String(player.user_id || player.id || '').slice(0, 8) || 'player';
  const role = player.role === 'spymaster' ? 'Spymaster' : player.role === 'operative' ? 'Operative' : player.role || 'Operative';

  return normalizeUser({
    id: player.user_id || player.id,
    username,
    name: displayNameFromUsername(username),
    team: player.team || 'spectator',
    role,
    status: 'online',
    isReady: Boolean(player.is_ready ?? player.isReady)
  });
};

const normalizeRoom = (room = {}) => {
  const settings = room.settings || {};
  const code = room.code || room.roomCode || room.room_code || '';
  const status = room.status === 'in_progress' ? 'In Game' : room.status === 'waiting' ? 'Waiting' : room.status || 'Waiting';
  const host = room.host ? normalizeUser(room.host) : null;
  const players = (room.players || []).map(normalizeRoomPlayer);
  // Preserve host_id from backend (UUID string) for admin permission checks
  const hostId = room.host_id || room.hostId || (host ? host.id : null);

  return {
    id: String(room.id || code || ''),
    code,
    host_id: hostId ? String(hostId) : null,
    name: room.name || settings.name || settings.roomName || `${room.theme || settings.theme || 'Classic'} Room`,
    host,
    playerCount: Number(room.playerCount ?? room.player_count ?? room.players?.length ?? 0),
    maxPlayers: Number(room.maxPlayers ?? room.max_players ?? 10),
    status,
    theme: room.theme || settings.theme || settings.festivalTheme || 'Classic',
    privacy: room.privacy || (status === 'Private' ? 'Private' : 'Public'),
    settings,
    players,
    readyPlayers: players.filter((player) => player.isReady).map((player) => player.id)
  };
};

const normalizeLeaderboardEntry = (entry, index) => ({
  id: String(entry.id || `rank-${index + 1}`),
  rank: Number(entry.rank || index + 1),
  name: entry.name || titleCase(entry.username || `Player ${index + 1}`),
  country: entry.country || 'India',
  xp: Number(entry.xp || 0),
  streak: Number(entry.streak || 0),
  winRate: Number(entry.winRate ?? entry.win_rate ?? 0),
  badge: entry.badge || (index < 3 ? 'Maharaja Tier' : index < 10 ? 'Platinum Adda' : 'Gold Adda')
});

const normalizeDashboard = (dashboard = {}) => ({
  currentUser: dashboard.currentUser || dashboard.current_user ? normalizeUser(dashboard.currentUser || dashboard.current_user) : null,
  rooms: (dashboard.rooms || []).map(normalizeRoom),
  friends: (dashboard.friends || []).map(normalizeUser),
  friendRequests: dashboard.friendRequests || dashboard.friend_requests || [],
  achievements: dashboard.achievements || []
});

const buildAuthSession = async (tokens) => {
  const token = tokens.access_token || tokens.token;

  if (!token) {
    throw new Error('Backend did not return an access token');
  }

  setStoredToken(token);
  const user = await fetchCurrentUser();
  return { token, user };
};

export const fetchCurrentUser = async () => {
  return normalizeUser(await request('/users/me'));
};

export const loginUser = async ({ email, password }) => {
  const tokens = await request('/auth/login', {
    method: 'POST',
    auth: false,
    body: { email, password }
  });
  return buildAuthSession(tokens);
};

export const getGoogleLoginUrl = async () => {
  const response = await request('/auth/google', { auth: false });
  if (!response.url) {
    throw new Error('Backend did not return a Google login URL');
  }
  return response.url;
};

export const completeOAuthLogin = async ({ accessToken }) => {
  return buildAuthSession({ access_token: accessToken });
};

export const registerUser = async ({ name, email, password }) => {
  const tokens = await request('/auth/register', {
    method: 'POST',
    auth: false,
    body: {
      username: toUsername({ name, email }),
      email,
      password
    }
  });
  return buildAuthSession(tokens);
};

export const logoutUser = async () => {
  if (getStoredToken()) {
    await request('/auth/logout', { method: 'POST' });
  }

  clearStoredToken();
};

export const fetchDashboard = async () => {
  return normalizeDashboard(await request('/dashboard'));
};

export const fetchLeaderboard = async () => {
  const entries = await request('/leaderboard');
  return entries.map(normalizeLeaderboardEntry);
};

export const fetchPublicRooms = async () => request('/rooms/public');

export const fetchRoomByCode = async (roomCode) => {
  return normalizeRoom(await request(`/rooms/code/${encodeURIComponent(roomCode)}`));
};

export const requestPasswordReset = async (email) => {
  const response = await request('/auth/forgot-password', {
    method: 'POST',
    auth: false,
    body: { email }
  });
  return {
    ok: true,
    email,
    message: response.message
  };
};

export const createRoomRequest = async ({ maxPlayers = 10, settings = {} } = {}) => {
  return normalizeRoom(
    await request('/rooms/create', {
      method: 'POST',
      body: {
        max_players: maxPlayers,
        settings
      }
    })
  );
};

export const joinRoomRequest = async ({ roomCode, password, team = 'spectator' }) => {
  return normalizeRoom(
    await request('/rooms/join', {
      method: 'POST',
      body: {
        room_code: roomCode,
        password,
        team
      }
    })
  );
};
