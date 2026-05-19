// /media/yagaven_25/coding/Projects/codeNames/src/components/game/ClueInput.jsx
import { useState } from 'react';
import { Lightbulb, Send } from 'lucide-react';
import { Button } from '../ui/Button.jsx';
import { useToast } from '../ui/Toast.jsx';
import { useAuth } from '../../hooks/useAuth.js';
import { useGame } from '../../hooks/useGame.js';
import { useSocket } from '../../hooks/useSocket.js';
import { validateClue } from '../../services/gameLogic.js';
import { SOCKET_EVENTS } from '../../services/socket.js';

export const ClueInput = ({ compact = false }) => {
  const { user } = useAuth();
  const { board, giveClue } = useGame();
  const { emit } = useSocket();
  const { showToast } = useToast();
  const [word, setWord] = useState('');
  const [count, setCount] = useState(2);
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    const error = validateClue({ word, count }, board);

    if (error) {
      showToast({ type: 'warning', title: 'Clue needs a tweak', message: error });
      return;
    }

    setLoading(true);
    const clue = { word: word.trim(), count: Number(count), from: user };
    giveClue(clue);
    await emit(SOCKET_EVENTS.GIVE_CLUE, { clue });
    setLoading(false);
    setWord('');
    showToast({ type: 'success', title: 'Clue sent', message: `${clue.word} for ${clue.count}` });
  };

  return (
    <form onSubmit={submit} className="glass-panel rounded-2xl p-4" aria-label="Spymaster clue form">
      <div className="flex items-center gap-2">
        <Lightbulb className="h-5 w-5 text-gold" aria-hidden="true" />
        <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Give Clue</h2>
      </div>
      <div className={`mt-4 grid gap-3 ${compact ? '' : 'sm:grid-cols-[1fr_7rem_auto]'}`}>
        <input
          value={word}
          onChange={(event) => setWord(event.target.value)}
          aria-label="Clue word"
          placeholder="e.g. Monsoon"
          className="rounded-lg border border-white/10 bg-white/5 px-3 py-3 text-cream outline-none placeholder:text-cream/35 focus:border-saffron/60 light:text-slate-900 light:placeholder:text-slate-400"
        />
        <input
          value={count}
          onChange={(event) => setCount(event.target.value)}
          aria-label="Clue count"
          type="number"
          min="1"
          max="9"
          className="rounded-lg border border-white/10 bg-white/5 px-3 py-3 text-cream outline-none focus:border-saffron/60 light:text-slate-900"
        />
        <Button type="submit" loading={loading} icon={Send} aria-label="Send spymaster clue">
          Send
        </Button>
      </div>
    </form>
  );
};
