// /media/yagaven_25/coding/Projects/codeNames/src/components/ui/Button.jsx
import { forwardRef, useMemo } from 'react';
import { Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/helpers.js';

const variants = {
  primary:
    'bg-gradient-to-r from-saffron via-gold to-emerald text-night shadow-saffron hover:shadow-[0_0_42px_rgba(255,153,51,0.5)]',
  secondary:
    'border border-white/15 bg-white/10 text-cream hover:border-saffron/60 hover:bg-white/15 dark:text-cream light:text-slate-900',
  ghost:
    'bg-transparent text-cream hover:bg-white/10 light:text-slate-700 light:hover:bg-slate-900/5',
  danger: 'bg-danger text-white shadow-[0_0_24px_rgba(239,68,68,0.28)] hover:bg-red-500',
  icon: 'border border-white/15 bg-white/10 text-cream hover:border-saffron/60 hover:bg-white/15'
};

const sizes = {
  sm: 'h-9 px-3 text-sm',
  md: 'h-11 px-4 text-sm',
  lg: 'h-12 px-5 text-base',
  icon: 'h-11 w-11 p-0'
};

export const Button = forwardRef(
  (
    {
      children,
      className,
      as: Component = 'button',
      variant = 'primary',
      size = variant === 'icon' ? 'icon' : 'md',
      loading = false,
      icon: Icon,
      type = 'button',
      disabled,
      ...props
    },
    ref
  ) => {
    const MotionComponent = useMemo(
      () => (Component === 'button' ? motion.button : motion.create(Component)),
      [Component]
    );
    const isNativeButton = Component === 'button';
    const disabledState = disabled || loading;

    return (
      <MotionComponent
        ref={ref}
        whileHover={disabledState ? undefined : { scale: 1.03 }}
        whileTap={disabledState ? undefined : { scale: 0.97 }}
        className={cn(
          'touch-target inline-flex items-center justify-center gap-2 rounded-lg font-label font-semibold transition duration-200 focus:outline-none focus:ring-2 focus:ring-saffron/60 focus:ring-offset-2 focus:ring-offset-night disabled:cursor-not-allowed disabled:opacity-55',
          variants[variant],
          sizes[size],
          disabledState && !isNativeButton && 'pointer-events-none opacity-55',
          className
        )}
        {...(isNativeButton ? { type, disabled: disabledState } : { 'aria-disabled': disabledState })}
        {...props}
      >
        {loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : Icon ? <Icon className="h-4 w-4" aria-hidden="true" /> : null}
        {children}
      </MotionComponent>
    );
  }
);

Button.displayName = 'Button';
