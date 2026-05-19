// /media/yagaven_25/coding/Projects/codeNames/src/pages/LandingPage.jsx
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Gamepad2, ShieldCheck, Sparkles, Trophy, UsersRound } from 'lucide-react';
import { Button } from '../components/ui/Button.jsx';
import { Badge } from '../components/ui/Badge.jsx';
import { Footer } from '../components/layout/Footer.jsx';
import rangoliPattern from '../assets/patterns/rangoli-mandala.svg';
import circuitPattern from '../assets/patterns/india-circuit.svg';
import { mockRooms } from '../data/mockRooms.js';
import { formatNumber } from '../utils/helpers.js';

const features = [
  { icon: UsersRound, title: 'Real-time Addas', text: 'Private and public rooms for 2-16 players with ready checks and spectators.' },
  { icon: Sparkles, title: 'Indian Word Decks', text: 'Bollywood, cricket, food, festivals, cities, mythology, tech, politics, and history.' },
  { icon: ShieldCheck, title: 'Spymaster Mode', text: 'A color-coded hidden map, clue validation, and turn-safe team controls.' }
];

const stats = [
  ['Active rooms', mockRooms.length],
  ['Word cards', 100],
  ['Festival themes', 3],
  ['Mock events', 11]
];

const LandingPage = () => (
  <div className="min-h-screen overflow-hidden text-cream light:text-slate-950">
    <header className="absolute inset-x-0 top-0 z-30 px-4 py-5 sm:px-6 lg:px-8">
      <nav className="mx-auto flex max-w-7xl items-center justify-between" aria-label="Landing navigation">
        <Link to="/" className="flex items-center gap-3" aria-label="Codenames India home">
          <motion.span
            animate={{ rotate: [0, 4, -4, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
            className="grid h-11 w-11 place-items-center rounded-lg bg-gradient-to-br from-saffron to-emerald font-heading text-lg font-bold text-night shadow-saffron"
          >
            CI
          </motion.span>
          <span className="font-heading text-2xl font-bold">Codenames India</span>
        </Link>
        <div className="flex items-center gap-2">
          <Link className="hidden rounded-lg px-3 py-2 text-sm font-semibold text-cream/75 hover:text-saffron light:text-slate-700 sm:block" to="/leaderboard">
            Leaderboard
          </Link>
          <Link
            className="hidden h-11 items-center justify-center rounded-lg border border-white/15 bg-white/10 px-4 font-label text-sm font-semibold text-cream transition hover:border-saffron/60 hover:bg-white/15 light:text-slate-900 sm:inline-flex"
            to="/login"
            aria-label="Open login"
          >
            Login
          </Link>
        </div>
      </nav>
    </header>

    <main>
      <section className="relative min-h-[92vh] px-4 pb-16 pt-28 sm:px-6 lg:px-8">
        <img src={rangoliPattern} alt="" aria-hidden="true" className="absolute right-[-7rem] top-14 h-[28rem] w-[28rem] opacity-35 sm:h-[40rem] sm:w-[40rem]" />
        <img src={circuitPattern} alt="" aria-hidden="true" className="absolute bottom-8 left-1/2 hidden h-64 w-[32rem] -translate-x-1/2 rounded-[2rem] opacity-25 mix-blend-screen lg:block" />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(10,10,20,0)_0%,rgba(10,10,20,0.72)_82%)] light:hidden" />

        <div className="relative z-10 mx-auto flex max-w-7xl flex-col justify-center">
          <Badge tone="saffron" className="w-max">
            <Gamepad2 className="h-3.5 w-3.5" aria-hidden="true" />
            Live multiplayer mock ready
          </Badge>
          <h1 className="mt-5 max-w-4xl font-heading text-6xl font-bold leading-none sm:text-7xl lg:text-8xl">
            Codenames <span className="festival-text">India</span>
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-cream/75 light:text-slate-700 sm:text-xl">
            A festival-lit, culturally reimagined word strategy game for Indian players who know their chai from their Chandrayaan.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button as={Link} to="/dashboard" size="lg" icon={ArrowRight} aria-label="Start playing Codenames India">
              Start Playing
            </Button>
            <Button as={Link} to="/lobby/IND-2048" size="lg" variant="secondary" aria-label="Join featured lobby">
              Join IND-2048
            </Button>
          </div>
          <div className="mt-10 grid max-w-3xl grid-cols-2 gap-3 sm:grid-cols-4">
            {stats.map(([label, value]) => (
              <div key={label} className="glass-panel rounded-xl p-4">
                <p className="font-heading text-3xl font-bold text-cream light:text-slate-900">{formatNumber(value)}</p>
                <p className="text-xs font-semibold uppercase tracking-normal text-cream/50 light:text-slate-500">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-4 px-4 pb-14 sm:px-6 md:grid-cols-3 lg:px-8">
        {features.map(({ icon: Icon, title, text }) => (
          <article key={title} className="glass-panel rangoli-border rounded-2xl p-5">
            <Icon className="h-7 w-7 text-saffron" aria-hidden="true" />
            <h2 className="mt-4 font-heading text-2xl font-bold text-cream light:text-slate-900">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-cream/65 light:text-slate-600">{text}</p>
          </article>
        ))}
      </section>
    </main>
    <Footer />
  </div>
);

export default LandingPage;
