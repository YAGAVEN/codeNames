import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';
import { Badge } from '../components/ui/Badge.jsx';
import { useToast } from '../components/ui/Toast.jsx';
import { useAuth } from '../hooks/useAuth.js';

const readCallbackParams = () => {
  const hash = new URLSearchParams(window.location.hash.replace(/^#/, ''));
  const search = new URLSearchParams(window.location.search);
  return {
    accessToken: hash.get('access_token') || search.get('access_token'),
    error: hash.get('error_description') || hash.get('error') || search.get('error_description') || search.get('error')
  };
};

const AuthCallbackPage = () => {
  const navigate = useNavigate();
  const { completeOAuth } = useAuth();
  const { showToast } = useToast();

  useEffect(() => {
    const finish = async () => {
      const { accessToken, error } = readCallbackParams();

      if (error) {
        showToast({ type: 'error', title: 'Login failed', message: error });
        navigate('/login', { replace: true });
        return;
      }

      if (!accessToken) {
        showToast({ type: 'error', title: 'Login failed', message: 'Missing OAuth access token.' });
        navigate('/login', { replace: true });
        return;
      }

      try {
        await completeOAuth({ accessToken });
        navigate('/dashboard', { replace: true });
      } catch (callbackError) {
        showToast({ type: 'error', title: 'Login failed', message: callbackError.message });
        navigate('/login', { replace: true });
      }
    };

    finish();
  }, [completeOAuth, navigate, showToast]);

  return (
    <section className="glass-panel-strong mx-auto w-full max-w-md rounded-2xl p-6 text-center">
      <Badge tone="emerald">
        <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
        Secure callback
      </Badge>
      <h1 className="mt-4 font-heading text-4xl font-bold text-cream light:text-slate-900">Signing you in</h1>
      <p className="mt-2 text-sm text-cream/65 light:text-slate-600">Completing Google authentication.</p>
    </section>
  );
};

export default AuthCallbackPage;
