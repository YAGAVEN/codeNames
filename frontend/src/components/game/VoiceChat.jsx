// /media/yagaven_25/coding/Projects/codeNames/src/components/game/VoiceChat.jsx
import { useState } from 'react';
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import { Button } from '../ui/Button.jsx';
import { PlayerAvatar } from '../lobby/PlayerAvatar.jsx';

export const VoiceChat = ({ players = [] }) => {
  const [micEnabled, setMicEnabled] = useState(true);
  const [speakerEnabled, setSpeakerEnabled] = useState(true);

  return (
    <section className="glass-panel rounded-2xl p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Voice Adda</h2>
          <p className="text-sm text-cream/60 light:text-slate-600">Mock voice chat controls and speaker grid.</p>
        </div>
        <div className="flex gap-2">
          <Button
            aria-label={micEnabled ? 'Mute microphone' : 'Unmute microphone'}
            variant="icon"
            icon={micEnabled ? Mic : MicOff}
            onClick={() => setMicEnabled((value) => !value)}
          />
          <Button
            aria-label={speakerEnabled ? 'Mute speakers' : 'Unmute speakers'}
            variant="icon"
            icon={speakerEnabled ? Volume2 : VolumeX}
            onClick={() => setSpeakerEnabled((value) => !value)}
          />
        </div>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
        {players.slice(0, 8).map((player, index) => (
          <div key={player.id} className="flex items-center gap-2 rounded-xl bg-white/5 p-2">
            <PlayerAvatar player={player} size="sm" showLevel={false} />
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-cream light:text-slate-900">{player.name.split(' ')[0]}</p>
              <p className={`text-xs ${index % 3 === 0 ? 'text-emerald' : 'text-cream/45 light:text-slate-500'}`}>
                {index % 3 === 0 ? 'Speaking' : 'Muted'}
              </p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
