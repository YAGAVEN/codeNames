// /media/yagaven_25/coding/Projects/codeNames/src/data/leaderboard.js
const names = [
  ['Aarav Nair', 'India', 28400, 11],
  ['Saanvi Kapoor', 'India', 27120, 9],
  ['Ritvik Bose', 'India', 26650, 8],
  ['Prisha Reddy', 'India', 24880, 7],
  ['Vihaan Arora', 'India', 23920, 6],
  ['Maya Pillai', 'India', 23100, 5],
  ['Neel Shah', 'India', 22640, 5],
  ['Aisha Sheikh', 'India', 21990, 4],
  ['Yuvan Rao', 'India', 21430, 4],
  ['Sara Dutta', 'India', 20780, 3],
  ['Kian Gill', 'India', 19940, 3],
  ['Myra Joshi', 'India', 19200, 3],
  ['Reyansh Jain', 'India', 18590, 2],
  ['Inaya Thomas', 'India', 18110, 2],
  ['Advait Kulkarni', 'India', 17680, 2],
  ['Anika Sen', 'India', 16920, 2],
  ['Veer Malhotra', 'India', 16240, 1],
  ['Kiara Bhat', 'India', 15880, 1],
  ['Riya Chatterjee', 'India', 15120, 1],
  ['Omkar Patil', 'India', 14840, 1]
];

export const leaderboard = names.map(([name, country, xp, streak], index) => ({
  id: `rank-${index + 1}`,
  rank: index + 1,
  name,
  country,
  xp,
  streak,
  winRate: 72 - Math.min(index, 18),
  badge: index < 3 ? 'Maharaja Tier' : index < 10 ? 'Platinum Adda' : 'Gold Adda'
}));
