// /media/yagaven_25/coding/Projects/codeNames/src/components/ui/Modal.jsx
import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import { Button } from './Button.jsx';
import { modalTransition } from '../../utils/animations.js';
import { cn } from '../../utils/helpers.js';

export const Modal = ({ open, title, description, children, onClose, className }) => (
  <AnimatePresence>
    {open ? (
      <motion.div
        className="fixed inset-0 z-50 flex items-end justify-center bg-black/65 p-0 backdrop-blur-md sm:items-center sm:p-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        role="presentation"
      >
        <motion.section
          variants={modalTransition}
          initial="initial"
          animate="animate"
          exit="exit"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          aria-describedby={description ? 'modal-description' : undefined}
          className={cn(
            'glass-panel-strong safe-bottom max-h-[92vh] w-full overflow-y-auto rounded-t-2xl p-5 sm:max-w-lg sm:rounded-2xl sm:p-6',
            className
          )}
        >
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 id="modal-title" className="font-heading text-2xl font-bold text-cream light:text-slate-900">
                {title}
              </h2>
              {description ? (
                <p id="modal-description" className="mt-1 text-sm text-cream/70 light:text-slate-600">
                  {description}
                </p>
              ) : null}
            </div>
            <Button aria-label="Close modal" variant="icon" icon={X} onClick={onClose} />
          </div>
          <div className="mt-5">{children}</div>
        </motion.section>
      </motion.div>
    ) : null}
  </AnimatePresence>
);
