// /media/yagaven_25/coding/Projects/codeNames/src/components/lobby/InvitePanel.jsx
import { Copy, Share2, UserRoundPlus } from 'lucide-react';
import { Button } from '../ui/Button.jsx';
import { Badge } from '../ui/Badge.jsx';
import { useRoom } from '../../hooks/useRoom.js';
import { useToast } from '../ui/Toast.jsx';

export const InvitePanel = ({ roomCode = '' }) => {
  const { copyInvite } = useRoom();
  const { showToast } = useToast();

  const handleCopy = async () => {
    const copied = await copyInvite(roomCode);
    const label = roomCode || 'Room';
    showToast({
      type: copied ? 'success' : 'warning',
      title: copied ? 'Invite copied' : 'Clipboard unavailable',
      message: copied ? `${label} link is ready for WhatsApp or Discord.` : 'Share the room code manually.'
    });
  };

  return (
    <section className="glass-panel rounded-2xl p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="font-heading text-2xl font-bold text-cream light:text-slate-900">Invite Friends</h2>
          <p className="text-sm text-cream/60 light:text-slate-600">Copy link, share room code, or keep a private adda.</p>
        </div>
        <Badge tone="saffron">{roomCode || 'Lobby'}</Badge>
      </div>
      <div className="mt-4 grid gap-2 sm:grid-cols-3">
        <Button variant="secondary" icon={Copy} onClick={handleCopy} aria-label="Copy room invite link">
          Copy link
        </Button>
        <Button variant="secondary" icon={Share2} aria-label="Open share sheet">
          Share
        </Button>
        <Button variant="secondary" icon={UserRoundPlus} aria-label="Show pending friend invites" disabled>
          Pending invites
        </Button>
      </div>
    </section>
  );
};
