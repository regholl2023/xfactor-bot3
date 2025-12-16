import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface DemoModeContextType {
  isDemoMode: boolean;
  isUnlocked: boolean;
  unlock: (password: string) => boolean;
  lock: () => void;
}

const DemoModeContext = createContext<DemoModeContextType | undefined>(undefined);

// Check if running in demo mode (GitLab build)
const checkDemoMode = (): boolean => {
  // Demo mode is enabled if:
  // 1. VITE_DEMO_MODE env var is set to 'true'
  // 2. Or running from GitLab Pages (check URL)
  const envDemoMode = import.meta.env.VITE_DEMO_MODE === 'true';
  const isGitLabPages = window.location.hostname.includes('gitlab.io') || 
                        window.location.hostname.includes('gitlab.com');
  
  // For localhost and GitHub, demo mode is OFF by default
  const isLocalhost = window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1';
  const isGitHub = window.location.hostname.includes('github.io');
  
  if (isLocalhost || isGitHub) {
    return false; // Full features on localhost and GitHub
  }
  
  return envDemoMode || isGitLabPages;
};

// The unlock password - in production, this should be more secure
const UNLOCK_PASSWORD = 'xfactor2025';

export function DemoModeProvider({ children }: { children: ReactNode }) {
  const [isDemoMode] = useState(checkDemoMode);
  const [isUnlocked, setIsUnlocked] = useState(false);

  // Check for stored unlock state
  useEffect(() => {
    const stored = sessionStorage.getItem('xfactor_unlocked');
    if (stored === 'true' && isDemoMode) {
      setIsUnlocked(true);
    }
  }, [isDemoMode]);

  const unlock = (password: string): boolean => {
    if (password === UNLOCK_PASSWORD) {
      setIsUnlocked(true);
      sessionStorage.setItem('xfactor_unlocked', 'true');
      return true;
    }
    return false;
  };

  const lock = () => {
    setIsUnlocked(false);
    sessionStorage.removeItem('xfactor_unlocked');
  };

  return (
    <DemoModeContext.Provider value={{ isDemoMode, isUnlocked, unlock, lock }}>
      {children}
    </DemoModeContext.Provider>
  );
}

export function useDemoMode() {
  const context = useContext(DemoModeContext);
  if (context === undefined) {
    throw new Error('useDemoMode must be used within a DemoModeProvider');
  }
  return context;
}

// Helper hook to check if a feature is available
export function useFeatureAvailable() {
  const { isDemoMode, isUnlocked } = useDemoMode();
  
  return {
    // Full features available if not in demo mode, or if unlocked
    isFullFeaturesAvailable: !isDemoMode || isUnlocked,
    // Broker connections require unlock in demo mode
    canConnectBroker: !isDemoMode || isUnlocked,
    // Live data requires unlock in demo mode
    canUseLiveData: !isDemoMode || isUnlocked,
    // Trading requires unlock in demo mode
    canTrade: !isDemoMode || isUnlocked,
  };
}

