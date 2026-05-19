// /media/yagaven_25/coding/Projects/codeNames/src/pages/ForgotPasswordPage.jsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { MailCheck, Send } from 'lucide-react';
import { Button } from '../components/ui/Button.jsx';
import { Badge } from '../components/ui/Badge.jsx';
import { requestPasswordReset } from '../services/api.js';

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('anaya@codenames.in');
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true);
    await requestPasswordReset(email);
    setLoading(false);
    setStep(2);
  };

  return (
    <section className="glass-panel-strong mx-auto w-full max-w-md rounded-2xl p-5 sm:p-6">
      <Badge tone={step === 2 ? 'emerald' : 'saffron'}>{step === 2 ? 'Check inbox' : 'Step 1 of 2'}</Badge>
      <h1 className="mt-4 font-heading text-4xl font-bold text-cream light:text-slate-900">Reset Password</h1>
      <p className="mt-1 text-sm text-cream/65 light:text-slate-600">
        Get a secure reset link and return to your room without losing your streak.
      </p>

      <div className="mt-6 grid grid-cols-2 gap-2" aria-label="Password reset steps">
        {['Email', 'Verify'].map((label, index) => (
          <div key={label} className={`rounded-full px-3 py-2 text-center text-xs font-bold ${step > index ? 'bg-emerald/20 text-emerald' : 'bg-white/5 text-cream/50'}`}>
            {label}
          </div>
        ))}
      </div>

      {step === 1 ? (
        <form onSubmit={submit} className="mt-6 space-y-4">
          <label className="block">
            <span className="font-label text-sm font-semibold text-cream/75 light:text-slate-700">Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              aria-label="Password reset email"
              className="mt-2 w-full rounded-lg border border-white/10 bg-white/5 px-3 py-3 text-cream outline-none focus:border-saffron/60 light:text-slate-900"
              required
            />
          </label>
          <Button type="submit" className="w-full" loading={loading} icon={Send} aria-label="Send password reset link">
            Send Reset Link
          </Button>
        </form>
      ) : (
        <div className="mt-6 rounded-2xl border border-emerald/25 bg-emerald/10 p-5 text-center">
          <MailCheck className="mx-auto h-10 w-10 text-emerald" aria-hidden="true" />
          <h2 className="mt-3 font-heading text-2xl font-bold text-cream light:text-slate-900">Link sent</h2>
          <p className="mt-2 text-sm text-cream/65 light:text-slate-600">We sent a reset link to {email}. It expires after one match-length session.</p>
          <Button as={Link} to="/login" className="mt-5" variant="secondary" aria-label="Return to login">
            Back to login
          </Button>
        </div>
      )}
    </section>
  );
};

export default ForgotPasswordPage;
