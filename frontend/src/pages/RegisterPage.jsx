// /media/yagaven_25/coding/Projects/codeNames/src/pages/RegisterPage.jsx
import { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CheckCircle2, UserPlus } from 'lucide-react';
import { motion } from 'framer-motion';
import { Button } from '../components/ui/Button.jsx';
import { Badge } from '../components/ui/Badge.jsx';
import { useToast } from '../components/ui/Toast.jsx';
import { useAuth } from '../hooks/useAuth.js';

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, status } = useAuth();
  const { showToast } = useToast();
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: ''
  });

  const checks = useMemo(
    () => [
      { label: 'Name has two characters', valid: form.name.trim().length >= 2 },
      { label: 'Email looks playable', valid: /\S+@\S+\.\S+/.test(form.email) },
      { label: 'Password has eight characters', valid: form.password.length >= 8 }
    ],
    [form]
  );
  const valid = checks.every((check) => check.valid);

  const submit = async (event) => {
    event.preventDefault();

    if (!valid) {
      showToast({ type: 'warning', title: 'Almost there', message: 'Complete the highlighted signup checks.' });
      return;
    }

    try {
      await register(form);
      showToast({ type: 'success', title: 'Account created', message: 'Your first Chai Master badge is unlocked.' });
      navigate('/dashboard');
    } catch (error) {
      showToast({ type: 'error', title: 'Signup failed', message: error.message });
    }
  };

  return (
    <section className="glass-panel-strong mx-auto w-full max-w-md rounded-2xl p-5 sm:p-6">
      <Badge tone="saffron">New Player Bonus +250 XP</Badge>
      <h1 className="mt-4 font-heading text-4xl font-bold text-cream light:text-slate-900">Register</h1>
      <p className="mt-1 text-sm text-cream/65 light:text-slate-600">Start with a profile, then invite your first team.</p>

      <form onSubmit={submit} className="mt-6 space-y-4">
        {[
          ['name', 'Display name', 'text'],
          ['email', 'Email', 'email'],
          ['password', 'Password', 'password']
        ].map(([key, label, type]) => (
          <label key={key} className="block">
            <span className="font-label text-sm font-semibold text-cream/75 light:text-slate-700">{label}</span>
            <input
              type={type}
              value={form[key]}
              onChange={(event) => setForm({ ...form, [key]: event.target.value })}
              aria-label={label}
              className="mt-2 w-full rounded-lg border border-white/10 bg-white/5 px-3 py-3 text-cream outline-none focus:border-saffron/60 light:text-slate-900"
              required
            />
          </label>
        ))}

        <div className="space-y-2 rounded-xl border border-white/10 bg-white/5 p-3">
          {checks.map((check) => (
            <motion.p
              key={check.label}
              animate={{ opacity: check.valid ? 1 : 0.58 }}
              className={`flex items-center gap-2 text-sm ${check.valid ? 'text-emerald' : 'text-cream/60 light:text-slate-500'}`}
            >
              <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
              {check.label}
            </motion.p>
          ))}
        </div>

        <Button type="submit" className="w-full" loading={status === 'loading'} icon={UserPlus} aria-label="Create Codenames India account">
          Create Account
        </Button>
      </form>

      <p className="mt-5 text-center text-sm text-cream/60 light:text-slate-600">
        Already have a team?{' '}
        <Link className="font-semibold text-saffron" to="/login">
          Login
        </Link>
      </p>
    </section>
  );
};

export default RegisterPage;
