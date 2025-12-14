import { useState, useEffect, useCallback } from 'react'
import {
  Zap, Settings, TrendingUp, TrendingDown, AlertTriangle,
  Play, Pause, RotateCcw, ChevronDown, ChevronUp,
  Target, Activity, Shield, Clock, Brain, Sparkles
} from 'lucide-react'
import { apiUrl } from '../config/api'

interface OptimizerStatus {
  bot_id: string
  enabled: boolean
  mode: string
  last_adjustment: string | null
  adjustments_today: number
  metrics: {
    win_rate: number
    profit_factor: number
    max_drawdown_pct: number
    total_trades: number
    avg_profit: number
    avg_loss: number
  }
  recent_adjustments: Array<{
    timestamp: string
    parameter: string
    old_value: number
    new_value: number
    reason: string
  }>
}

interface OptimizerMode {
  name: string
  description: string
  max_adjustment_pct: number
  evaluation_interval_minutes: number
}

interface AutoOptimizerProps {
  botId: string
  botName: string
  onClose?: () => void
}

const MODES: OptimizerMode[] = [
  {
    name: 'conservative',
    description: 'Small, careful adjustments. Best for stable strategies.',
    max_adjustment_pct: 5,
    evaluation_interval_minutes: 60
  },
  {
    name: 'moderate',
    description: 'Balanced adjustments. Good for most use cases.',
    max_adjustment_pct: 15,
    evaluation_interval_minutes: 30
  },
  {
    name: 'aggressive',
    description: 'Larger, faster adjustments. For active optimization.',
    max_adjustment_pct: 30,
    evaluation_interval_minutes: 15
  }
]

