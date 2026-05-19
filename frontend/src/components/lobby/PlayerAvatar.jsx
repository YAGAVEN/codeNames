// /media/yagaven_25/coding/Projects/codeNames/src/components/lobby/PlayerAvatar.jsx
import { motion } from 'framer-motion';
import { Badge } from '../ui/Badge.jsx';
import { lobbyAvatarDrop } from '../../utils/animations.js';
import { cn, getInitials } from '../../utils/helpers.js';

const sizeClasses = {
  sm: 'h-9 w-9 text-xs',
  md: 'h-12 w-12 text-sm',
  lg: 'h-16 w-16 text-lg'
};

export const PlayerAvatar = ({ player, size = 'md', showLevel = true, className }) => {
  const onlineTone = player?.status === 'online' ? 'bg-emerald' : player?.status === 'away' ? 'bg-gold' : 'bg-slate-500';

  return (
    <motion.div variants={lobbyAvatarDrop} initial="initial" animate="animate" className={cn('relative inline-flex', className)}>
      <div
        className={cn(
          'grid shrink-0 place-items-center rounded-xl border border-white/15 bg-gradient-to-br from-saffron/80 to-indiaBlue/80 font-heading font-bold text-white shadow-card',
          sizeClasses[size]
        )}
        aria-label={`${player?.name || 'Player'} avatar`}
      >
        {player?.avatar ? <img src={player.avatar} alt="" className="h-full w-full rounded-xl object-cover" /> : getInitials(player?.name)}
      </div>
      <span className={cn('absolute -right-0.5 -top-0.5 h-3 w-3 rounded-full ring-2 ring-night', onlineTone)} />
      {showLevel ? (
        <Badge tone="saffron" className="absolute -bottom-2 left-1/2 -translate-x-1/2 px-1.5 py-0 text-[10px]">
          {player?.level}
        </Badge>
      ) : null}
    </motion.div>
  );
};
