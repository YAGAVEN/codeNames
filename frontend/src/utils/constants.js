// /media/yagaven_25/coding/Projects/codeNames/src/utils/constants.js
export const CARD_TYPES = {
  HIDDEN: 'hidden',
  RED: 'red',
  BLUE: 'blue',
  NEUTRAL: 'neutral',
  ASSASSIN: 'assassin'
};

export const TEAM_TYPES = {
  RED: 'red',
  BLUE: 'blue',
  SPECTATOR: 'spectator'
};

export const ROOM_STATUSES = {
  WAITING: 'Waiting',
  IN_GAME: 'In Game',
  PRIVATE: 'Private'
};

export const ROUTES = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Leaderboard', path: '/leaderboard' },
  { label: 'Profile', path: '/profile' },
  { label: 'Settings', path: '/settings' }
];

export const GAME_ROUTES = [
  { label: 'Lobby', path: '/lobby/IND-2048' },
  { label: 'Game', path: '/game/IND-2048' },
  { label: 'Spymaster', path: '/spymaster/IND-2048' },
  { label: 'Results', path: '/results' }
];

export const FESTIVAL_THEMES = [
  { id: 'diwali', label: 'Diwali', accent: 'Saffron lamps', color: '#FF9933' },
  { id: 'holi', label: 'Holi', accent: 'Powder burst', color: '#EC4899' },
  { id: 'navratri', label: 'Navratri', accent: 'Garba night', color: '#A855F7' }
];

export const LANGUAGES = [
  { id: 'en', label: 'English' },
  { id: 'hi', label: 'Hindi' },
  { id: 'ta', label: 'Tamil' },
  { id: 'bn', label: 'Bengali' },
  { id: 'mr', label: 'Marathi' }
];

export const DEFAULT_ROOM_SETTINGS = {
  categories: ['Bollywood', 'Cricket', 'Indian Food', 'Cities', 'Festivals'],
  timerLength: 60,
  maxTeamSize: 8,
  visibility: 'public',
  passwordEnabled: false,
  spectatorMode: true
};

export const EMOJI_REACTIONS = ['🔥', '👏', '🤯', '😂', '🏏', '🪔', '💙', '🥳'];

export const TEAM_STYLES = {
  red: {
    label: 'Red Team',
    border: 'border-red-400/40',
    bg: 'bg-red-500/15',
    text: 'text-red-100',
    glow: 'shadow-[0_0_34px_rgba(239,68,68,0.28)]'
  },
  blue: {
    label: 'Blue Team',
    border: 'border-blue-400/40',
    bg: 'bg-blue-500/15',
    text: 'text-blue-100',
    glow: 'shadow-[0_0_34px_rgba(37,99,235,0.28)]'
  },
  spectator: {
    label: 'Spectators',
    border: 'border-white/15',
    bg: 'bg-white/5',
    text: 'text-cream',
    glow: 'shadow-card'
  }
};
