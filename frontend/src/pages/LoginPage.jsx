// /media/yagaven_25/coding/Projects/codeNames/src/pages/LoginPage.jsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Chrome, Mail, ShieldCheck } from 'lucide-react';
import { Button } from '../components/ui/Button.jsx';
import { Badge } from '../components/ui/Badge.jsx';
import { useToast } from '../components/ui/Toast.jsx';
import { useAuth } from '../hooks/useAuth.js';
import circuitPattern from '../assets/patterns/india-circuit.svg';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, status } = useAuth();
  const { showToast } = useToast();
  const [form, setForm] = useState({ email: 'anaya@codenames.in', password: 'spymaster' });

  const submit = async (event) => {
    event.preventDefault();
    await login(form);
    showToast({ type: 'success', title: 'Welcome back', message: 'Your Diwali streak is waiting.' });
    navigate('/dashboard');
  };

  return (
    <section className="glass-panel-strong mx-auto w-full max-w-md rounded-2xl p-5 sm:p-6">
      <img src={circuitPattern} alt="" aria-hidden="true" className="mb-5 h-28 w-full rounded-xl object-cover opacity-80" />
      <Badge tone="emerald">
        <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
        Secure mock session
      </Badge>
      <h1 className="mt-4 font-heading text-4xl font-bold text-cream light:text-slate-900">Login</h1>
      <p className="mt-1 text-sm text-cream/65 light:text-slate-600">Resume your room, ranked climb, and festival rewards.</p>

      <form onSubmit={submit} className="mt-6 space-y-4">
        <label className="block">
          <span className="font-label text-sm font-semibold text-cream/75 light:text-slate-700">Email</span>
          <input
            type="email"
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
            aria-label="Email address"
            className="mt-2 w-full rounded-lg border border-white/10 bg-white/5 px-3 py-3 text-cream outline-none focus:border-saffron/60 light:text-slate-900"
            required
          />
        </label>
        <label className="block">
          <span className="font-label text-sm font-semibold text-cream/75 light:text-slate-700">Password</span>
          <input
            type="password"
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
            aria-label="Password"
            className="mt-2 w-full rounded-lg border border-white/10 bg-white/5 px-3 py-3 text-cream outline-none focus:border-saffron/60 light:text-slate-900"
            required
          />
        </label>
        <div className="flex items-center justify-between text-sm">
          <label className="flex items-center gap-2 text-cream/65 light:text-slate-600">
            <input type="checkbox" defaultChecked className="accent-saffron" aria-label="Remember this device" />
            Remember device
          </label>
          <Link className="font-semibold text-saffron hover:text-gold" to="/forgot-password">
            Forgot password?
          </Link>
        </div>
        <Button type="submit" className="w-full" loading={status === 'loading'} icon={Mail} aria-label="Login with email">
          Login
        </Button>
      </form>

      <div className="mt-5 grid gap-2 sm:grid-cols-2">
        <Button variant="secondary" icon={Chrome} aria-label="Continue with Google">
          Google
        </Button>
        <Button variant="secondary" aria-label="Continue with phone OTP">
          Phone OTP
        </Button>
      </div>
      <p className="mt-5 text-center text-sm text-cream/60 light:text-slate-600">
        New to the adda?{' '}
        <Link className="font-semibold text-saffron" to="/register">
          Create account
        </Link>
      </p>
    </section>
  );
};

export default LoginPage;
