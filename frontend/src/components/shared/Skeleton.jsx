// /media/yagaven_25/coding/Projects/codeNames/src/components/shared/Skeleton.jsx
import { cn } from '../../utils/helpers.js';

export const Skeleton = ({ className }) => (
  <div className={cn('relative overflow-hidden rounded-lg bg-white/10 light:bg-slate-900/10', className)}>
    <div className="absolute inset-y-0 left-0 w-1/2 animate-shimmer bg-gradient-to-r from-transparent via-white/20 to-transparent" />
  </div>
);
