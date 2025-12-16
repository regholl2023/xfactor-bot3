import { useState } from 'react';
import { AlertTriangle, Lock, X } from 'lucide-react';
import { useDemoMode } from '../contexts/DemoModeContext';
import UnlockModal from './UnlockModal';

export default function DemoModeBanner() {
  const { isDemoMode, isUnlocked } = useDemoMode();
  const [showUnlockModal, setShowUnlockModal] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  // Don't show if not in demo mode or already unlocked or dismissed
  if (!isDemoMode || isUnlocked || dismissed) return null;

  return (
    <>
      <div className="bg-gradient-to-r from-amber-600/90 to-orange-600/90 text-white px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-5 h-5" />
          <span className="text-sm font-medium">
            Demo Mode: Broker connections and live trading are disabled.
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowUnlockModal(true)}
            className="px-3 py-1 bg-white/20 hover:bg-white/30 rounded text-sm font-medium flex items-center gap-1 transition-colors"
          >
            <Lock className="w-4 h-4" />
            Unlock
          </button>
          <button
            onClick={() => setDismissed(true)}
            className="p-1 hover:bg-white/20 rounded transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      <UnlockModal 
        isOpen={showUnlockModal} 
        onClose={() => setShowUnlockModal(false)} 
      />
    </>
  );
}

