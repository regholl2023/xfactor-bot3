import { useState, useEffect } from 'react'
import { 
  Users, TrendingUp, TrendingDown, ExternalLink, RefreshCw,
  Star, AlertCircle, DollarSign, Building2, User
} from 'lucide-react'

interface InsiderTrade {
  ticker: string
  company: string
  insider: string
  title: string
  tradeType: 'Buy' | 'Sell'
  shares: number
  price: number
  value: number
  date: string
  filingDate: string
}

interface TopTrader {
  name: string
  handle: string
  platform: string
  followers: string
  winRate: number
  recentCalls: TraderCall[]
  verified: boolean
}

interface TraderCall {
  ticker: string
  action: 'Long' | 'Short' | 'Buy Calls' | 'Buy Puts'
  entry: number
  target?: number
  date: string
  status: 'Active' | 'Hit Target' | 'Stopped Out'
}

interface FinvizSignal {
  ticker: string
  company: string
  sector: string
  signal: string
  price: number
  change: number
  volume: string
  pattern?: string
}

export function TraderInsights() {
  const [activeTab, setActiveTab] = useState<'insiders' | 'traders' | 'finviz'>('insiders')
  const [insiderTrades, setInsiderTrades] = useState<InsiderTrade[]>([])
  const [topTraders, setTopTraders] = useState<TopTrader[]>([])
  const [finvizSignals, setFinvizSignals] = useState<FinvizSignal[]>([])
  const [loading, setLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  // Mock data - in production, these would come from API
  useEffect(() => {
    loadMockData()
  }, [])

  const loadMockData = () => {
    setLoading(true)
    
    // Mock insider trades (OpenInsider style)
    setInsiderTrades([
      {
        ticker: 'NVDA',
        company: 'NVIDIA Corporation',
        insider: 'Jensen Huang',
        title: 'CEO',
        tradeType: 'Sell',
        shares: 120000,
        price: 875.50,
        value: 105060000,
        date: '2024-12-10',
        filingDate: '2024-12-11'
      },
      {
        ticker: 'AAPL',
        company: 'Apple Inc',
        insider: 'Tim Cook',
        title: 'CEO',
        tradeType: 'Sell',
        shares: 50000,
        price: 195.25,
        value: 9762500,
        date: '2024-12-09',
        filingDate: '2024-12-10'
      },
      {
        ticker: 'TSLA',
        company: 'Tesla Inc',
        insider: 'Robyn Denholm',
        title: 'Chairman',
        tradeType: 'Buy',
        shares: 10000,
        price: 385.00,
        value: 3850000,
        date: '2024-12-08',
        filingDate: '2024-12-09'
      },
      {
        ticker: 'META',
        company: 'Meta Platforms',
        insider: 'Mark Zuckerberg',
        title: 'CEO',
        tradeType: 'Sell',
        shares: 75000,
        price: 585.00,
        value: 43875000,
        date: '2024-12-07',
        filingDate: '2024-12-08'
      },
      {
        ticker: 'AMD',
        company: 'AMD Inc',
        insider: 'Lisa Su',
        title: 'CEO',
        tradeType: 'Buy',
        shares: 25000,
        price: 142.50,
        value: 3562500,
        date: '2024-12-06',
        filingDate: '2024-12-07'
      },
    ])

    // Mock top traders
    setTopTraders([
      {
        name: 'Unusual Whales',
        handle: '@unusual_whales',
        platform: 'Twitter/X',
        followers: '850K',
        winRate: 68,
        verified: true,
        recentCalls: [
          { ticker: 'NVDA', action: 'Buy Calls', entry: 850, target: 950, date: '2024-12-10', status: 'Active' },
          { ticker: 'SPY', action: 'Buy Puts', entry: 605, target: 590, date: '2024-12-09', status: 'Hit Target' },
        ]
      },
      {
        name: 'Cheddar Flow',
        handle: '@CheddarFlow',
        platform: 'Twitter/X',
        followers: '320K',
        winRate: 72,
        verified: true,
        recentCalls: [
          { ticker: 'TSLA', action: 'Long', entry: 380, target: 420, date: '2024-12-10', status: 'Active' },
          { ticker: 'QQQ', action: 'Buy Calls', entry: 515, target: 530, date: '2024-12-08', status: 'Active' },
        ]
      },
      {
        name: 'Market Rebellion',
        handle: '@MarketRebels',
        platform: 'Twitter/X',
        followers: '180K',
        winRate: 65,
        verified: true,
        recentCalls: [
          { ticker: 'AAPL', action: 'Buy Calls', entry: 193, target: 205, date: '2024-12-09', status: 'Active' },
        ]
      },
      {
        name: 'Sweep Cast',
        handle: '@SweepCast',
        platform: 'Discord',
        followers: '95K',
        winRate: 70,
        verified: false,
        recentCalls: [
          { ticker: 'AMD', action: 'Long', entry: 140, target: 160, date: '2024-12-10', status: 'Active' },
          { ticker: 'GOOGL', action: 'Buy Calls', entry: 175, target: 190, date: '2024-12-07', status: 'Active' },
        ]
      },
    ])

    // Mock Finviz signals
    setFinvizSignals([
      { ticker: 'SMCI', company: 'Super Micro Computer', sector: 'Technology', signal: 'Unusual Volume', price: 42.50, change: 12.5, volume: '45M', pattern: 'Breakout' },
      { ticker: 'PLTR', company: 'Palantir', sector: 'Technology', signal: 'New High', price: 75.20, change: 5.2, volume: '82M', pattern: 'Bullish Flag' },
      { ticker: 'MSTR', company: 'MicroStrategy', sector: 'Technology', signal: 'Unusual Volume', price: 395.00, change: 8.7, volume: '12M', pattern: 'Cup & Handle' },
      { ticker: 'COIN', company: 'Coinbase', sector: 'Finance', signal: 'Gap Up', price: 312.50, change: 6.3, volume: '18M' },
      { ticker: 'RKLB', company: 'Rocket Lab', sector: 'Industrials', signal: 'Breakout', price: 27.80, change: 15.2, volume: '35M', pattern: 'Bull Flag' },
      { ticker: 'IONQ', company: 'IonQ Inc', sector: 'Technology', signal: 'New High', price: 45.60, change: 22.1, volume: '28M' },
    ])

    setLastUpdate(new Date())
    setLoading(false)
  }

  const formatValue = (value: number) => {
    if (value >= 1000000000) return `$${(value / 1000000000).toFixed(1)}B`
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`
    return `$${value.toFixed(0)}`
  }

  return (
    <div className="space-y-4">
      {/* Tabs */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('insiders')}
            className={`px-4 py-2 text-sm rounded-lg transition-colors flex items-center gap-2 ${
              activeTab === 'insiders'
                ? 'bg-xfactor-teal text-white'
                : 'bg-secondary text-muted-foreground hover:text-foreground'
            }`}
          >
            <Building2 className="h-4 w-4" />
            OpenInsider
          </button>
          <button
            onClick={() => setActiveTab('traders')}
            className={`px-4 py-2 text-sm rounded-lg transition-colors flex items-center gap-2 ${
              activeTab === 'traders'
                ? 'bg-xfactor-teal text-white'
                : 'bg-secondary text-muted-foreground hover:text-foreground'
            }`}
          >
            <Users className="h-4 w-4" />
            Top Traders
          </button>
          <button
            onClick={() => setActiveTab('finviz')}
            className={`px-4 py-2 text-sm rounded-lg transition-colors flex items-center gap-2 ${
              activeTab === 'finviz'
                ? 'bg-xfactor-teal text-white'
                : 'bg-secondary text-muted-foreground hover:text-foreground'
            }`}
          >
            <TrendingUp className="h-4 w-4" />
            Finviz Signals
          </button>
        </div>
        <button
          onClick={loadMockData}
          disabled={loading}
          className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors"
          title="Refresh data"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* OpenInsider Tab */}
      {activeTab === 'insiders' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>Recent SEC Form 4 Filings</span>
            <a 
              href="http://openinsider.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center gap-1 hover:text-xfactor-teal transition-colors"
            >
              openinsider.com <ExternalLink className="h-3 w-3" />
            </a>
          </div>
          <div className="space-y-2">
            {insiderTrades.map((trade, idx) => (
              <div 
                key={idx}
                className="p-3 rounded-lg bg-secondary/30 border border-border hover:border-xfactor-teal/50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${trade.tradeType === 'Buy' ? 'bg-profit/20' : 'bg-loss/20'}`}>
                      {trade.tradeType === 'Buy' ? (
                        <TrendingUp className="h-4 w-4 text-profit" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-loss" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-foreground">{trade.ticker}</span>
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          trade.tradeType === 'Buy' 
                            ? 'bg-profit/20 text-profit' 
                            : 'bg-loss/20 text-loss'
                        }`}>
                          {trade.tradeType}
                        </span>
                      </div>
                      <div className="text-xs text-muted-foreground">{trade.company}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-foreground">{formatValue(trade.value)}</div>
                    <div className="text-xs text-muted-foreground">{trade.shares.toLocaleString()} shares</div>
                  </div>
                </div>
                <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <User className="h-3 w-3" />
                    <span>{trade.insider}</span>
                    <span className="text-xfactor-teal">({trade.title})</span>
                  </div>
                  <span>Filed: {trade.filingDate}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Traders Tab */}
      {activeTab === 'traders' && (
        <div className="space-y-3">
          <div className="text-sm text-muted-foreground">
            Following top options flow & swing traders
          </div>
          <div className="space-y-3">
            {topTraders.map((trader, idx) => (
              <div 
                key={idx}
                className="p-3 rounded-lg bg-secondary/30 border border-border hover:border-xfactor-teal/50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-xfactor-teal/20 flex items-center justify-center">
                      <Users className="h-5 w-5 text-xfactor-teal" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-foreground">{trader.name}</span>
                        {trader.verified && <Star className="h-3 w-3 text-yellow-500 fill-yellow-500" />}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {trader.handle} • {trader.platform} • {trader.followers} followers
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-sm font-bold ${trader.winRate >= 70 ? 'text-profit' : trader.winRate >= 60 ? 'text-yellow-500' : 'text-muted-foreground'}`}>
                      {trader.winRate}% Win Rate
                    </div>
                  </div>
                </div>
                {trader.recentCalls.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/50">
                    <div className="text-xs text-muted-foreground mb-2">Recent Calls:</div>
                    <div className="flex flex-wrap gap-2">
                      {trader.recentCalls.map((call, cidx) => (
                        <div 
                          key={cidx}
                          className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
                            call.status === 'Hit Target' 
                              ? 'bg-profit/20 text-profit' 
                              : call.status === 'Stopped Out'
                                ? 'bg-loss/20 text-loss'
                                : 'bg-xfactor-teal/20 text-xfactor-teal'
                          }`}
                        >
                          <span className="font-bold">{call.ticker}</span>
                          <span>{call.action}</span>
                          <span>@{call.entry}</span>
                          {call.target && <span>→{call.target}</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Finviz Tab */}
      {activeTab === 'finviz' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>Unusual Volume & Breakout Signals</span>
            <a 
              href="https://finviz.com/screener.ashx" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center gap-1 hover:text-xfactor-teal transition-colors"
            >
              finviz.com <ExternalLink className="h-3 w-3" />
            </a>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {finvizSignals.map((signal, idx) => (
              <div 
                key={idx}
                className="p-3 rounded-lg bg-secondary/30 border border-border hover:border-xfactor-teal/50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-foreground">{signal.ticker}</span>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        signal.change >= 10 
                          ? 'bg-profit/30 text-profit' 
                          : signal.change >= 5 
                            ? 'bg-profit/20 text-profit' 
                            : 'bg-secondary text-muted-foreground'
                      }`}>
                        +{signal.change.toFixed(1)}%
                      </span>
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">{signal.company}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-foreground">${signal.price.toFixed(2)}</div>
                    <div className="text-xs text-muted-foreground">Vol: {signal.volume}</div>
                  </div>
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-xs px-2 py-0.5 rounded bg-xfactor-teal/20 text-xfactor-teal">
                    {signal.signal}
                  </span>
                  {signal.pattern && (
                    <span className="text-xs px-2 py-0.5 rounded bg-xfactor-money/20 text-xfactor-money">
                      {signal.pattern}
                    </span>
                  )}
                  <span className="text-xs text-muted-foreground">{signal.sector}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Last Update */}
      <div className="text-xs text-muted-foreground text-right">
        Last updated: {lastUpdate.toLocaleTimeString()}
      </div>
    </div>
  )
}

