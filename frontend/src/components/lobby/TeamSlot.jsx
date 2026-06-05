// /media/yagaven_25/coding/Projects/codeNames/src/components/lobby/TeamSlot.jsx
import { Crown, Eye, ShieldCheck, UserPlus } from 'lucide-react';
import { motion } from 'framer-motion';
import { PlayerAvatar } from './PlayerAvatar.jsx';
import { Badge } from '../ui/Badge.jsx';
import { Button } from '../ui/Button.jsx';
import { TEAM_STYLES } from '../../utils/constants.js';
import { cn } from '../../utils/helpers.js';

export const TeamSlot = ({ team = 'red', players = [], readyPlayers = [], maxPlayers = 8, onJoin, onChangeRole, currentUserId }) => {
  const styles = TEAM_STYLES[team];
  const spymaster = players.find((player) => player.role === 'Spymaster');
  const operatives = players.filter((player) => player.role !== 'Spymaster');
  const currentUserOnThisTeam = players.find((p) => p.id === currentUserId);

  return (
    <section className={cn('glass-panel rounded-2xl border p-4', styles.border, styles.glow)}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className={cn('font-heading text-2xl font-bold', styles.text)}>{styles.label}</h3>
          <p className="text-sm text-cream/60 light:text-slate-600">
            {players.length}/{maxPlayers} players
          </p>
        </div>
        <Badge tone={team === 'red' ? 'red' : team === 'blue' ? 'blue' : 'neutral'}>{readyPlayers.length} ready</Badge>
      </div>

      {/* Role picker — only shown when the current user is already on this team */}
      {currentUserOnThisTeam ? (
        <div className="mt-3 flex gap-2">
          <button
            type="button"
            aria-pressed={currentUserOnThisTeam.role === 'Spymaster'}
            onClick={() => onChangeRole?.('spymaster')}
            className={cn(
              'flex flex-1 items-center justify-center gap-1.5 rounded-lg border px-3 py-2 text-xs font-semibold transition',
              currentUserOnThisTeam.role === 'Spymaster'
                ? 'border-saffron/60 bg-saffron/15 text-saffron'
                : 'border-white/10 bg-white/5 text-cream/60 hover:border-white/25'
            )}
          >
            <Crown className="h-3.5 w-3.5" aria-hidden="true" />
            Spymaster
          </button>
          <button
            type="button"
            aria-pressed={currentUserOnThisTeam.role !== 'Spymaster'}
            onClick={() => onChangeRole?.('operative')}
            className={cn(
              'flex flex-1 items-center justify-center gap-1.5 rounded-lg border px-3 py-2 text-xs font-semibold transition',
              currentUserOnThisTeam.role !== 'Spymaster'
                ? 'border-saffron/60 bg-saffron/15 text-saffron'
                : 'border-white/10 bg-white/5 text-cream/60 hover:border-white/25'
            )}
          >
            <Eye className="h-3.5 w-3.5" aria-hidden="true" />
            Field Operative
          </button>
        </div>
      ) : null}

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
        ) : (
          <div className="flex items-center gap-2 rounded-xl border border-dashed border-white/15 p-3 text-sm text-cream/40">
            <Crown className="h-4 w-4" aria-hidden="true" />
            No Spymaster yet — pick a role above
          </div>
        )}

        <div className="grid gap-2 sm:grid-cols-2">
          {operatives.map((player) => (
            <motion.div key={player.id} layout className="flex items-center gap-2 rounded-lg bg-white/5 p-2">
              <PlayerAvatar player={player} size="sm" showLevel={false} />
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-cream light:text-slate-900">{player.name}</p>
                <p className="text-xs text-cream/50 light:text-slate-500">{readyPlayers.includes(player.id) ? 'Ready' : 'Field Operative'}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {!currentUserOnThisTeam ? (
        <Button className="mt-4 w-full" variant="secondary" icon={UserPlus} onClick={() => onJoin?.(team)} aria-label={`Join ${styles.label}`}>
          Join {styles.label}
        </Button>
      ) : null}
    </section>
  );
};
