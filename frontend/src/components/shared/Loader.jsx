// /media/yagaven_25/coding/Projects/codeNames/src/components/shared/Loader.jsx
import { Loader2 } from 'lucide-react';
import { cn } from '../../utils/helpers.js';

export const Loader = ({ label = 'Loading Codenames India', className }) => (
  <div className={cn('flex items-center justify-center gap-3 text-cream/80 light:text-slate-600', className)}>
    <Loader2 className="h-5 w-5 animate-spin text-saffron" aria-hidden="true" />
    <span className="font-label text-sm font-semibold">{label}</span>
  </div>
);
