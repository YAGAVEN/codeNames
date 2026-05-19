// /media/yagaven_25/coding/Projects/codeNames/src/layouts/AuthLayout.jsx
import { Link, Outlet } from 'react-router-dom';
import rangoliPattern from '../assets/patterns/rangoli-mandala.svg';

export const AuthLayout = () => (
  <main className="relative min-h-screen overflow-hidden px-4 py-6 text-cream light:text-slate-950 sm:px-6 lg:px-8">
    <img
      src={rangoliPattern}
      alt=""
      className="pointer-events-none absolute -right-24 -top-20 h-80 w-80 opacity-35 blur-[1px] sm:h-[34rem] sm:w-[34rem]"
      aria-hidden="true"
    />
    <div className="relative z-10 mx-auto flex min-h-[calc(100vh-3rem)] max-w-6xl flex-col">
      <Link to="/" className="flex w-max items-center gap-3" aria-label="Codenames India home">
        <span className="grid h-10 w-10 place-items-center rounded-lg bg-gradient-to-br from-saffron to-emerald font-heading text-lg font-bold text-night shadow-saffron">
          CI
        </span>
        <span className="font-heading text-2xl font-bold">Codenames India</span>
      </Link>
      <div className="grid flex-1 items-center gap-8 py-8 lg:grid-cols-[0.9fr_1.1fr]">
        <section className="hidden lg:block">
          <p className="font-label text-sm uppercase tracking-[0.24em] text-saffron">Secure Adda Login</p>
          <h1 className="mt-3 max-w-xl font-heading text-6xl font-bold leading-none">
            Bring your crew, decode the country.
          </h1>
          <p className="mt-5 max-w-lg text-lg text-cream/70 light:text-slate-600">
            Create festival rooms, take the spymaster chair, and play words that feel like home.
          </p>
        </section>
        <Outlet />
      </div>
    </div>
  </main>
);
