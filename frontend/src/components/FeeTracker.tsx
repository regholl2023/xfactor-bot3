import { useState, useEffect } from 'react'
import { DollarSign, TrendingDown, Building2, Bot, Calculator, RefreshCw } from 'lucide-react'

interface FeeSummary {
  period: { start: string; end: string }
  totals: {
    total_fees: number
    fees_pct_of_portfolio: number
    fees_pct_of_volume: number
    trade_count: number
    avg_fee_per_trade: number
    total_trade_volume: number
    portfolio_value: number
  }
  breakdown_by_type: Record<string, number>
  breakdown_by_broker: Record<string, number>
  breakdown_by_bot: Record<string, number>
}

interface BrokerInfo {
  id: string
  name: string
  stock_commission: string | number
  options_per_contract: number
  crypto_fee_pct: number
}

interface FeeEstimate {
  estimate: {
    monthly_trades: number
    monthly_volume: number
    monthly_fees: number
    yearly_fees: number
    fee_per_trade: number
    fee_pct_of_volume: number
  }
}

export function FeeTracker() {
  const [summary, setSummary] = useState<FeeSummary | null>(null)
  const [brokers, setBrokers] = useState<BrokerInfo[]>([])
  const [estimate, setEstimate] = useState<FeeEstimate | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'summary' | 'brokers' | 'estimate'>('summary')
  
  // Estimate parameters
  const [tradesPerDay, setTradesPerDay] = useState(10)
  const [avgTradeValue, setAvgTradeValue] = useState(5000)
  const [selectedBroker, setSelectedBroker] = useState('ibkr_pro')

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    if (activeTab === 'estimate') {
      fetchEstimate()
    }
  }, [activeTab, tradesPerDay, avgTradeValue, selectedBroker])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [summaryRes, brokersRes] = await Promise.all([
        fetch('/api/fees/summary'),
        fetch('/api/fees/brokers'),
      ])
      
      if (summaryRes.ok) setSummary(await summaryRes.json())
      if (brokersRes.ok) {
        const data = await brokersRes.json()
        setBrokers(data.brokers || [])
      }
    } catch (e) {
      console.error('Error fetching fee data:', e)
    }
    setLoading(false)
  }

  const fetchEstimate = async () => {
    try {
      const res = await fetch(`/api/fees/estimate?trades_per_day=${tradesPerDay}&avg_trade_value=${avgTradeValue}&broker=${selectedBroker}`)
      if (res.ok) setEstimate(await res.json())
    } catch (e) {
      console.error('Error fetching estimate:', e)
    }
  }

  const formatCurrency = (value: number) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(2)}M`
    if (value >= 1000) return `$${(value / 1000).toFixed(1)}K`
    return `$${value.toFixed(2)}`
  }

  const feeTypeLabels: Record<string, string> = {
    commission: '💰 Commission',
    spread: '📊 Spread',
    exchange: '🏛️ Exchange',
    regulatory: '📜 Regulatory (SEC/FINRA)',
    clearing: '🔄 Clearing',
    data: '📈 Market Data',
    platform: '💻 Platform',
    margin_interest: '💳 Margin Interest',
    crypto_network: '🔗 Network Fees',
    other: '📦 Other',
  }

  return (
    <div className="space-y-4">
      {/* Tabs */}
      <div className="flex gap-2 border-b border-border pb-2">
        {[
          { id: 'summary', label: 'Fee Summary', icon: <DollarSign className="h-4 w-4" /> },
          { id: 'brokers', label: 'Broker Fees', icon: <Building2 className="h-4 w-4" /> },
          { id: 'estimate', label: 'Estimate', icon: <Calculator className="h-4 w-4" /> },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-3 py-2 text-sm rounded-lg transition-colors ${
              activeTab === tab.id
                ? 'bg-xfactor-teal text-white'
                : 'bg-secondary hover:bg-secondary/80 text-muted-foreground'
            }`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
        <button onClick={fetchData} className="ml-auto p-2 rounded-lg bg-secondary hover:bg-secondary/80">
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Summary Tab */}
      {activeTab === 'summary' && summary && (
        <div className="space-y-4">
          {/* Key Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="p-3 rounded-lg bg-loss/10 border border-loss/30">
              <div className="text-xs text-muted-foreground mb-1">Total Fees</div>
              <div className="text-xl font-bold text-loss">{formatCurrency(summary.totals.total_fees)}</div>
              <div className="text-xs text-muted-foreground">
                {summary.totals.fees_pct_of_portfolio.toFixed(3)}% of portfolio
              </div>
            </div>
            <div className="p-3 rounded-lg bg-secondary/50 border border-border">
              <div className="text-xs text-muted-foreground mb-1">Avg Fee/Trade</div>
              <div className="text-xl font-bold">{formatCurrency(summary.totals.avg_fee_per_trade)}</div>
              <div className="text-xs text-muted-foreground">{summary.totals.trade_count} trades</div>
            </div>
            <div className="p-3 rounded-lg bg-secondary/50 border border-border">
              <div className="text-xs text-muted-foreground mb-1">% of Volume</div>
              <div className="text-xl font-bold">{summary.totals.fees_pct_of_volume.toFixed(3)}%</div>
              <div className="text-xs text-muted-foreground">
                Vol: {formatCurrency(summary.totals.total_trade_volume)}
              </div>
            </div>
            <div className="p-3 rounded-lg bg-secondary/50 border border-border">
              <div className="text-xs text-muted-foreground mb-1">Portfolio Value</div>
              <div className="text-xl font-bold text-xfactor-teal">{formatCurrency(summary.totals.portfolio_value)}</div>
              <div className="text-xs text-muted-foreground">
                Period: {summary.period.start} - {summary.period.end}
              </div>
            </div>
          </div>

          {/* Fee Breakdown by Type */}
          <div className="p-4 rounded-lg bg-secondary/30 border border-border">
            <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-loss" /> Fee Breakdown by Type
            </h3>
            <div className="space-y-2">
              {Object.entries(summary.breakdown_by_type).map(([type, amount]) => {
                const pct = summary.totals.total_fees > 0 ? (amount / summary.totals.total_fees * 100) : 0
                return (
                  <div key={type} className="flex items-center gap-3">
                    <span className="text-sm w-48 truncate">{feeTypeLabels[type] || type}</span>
                    <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-loss rounded-full"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="text-sm font-mono w-20 text-right">{formatCurrency(amount)}</span>
                    <span className="text-xs text-muted-foreground w-12 text-right">{pct.toFixed(1)}%</span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Fee Breakdown by Broker & Bot */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* By Broker */}
            <div className="p-4 rounded-lg bg-secondary/30 border border-border">
              <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                <Building2 className="h-4 w-4" /> By Broker
              </h3>
              {Object.keys(summary.breakdown_by_broker).length > 0 ? (
                <div className="space-y-2">
                  {Object.entries(summary.breakdown_by_broker).map(([broker, amount]) => (
                    <div key={broker} className="flex justify-between text-sm">
                      <span>{broker}</span>
                      <span className="font-mono text-loss">{formatCurrency(amount)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">No broker fees recorded</div>
              )}
            </div>

            {/* By Bot */}
            <div className="p-4 rounded-lg bg-secondary/30 border border-border">
              <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                <Bot className="h-4 w-4" /> By Bot
              </h3>
              {Object.keys(summary.breakdown_by_bot).length > 0 ? (
                <div className="space-y-2">
                  {Object.entries(summary.breakdown_by_bot).map(([bot, amount]) => (
                    <div key={bot} className="flex justify-between text-sm">
                      <span className="truncate">{bot}</span>
                      <span className="font-mono text-loss">{formatCurrency(amount)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">No bot fees recorded</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Brokers Tab */}
      {activeTab === 'brokers' && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-muted-foreground text-left border-b border-border">
                <th className="py-2 font-medium">Broker</th>
                <th className="py-2 font-medium text-right">Stock Commission</th>
                <th className="py-2 font-medium text-right">Options/Contract</th>
                <th className="py-2 font-medium text-right">Crypto Fee %</th>
              </tr>
            </thead>
            <tbody>
              {brokers.map(broker => (
                <tr key={broker.id} className="border-b border-border/50 hover:bg-secondary/30">
                  <td className="py-3">
                    <div className="font-medium">{broker.name}</div>
                    <div className="text-xs text-muted-foreground">{broker.id}</div>
                  </td>
                  <td className="py-3 text-right font-mono">
                    {typeof broker.stock_commission === 'number' 
                      ? `$${broker.stock_commission.toFixed(2)}`
                      : broker.stock_commission === '0' || broker.stock_commission === '$0.0/share'
                        ? <span className="text-profit">Free</span>
                        : broker.stock_commission
                    }
                  </td>
                  <td className="py-3 text-right font-mono">
                    {broker.options_per_contract === 0 
                      ? <span className="text-profit">Free</span>
                      : `$${broker.options_per_contract.toFixed(2)}`
                    }
                  </td>
                  <td className="py-3 text-right font-mono">
                    {broker.crypto_fee_pct > 0 ? `${broker.crypto_fee_pct.toFixed(2)}%` : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Estimate Tab */}
      {activeTab === 'estimate' && (
        <div className="space-y-4">
          {/* Input Controls */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-lg bg-secondary/30 border border-border">
            <div>
              <label className="text-sm font-medium block mb-2">Trades per Day</label>
              <input
                type="number"
                value={tradesPerDay}
                onChange={(e) => setTradesPerDay(Number(e.target.value))}
                className="w-full px-3 py-2 rounded-lg bg-secondary border border-border"
              />
            </div>
            <div>
              <label className="text-sm font-medium block mb-2">Avg Trade Value ($)</label>
              <input
                type="number"
                value={avgTradeValue}
                onChange={(e) => setAvgTradeValue(Number(e.target.value))}
                className="w-full px-3 py-2 rounded-lg bg-secondary border border-border"
              />
            </div>
            <div>
              <label className="text-sm font-medium block mb-2">Broker</label>
              <select
                value={selectedBroker}
                onChange={(e) => setSelectedBroker(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-secondary border border-border"
              >
                {brokers.map(b => (
                  <option key={b.id} value={b.id}>{b.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Estimate Results */}
          {estimate && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-loss/10 border border-loss/30">
                <div className="text-xs text-muted-foreground mb-1">Monthly Fees</div>
                <div className="text-2xl font-bold text-loss">{formatCurrency(estimate.estimate.monthly_fees)}</div>
              </div>
              <div className="p-4 rounded-lg bg-loss/10 border border-loss/30">
                <div className="text-xs text-muted-foreground mb-1">Yearly Fees</div>
                <div className="text-2xl font-bold text-loss">{formatCurrency(estimate.estimate.yearly_fees)}</div>
              </div>
              <div className="p-4 rounded-lg bg-secondary/50 border border-border">
                <div className="text-xs text-muted-foreground mb-1">Fee per Trade</div>
                <div className="text-2xl font-bold">{formatCurrency(estimate.estimate.fee_per_trade)}</div>
              </div>
              <div className="p-4 rounded-lg bg-secondary/50 border border-border">
                <div className="text-xs text-muted-foreground mb-1">Monthly Trades</div>
                <div className="text-2xl font-bold">{estimate.estimate.monthly_trades}</div>
              </div>
              <div className="p-4 rounded-lg bg-secondary/50 border border-border">
                <div className="text-xs text-muted-foreground mb-1">Monthly Volume</div>
                <div className="text-2xl font-bold">{formatCurrency(estimate.estimate.monthly_volume)}</div>
              </div>
              <div className="p-4 rounded-lg bg-secondary/50 border border-border">
                <div className="text-xs text-muted-foreground mb-1">% of Volume</div>
                <div className="text-2xl font-bold">{estimate.estimate.fee_pct_of_volume.toFixed(3)}%</div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