export function AutoOptimizer({ botId, botName, onClose }: AutoOptimizerProps) {
  const [status, setStatus] = useState<OptimizerStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedMode, setSelectedMode] = useState('moderate')
  const [showAdjustments, setShowAdjustments] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)

  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch(apiUrl(`/api/optimizer/bot/${botId}/status`))
      if (response.ok) {
        const data = await response.json()
        setStatus(data)
        if (data.mode) {
          setSelectedMode(data.mode)
        }
      } else if (response.status === 404) {
        // Bot not registered for optimization yet
        setStatus(null)
      }
    } catch (err) {
      console.error('Failed to fetch optimizer status:', err)
    } finally {
      setLoading(false)
    }
  }, [botId])

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [fetchStatus])

  const enableOptimizer = async () => {
    setActionLoading(true)
    setError('')
    try {
      const response = await fetch(apiUrl(`/api/optimizer/bot/${botId}/enable`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: selectedMode })
      })
      if (response.ok) {
        await fetchStatus()
      } else {
        const data = await response.json()
        setError(data.detail || 'Failed to enable optimizer')
      }
    } catch (err) {
      setError('Failed to enable optimizer')
    } finally {
      setActionLoading(false)
    }
  }

  const disableOptimizer = async () => {
    setActionLoading(true)
    setError('')
    try {
      const response = await fetch(apiUrl(`/api/optimizer/bot/${botId}/disable`), {
        method: 'POST'
      })
      if (response.ok) {
        await fetchStatus()
      } else {
        const data = await response.json()
        setError(data.detail || 'Failed to disable optimizer')
      }
    } catch (err) {
      setError('Failed to disable optimizer')
    } finally {
      setActionLoading(false)
    }
  }

  const resetOptimizer = async () => {
    setActionLoading(true)
    setError('')
    try {
      const response = await fetch(apiUrl(`/api/optimizer/bot/${botId}/reset`), {
        method: 'POST'
      })
      if (response.ok) {
        await fetchStatus()
      } else {
        const data = await response.json()
        setError(data.detail || 'Failed to reset optimizer')
      }
    } catch (err) {
      setError('Failed to reset optimizer')
    } finally {
      setActionLoading(false)
    }
  }

  const getModeColor = (mode: string) => {
    switch (mode) {
      case 'conservative': return 'text-blue-400 bg-blue-500/10'
      case 'moderate': return 'text-yellow-400 bg-yellow-500/10'
      case 'aggressive': return 'text-red-400 bg-red-500/10'
      default: return 'text-gray-400 bg-gray-500/10'
    }
  }

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-xfactor-teal border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="bg-secondary/30 rounded-lg border border-border">
      {/* Header */}
      <div className="p-4 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-xfactor-teal/20">
            <Brain className="h-5 w-5 text-xfactor-teal" />
          </div>
          <div>
            <h3 className="font-semibold">Auto-Optimizer</h3>
            <p className="text-xs text-muted-foreground">
              Automatically tune strategy parameters
            </p>
          </div>
        </div>
        {status?.enabled && (
          <span className={`px-2 py-1 rounded text-xs font-medium ${getModeColor(status.mode)}`}>
            {status.mode.toUpperCase()}
          </span>
        )}
      </div>

      {error && (
        <div className="mx-4 mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Main Content */}
      <div className="p-4 space-y-4">
        {!status?.enabled ? (
          /* Enable Optimizer UI */
          <div className="space-y-4">
            <div className="p-4 bg-gradient-to-r from-xfactor-teal/10 to-purple-500/10 rounded-lg border border-xfactor-teal/30">
              <div className="flex items-start gap-3">
                <Sparkles className="h-5 w-5 text-xfactor-teal mt-0.5" />
                <div>
                  <p className="font-medium text-sm">Enable Auto-Optimization</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    The optimizer will monitor performance and automatically adjust
                    strategy parameters to maximize profits and minimize losses.
                  </p>
                </div>
              </div>
            </div>

            {/* Mode Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Select Optimization Mode</label>
              <div className="grid grid-cols-3 gap-2">
                {MODES.map((mode) => (
                  <button
                    key={mode.name}
                    onClick={() => setSelectedMode(mode.name)}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      selectedMode === mode.name
                        ? 'border-xfactor-teal bg-xfactor-teal/10'
                        : 'border-border hover:border-muted-foreground'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      {mode.name === 'conservative' && <Shield className="h-4 w-4 text-blue-400" />}
                      {mode.name === 'moderate' && <Target className="h-4 w-4 text-yellow-400" />}
                      {mode.name === 'aggressive' && <Zap className="h-4 w-4 text-red-400" />}
                      <span className="text-sm font-medium capitalize">{mode.name}</span>
                    </div>
                    <p className="text-xs text-muted-foreground">{mode.description}</p>
                    <div className="mt-2 text-xs text-muted-foreground">
                      <span>Max adjustment: {mode.max_adjustment_pct}%</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={enableOptimizer}
              disabled={actionLoading}
              className="w-full py-2 px-4 bg-xfactor-teal hover:bg-xfactor-teal/80 text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
            >
              {actionLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Enable Auto-Optimizer
                </>
              )}
            </button>
          </div>
        ) : (
          /* Active Optimizer UI */
          <div className="space-y-4">
            {/* Performance Metrics */}
            {status.metrics && (
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 bg-background rounded-lg text-center">
                  <p className={`text-lg font-bold ${status.metrics.win_rate >= 0.5 ? 'text-green-500' : 'text-red-500'}`}>
                    {(status.metrics.win_rate * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-muted-foreground">Win Rate</p>
                </div>
                <div className="p-3 bg-background rounded-lg text-center">
                  <p className={`text-lg font-bold ${status.metrics.profit_factor >= 1 ? 'text-green-500' : 'text-red-500'}`}>
                    {status.metrics.profit_factor.toFixed(2)}
                  </p>
                  <p className="text-xs text-muted-foreground">Profit Factor</p>
                </div>
                <div className="p-3 bg-background rounded-lg text-center">
                  <p className="text-lg font-bold text-orange-500">
                    {status.metrics.max_drawdown_pct.toFixed(1)}%
                  </p>
                  <p className="text-xs text-muted-foreground">Max Drawdown</p>
                </div>
              </div>
            )}

            {/* Status Info */}
            <div className="flex items-center justify-between p-3 bg-background rounded-lg">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-xfactor-teal" />
                <span className="text-sm">Adjustments Today</span>
              </div>
              <span className="font-bold">{status.adjustments_today}</span>
            </div>

            {status.last_adjustment && (
              <div className="flex items-center justify-between p-3 bg-background rounded-lg">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">Last Adjustment</span>
                </div>
                <span className="text-sm text-muted-foreground">
                  {new Date(status.last_adjustment).toLocaleString()}
                </span>
              </div>
            )}

            {/* Recent Adjustments */}
            {status.recent_adjustments && status.recent_adjustments.length > 0 && (
              <div className="border border-border rounded-lg">
                <button
                  onClick={() => setShowAdjustments(!showAdjustments)}
                  className="w-full p-3 flex items-center justify-between hover:bg-secondary/50 transition-colors"
                >
                  <span className="text-sm font-medium">Recent Adjustments ({status.recent_adjustments.length})</span>
                  {showAdjustments ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </button>
                {showAdjustments && (
                  <div className="border-t border-border max-h-48 overflow-y-auto">
                    {status.recent_adjustments.map((adj, i) => (
                      <div key={i} className="p-3 border-b border-border last:border-0 text-sm">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{adj.parameter}</span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(adj.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-muted-foreground">{adj.old_value.toFixed(2)}</span>
                          <span>→</span>
                          <span className={adj.new_value > adj.old_value ? 'text-green-500' : 'text-red-500'}>
                            {adj.new_value.toFixed(2)}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">{adj.reason}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={disableOptimizer}
                disabled={actionLoading}
                className="flex-1 py-2 px-4 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                <Pause className="h-4 w-4" />
                Disable
              </button>
              <button
                onClick={resetOptimizer}
                disabled={actionLoading}
                className="flex-1 py-2 px-4 bg-secondary hover:bg-secondary/80 text-foreground border border-border rounded-lg font-medium flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                <RotateCcw className="h-4 w-4" />
                Reset
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Compact inline version for bot list items
 */
export function AutoOptimizerToggle({ botId, enabled, mode, onToggle }: {
  botId: string
  enabled: boolean
  mode?: string
  onToggle: () => void
}) {
  const [loading, setLoading] = useState(false)

  const handleToggle = async () => {
    setLoading(true)
    try {
      const endpoint = enabled ? 'disable' : 'enable'
      const response = await fetch(apiUrl(`/api/optimizer/bot/${botId}/${endpoint}`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: 'moderate' })
      })
      if (response.ok) {
        onToggle()
      }
    } catch (err) {
      console.error('Failed to toggle optimizer:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={handleToggle}
      disabled={loading}
      className={`p-1.5 rounded transition-colors ${
        enabled
          ? 'bg-xfactor-teal/20 text-xfactor-teal hover:bg-xfactor-teal/30'
          : 'bg-secondary text-muted-foreground hover:text-foreground'
      }`}
      title={enabled ? 'Disable Auto-Optimizer' : 'Enable Auto-Optimizer'}
    >
      {loading ? (
        <div className="animate-spin rounded-full h-3.5 w-3.5 border border-current border-t-transparent" />
      ) : (
        <Brain className="h-3.5 w-3.5" />
      )}
    </button>
  )
}

