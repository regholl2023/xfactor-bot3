import { useState, useEffect, useMemo } from 'react'
import { RefreshCw, TrendingUp, TrendingDown, Search, SortAsc, SortDesc, X, Info, AlertTriangle, Wallet, Bot, TestTube2, Shield, Zap } from 'lucide-react'
import { useTradingMode } from '../context/TradingModeContext'

interface Position {
  symbol: string
  quantity: number
  avg_cost: number
  current_price: number
  market_value: number
  unrealized_pnl: number
  unrealized_pnl_pct: number
  sector?: string
  strategy?: string
}

interface PortfolioSummary {
  total_value: number
  cash: number
  positions_value: number
  unrealized_pnl: number
  realized_pnl: number
  daily_pnl: number
  position_count: number
}

// Empty positions - real data comes from broker API when connected
const emptyPositions: Position[] = []

const emptySummary: PortfolioSummary = {
  total_value: 0,
  cash: 0,
  positions_value: 0,
  unrealized_pnl: 0,
  realized_pnl: 0,
  daily_pnl: 0,
  position_count: 0,
}

type SortField = 'symbol' | 'quantity' | 'market_value' | 'unrealized_pnl' | 'unrealized_pnl_pct'
type SortDir = 'asc' | 'desc'

export function PositionsTable() {
  const { mode, broker } = useTradingMode()
  const [positions, setPositions] = useState<Position[]>(emptyPositions)
  const [summary, setSummary] = useState<PortfolioSummary>(emptySummary)
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [sortField, setSortField] = useState<SortField>('unrealized_pnl')
  const [sortDir, setSortDir] = useState<SortDir>('desc')
  const [showHelp, setShowHelp] = useState(false)
  const [isLiveData, setIsLiveData] = useState(false)
  
  const getModeLabel = () => {
    switch (mode) {
      case 'demo': return { label: 'Demo Mode', icon: <TestTube2 className="h-4 w-4" />, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' }
      case 'paper': return { label: 'Paper Trading', icon: <Shield className="h-4 w-4" />, color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' }
      case 'live': return { label: 'LIVE Trading', icon: <Zap className="h-4 w-4" />, color: 'text-profit', bg: 'bg-profit/10', border: 'border-profit/20' }
    }
  }
  
  const modeInfo = getModeLabel()

  const fetchPositions = async () => {
    setLoading(true)
    try {
      const [posRes, summaryRes] = await Promise.all([
        fetch('/api/positions/'),
        fetch('/api/positions/summary'),
      ])
      
      if (posRes.ok) {
        const data = await posRes.json()
        setPositions(data.positions || [])
        setIsLiveData(data.positions && data.positions.length > 0)
      } else {
        setPositions([])
        setIsLiveData(false)
      }
      
      if (summaryRes.ok) {
        const data = await summaryRes.json()
        setSummary({
          total_value: data.total_value || 0,
          cash: data.cash || 0,
          positions_value: data.positions_value || 0,
          unrealized_pnl: data.unrealized_pnl || 0,
          realized_pnl: data.realized_pnl || 0,
          daily_pnl: data.daily_pnl || 0,
          position_count: data.position_count || 0,
        })
      } else {
        setSummary(emptySummary)
      }
    } catch (e) {
      console.error('Failed to fetch positions:', e)
      setPositions([])
      setSummary(emptySummary)
      setIsLiveData(false)
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchPositions()
    const interval = setInterval(fetchPositions, 15000) // Refresh every 15s
    return () => clearInterval(interval)
  }, [])

  // Filtered and sorted positions
  const filteredPositions = useMemo(() => {
    let result = [...positions]
    
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      result = result.filter(p => 
        p.symbol.toLowerCase().includes(query) ||
        p.strategy?.toLowerCase().includes(query) ||
        p.sector?.toLowerCase().includes(query)
      )
    }
    
    result.sort((a, b) => {
      let aVal = a[sortField]
      let bVal = b[sortField]
      
      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase() as any
        bVal = (bVal as string).toLowerCase() as any
      }
      
      if ((aVal as number) < (bVal as number)) return sortDir === 'asc' ? -1 : 1
      if ((aVal as number) > (bVal as number)) return sortDir === 'asc' ? 1 : -1
      return 0
    })
    
    return result
  }, [positions, searchQuery, sortField, sortDir])

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDir('desc')
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value)
  }

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <SortAsc className="h-3 w-3 opacity-30" />
    return sortDir === 'asc' ? <SortAsc className="h-3 w-3" /> : <SortDesc className="h-3 w-3" />
  }

  return (
    <div className="space-y-4">
      {/* Trading Mode Status Banner */}
      <div className={`flex items-center gap-3 p-3 rounded-lg ${modeInfo.bg} border ${modeInfo.border}`}>
        <span className={modeInfo.color}>{modeInfo.icon}</span>
        <div className="flex-1">
          <div className={`text-sm font-medium ${modeInfo.color}`}>{modeInfo.label}</div>
          <div className="text-xs text-muted-foreground">
            {mode === 'demo' && 'Showing sample positions for demonstration. Connect a broker for real data.'}
            {mode === 'paper' && (broker.isConnected 
              ? `Connected to ${broker.provider?.toUpperCase()}. Simulated trades - no real money at risk.`
              : 'Paper trading mode. Connect a broker in Admin panel to start.'
            )}
            {mode === 'live' && `⚠️ LIVE TRADING - Real money. Connected to ${broker.provider?.toUpperCase()} (${broker.accountId})`}
          </div>
        </div>
        <button
          onClick={() => setShowHelp(!showHelp)}
          className={`px-3 py-1.5 text-xs rounded-lg ${modeInfo.bg} ${modeInfo.color} hover:opacity-80 transition-colors border ${modeInfo.border}`}
        >
          Learn More
        </button>
      </div>

      {/* Help Panel */}
      {showHelp && (
        <div className="p-4 rounded-lg bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <Info className="h-5 w-5 text-blue-400 mt-0.5" />
              <div>
                <h4 className="font-medium text-foreground mb-2">Understanding Open Positions</h4>
                <div className="space-y-3 text-sm text-muted-foreground">
                  <p>
                    <strong className="text-foreground">Open Positions</strong> are stocks, ETFs, or other securities currently held in your brokerage account.
                    These positions are created when your trading bots execute buy orders through your connected broker.
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-3 rounded-lg bg-background/50">
                      <div className="flex items-center gap-2 mb-2">
                        <Wallet className="h-4 w-4 text-xfactor-teal" />
                        <span className="font-medium text-foreground">Position Types</span>
                      </div>
                      <ul className="space-y-1 text-xs">
                        <li className="flex items-center gap-2">
                          <TrendingUp className="h-3 w-3 text-profit" />
                          <span><strong>Long</strong> (positive qty) - You own shares, profit when price rises</span>
                        </li>
                        <li className="flex items-center gap-2">
                          <TrendingDown className="h-3 w-3 text-loss" />
                          <span><strong>Short</strong> (negative qty) - Borrowed shares, profit when price falls</span>
                        </li>
                      </ul>
                    </div>
                    
                    <div className="p-3 rounded-lg bg-background/50">
                      <div className="flex items-center gap-2 mb-2">
                        <Bot className="h-4 w-4 text-xfactor-teal" />
                        <span className="font-medium text-foreground">How Positions Are Opened</span>
                      </div>
                      <ul className="space-y-1 text-xs">
                        <li>• Bots analyze market data and news sentiment</li>
                        <li>• When signals trigger, orders are sent to your broker</li>
                        <li>• Executed orders become open positions</li>
                        <li>• Bots manage exits based on strategy rules</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div className="p-3 rounded-lg bg-background/50">
                    <div className="font-medium text-foreground mb-1">Key Metrics Explained</div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                      <div><strong>Qty:</strong> Number of shares held</div>
                      <div><strong>Avg Cost:</strong> Your purchase price per share</div>
                      <div><strong>P&L:</strong> Unrealized profit/loss (not yet sold)</div>
                      <div><strong>Strategy:</strong> Which bot strategy opened this position</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <button
              onClick={() => setShowHelp(false)}
              className="p-1 hover:bg-secondary rounded shrink-0"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="p-3 rounded-lg bg-secondary/50">
          <div className="text-xs text-muted-foreground">Total Value</div>
          <div className="text-lg font-semibold">{formatCurrency(summary.total_value)}</div>
        </div>
        <div className="p-3 rounded-lg bg-secondary/50">
          <div className="text-xs text-muted-foreground">Unrealized P&L</div>
          <div className={`text-lg font-semibold ${summary.unrealized_pnl >= 0 ? 'text-profit' : 'text-loss'}`}>
            {summary.unrealized_pnl >= 0 ? '+' : ''}{formatCurrency(summary.unrealized_pnl)}
          </div>
        </div>
        <div className="p-3 rounded-lg bg-secondary/50">
          <div className="text-xs text-muted-foreground">Daily P&L</div>
          <div className={`text-lg font-semibold ${summary.daily_pnl >= 0 ? 'text-profit' : 'text-loss'}`}>
            {summary.daily_pnl >= 0 ? '+' : ''}{formatCurrency(summary.daily_pnl)}
          </div>
        </div>
        <div className="p-3 rounded-lg bg-secondary/50">
          <div className="text-xs text-muted-foreground">Cash</div>
          <div className="text-lg font-semibold">{formatCurrency(summary.cash)}</div>
        </div>
      </div>

      {/* Search and Controls */}
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search positions..."
            className="w-full pl-10 pr-8 py-2 text-sm rounded-lg bg-secondary border border-border"
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery('')} className="absolute right-3 top-1/2 -translate-y-1/2">
              <X className="h-4 w-4 text-muted-foreground" />
            </button>
          )}
        </div>
        <button
          onClick={() => setShowHelp(!showHelp)}
          className={`p-2 rounded-lg transition-colors ${showHelp ? 'bg-blue-500/20 text-blue-400' : 'bg-secondary hover:bg-secondary/80'}`}
          title="What are open positions?"
        >
          <Info className="h-4 w-4" />
        </button>
        <button
          onClick={fetchPositions}
          disabled={loading}
          className="p-2 rounded-lg bg-secondary hover:bg-secondary/80"
          title="Refresh positions"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Positions Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border text-left text-sm text-muted-foreground">
              <th className="pb-2">
                <button onClick={() => toggleSort('symbol')} className="flex items-center gap-1 hover:text-foreground">
                  Symbol <SortIcon field="symbol" />
                </button>
              </th>
              <th className="pb-2">
                <button onClick={() => toggleSort('quantity')} className="flex items-center gap-1 hover:text-foreground">
                  Qty <SortIcon field="quantity" />
                </button>
              </th>
              <th className="pb-2">Avg Cost</th>
              <th className="pb-2">Price</th>
              <th className="pb-2">
                <button onClick={() => toggleSort('market_value')} className="flex items-center gap-1 hover:text-foreground">
                  Value <SortIcon field="market_value" />
                </button>
              </th>
              <th className="pb-2">
                <button onClick={() => toggleSort('unrealized_pnl')} className="flex items-center gap-1 hover:text-foreground">
                  P&L <SortIcon field="unrealized_pnl" />
                </button>
              </th>
              <th className="pb-2">
                <button onClick={() => toggleSort('unrealized_pnl_pct')} className="flex items-center gap-1 hover:text-foreground">
                  P&L % <SortIcon field="unrealized_pnl_pct" />
                </button>
              </th>
              <th className="pb-2">Strategy</th>
            </tr>
          </thead>
          <tbody>
            {filteredPositions.map((pos) => (
              <tr key={pos.symbol} className="border-b border-border/50 hover:bg-secondary/30">
                <td className="py-2 font-medium flex items-center gap-2">
                  {pos.quantity > 0 ? (
                    <TrendingUp className="h-3 w-3 text-profit" />
                  ) : (
                    <TrendingDown className="h-3 w-3 text-loss" />
                  )}
                  {pos.symbol}
                </td>
                <td className={`py-2 ${pos.quantity < 0 ? 'text-loss' : ''}`}>
                  {pos.quantity.toLocaleString()}
                </td>
                <td className="py-2">${pos.avg_cost.toFixed(2)}</td>
                <td className="py-2">${pos.current_price.toFixed(2)}</td>
                <td className="py-2">{formatCurrency(Math.abs(pos.market_value))}</td>
                <td className={`py-2 ${pos.unrealized_pnl >= 0 ? 'text-profit' : 'text-loss'}`}>
                  {pos.unrealized_pnl >= 0 ? '+' : ''}{formatCurrency(pos.unrealized_pnl)}
                </td>
                <td className={`py-2 ${pos.unrealized_pnl_pct >= 0 ? 'text-profit' : 'text-loss'}`}>
                  {pos.unrealized_pnl_pct >= 0 ? '+' : ''}{pos.unrealized_pnl_pct.toFixed(2)}%
                </td>
                <td className="py-2">
                  <span className="px-2 py-0.5 text-xs rounded bg-secondary text-muted-foreground">
                    {pos.strategy}
                  </span>
                </td>
              </tr>
            ))}
            {filteredPositions.length === 0 && (
              <tr>
                <td colSpan={8} className="py-4 text-center text-muted-foreground">
                  {searchQuery ? 'No positions match your search' : 'No open positions'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Position Count */}
      <div className="text-xs text-muted-foreground text-right">
        {filteredPositions.length} of {positions.length} positions
      </div>
    </div>
  )
}
