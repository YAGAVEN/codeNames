// /media/yagaven_25/coding/Projects/codeNames/src/components/ui/Toast.jsx
import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { AlertCircle, CheckCircle2, Info, X, XCircle } from 'lucide-react';
import { Button } from './Button.jsx';
import { cn } from '../../utils/helpers.js';

const ToastContext = createContext(null);

const severity = {
  success: { icon: CheckCircle2, className: 'border-emerald/35 bg-emerald/15 text-emerald-100' },
  info: { icon: Info, className: 'border-blue-400/35 bg-blue-500/15 text-blue-100' },
  warning: { icon: AlertCircle, className: 'border-gold/35 bg-gold/15 text-amber-100' },
  error: { icon: XCircle, className: 'border-danger/35 bg-danger/15 text-red-100' }
};

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const showToast = useCallback(
    ({ title, message, type = 'info', duration = 4200 }) => {
      const id = crypto.randomUUID();
      setToasts((current) => [...current, { id, title, message, type }]);
      window.setTimeout(() => removeToast(id), duration);
      return id;
    },
    [removeToast]
  );

  const value = useMemo(() => ({ showToast, removeToast }), [removeToast, showToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed right-4 top-4 z-[60] flex w-[calc(100vw-2rem)] max-w-sm flex-col gap-3">
        <AnimatePresence initial={false}>
          {toasts.map((toast) => {
            const Icon = severity[toast.type]?.icon || Info;

            return (
              <motion.article
                key={toast.id}
                layout
                initial={{ opacity: 0, x: 32, scale: 0.96 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 28, scale: 0.96 }}
                className={cn('glass-panel flex items-start gap-3 rounded-xl p-3', severity[toast.type]?.className)}
              >
                <Icon className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
                <div className="min-w-0 flex-1">
                  <h3 className="font-label text-sm font-bold">{toast.title}</h3>
                  {toast.message ? <p className="mt-0.5 text-xs opacity-80">{toast.message}</p> : null}
                </div>
                <Button aria-label="Dismiss notification" variant="ghost" size="sm" className="h-8 px-2" onClick={() => removeToast(toast.id)}>
                  <X className="h-4 w-4" aria-hidden="true" />
                </Button>
              </motion.article>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);

  if (!context) {
    throw new Error('useToast must be used inside ToastProvider');
  }

  return context;
};
