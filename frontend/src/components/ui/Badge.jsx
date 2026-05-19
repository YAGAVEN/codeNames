// /media/yagaven_25/coding/Projects/codeNames/src/components/ui/Badge.jsx
import { cn } from '../../utils/helpers.js';

const toneClasses = {
  saffron: 'border-saffron/35 bg-saffron/15 text-orange-100 light:text-orange-700',
  emerald: 'border-emerald/35 bg-emerald/15 text-emerald-100 light:text-emerald-700',
  blue: 'border-blue-400/35 bg-blue-500/15 text-blue-100 light:text-blue-700',
  red: 'border-red-400/35 bg-red-500/15 text-red-100 light:text-red-700',
  neutral: 'border-white/15 bg-white/10 text-cream light:text-slate-700'
};

export const Badge = ({ children, tone = 'neutral', className }) => (
  <span
    className={cn(
      'inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-label font-semibold',
      toneClasses[tone],
      className
    )}
  >
    {children}
  </span>
);
