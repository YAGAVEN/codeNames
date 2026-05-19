// /media/yagaven_25/coding/Projects/codeNames/src/components/game/Timer.jsx
import { useEffect } from 'react';
import { Clock3 } from 'lucide-react';
import { formatTime } from '../../utils/helpers.js';

export const Timer = ({ seconds, total = 60, running = true, onTick, onExpire }) => {
  const urgency = seconds <= 10;
  const percent = Math.max(0, Math.min(100, (seconds / total) * 100));

  useEffect(() => {
    if (!running || seconds <= 0) {
      if (seconds <= 0) {
        onExpire?.();
      }
      return undefined;
    }

    const timerId = window.setTimeout(() => onTick?.(seconds - 1), 1000);
    return () => window.clearTimeout(timerId);
  }, [onExpire, onTick, running, seconds]);

  return (
    <section className={`glass-panel rounded-2xl p-4 ${urgency ? 'animate-pulseGlow' : ''}`} aria-label="Turn timer">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Clock3 className={`h-5 w-5 ${urgency ? 'text-danger' : 'text-saffron'}`} aria-hidden="true" />
          <span className="font-label text-sm font-semibold text-cream/70 light:text-slate-600">Turn Timer</span>
        </div>
        <strong className={`font-heading text-3xl ${urgency ? 'text-danger' : 'text-cream light:text-slate-950'}`}>
          {formatTime(seconds)}
        </strong>
      </div>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
        <div
          className={`h-full rounded-full transition-all duration-500 ${urgency ? 'bg-danger' : 'bg-gradient-to-r from-saffron to-emerald'}`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </section>
  );
};
