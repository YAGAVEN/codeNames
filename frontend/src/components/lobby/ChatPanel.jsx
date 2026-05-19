// /media/yagaven_25/coding/Projects/codeNames/src/components/lobby/ChatPanel.jsx
import { useState } from 'react';
import { Send, SmilePlus } from 'lucide-react';
import { motion } from 'framer-motion';
import { Button } from '../ui/Button.jsx';
import { PlayerAvatar } from './PlayerAvatar.jsx';
import { useAuth } from '../../hooks/useAuth.js';
import { useGame } from '../../hooks/useGame.js';
import { useSocket } from '../../hooks/useSocket.js';
import { SOCKET_EVENTS } from '../../services/socket.js';
import { EMOJI_REACTIONS } from '../../utils/constants.js';
import { relativeTime } from '../../utils/helpers.js';

export const ChatPanel = ({ compact = false }) => {
  const { user } = useAuth();
  const { chatMessages, addChatMessage, addReaction } = useGame();
  const { emit } = useSocket();
  const [message, setMessage] = useState('');

  const submitMessage = async (event) => {
    event.preventDefault();
    const trimmed = message.trim();

    if (!trimmed) {
      return;
    }

    const nextMessage = {
      id: crypto.randomUUID(),
      author: user,
      message: trimmed,
      createdAt: new Date().toISOString()
    };

    addChatMessage(nextMessage);
    await emit(SOCKET_EVENTS.CHAT_MESSAGE, nextMessage);
    setMessage('');
  };

  const react = async (emoji) => {
    addReaction({ emoji, player: user });
    await emit(SOCKET_EVENTS.EMOJI_REACTION, { emoji, playerId: user.id });
  };

  return (
    <section className="glass-panel flex h-full min-h-[28rem] flex-col rounded-2xl p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Room Chat</h2>
          <p className="text-sm text-cream/55 light:text-slate-500">Live messages, reactions, and team banter.</p>
        </div>
        <SmilePlus className="h-5 w-5 text-saffron" aria-hidden="true" />
      </div>

      <div className="mt-4 flex-1 space-y-3 overflow-y-auto pr-1">
        {chatMessages.map((chat) => (
          <motion.article
            key={chat.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-3 rounded-xl bg-white/5 p-3"
          >
            <PlayerAvatar player={chat.author} size="sm" showLevel={false} />
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <p className="truncate text-sm font-semibold text-cream light:text-slate-900">{chat.author.name}</p>
                <time className="shrink-0 text-[11px] text-cream/45 light:text-slate-500">{relativeTime(chat.createdAt)}</time>
              </div>
              <p className="mt-1 text-sm text-cream/75 light:text-slate-700">{chat.message}</p>
            </div>
          </motion.article>
        ))}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {EMOJI_REACTIONS.slice(0, compact ? 5 : 8).map((emoji) => (
          <button
            key={emoji}
            type="button"
            aria-label={`Send ${emoji} reaction`}
            onClick={() => react(emoji)}
            className="touch-target rounded-lg border border-white/10 bg-white/5 text-lg transition hover:border-saffron/50 hover:bg-white/10"
          >
            {emoji}
          </button>
        ))}
      </div>

      <form onSubmit={submitMessage} className="mt-4 flex gap-2">
        <input
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          aria-label="Message room chat"
          placeholder="Send a clue-safe message"
          className="min-w-0 flex-1 rounded-lg border border-white/10 bg-white/5 px-3 py-3 text-sm text-cream outline-none transition placeholder:text-cream/35 focus:border-saffron/60 light:text-slate-900 light:placeholder:text-slate-400"
        />
        <Button type="submit" aria-label="Send chat message" icon={Send} />
      </form>
    </section>
  );
};
