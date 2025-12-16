import { ReactNode, useState } from 'react';
import { Lock } from 'lucide-react';
import { useFeatureAvailable } from '../contexts/DemoModeContext';
import UnlockModal from './UnlockModal';

interface RestrictedFeatureProps {
  children: ReactNode;
  feature?: 'broker' | 'liveData' | 'trading' | 'all';
  message?: string;
  showOverlay?: boolean;
}

export default function RestrictedFeature({ 
  children, 
  feature = 'all',
  message = 'This feature is restricted in demo mode',
  showOverlay = true
}: RestrictedFeatureProps) {
  const { isFullFeaturesAvailable, canConnectBroker, canUseLiveData, canTrade } = useFeatureAvailable();
  const [showUnlockModal, setShowUnlockModal] = useState(false);

  // Check if this specific feature is available
  const isAvailable = (() => {
    switch (feature) {
      case 'broker': return canConnectBroker;
      case 'liveData': return canUseLiveData;
      case 'trading': return canTrade;
      default: return isFullFeaturesAvailable;
    }
  })();

  if (isAvailable) {
    return <>{children}</>;
  }

  return (
    <>
      <div className="relative">
        {/* Grayed out content */}
        <div className="opacity-50 pointer-events-none select-none filter grayscale">
          {children}
        </div>

        {/* Overlay */}
        {showOverlay && (
          <div 
            className="absolute inset-0 bg-slate-900/60 backdrop-blur-[1px] flex items-center justify-center cursor-pointer rounded-lg"
            onClick={() => setShowUnlockModal(true)}
          >
            <div className="text-center p-4">
              <div className="w-12 h-12 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <Lock className="w-6 h-6 text-amber-400" />
              </div>
              <p className="text-sm text-slate-300 max-w-xs">{message}</p>
              <button className="mt-3 px-4 py-2 bg-amber-500/20 hover:bg-amber-500/30 text-amber-400 text-sm rounded-lg transition-colors">
                Click to Unlock
              </button>
            </div>
          </div>
        )}
      </div>

      <UnlockModal 
        isOpen={showUnlockModal} 
        onClose={() => setShowUnlockModal(false)} 
      />
    </>
  );
}

// Simple hook-based check for inline use
export function useIsRestricted(feature?: 'broker' | 'liveData' | 'trading' | 'all') {
  const { isFullFeaturesAvailable, canConnectBroker, canUseLiveData, canTrade } = useFeatureAvailable();
  
  switch (feature) {
    case 'broker': return !canConnectBroker;
    case 'liveData': return !canUseLiveData;
    case 'trading': return !canTrade;
    default: return !isFullFeaturesAvailable;
  }
}

