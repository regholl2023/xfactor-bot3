import { useState } from 'react'
import { Pause, Power } from 'lucide-react'

interface HeaderProps {
  connected: boolean
}

export function Header({ connected }: HeaderProps) {
  const [logoError, setLogoError] = useState(false)

  return (
    <header className="border-b border-border bg-card px-6 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {/* XFactor Bot Logo */}
          {!logoError ? (
            <img 
              src="/assets/xfactor-logo.png" 
              alt="XFactor Bot" 
              className="h-12 w-auto"
              onError={() => setLogoError(true)}
            />
          ) : (
            <div className="h-12 w-12 bg-xfactor-slate rounded-lg flex items-center justify-center border border-xfactor-teal/30">
              <span className="text-2xl font-bold text-xfactor-teal">X</span>
            </div>
          )}
          <div className="flex flex-col">
            <h1 className="text-lg font-bold xfactor-title tracking-wide">
              THE XFACTOR BOT
            </h1>
            <span className="text-xs text-muted-foreground">
              AI-Powered Trading System
            </span>
          </div>
          <span className="rounded-full bg-xfactor-money/20 px-3 py-1 text-sm text-xfactor-money border border-xfactor-money/30">
            Paper Mode
          </span>
        </div>
        
        <div className="flex items-center gap-6">
          {/* Connection Status */}
          <div className="flex items-center gap-2">
            <div className={`h-2.5 w-2.5 rounded-full ${connected ? 'bg-profit money-glow' : 'bg-loss'}`} />
            <span className="text-sm text-muted-foreground">
              {connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          {/* Trading Controls */}
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-2 rounded-lg bg-secondary px-4 py-2 text-sm hover:bg-secondary/80 border border-border transition-all hover:border-xfactor-teal">
              <Pause className="h-4 w-4" />
              Pause
            </button>
            <button className="flex items-center gap-2 rounded-lg bg-destructive px-4 py-2 text-sm text-destructive-foreground hover:bg-destructive/80 transition-all">
              <Power className="h-4 w-4" />
              Kill Switch
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
