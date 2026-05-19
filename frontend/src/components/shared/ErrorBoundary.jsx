// /media/yagaven_25/coding/Projects/codeNames/src/components/shared/ErrorBoundary.jsx
import { useEffect, useState } from 'react';
import { AlertTriangle } from 'lucide-react';
import { Button } from '../ui/Button.jsx';

export const ErrorBoundary = ({ children }) => {
  const [error, setError] = useState(null);

  useEffect(() => {
    const onError = (event) => setError(event.error || new Error(event.message));
    const onRejection = (event) => setError(event.reason || new Error('Async action failed'));

    window.addEventListener('error', onError);
    window.addEventListener('unhandledrejection', onRejection);

    return () => {
      window.removeEventListener('error', onError);
      window.removeEventListener('unhandledrejection', onRejection);
    };
  }, []);

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center p-4">
        <section className="glass-panel max-w-md rounded-2xl p-6 text-center">
          <AlertTriangle className="mx-auto h-10 w-10 text-gold" aria-hidden="true" />
          <h1 className="mt-4 font-heading text-3xl font-bold text-cream light:text-slate-900">Game Room Error</h1>
          <p className="mt-2 text-sm text-cream/70 light:text-slate-600">
            Something interrupted this room session. Reset the view and the mock game state will keep running.
          </p>
          <Button className="mt-5" onClick={() => setError(null)}>
            Reset view
          </Button>
        </section>
      </main>
    );
  }

  return children;
};
