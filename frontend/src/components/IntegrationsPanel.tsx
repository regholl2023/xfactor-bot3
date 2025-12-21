import { useState } from 'react'

export function IntegrationsPanel() {
  const [showConfig, setShowConfig] = useState(false)
  
  const brokers = [
    { name: 'Interactive Brokers', status: 'connected', color: 'text-profit', configurable: true },
    { name: 'Alpaca', status: 'ready', color: 'text-muted-foreground', configurable: true },
    { name: 'Charles Schwab', status: 'ready', color: 'text-muted-foreground', configurable: true },
    { name: 'Tradier', status: 'ready', color: 'text-muted-foreground', configurable: true },
  ]
  
  const dataSources = [
    { name: 'TradingView', status: 'webhooks active', color: 'text-profit', configurable: true },
    { name: 'Polygon.io', status: 'ready', color: 'text-muted-foreground', configurable: true },
    { name: 'Yahoo Finance', status: 'enabled', color: 'text-profit', configurable: false },
  ]
  
  const aiProviders = [
    { name: 'OpenAI GPT-4', status: 'not configured', color: 'text-yellow-500', configurable: true },
    { name: 'Anthropic Claude', status: 'not configured', color: 'text-yellow-500', configurable: true },
    { name: 'Ollama (Local)', status: 'checking...', color: 'text-muted-foreground', configurable: true },
  ]
  
  const banking = [
    { name: 'Plaid', status: 'ready', color: 'text-muted-foreground', configurable: true },
  ]

  return (
    <div className="space-y-4">
      {/* Brokers */}
      <div>
        <h4 className="text-sm font-medium text-muted-foreground mb-2">Brokers</h4>
        <div className="space-y-2">
          {brokers.map((broker) => (
            <div key={broker.name} className="flex items-center justify-between text-sm">
              <span className="text-foreground">{broker.name}</span>
              <div className="flex items-center gap-2">
                <span className={broker.color}>{broker.status}</span>
                {showConfig && broker.configurable && (
                  <button className="text-xs text-blue-400 hover:text-blue-300">Configure</button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Data Sources */}
      <div>
        <h4 className="text-sm font-medium text-muted-foreground mb-2">Data Sources</h4>
        <div className="space-y-2">
          {dataSources.map((source) => (
            <div key={source.name} className="flex items-center justify-between text-sm">
              <span className="text-foreground">{source.name}</span>
              <div className="flex items-center gap-2">
                <span className={source.color}>{source.status}</span>
                {showConfig && source.configurable && (
                  <button className="text-xs text-blue-400 hover:text-blue-300">Configure</button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* AI Providers - shown when managing */}
      {showConfig && (
        <div>
          <h4 className="text-sm font-medium text-muted-foreground mb-2">AI Providers</h4>
          <div className="space-y-2">
            {aiProviders.map((provider) => (
              <div key={provider.name} className="flex items-center justify-between text-sm">
                <span className="text-foreground">{provider.name}</span>
                <div className="flex items-center gap-2">
                  <span className={provider.color}>{provider.status}</span>
                  <button className="text-xs text-blue-400 hover:text-blue-300">Configure</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Banking */}
      <div>
        <h4 className="text-sm font-medium text-muted-foreground mb-2">Banking</h4>
        <div className="space-y-2">
          {banking.map((bank) => (
            <div key={bank.name} className="flex items-center justify-between text-sm">
              <span className="text-foreground">{bank.name}</span>
              <div className="flex items-center gap-2">
                <span className={bank.color}>{bank.status}</span>
                {showConfig && bank.configurable && (
                  <button className="text-xs text-blue-400 hover:text-blue-300">Configure</button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <button 
        onClick={() => setShowConfig(!showConfig)}
        className={`w-full mt-2 px-4 py-2 text-sm rounded-lg transition-colors border ${
          showConfig 
            ? 'bg-blue-600 hover:bg-blue-700 text-white border-blue-500' 
            : 'bg-secondary hover:bg-secondary/80 border-border'
        }`}
      >
        {showConfig ? '✓ Done Managing' : '⚙️ Manage Integrations'}
      </button>
    </div>
  )
}

