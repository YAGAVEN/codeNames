// /media/yagaven_25/coding/Projects/codeNames/src/components/lobby/TeamSlot.jsx
import { Crown, ShieldCheck, UserPlus } from 'lucide-react';
import { motion } from 'framer-motion';
import { PlayerAvatar } from './PlayerAvatar.jsx';
import { Badge } from '../ui/Badge.jsx';
import { Button } from '../ui/Button.jsx';
import { TEAM_STYLES } from '../../utils/constants.js';
import { cn } from '../../utils/helpers.js';

export const TeamSlot = ({ team = 'red', players = [], readyPlayers = [], maxPlayers = 8, onJoin }) => {
  const styles = TEAM_STYLES[team];
  const spymaster = players.find((player) => player.role === 'Spymaster');
  const operatives = players.filter((player) => player.role !== 'Spymaster');

  return (
    <section className={cn('glass-panel rounded-2xl border p-4', styles.border, styles.glow)}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className={cn('font-heading text-2xl font-bold', styles.text)}>{styles.label}</h3>
          <p className="text-sm text-cream/60 light:text-slate-600">
            {players.length}/{maxPlayers} players ready for this side.
          </p>
        </div>
        <Badge tone={team === 'red' ? 'red' : team === 'blue' ? 'blue' : 'neutral'}>{readyPlayers.length} ready</Badge>
      </div>

      <div className="mt-4 space-y-3">
        {spymaster ? (
          <motion.div layout className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 p-3">
            <PlayerAvatar player={spymaster} />
            <div className="min-w-0 flex-1">
              <p className="truncate font-semibold text-cream light:text-slate-900">{spymaster.name}</p>
              <p className="flex items-center gap-1 text-xs text-saffron">
                <Crown className="h-3.5 w-3.5" aria-hidden="true" />
                Spymaster
              </p>
            </div>
            {readyPlayers.includes(spymaster.id) ? <ShieldCheck className="h-5 w-5 text-emerald" aria-label="Ready" /> : null}
          </motion.div>
        ) : null}

        <div className="grid gap-2 sm:grid-cols-2">
          {operatives.map((player) => (
            <motion.div key={player.id} layout className="flex items-center gap-2 rounded-lg bg-white/5 p-2">
              <PlayerAvatar player={player} size="sm" showLevel={false} />
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-cream light:text-slate-900">{player.name}</p>
                <p className="text-xs text-cream/50 light:text-slate-500">{readyPlayers.includes(player.id) ? 'Ready' : 'Choosing role'}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <Button className="mt-4 w-full" variant="secondary" icon={UserPlus} onClick={() => onJoin?.(team)} aria-label={`Join ${styles.label}`}>
        Join {styles.label}
      </Button>
    </section>
  );
};
