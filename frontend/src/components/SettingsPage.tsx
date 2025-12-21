import { Settings, Shield, Lock, Wallet, DollarSign, ArrowLeft } from 'lucide-react'
import { StrategyPanel } from './StrategyPanel'
import { RiskControls } from './RiskControls'
import { AdminPanel } from './AdminPanel'
import { IntegrationsPanel } from './IntegrationsPanel'
import { FeeTracker } from './FeeTracker'
import { CollapsiblePanel } from './CollapsiblePanel'

interface SettingsPageProps {
  onBack: () => void
}

export function SettingsPage({ onBack }: SettingsPageProps) {
  return (
    <div className="space-y-6">
      {/* Header with Back Button */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="flex items-center gap-2 px-4 py-2 bg-secondary hover:bg-secondary/80 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Dashboard</span>
          </button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Settings className="h-6 w-6 text-teal-400" />
              Settings & Configuration
            </h1>
            <p className="text-sm text-muted-foreground">
              Manage strategies, risk controls, integrations, and administrative settings
            </p>
          </div>
        </div>
      </div>

      {/* Settings Panels Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <CollapsiblePanel
            title="Strategy Controls"
            icon={<Settings className="h-5 w-5" />}
            defaultExpanded={true}
          >
            <StrategyPanel />
          </CollapsiblePanel>

          <CollapsiblePanel
            title="Risk Management"
            icon={<Shield className="h-5 w-5" />}
            defaultExpanded={true}
          >
            <RiskControls />
          </CollapsiblePanel>

          <CollapsiblePanel
            title="Fees & Expenses"
            icon={<DollarSign className="h-5 w-5" />}
            badge="costs"
            defaultExpanded={false}
          >
            <FeeTracker />
          </CollapsiblePanel>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <CollapsiblePanel
            title="Admin Panel"
            icon={<Lock className="h-5 w-5" />}
            defaultExpanded={true}
          >
            <AdminPanel />
          </CollapsiblePanel>

          <CollapsiblePanel
            title="Integrations"
            icon={<Wallet className="h-5 w-5" />}
            defaultExpanded={true}
          >
            <IntegrationsPanel />
          </CollapsiblePanel>
        </div>
      </div>
    </div>
  )
}

