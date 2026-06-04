// /media/yagaven_25/coding/Projects/codeNames/src/components/game/TeamPanel.jsx
import { UsersRound } from 'lucide-react';
import { PlayerAvatar } from '../lobby/PlayerAvatar.jsx';
import { Badge } from '../ui/Badge.jsx';
import { TEAM_STYLES } from '../../utils/constants.js';
import { cn } from '../../utils/helpers.js';

export const TeamPanel = ({ players, currentTurn }) => {
  const groups = ['red', 'blue', 'spectator'].map((team) => ({
    team,
    players: players.filter((player) => player.team === team)
  }));

  return (
    <section className="glass-panel rounded-2xl p-4">
      <div className="flex items-center gap-2">
        <UsersRound className="h-5 w-5 text-saffron" aria-hidden="true" />
        <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Teams</h2>
      </div>
      <div className="mt-4 space-y-3">
        {groups.map(({ team, players: teamPlayers }) => {
          const styles = TEAM_STYLES[team];

          return (
            <article
              key={team}
              className={cn(
                'rounded-xl border p-3 transition',
                styles.border,
                styles.bg,
                currentTurn === team && 'animate-pulseGlow ring-1 ring-saffron/40'
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <h3 className={cn('font-label font-bold', styles.text)}>{styles.label}</h3>
                <Badge tone={team === 'red' ? 'red' : team === 'blue' ? 'blue' : 'neutral'}>{teamPlayers.length}</Badge>
              </div>
              <div className="mt-3 space-y-2">
                {teamPlayers.slice(0, 8).map((player) => (
                  <div key={player.id} className="flex items-center gap-2 rounded-lg bg-white/5 p-2">
                    <PlayerAvatar player={player} size="sm" showLevel={false} />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold text-cream light:text-slate-900">{player.name}</p>
                      <p className="text-xs text-cream/50 light:text-slate-500">{player.role}</p>
                    </div>
                  </div>
                ))}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
};
