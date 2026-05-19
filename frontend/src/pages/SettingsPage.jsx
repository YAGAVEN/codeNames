// /media/yagaven_25/coding/Projects/codeNames/src/pages/SettingsPage.jsx
import { Bell, Languages, Moon, Music2, Palette, Sun } from 'lucide-react';
import { Badge } from '../components/ui/Badge.jsx';
import { Button } from '../components/ui/Button.jsx';
import { useToast } from '../components/ui/Toast.jsx';
import { useAuth } from '../hooks/useAuth.js';
import { FESTIVAL_THEMES, LANGUAGES } from '../utils/constants.js';

const themeSwatches = {
  diwali: 'bg-saffron',
  holi: 'bg-pink-500',
  navratri: 'bg-purple-500'
};

const SettingsPage = () => {
  const {
    theme,
    setTheme,
    festivalTheme,
    setFestivalTheme,
    language,
    setLanguage,
    soundEnabled,
    setSoundEnabled,
    notificationsEnabled,
    setNotificationsEnabled
  } = useAuth();
  const { showToast } = useToast();

  const announce = (title, message) => showToast({ type: 'success', title, message });

  return (
    <div className="space-y-5">
      <section className="glass-panel rangoli-border rounded-2xl p-5">
        <Badge tone="saffron">Bonus Page</Badge>
        <h1 className="mt-3 font-heading text-4xl font-bold text-cream light:text-slate-900">Settings</h1>
        <p className="text-cream/65 light:text-slate-600">Audio, theme, language, notifications, and festival identity.</p>
      </section>

      <div className="grid gap-5 lg:grid-cols-2">
        <section className="glass-panel rounded-2xl p-5">
          <div className="flex items-center gap-2">
            <Palette className="h-5 w-5 text-saffron" aria-hidden="true" />
            <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Festival Theme</h2>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            {FESTIVAL_THEMES.map((item) => (
              <button
                key={item.id}
                type="button"
                aria-pressed={festivalTheme === item.id}
                onClick={() => {
                  setFestivalTheme(item.id);
                  announce(`${item.label} theme active`, item.accent);
                }}
                className={`rounded-xl border p-4 text-left transition ${
                  festivalTheme === item.id ? 'border-saffron/55 bg-saffron/15' : 'border-white/10 bg-white/5 hover:border-white/25'
                }`}
              >
                <span className={`block h-3 w-10 rounded-full ${themeSwatches[item.id]}`} />
                <span className="mt-3 block font-heading text-xl font-bold text-cream light:text-slate-900">{item.label}</span>
                <span className="text-sm text-cream/55 light:text-slate-500">{item.accent}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="glass-panel rounded-2xl p-5">
          <div className="flex items-center gap-2">
            {theme === 'dark' ? <Moon className="h-5 w-5 text-saffron" aria-hidden="true" /> : <Sun className="h-5 w-5 text-saffron" aria-hidden="true" />}
            <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Display</h2>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <Button
              variant={theme === 'dark' ? 'primary' : 'secondary'}
              icon={Moon}
              onClick={() => setTheme('dark')}
              aria-label="Use dark mode"
            >
              Dark Mode
            </Button>
            <Button
              variant={theme === 'light' ? 'primary' : 'secondary'}
              icon={Sun}
              onClick={() => setTheme('light')}
              aria-label="Use light mode"
            >
              Light Mode
            </Button>
          </div>
        </section>

        <section className="glass-panel rounded-2xl p-5">
          <div className="flex items-center gap-2">
            <Music2 className="h-5 w-5 text-saffron" aria-hidden="true" />
            <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Audio & Alerts</h2>
          </div>
          <div className="mt-4 space-y-3">
            <label className="flex items-center justify-between gap-4 rounded-xl bg-white/5 p-4">
              <span>
                <span className="block font-semibold text-cream light:text-slate-900">Sound effects</span>
                <span className="text-sm text-cream/55 light:text-slate-500">Card flips, timers, wins, and joins.</span>
              </span>
              <input
                type="checkbox"
                checked={soundEnabled}
                onChange={(event) => setSoundEnabled(event.target.checked)}
                className="h-5 w-5 accent-saffron"
                aria-label="Toggle sound effects"
              />
            </label>
            <label className="flex items-center justify-between gap-4 rounded-xl bg-white/5 p-4">
              <span>
                <span className="flex items-center gap-2 font-semibold text-cream light:text-slate-900">
                  <Bell className="h-4 w-4 text-saffron" aria-hidden="true" />
                  Notifications
                </span>
                <span className="text-sm text-cream/55 light:text-slate-500">Friend invites, ready checks, and achievement unlocks.</span>
              </span>
              <input
                type="checkbox"
                checked={notificationsEnabled}
                onChange={(event) => setNotificationsEnabled(event.target.checked)}
                className="h-5 w-5 accent-saffron"
                aria-label="Toggle notifications"
              />
            </label>
          </div>
        </section>

        <section className="glass-panel rounded-2xl p-5">
          <div className="flex items-center gap-2">
            <Languages className="h-5 w-5 text-saffron" aria-hidden="true" />
            <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Language</h2>
          </div>
          <div className="mt-4 grid gap-2 sm:grid-cols-2">
            {LANGUAGES.map((item) => (
              <button
                key={item.id}
                type="button"
                aria-pressed={language === item.id}
                onClick={() => setLanguage(item.id)}
                className={`rounded-xl border px-4 py-3 text-left font-semibold transition ${
                  language === item.id ? 'border-emerald/45 bg-emerald/15 text-emerald' : 'border-white/10 bg-white/5 text-cream/70 hover:border-white/25 light:text-slate-700'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

export default SettingsPage;
