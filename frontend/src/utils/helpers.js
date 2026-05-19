// /media/yagaven_25/coding/Projects/codeNames/src/utils/helpers.js
export const cn = (...classes) => classes.filter(Boolean).join(' ');

export const getInitials = (name = 'Player') =>
  name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

export const formatNumber = (value) =>
  new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: 0
  }).format(value);

export const formatPercent = (value) => `${Math.round(value)}%`;

export const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
    .toString()
    .padStart(2, '0');
  const secs = Math.max(0, seconds % 60)
    .toString()
    .padStart(2, '0');
  return `${mins}:${secs}`;
};

export const relativeTime = (isoDate) => {
  const diff = Date.now() - new Date(isoDate).getTime();
  const hours = Math.max(1, Math.round(diff / 36e5));
  return hours < 24 ? `${hours}h ago` : `${Math.round(hours / 24)}d ago`;
};

export const createRoomCode = () => {
  const suffix = Math.floor(1000 + Math.random() * 9000);
  return `IND-${suffix}`;
};

export const copyToClipboard = async (text) => {
  if (!navigator.clipboard) {
    return false;
  }

  await navigator.clipboard.writeText(text);
  return true;
};

export const pick = (items) => items[Math.floor(Math.random() * items.length)];
