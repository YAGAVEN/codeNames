// /media/yagaven_25/coding/Projects/codeNames/src/components/ui/Tooltip.jsx
import { cn } from '../../utils/helpers.js';

export const Tooltip = ({ label, children, side = 'top' }) => {
  const position = side === 'bottom' ? 'top-full mt-2' : 'bottom-full mb-2';

  return (
    <span className="group relative inline-flex">
      {children}
      <span
        role="tooltip"
        className={cn(
          'pointer-events-none absolute left-1/2 z-40 w-max max-w-48 -translate-x-1/2 rounded-md border border-white/10 bg-night px-2.5 py-1.5 text-xs text-cream opacity-0 shadow-card transition group-hover:opacity-100 group-focus-within:opacity-100',
          position
        )}
      >
        {label}
      </span>
    </span>
  );
};
