// /media/yagaven_25/coding/Projects/codeNames/src/components/lobby/RoomSettings.jsx
import { Lock, TimerReset, Unlock } from 'lucide-react';
import { Badge } from '../ui/Badge.jsx';
import { Button } from '../ui/Button.jsx';
import { useGame } from '../../hooks/useGame.js';
import { WORD_PACK_OPTIONS } from '../../utils/constants.js';

export const RoomSettings = () => {
  const { roomSettings, updateRoomSettings } = useGame();

  return (
    <section className="glass-panel rounded-2xl p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Room Settings</h2>
          <p className="text-sm text-cream/60 light:text-slate-600">Tune word pack, timer, team sizes, and privacy.</p>
        </div>
        <Badge tone={roomSettings.visibility === 'private' ? 'red' : 'emerald'}>
          {roomSettings.visibility === 'private' ? 'Private' : 'Public'}
        </Badge>
      </div>

      <div className="mt-4">
        <p className="font-label text-sm font-semibold text-cream/75 light:text-slate-700">Word pack</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {WORD_PACK_OPTIONS.map((pack) => {
            const selected = roomSettings.wordPack === pack.id;

            return (
              <button
                key={pack.id}
                type="button"
                aria-pressed={selected}
                onClick={() => updateRoomSettings({ wordPack: pack.id })}
                className={`rounded-full border px-3 py-2 text-xs font-semibold transition ${
                  selected
                    ? 'border-saffron/50 bg-saffron/15 text-orange-100 light:text-orange-700'
                    : 'border-white/10 bg-white/5 text-cream/60 hover:border-white/25 light:text-slate-600'
                }`}
              >
                {pack.label}
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <label className="space-y-2">
          <span className="flex items-center gap-2 font-label text-sm font-semibold text-cream/75 light:text-slate-700">
            <TimerReset className="h-4 w-4 text-saffron" aria-hidden="true" />
            Timer length
          </span>
          <input
            aria-label="Timer length in seconds"
            type="range"
            min="30"
            max="120"
            step="15"
            value={roomSettings.timerLength}
            onChange={(event) => updateRoomSettings({ timerLength: Number(event.target.value) })}
            className="w-full accent-saffron"
          />
          <Badge tone="saffron">{roomSettings.timerLength}s</Badge>
        </label>

        <label className="space-y-2">
          <span className="font-label text-sm font-semibold text-cream/75 light:text-slate-700">Max team size</span>
          <input
            aria-label="Maximum team size"
            type="number"
            min="2"
            max="8"
            value={roomSettings.maxTeamSize}
            onChange={(event) => updateRoomSettings({ maxTeamSize: Number(event.target.value) })}
            className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-3 text-cream outline-none focus:border-saffron/60 light:text-slate-900"
          />
        </label>
      </div>

      <div className="mt-5 grid gap-2 sm:grid-cols-2">
        <Button
          variant={roomSettings.visibility === 'private' ? 'primary' : 'secondary'}
          icon={roomSettings.visibility === 'private' ? Lock : Unlock}
          onClick={() => updateRoomSettings({ visibility: roomSettings.visibility === 'private' ? 'public' : 'private' })}
          aria-label="Toggle public or private room"
        >
          {roomSettings.visibility === 'private' ? 'Private room' : 'Public room'}
        </Button>
        <Button
          variant={roomSettings.passwordEnabled ? 'primary' : 'secondary'}
          icon={Lock}
          onClick={() => updateRoomSettings({ passwordEnabled: !roomSettings.passwordEnabled })}
          aria-label="Toggle room password"
        >
          Password {roomSettings.passwordEnabled ? 'on' : 'off'}
        </Button>
      </div>
    </section>
  );
};
