import { useState } from 'react';
import { X, HelpCircle, Zap, Bot, LineChart, Shield, Settings, Cpu, Globe, Calendar, Book, TrendingUp, TrendingDown, BarChart3, Activity, Target, Layers, Search, ChevronDown, ChevronUp } from 'lucide-react';

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const VERSION = '1.0.4';
const RELEASE_DATE = 'December 18, 2025';

const features = [
  {
    icon: Bot,
    title: '37+ Trading Bots',
    description: 'Pre-configured bots for stocks, options, futures, crypto, and commodities with customizable strategies.'
  },
  {
    icon: Zap,
    title: 'Multi-Broker Support',
    description: 'Connect to IBKR, Alpaca, Schwab, Tradier, and NinjaTrader 8 for futures. OAuth, API keys, or username/password.'
  },
  {
    icon: LineChart,
    title: 'Volatility-Adaptive Stops',
    description: 'ATR-based dynamic stop losses and take profits that automatically adjust to market volatility.'
  },
  {
    icon: Shield,
    title: 'Risk Management',
    description: 'Real-time VaR, max drawdown protection, Martingale sizing options, and VIX-based circuit breakers.'
  },
  {
    icon: Cpu,
    title: 'AI-Powered Analysis',
    description: 'Integration with OpenAI, Anthropic Claude, and local Ollama for market insights and strategy optimization.'
  },
  {
    icon: Calendar,
    title: 'Market Regime Detection',
    description: 'Automatic trend vs range detection with ADX, Bollinger squeeze, and trading recommendations.'
  },
  {
    icon: Settings,
    title: 'Strategy Templates & Builder',
    description: '10+ pre-built strategy templates plus visual drag-and-drop strategy builder for custom strategies.'
  },
  {
    icon: Globe,
    title: 'Social Trading & TradingView',
    description: 'Copy top traders, share strategies, and receive TradingView webhook alerts directly.'
  }
];

const quickStart = [
  { step: 1, title: 'Connect Broker', description: 'Go to Admin Panel > Broker Config and connect your trading account.' },
  { step: 2, title: 'Select Trading Mode', description: 'Choose Demo (simulated), Paper (broker paper trading), or Live mode.' },
  { step: 3, title: 'Configure Bots', description: 'Enable desired bots from the Bot Manager panel and customize their strategies.' },
  { step: 4, title: 'Set Risk Controls', description: 'Configure position limits, stop-losses, and daily loss limits in Risk Controls.' },
  { step: 5, title: 'Start Trading', description: 'Click Start on individual bots or use Start All to begin automated trading.' }
];

const changelog = [
  {
    version: '1.0.4',
    date: 'December 18, 2025',
    changes: [
      '📊 Stock Analyzer - Comprehensive Time Series Analysis',
      'Search any stock across all global exchanges',
      'Interactive candlestick chart with technical overlays',
      'Toggle SMA/EMA/RSI/Volume overlays independently',
      '🎯 Inflection Point Detection (peaks, troughs, crossovers)',
      'Golden Cross & Death Cross visual markers',
      '📈 Analyst Price Targets with projection lines',
      'Target Meeting Analysis with confidence levels',
      'Earnings history with surprise tracking',
      'Future EPS estimates visualization',
      'Fundamental metrics: P/E, PEG, profit margin, beta'
    ]
  },
  {
    version: '1.0.3',
    date: 'December 17, 2025',
    changes: [
      '🔮 AI-Powered Market Forecasting Engine',
      '📹 Video Platform Analysis (YouTube, TikTok, Instagram)',
      '🛡️ Bot Risk Management System (0-100 scoring)',
      'Track FinTok & YouTube finance influencers',
      'Viral content alerts across all platforms',
      'Risk-Adjusted Metrics: Sharpe, Sortino, VaR',
      'Social Sentiment (Twitter/X, Reddit, StockTwits)',
      'Speculation Scoring Algorithm',
      'Catalyst Tracker & AI Hypothesis Generator',
      '50+ Known Financial Influencer Database'
    ]
  },
  {
    version: '1.0.2',
    date: 'December 17, 2025',
    changes: [
      '🌍 Comprehensive Forex Trading',
      '60+ Currency Pairs with pip calculator',
      'Currency Strength Meter',
      'Economic Calendar',
      'MT5 & OANDA Integration'
    ]
  },
  {
    version: '1.0.1',
    date: 'December 17, 2025',
    changes: [
      '🎉 Quantvue-Inspired Features',
      'Volatility-Adaptive SL/TP with ATR-based dynamic stops',
      'TradingView Webhook Integration',
      'Market Regime Detection',
      'Martingale Position Sizing',
      'Strategy Templates Library (10+ strategies)',
      'NinjaTrader 8 Integration',
      'Visual Strategy Builder',
      'Social Trading Platform'
    ]
  },
  {
    version: '0.9.8',
    date: 'December 17, 2025',
    changes: [
      'Platform-specific fixes for Windows and Linux releases',
      'Exclude uvloop on Windows (Unix-only library)',
      'Enhanced zombie process cleanup with fallback commands',
      'Comprehensive debug logging for connection troubleshooting',
      'Fixed WebSocket connection loops (stable refs, no dependency loops)'
    ]
  },
  {
    version: '0.9.7',
    date: 'December 16, 2025',
    changes: [
      'Offline admin login - works even when backend is down',
      'Enhanced debug logging for "Failed to fetch bots" errors',
      'Fixed CSP to allow 127.0.0.1 connections in desktop app',
      'Improved API URL handling for Tauri desktop',
      'Added agentic tuning algorithm (ATRWAC) for bot optimization',
      'Zombie process cleanup scripts for macOS/Linux/Windows'
    ]
  },
  {
    version: '0.9.6',
    date: 'December 16, 2025',
    changes: [
      'Rebuilt x64 backend with all dependencies properly bundled',
      'Fixed Gatekeeper blocking on Intel Macs',
      'ChromeOS support via Linux .deb package',
      'Manual DMG creation fallback for reliable builds',
      'Version sync across all config files'
    ]
  },
  {
    version: '0.9.5',
    date: 'December 15, 2025',
    changes: [
      'Help popup with features, quick start, and changelog',
      'API-based LLM support (OpenAI, Anthropic, Ollama)',
      'Replaced pandas-ta with ta library for NumPy compatibility',
      'Cross-platform desktop builds (macOS ARM64/Intel, Windows, Linux)',
      'Added hypothesis testing framework'
    ]
  },
  {
    version: '0.9.4',
    date: 'December 13, 2025',
    changes: [
      'Fixed sidecar binary bundling for desktop app',
      'Backend auto-launch improvements'
    ]
  },
  {
    version: '0.9.3',
    date: 'December 13, 2025',
    changes: [
      'Auto-Tune UI for automatic strategy optimization',
      'Seasonal Events UI in Strategy Controls',
      'Enhanced bot details with Win Rate, Uptime, Error tracking'
    ]
  },
  {
    version: '0.9.0',
    date: 'December 12, 2025',
    changes: [
      'Desktop application with Tauri',
      'Multiple broker authentication methods',
      '37 pre-configured trading bots',
      'Global stock exchange support (40+ exchanges)'
    ]
  }
];

// ============================================================================
// GLOSSARY DATA - Trading Terminology Encyclopedia
// ============================================================================

interface GlossaryTerm {
  term: string;
  category: 'basics' | 'indicators' | 'strategies' | 'risk' | 'fundamentals' | 'patterns';
  shortDef: string;
  fullExplanation: string;
  whyUseful: string;
  whyNotUseful?: string;
  formula?: string;
  example?: string;
  xfactorUsage?: string;
  relatedTerms?: string[];
  visualType?: 'chart' | 'diagram' | 'formula' | 'table';
}

const glossaryTerms: GlossaryTerm[] = [
  // ===== BASICS =====
  {
    term: 'Bullish',
    category: 'basics',
    shortDef: 'Expecting prices to rise',
    fullExplanation: 'A bullish outlook means expecting the price of a security to increase. The term comes from how a bull attacks—thrusting its horns upward. When someone is "bullish" on a stock, they believe it will go up in value.',
    whyUseful: 'Understanding market sentiment helps you align your trades with the overall direction. Trading with the trend (bullish in an uptrend) typically has higher success rates than fighting it.',
    example: 'If NVDA is trading at $130 and you believe it will reach $150, you are bullish on NVDA. You might buy shares or call options.',
    xfactorUsage: 'XFactor displays bullish/bearish sentiment in the Market Forecasting panel based on social media analysis and technical indicators.',
    relatedTerms: ['Bearish', 'Trend', 'Long Position'],
  },
  {
    term: 'Bearish',
    category: 'basics',
    shortDef: 'Expecting prices to fall',
    fullExplanation: 'A bearish outlook means expecting the price to decrease. The term comes from how a bear attacks—swiping its paws downward. Bearish traders profit from falling prices through short selling or put options.',
    whyUseful: 'Recognizing bearish conditions helps you avoid buying at tops and potentially profit from downtrends. Bear markets present opportunities for short sellers.',
    whyNotUseful: 'Being overly bearish in a strong bull market can cause you to miss significant gains. Markets have historically trended upward over long periods.',
    example: 'If you think a company will miss earnings and drop from $100 to $80, you are bearish and might buy put options or short the stock.',
    relatedTerms: ['Bullish', 'Short Position', 'Put Option'],
  },
  {
    term: 'P&L (Profit & Loss)',
    category: 'basics',
    shortDef: 'The net gain or loss from trades',
    fullExplanation: 'P&L represents the total profit or loss from your trading activities. It can be calculated as "realized" (closed trades) or "unrealized" (open positions). Understanding P&L is fundamental to evaluating trading performance.',
    whyUseful: 'Tracking P&L helps you understand your actual trading performance, identify which strategies work, and make informed decisions about position sizing.',
    formula: 'P&L = (Exit Price - Entry Price) × Quantity × (1 if Long, -1 if Short) - Fees',
    example: 'Buy 100 shares at $50, sell at $55. P&L = ($55 - $50) × 100 = $500 profit (before fees)',
    xfactorUsage: 'XFactor tracks P&L for each bot in real-time, displaying daily, weekly, and all-time P&L in the dashboard.',
    relatedTerms: ['ROI', 'Win Rate', 'Drawdown'],
  },
  {
    term: 'Long Position',
    category: 'basics',
    shortDef: 'Buying an asset expecting it to rise',
    fullExplanation: 'Going "long" means buying a security with the expectation that its price will increase. You profit when the price goes up and lose when it goes down. This is the most common type of trade.',
    whyUseful: 'Long positions are straightforward and align with the natural upward bias of equity markets over time. No borrowing costs or short-selling restrictions.',
    example: 'You buy 50 shares of AAPL at $180. If the price rises to $200, your profit is $1,000. If it falls to $160, your loss is $1,000.',
    relatedTerms: ['Short Position', 'Bullish', 'Buy and Hold'],
  },
  {
    term: 'Short Position',
    category: 'basics',
    shortDef: 'Selling borrowed shares expecting price to fall',
    fullExplanation: 'Short selling involves borrowing shares from your broker and selling them immediately, hoping to buy them back later at a lower price. You profit from price declines but have unlimited loss potential if prices rise.',
    whyUseful: 'Shorting allows you to profit in bearish markets and hedge long positions. It provides opportunities regardless of market direction.',
    whyNotUseful: 'Short positions have unlimited loss potential (price can rise infinitely), borrowing costs, and short squeezes can cause rapid losses.',
    example: 'You borrow and sell 100 shares at $50. If the price drops to $40, you buy back (cover) for $4,000, keeping the $1,000 difference. If it rises to $70, you lose $2,000.',
    relatedTerms: ['Long Position', 'Short Squeeze', 'Margin'],
  },
  {
    term: 'Spread',
    category: 'basics',
    shortDef: 'The difference between bid and ask prices',
    fullExplanation: 'The spread is the difference between the highest price a buyer is willing to pay (bid) and the lowest price a seller is willing to accept (ask). Tighter spreads indicate more liquidity.',
    whyUseful: 'Understanding spreads helps you calculate true trading costs. In highly liquid markets, spreads are minimal; in illiquid markets, they can significantly impact profits.',
    formula: 'Spread = Ask Price - Bid Price',
    example: 'If AAPL bid is $179.95 and ask is $180.00, the spread is $0.05. Buying 1000 shares costs you $50 just in spread.',
    relatedTerms: ['Bid', 'Ask', 'Liquidity', 'Slippage'],
  },
  {
    term: 'Volume',
    category: 'basics',
    shortDef: 'Number of shares traded in a period',
    fullExplanation: 'Volume represents the total number of shares or contracts traded during a specific time period. High volume confirms price movements, while low volume may indicate weak trends.',
    whyUseful: 'Volume confirms trend strength—rising prices on high volume suggest strong buying interest. Breakouts on high volume are more reliable than those on low volume.',
    whyNotUseful: 'Volume alone doesn\'t indicate direction. High volume can occur during both advances and declines.',
    example: 'A stock breaks above resistance with 3x normal volume—this is a strong bullish signal. The same breakout on 0.5x volume might be a false breakout.',
    xfactorUsage: 'XFactor displays volume overlays on charts and uses volume analysis in breakout detection strategies.',
    relatedTerms: ['OBV', 'Volume Profile', 'Liquidity'],
  },
  {
    term: 'Volatility',
    category: 'basics',
    shortDef: 'The degree of price variation over time',
    fullExplanation: 'Volatility measures how much a price fluctuates. High volatility means larger price swings (more risk and opportunity); low volatility means smaller, steadier movements. Implied volatility reflects expected future volatility.',
    whyUseful: 'Volatility helps determine position sizing, stop-loss distances, and option pricing. Adaptive strategies adjust to volatility conditions.',
    formula: 'Historical Volatility = Standard Deviation of Returns × √252 (annualized)',
    example: 'A stock with 40% annual volatility might swing ±2.5% daily on average. A 20% volatility stock might only move ±1.25% daily.',
    xfactorUsage: 'XFactor uses ATR (Average True Range) for volatility-adaptive stop losses and position sizing. VIX-based circuit breakers pause trading in extreme volatility.',
    relatedTerms: ['ATR', 'VIX', 'Standard Deviation', 'Beta'],
  },

  // ===== TECHNICAL INDICATORS =====
  {
    term: 'SMA (Simple Moving Average)',
    category: 'indicators',
    shortDef: 'Average price over a specific period',
    fullExplanation: 'SMA calculates the arithmetic mean of prices over N periods. Common periods are 20 (short-term), 50 (medium-term), and 200 (long-term). It smooths out price noise to identify trend direction.',
    whyUseful: 'SMAs identify trend direction, provide dynamic support/resistance levels, and generate crossover signals. The 200 SMA is widely watched by institutions.',
    whyNotUseful: 'SMAs lag price action because they use historical data. They work poorly in choppy, sideways markets and can generate many false signals.',
    formula: 'SMA = (P₁ + P₂ + ... + Pₙ) / n',
    example: '20 SMA: Add the last 20 closing prices, divide by 20. If prices are above the SMA, the short-term trend is up.',
    xfactorUsage: 'XFactor offers SMA 20, 50, and 200 as chart overlays. The trend_ma_crossover strategy uses SMA crossovers for entry signals.',
    relatedTerms: ['EMA', 'Golden Cross', 'Death Cross', 'Moving Average'],
    visualType: 'chart',
  },
  {
    term: 'EMA (Exponential Moving Average)',
    category: 'indicators',
    shortDef: 'Weighted moving average favoring recent prices',
    fullExplanation: 'EMA gives more weight to recent prices, making it more responsive to new information than SMA. The weighting decreases exponentially. Common periods are 12 and 26 for MACD, or 9 for short-term trading.',
    whyUseful: 'EMAs react faster to price changes, catching trend reversals earlier. They\'re preferred by short-term traders who need quicker signals.',
    whyNotUseful: 'The increased sensitivity means more false signals in choppy markets. May whipsaw more than SMA during consolidation.',
    formula: 'EMA = (Price × k) + (Previous EMA × (1-k)), where k = 2/(n+1)',
    example: '12 EMA crossing above 26 EMA is a bullish signal (MACD crossover). Crossing below is bearish.',
    xfactorUsage: 'XFactor offers EMA 12 and EMA 26 overlays, used in trend_adx_macd and momentum strategies.',
    relatedTerms: ['SMA', 'MACD', 'Moving Average'],
    visualType: 'chart',
  },
  {
    term: 'RSI (Relative Strength Index)',
    category: 'indicators',
    shortDef: 'Momentum oscillator measuring overbought/oversold conditions',
    fullExplanation: 'RSI measures the speed and magnitude of price changes on a 0-100 scale. Readings above 70 suggest overbought conditions (potential pullback), while below 30 suggests oversold (potential bounce). The standard period is 14.',
    whyUseful: 'RSI helps identify potential reversal points and confirm trend strength. Divergences between RSI and price often precede reversals.',
    whyNotUseful: 'In strong trends, RSI can remain overbought/oversold for extended periods. Using it alone for entries can result in fighting the trend.',
    formula: 'RSI = 100 - (100 / (1 + RS)), where RS = Avg Gain / Avg Loss over n periods',
    example: 'RSI drops to 25 while price makes a new low—this oversold condition might signal a buying opportunity. RSI divergence (price makes lower low, RSI makes higher low) is a bullish signal.',
    xfactorUsage: 'XFactor displays RSI as an overlay and uses it in reversion_rsi_bb and momentum_rsi_divergence strategies.',
    relatedTerms: ['Oversold', 'Overbought', 'Divergence', 'Momentum'],
    visualType: 'chart',
  },
  {
    term: 'MACD (Moving Average Convergence Divergence)',
    category: 'indicators',
    shortDef: 'Trend-following momentum indicator',
    fullExplanation: 'MACD shows the relationship between two EMAs (typically 12 and 26). The MACD line is the difference between these EMAs. A 9-period EMA of MACD (signal line) triggers buy/sell signals when crossed.',
    whyUseful: 'MACD captures both trend direction and momentum. Crossovers, divergences, and histogram patterns provide multiple signal types.',
    whyNotUseful: 'As a lagging indicator, MACD often signals after moves have begun. It can produce many false signals in ranging markets.',
    formula: 'MACD Line = 12 EMA - 26 EMA; Signal Line = 9 EMA of MACD Line; Histogram = MACD - Signal',
    example: 'MACD crosses above signal line = bullish. Histogram expanding above zero = strengthening bullish momentum.',
    xfactorUsage: 'XFactor uses MACD in the trend_adx_macd strategy template for trend confirmation.',
    relatedTerms: ['EMA', 'Crossover', 'Divergence', 'Histogram'],
    visualType: 'chart',
  },
  {
    term: 'Bollinger Bands',
    category: 'indicators',
    shortDef: 'Volatility bands around a moving average',
    fullExplanation: 'Bollinger Bands consist of a 20-period SMA (middle band) with upper and lower bands set at 2 standard deviations. Bands widen during high volatility and narrow during low volatility (squeeze).',
    whyUseful: 'Bands provide dynamic support/resistance and identify volatility conditions. Squeezes often precede large moves. Price touching bands can signal reversals.',
    whyNotUseful: 'In strong trends, price can "walk the band" staying at extremes. Using bands alone for mean reversion can be dangerous in trending markets.',
    formula: 'Upper Band = 20 SMA + (2 × StdDev); Lower Band = 20 SMA - (2 × StdDev)',
    example: 'Bollinger squeeze (bands narrowing) followed by expansion often signals a breakout. Price hitting lower band in uptrend might be a buy-the-dip opportunity.',
    xfactorUsage: 'XFactor uses Bollinger Bands in reversion_rsi_bb and breakout_squeeze strategies. The stdDev parameter controls band width.',
    relatedTerms: ['Standard Deviation', 'Squeeze', 'Volatility', 'Mean Reversion'],
    visualType: 'chart',
  },
  {
    term: 'ATR (Average True Range)',
    category: 'indicators',
    shortDef: 'Measures market volatility',
    fullExplanation: 'ATR calculates the average of "true ranges" over a period (typically 14). True range is the greatest of: current high minus low, absolute value of high minus previous close, or absolute value of low minus previous close.',
    whyUseful: 'ATR is essential for position sizing and setting stop-losses that adapt to current volatility. A 2 ATR stop gives your trade room to breathe.',
    whyNotUseful: 'ATR doesn\'t indicate direction—only volatility magnitude. It can\'t tell you if price will go up or down.',
    formula: 'True Range = max(High-Low, |High-PrevClose|, |Low-PrevClose|); ATR = 14-period average of TR',
    example: 'If ATR is $5, a 2 ATR stop-loss would be $10 from entry. This adapts automatically—in calm markets ATR shrinks, in volatile markets it expands.',
    xfactorUsage: 'XFactor uses ATR for volatility-adaptive stop losses. The ATR multiplier setting controls how many ATRs away stops are placed.',
    relatedTerms: ['Volatility', 'Stop Loss', 'Position Sizing'],
    visualType: 'formula',
  },
  {
    term: 'ADX (Average Directional Index)',
    category: 'indicators',
    shortDef: 'Measures trend strength (not direction)',
    fullExplanation: 'ADX measures how strong a trend is on a 0-100 scale, regardless of direction. Readings above 25 indicate a strong trend; below 20 indicates a weak or ranging market. It\'s derived from +DI and -DI directional indicators.',
    whyUseful: 'ADX helps you decide whether to use trend-following or mean-reversion strategies. High ADX = trend strategies; Low ADX = range strategies.',
    whyNotUseful: 'ADX doesn\'t indicate direction—you need +DI/-DI or price action for that. It also lags, so trends may be ending when ADX peaks.',
    formula: 'ADX = 14-period smoothed average of DX, where DX = |(+DI - -DI)| / (+DI + -DI) × 100',
    example: 'ADX at 35 with +DI > -DI = strong uptrend. ADX at 15 = ranging market, use range-bound strategies instead.',
    xfactorUsage: 'XFactor uses ADX in Market Regime Detection. ADX > 25 triggers trend-following mode; ADX < 20 triggers range mode.',
    relatedTerms: ['Trend', 'DMI', 'Market Regime'],
    visualType: 'chart',
  },
  {
    term: 'Fibonacci Retracement',
    category: 'indicators',
    shortDef: 'Key price levels based on Fibonacci ratios',
    fullExplanation: 'Fibonacci retracement levels (23.6%, 38.2%, 50%, 61.8%, 78.6%) are horizontal lines indicating potential support/resistance based on the Fibonacci sequence. They\'re drawn from swing high to swing low (or vice versa).',
    whyUseful: 'Many traders watch Fibonacci levels, creating self-fulfilling prophecies. The 61.8% "golden ratio" level is particularly significant for pullback entries.',
    whyNotUseful: 'Fibonacci levels are subjective—different traders draw them differently. They don\'t always hold and work better in trending markets.',
    example: 'In an uptrend from $100 to $150, the 61.8% retracement is $119 (38.2% pullback). Buying near this level offers a potential bounce with defined risk.',
    xfactorUsage: 'XFactor displays Fibonacci levels in the Stock Analyzer chart for identifying key support/resistance zones.',
    relatedTerms: ['Support', 'Resistance', 'Retracement', 'Golden Ratio'],
    visualType: 'chart',
  },
  {
    term: 'VWAP (Volume Weighted Average Price)',
    category: 'indicators',
    shortDef: 'Average price weighted by volume',
    fullExplanation: 'VWAP calculates the average price weighted by volume for the day. Institutional traders use it as a benchmark—buying below VWAP is considered "good" execution. It resets each trading day.',
    whyUseful: 'VWAP provides dynamic intraday support/resistance. Price above VWAP is bullish; below is bearish. Institutions often target VWAP for large orders.',
    whyNotUseful: 'VWAP is primarily an intraday tool—less useful for swing or position traders. It loses meaning after the first hour of trading.',
    formula: 'VWAP = Σ(Price × Volume) / Σ(Volume)',
    example: 'A stock opens at $100, rises to $105 on high volume, then drifts. If VWAP is $103, buying near $103 might find support.',
    xfactorUsage: 'XFactor uses VWAP in the scalp_vwap_reversion strategy for intraday mean reversion trades.',
    relatedTerms: ['Volume', 'Intraday', 'Mean Reversion'],
    visualType: 'chart',
  },
  {
    term: 'Stochastic Oscillator',
    category: 'indicators',
    shortDef: 'Momentum indicator comparing close to price range',
    fullExplanation: 'Stochastic measures where the current close is relative to the high-low range over a period (typically 14). %K is the main line; %D is a 3-period SMA of %K. Readings above 80 are overbought; below 20 are oversold.',
    whyUseful: 'Stochastic is more sensitive than RSI, catching turns earlier. It works well in ranging markets for identifying reversal points.',
    whyNotUseful: 'In strong trends, Stochastic can remain overbought/oversold for extended periods, generating premature reversal signals.',
    formula: '%K = (Current Close - Lowest Low) / (Highest High - Lowest Low) × 100',
    example: 'Stochastic %K crosses above %D from below 20 = bullish reversal signal. Works best when confirmed by price action.',
    relatedTerms: ['RSI', 'Overbought', 'Oversold', 'Momentum'],
    visualType: 'chart',
  },

  // ===== STRATEGIES =====
  {
    term: 'Trend Following',
    category: 'strategies',
    shortDef: 'Trading in the direction of the prevailing trend',
    fullExplanation: 'Trend following strategies buy when prices are rising and sell when prices are falling. They use indicators like moving averages, ADX, or price action to identify and follow trends until they reverse.',
    whyUseful: 'Trends tend to persist longer than expected. "The trend is your friend" captures the idea that trading with momentum increases win probability.',
    whyNotUseful: 'Trend following suffers during ranging/choppy markets with frequent whipsaws. It also means buying after prices have already moved up.',
    example: 'Buy when price crosses above 50 SMA and RSI > 50. Hold until price closes below 50 SMA. This captures trending moves while avoiding chop.',
    xfactorUsage: 'XFactor offers trend_ma_crossover, trend_adx_macd, and trend_supertrend strategy templates.',
    relatedTerms: ['Moving Average', 'ADX', 'Breakout', 'Momentum'],
  },
  {
    term: 'Mean Reversion',
    category: 'strategies',
    shortDef: 'Trading based on price returning to average',
    fullExplanation: 'Mean reversion assumes prices oscillate around a central value (mean) and will eventually return to it. Traders buy when price is "too low" and sell when "too high" relative to this mean.',
    whyUseful: 'Works well in range-bound markets where prices oscillate between support and resistance. Many statistical arbitrage strategies are mean-reverting.',
    whyNotUseful: 'Can be disastrous in trending markets—"catching a falling knife." What seems oversold can become more oversold.',
    example: 'Buy when RSI < 30 and price touches lower Bollinger Band. Sell when RSI > 70 or price touches upper band.',
    xfactorUsage: 'XFactor offers reversion_rsi_bb and reversion_zscore strategy templates for mean reversion trading.',
    relatedTerms: ['RSI', 'Bollinger Bands', 'Oversold', 'Statistical Arbitrage'],
  },
  {
    term: 'Breakout Trading',
    category: 'strategies',
    shortDef: 'Entering when price breaks key levels',
    fullExplanation: 'Breakout trading involves entering positions when price moves beyond established support/resistance levels with conviction (usually confirmed by volume). The idea is that breaking a level often leads to continued momentum.',
    whyUseful: 'Breakouts can capture the beginning of new trends. When combined with volume confirmation, they offer defined entry points with clear invalidation levels.',
    whyNotUseful: 'Many breakouts fail (false breakouts), leading to losses. Breakouts often occur at extremes, making stop placement challenging.',
    example: 'Stock consolidates between $95-$100 for weeks. Buy when it closes above $100 on 2x average volume, with stop at $98.',
    xfactorUsage: 'XFactor offers breakout_donchian and breakout_squeeze strategy templates.',
    relatedTerms: ['Support', 'Resistance', 'Volume', 'False Breakout'],
  },
  {
    term: 'Scalping',
    category: 'strategies',
    shortDef: 'Very short-term trading for small profits',
    fullExplanation: 'Scalping involves making many trades throughout the day to capture small price movements. Positions are held for seconds to minutes. Success requires tight spreads, fast execution, and strict discipline.',
    whyUseful: 'Scalping can generate consistent small profits with limited overnight risk. High frequency means many opportunities per day.',
    whyNotUseful: 'Transaction costs can eat into profits. Requires constant attention and fast execution. Stressful and time-intensive.',
    example: 'Buy at VWAP support, sell when price moves 10 cents (0.1%). Do this 50 times per day for $500 profit.',
    xfactorUsage: 'XFactor offers scalp_vwap_reversion for intraday scalping strategies.',
    relatedTerms: ['VWAP', 'Day Trading', 'Spread', 'Slippage'],
  },
  {
    term: 'Momentum Trading',
    category: 'strategies',
    shortDef: 'Trading based on the strength of price movement',
    fullExplanation: 'Momentum trading bets that stocks with strong recent performance will continue performing well, and weak performers will continue underperforming. It\'s based on behavioral finance—investors tend to herd.',
    whyUseful: 'Momentum is one of the most documented anomalies in finance. Strong momentum stocks often continue rising due to institutional buying and FOMO.',
    whyNotUseful: 'Momentum can reverse suddenly, especially in high-flying stocks. Buying high hoping for higher is psychologically difficult.',
    example: 'Screen for stocks up 20%+ in the past month with positive RSI. Buy the strongest, sell when momentum fades (RSI divergence).',
    xfactorUsage: 'XFactor uses momentum_rsi_divergence strategy and includes momentum scoring in the speculation algorithm.',
    relatedTerms: ['RSI', 'Relative Strength', 'Trend', 'FOMO'],
  },
  {
    term: 'Golden Cross',
    category: 'strategies',
    shortDef: 'Bullish signal when short MA crosses above long MA',
    fullExplanation: 'A Golden Cross occurs when a shorter-term moving average (typically 50 SMA) crosses above a longer-term one (typically 200 SMA). It signals a potential shift from bearish to bullish trend.',
    whyUseful: 'Golden Crosses often mark the beginning of major bull runs. The 50/200 crossover is widely watched by institutions.',
    whyNotUseful: 'Golden Crosses lag significantly—by the time it triggers, much of the move may be over. False signals occur in choppy markets.',
    example: 'S&P 500\'s 50 SMA crosses above 200 SMA. Historically, this has preceded major bull markets, though not always immediately.',
    xfactorUsage: 'XFactor detects Golden Crosses in the Stock Analyzer inflection point detection.',
    relatedTerms: ['Death Cross', 'SMA', 'Trend Reversal'],
    visualType: 'chart',
  },
  {
    term: 'Death Cross',
    category: 'strategies',
    shortDef: 'Bearish signal when short MA crosses below long MA',
    fullExplanation: 'A Death Cross occurs when a shorter-term moving average crosses below a longer-term one. It suggests potential trend reversal from bullish to bearish.',
    whyUseful: 'Death Crosses can signal the start of bear markets, helping you reduce exposure or hedge.',
    whyNotUseful: 'Like Golden Crosses, Death Crosses lag. They often trigger near market bottoms after much of the decline has occurred.',
    example: 'SPY\'s 50 SMA crosses below 200 SMA. This triggered in 2008 and 2022, preceding further declines—but also in 2015 which was a false signal.',
    xfactorUsage: 'XFactor detects Death Crosses in the Stock Analyzer inflection point detection.',
    relatedTerms: ['Golden Cross', 'SMA', 'Bear Market'],
    visualType: 'chart',
  },
  {
    term: 'Martingale',
    category: 'strategies',
    shortDef: 'Doubling down after losses',
    fullExplanation: 'Martingale involves doubling position size after each loss, so that one win recovers all losses plus original profit. It\'s derived from gambling theory and is extremely risky.',
    whyUseful: 'In theory, a single win recovers all previous losses. Can work in mean-reverting markets with high win rates.',
    whyNotUseful: 'EXTREMELY DANGEROUS. A losing streak can exponentially increase position size until account is blown. Even small losing streaks require huge capital.',
    example: 'Bet $100, lose. Bet $200, lose. Bet $400, lose. Bet $800, win $800. Net: -$100-$200-$400+$800 = +$100. But what if you lost 10 times?',
    xfactorUsage: 'XFactor offers Martingale position sizing as an OPTIONAL feature with strict limits. Use with extreme caution.',
    relatedTerms: ['Position Sizing', 'Risk Management', 'Drawdown'],
  },

  // ===== RISK MANAGEMENT =====
  {
    term: 'Stop Loss',
    category: 'risk',
    shortDef: 'Order to exit position at a predetermined loss level',
    fullExplanation: 'A stop loss is an order that automatically closes a position when price reaches a specified level, limiting potential losses. It\'s the most fundamental risk management tool.',
    whyUseful: 'Stop losses protect capital, remove emotion from exit decisions, and define risk before entering trades. "Cut your losses short."',
    whyNotUseful: 'Stops can be triggered by volatility spikes before price reverses in your favor (stop hunting). Very tight stops increase false exits.',
    example: 'Buy AAPL at $180 with stop at $175. Maximum loss is $5 per share (2.8%). If AAPL drops to $175, position closes automatically.',
    xfactorUsage: 'XFactor uses ATR-based dynamic stop losses that adapt to volatility. Configured via ATR multiplier setting.',
    relatedTerms: ['ATR', 'Risk/Reward', 'Trailing Stop', 'Take Profit'],
  },
  {
    term: 'Take Profit',
    category: 'risk',
    shortDef: 'Order to exit position at a predetermined profit level',
    fullExplanation: 'A take profit order automatically closes a position when price reaches a target level, locking in gains. It removes the temptation to hold too long or close too early.',
    whyUseful: 'Take profits ensure you capture gains rather than watching them evaporate. Helps maintain disciplined exit strategy.',
    whyNotUseful: 'In trending markets, fixed take profits can exit too early, missing larger moves. Consider trailing stops for trending strategies.',
    example: 'Buy at $100 with take profit at $110. When price hits $110, position closes with $10 profit regardless of how high it might go.',
    xfactorUsage: 'XFactor uses ATR-based dynamic take profits. The TP is typically 1.5-2x the ATR stop distance for positive risk/reward.',
    relatedTerms: ['Stop Loss', 'Risk/Reward', 'Trailing Stop'],
  },
  {
    term: 'Risk/Reward Ratio',
    category: 'risk',
    shortDef: 'Potential profit divided by potential loss',
    fullExplanation: 'Risk/Reward (R:R) compares how much you could lose versus how much you could gain on a trade. A 1:3 ratio means risking $1 to potentially make $3. Higher ratios allow lower win rates to be profitable.',
    whyUseful: 'Understanding R:R helps you take only trades where the potential payoff justifies the risk. Even 40% win rate is profitable with 1:3 R:R.',
    formula: 'R:R = (Target Price - Entry) / (Entry - Stop Loss) for longs',
    example: 'Entry $100, Stop $95, Target $115. Risk = $5, Reward = $15. R:R = 1:3. You need only 25% win rate to break even.',
    xfactorUsage: 'XFactor calculates and displays R:R for trade setups. The TP/SL multiplier settings control the ratio.',
    relatedTerms: ['Stop Loss', 'Take Profit', 'Win Rate', 'Expected Value'],
  },
  {
    term: 'Drawdown',
    category: 'risk',
    shortDef: 'Peak-to-trough decline in account value',
    fullExplanation: 'Drawdown measures the decline from a portfolio\'s peak value to its lowest point before a new peak. Maximum drawdown is the largest such decline ever recorded. It indicates worst-case scenario.',
    whyUseful: 'Drawdown measures psychological and financial pain. A 50% drawdown requires 100% gain to recover. Understanding worst-case helps with position sizing.',
    formula: 'Drawdown = (Peak Value - Trough Value) / Peak Value × 100%',
    example: 'Account peaks at $100,000, drops to $80,000. Drawdown = 20%. If this is your max drawdown, you\'ve only ever lost 20% from peak.',
    xfactorUsage: 'XFactor tracks max drawdown in bot performance metrics and can pause trading when drawdown exceeds limits.',
    relatedTerms: ['Risk Management', 'Recovery', 'Max Loss'],
  },
  {
    term: 'Position Sizing',
    category: 'risk',
    shortDef: 'Determining how much capital to allocate to a trade',
    fullExplanation: 'Position sizing determines how many shares/contracts to trade based on account size and risk tolerance. Proper sizing ensures no single trade can significantly damage the account.',
    whyUseful: 'Position sizing is arguably the most important factor in long-term success. It determines if you survive losing streaks.',
    formula: 'Position Size = (Account × Risk %) / (Entry - Stop); e.g., $100,000 × 1% / $5 stop = 200 shares',
    example: '$100,000 account, risk 1% ($1,000) per trade. With a $5 stop loss, buy 200 shares. Win or lose, you only risk $1,000.',
    xfactorUsage: 'XFactor calculates position sizes based on risk % per trade and ATR-based stops in the Risk Controls panel.',
    relatedTerms: ['Risk Management', 'Stop Loss', 'Kelly Criterion'],
  },
  {
    term: 'VaR (Value at Risk)',
    category: 'risk',
    shortDef: 'Maximum expected loss at a confidence level',
    fullExplanation: 'VaR estimates the maximum loss expected over a time period at a given confidence level. 95% daily VaR of $10,000 means there\'s only a 5% chance of losing more than $10,000 in a day.',
    whyUseful: 'VaR provides a single number to communicate portfolio risk. It\'s used by institutions and regulators for risk management.',
    whyNotUseful: 'VaR doesn\'t capture tail risks—what happens in the 5% worst cases. The 2008 crisis showed VaR\'s limitations.',
    formula: 'VaR = Portfolio Value × σ × Z-score × √time; e.g., $100,000 × 2% × 1.65 × √1 = $3,300 (95% daily)',
    example: '95% daily VaR of $5,000 means on 95% of days, you won\'t lose more than $5,000. But 5% of days could be worse.',
    xfactorUsage: 'XFactor calculates and displays real-time VaR in the Risk Management panel.',
    relatedTerms: ['Risk Management', 'Standard Deviation', 'Confidence Interval'],
  },
  {
    term: 'Sharpe Ratio',
    category: 'risk',
    shortDef: 'Risk-adjusted return measure',
    fullExplanation: 'Sharpe Ratio measures return per unit of risk (volatility). A ratio of 1 means 1% excess return for each 1% of volatility. Higher is better. Above 1 is good, above 2 is excellent.',
    whyUseful: 'Sharpe Ratio allows comparing strategies with different return/risk profiles. A 10% return with 5% volatility beats 15% with 20% volatility.',
    whyNotUseful: 'Sharpe assumes returns are normally distributed—doesn\'t capture tail risks. Also penalizes upside volatility equally with downside.',
    formula: 'Sharpe = (Strategy Return - Risk-Free Rate) / Strategy Volatility',
    example: 'Strategy: 15% return, 10% volatility. Risk-free: 5%. Sharpe = (15-5)/10 = 1.0',
    xfactorUsage: 'XFactor displays Sharpe Ratio in bot performance metrics and uses it in risk scoring.',
    relatedTerms: ['Sortino Ratio', 'Risk-Adjusted Return', 'Volatility'],
  },
  {
    term: 'Sortino Ratio',
    category: 'risk',
    shortDef: 'Like Sharpe but only penalizes downside volatility',
    fullExplanation: 'Sortino Ratio is similar to Sharpe but uses downside deviation instead of total volatility. This is more meaningful because upside volatility is desirable.',
    whyUseful: 'Sortino better captures what investors care about—avoiding losses while welcoming gains. More accurate for asymmetric return distributions.',
    formula: 'Sortino = (Strategy Return - Risk-Free Rate) / Downside Deviation',
    example: 'A strategy that\'s up 20% half the time and flat half the time has high Sharpe volatility but zero downside, so excellent Sortino.',
    xfactorUsage: 'XFactor calculates Sortino Ratio in bot risk metrics for more nuanced risk assessment.',
    relatedTerms: ['Sharpe Ratio', 'Downside Risk', 'Risk-Adjusted Return'],
  },

  // ===== FUNDAMENTALS =====
  {
    term: 'P/E Ratio (Price-to-Earnings)',
    category: 'fundamentals',
    shortDef: 'Stock price divided by earnings per share',
    fullExplanation: 'P/E Ratio measures how much investors pay for each dollar of earnings. A P/E of 20 means investors pay $20 for $1 of annual earnings. It\'s the most common valuation metric.',
    whyUseful: 'P/E allows comparing valuations across companies. Low P/E may indicate undervaluation or problems; high P/E suggests growth expectations.',
    whyNotUseful: 'P/E doesn\'t work for unprofitable companies. It can be manipulated by accounting. Doesn\'t account for growth or quality of earnings.',
    formula: 'P/E = Share Price / Earnings Per Share (EPS)',
    example: 'Stock at $100, EPS of $5. P/E = 20. If competitor has P/E of 15 with similar growth, this stock might be overvalued.',
    xfactorUsage: 'XFactor displays P/E ratio in the Stock Analyzer and tracks P/E history over time.',
    relatedTerms: ['EPS', 'PEG Ratio', 'Valuation', 'Earnings'],
  },
  {
    term: 'EPS (Earnings Per Share)',
    category: 'fundamentals',
    shortDef: 'Net income divided by shares outstanding',
    fullExplanation: 'EPS represents the portion of a company\'s profit allocated to each outstanding share. It\'s the foundation of P/E ratio and a key metric for company profitability.',
    whyUseful: 'EPS growth drives stock prices over the long term. Comparing actual EPS to estimates (earnings surprise) often causes significant price moves.',
    formula: 'EPS = (Net Income - Preferred Dividends) / Weighted Average Shares Outstanding',
    example: 'Company earns $1B with 100M shares. EPS = $10. If analysts expected $9 (11% beat), stock might jump 5-10%.',
    xfactorUsage: 'XFactor displays EPS history and estimates in Stock Analyzer. Tracks earnings surprises (beats/misses).',
    relatedTerms: ['P/E Ratio', 'Earnings', 'Net Income'],
  },
  {
    term: 'PEG Ratio',
    category: 'fundamentals',
    shortDef: 'P/E ratio adjusted for growth',
    fullExplanation: 'PEG divides P/E by expected earnings growth rate. A PEG of 1 is "fairly valued." Below 1 may be undervalued relative to growth; above 1 may be overvalued.',
    whyUseful: 'PEG accounts for growth—a high P/E might be justified by high growth. Allows apples-to-apples comparison of growth stocks.',
    whyNotUseful: 'Relies on growth estimates which are often wrong. Doesn\'t work for declining earnings or very low growth.',
    formula: 'PEG = P/E Ratio / Annual EPS Growth Rate',
    example: 'Stock has P/E of 30, expected to grow EPS 30% annually. PEG = 1. A P/E 30 stock growing 15% has PEG of 2 (overvalued).',
    xfactorUsage: 'XFactor displays PEG ratio in Stock Analyzer fundamental metrics.',
    relatedTerms: ['P/E Ratio', 'EPS', 'Growth Investing'],
  },
  {
    term: 'Market Cap',
    category: 'fundamentals',
    shortDef: 'Total market value of all shares',
    fullExplanation: 'Market capitalization is the total value of a company\'s outstanding shares. It determines company size classification: micro (<$300M), small ($300M-$2B), mid ($2B-$10B), large ($10B-$200B), mega (>$200B).',
    whyUseful: 'Market cap indicates company size, risk profile, and liquidity. Larger caps are typically less volatile but slower growing.',
    formula: 'Market Cap = Current Share Price × Total Shares Outstanding',
    example: 'Apple at $180 with 15.5B shares = $2.79T market cap (mega cap). A $10 stock with 50M shares = $500M (small cap).',
    xfactorUsage: 'XFactor displays market cap and tracks market cap history in Stock Analyzer.',
    relatedTerms: ['Share Price', 'Valuation', 'Large Cap', 'Small Cap'],
  },
  {
    term: 'Dividend Yield',
    category: 'fundamentals',
    shortDef: 'Annual dividend as percentage of stock price',
    fullExplanation: 'Dividend yield shows the cash return from dividends relative to stock price. A $100 stock paying $3 annual dividend has 3% yield. Higher yield provides income; lower yield suggests growth focus.',
    whyUseful: 'Dividend yield provides consistent income. Dividends have historically contributed ~40% of total stock returns. High yield can cushion drawdowns.',
    whyNotUseful: 'Very high yields may signal dividend cuts ahead. Focus on yield alone misses growth opportunities.',
    formula: 'Dividend Yield = Annual Dividend Per Share / Stock Price × 100%',
    example: 'AT&T at $20 pays $1.11 annual dividend. Yield = 5.55%. Apple at $180 pays $0.96. Yield = 0.53%.',
    xfactorUsage: 'XFactor displays dividend yield in Stock Analyzer and tracks historical dividend trends.',
    relatedTerms: ['Dividends', 'Income Investing', 'Payout Ratio'],
  },
  {
    term: 'Beta',
    category: 'fundamentals',
    shortDef: 'Stock\'s volatility relative to the market',
    fullExplanation: 'Beta measures how much a stock moves relative to the broader market. Beta of 1 = moves with market. Beta > 1 = more volatile. Beta < 1 = less volatile. Negative beta = moves opposite.',
    whyUseful: 'Beta helps estimate how your portfolio will react to market moves. High beta for aggressive; low beta for defensive.',
    whyNotUseful: 'Beta is based on historical data and can change. Doesn\'t capture company-specific risks.',
    formula: 'Beta = Covariance(Stock, Market) / Variance(Market)',
    example: 'NVDA beta of 1.8 means if market rises 1%, NVDA typically rises 1.8%. If market drops 1%, NVDA typically drops 1.8%.',
    xfactorUsage: 'XFactor displays beta in Stock Analyzer fundamental metrics.',
    relatedTerms: ['Volatility', 'Correlation', 'Risk', 'Alpha'],
  },
  {
    term: 'Profit Margin',
    category: 'fundamentals',
    shortDef: 'Percentage of revenue that becomes profit',
    fullExplanation: 'Profit margin shows how much of each revenue dollar is profit. Net profit margin uses bottom-line income; gross margin uses revenue minus cost of goods. Higher margins indicate pricing power and efficiency.',
    whyUseful: 'High margins indicate competitive advantages (moat). Improving margins suggest operational improvements. Compare within industries.',
    formula: 'Net Profit Margin = Net Income / Revenue × 100%',
    example: 'Apple revenue $100B, net income $25B. Net margin = 25%. Grocery stores might have 2% margin. Software companies often 20%+.',
    xfactorUsage: 'XFactor displays profit margin in Stock Analyzer and tracks margin trends over time.',
    relatedTerms: ['Revenue', 'Net Income', 'Gross Margin'],
  },

  // ===== CHART PATTERNS =====
  {
    term: 'Support',
    category: 'patterns',
    shortDef: 'Price level where buying prevents further decline',
    fullExplanation: 'Support is a price level where buying interest is strong enough to prevent price from falling further. It often forms at previous lows, round numbers, or moving averages. Support becomes resistance when broken.',
    whyUseful: 'Support levels offer low-risk entry points with clear invalidation. Buying near support with stop just below creates favorable risk/reward.',
    example: 'Stock bounces off $100 three times over several months. $100 is strong support. Buying at $102 with stop at $98 risks $4 to potentially gain $10+.',
    xfactorUsage: 'XFactor identifies support levels in Stock Analyzer and uses them in breakout strategies.',
    relatedTerms: ['Resistance', 'Breakout', 'Technical Analysis'],
    visualType: 'chart',
  },
  {
    term: 'Resistance',
    category: 'patterns',
    shortDef: 'Price level where selling prevents further rise',
    fullExplanation: 'Resistance is a price level where selling pressure is strong enough to halt advances. It often forms at previous highs, round numbers, or moving averages. When broken convincingly, resistance becomes support.',
    whyUseful: 'Resistance levels offer targets for exits and potential short entry points. Breakouts above resistance often lead to momentum runs.',
    example: 'Stock fails at $150 multiple times. $150 is strong resistance. Breaking above on volume signals potential run to $160-$170.',
    xfactorUsage: 'XFactor identifies resistance levels in Stock Analyzer for target setting.',
    relatedTerms: ['Support', 'Breakout', 'Technical Analysis'],
    visualType: 'chart',
  },
  {
    term: 'Divergence',
    category: 'patterns',
    shortDef: 'When price and indicator move in opposite directions',
    fullExplanation: 'Divergence occurs when price makes a new high/low but an indicator (RSI, MACD) doesn\'t confirm. Bullish divergence: lower price low, higher indicator low. Bearish divergence: higher price high, lower indicator high.',
    whyUseful: 'Divergences often precede reversals—they show weakening momentum before price turns. A powerful early warning signal.',
    whyNotUseful: 'Divergences can persist through multiple new highs/lows before resolving. Not reliable timing signals alone.',
    example: 'Stock makes new high at $120 (previous high $110), but RSI at 65 (previous 75). Bearish divergence suggests weakening—potential top.',
    xfactorUsage: 'XFactor uses momentum_rsi_divergence strategy to detect and trade divergence patterns.',
    relatedTerms: ['RSI', 'MACD', 'Momentum', 'Reversal'],
    visualType: 'chart',
  },
  {
    term: 'Overbought',
    category: 'patterns',
    shortDef: 'When price has risen too fast and may pull back',
    fullExplanation: 'Overbought conditions suggest a security has risen too quickly and may be due for a pullback. Common thresholds: RSI > 70, Stochastic > 80. However, in strong uptrends, overbought can remain for extended periods.',
    whyUseful: 'Overbought warnings help avoid buying at tops. Can signal exit points for long positions or short entry for mean reversion.',
    whyNotUseful: 'In strong trends, RSI can stay above 70 for months. Selling purely on overbought readings can miss massive gains.',
    example: 'RSI hits 85 after 30% rally. Consider taking partial profits or tightening stops rather than outright selling.',
    xfactorUsage: 'XFactor displays overbought conditions in technical overlays and uses them in mean reversion strategies.',
    relatedTerms: ['RSI', 'Oversold', 'Mean Reversion'],
  },
  {
    term: 'Oversold',
    category: 'patterns',
    shortDef: 'When price has fallen too fast and may bounce',
    fullExplanation: 'Oversold conditions suggest a security has declined too quickly and may be due for a bounce. Common thresholds: RSI < 30, Stochastic < 20. In strong downtrends, oversold can persist.',
    whyUseful: 'Oversold readings can identify bounce opportunities in quality stocks. Good for mean reversion entries with defined risk.',
    whyNotUseful: 'In bear markets, stocks can stay oversold for months. "Catching a falling knife" is a real risk.',
    example: 'Quality stock drops 20% on market panic, RSI at 25. Might be buying opportunity—but use stops in case decline continues.',
    xfactorUsage: 'XFactor uses oversold conditions in reversion_rsi_bb strategy for bounce trades.',
    relatedTerms: ['RSI', 'Overbought', 'Mean Reversion', 'Support'],
  },
];

// Glossary categories for filtering
const glossaryCategories = [
  { id: 'all', label: 'All Terms', icon: Book },
  { id: 'basics', label: 'Basics', icon: Activity },
  { id: 'indicators', label: 'Indicators', icon: BarChart3 },
  { id: 'strategies', label: 'Strategies', icon: Target },
  { id: 'risk', label: 'Risk Mgmt', icon: Shield },
  { id: 'fundamentals', label: 'Fundamentals', icon: TrendingUp },
  { id: 'patterns', label: 'Patterns', icon: Layers },
];

interface GlossaryTermCardProps {
  term: GlossaryTerm;
  isExpanded: boolean;
  onToggle: () => void;
}

function GlossaryTermCard({ term, isExpanded, onToggle }: GlossaryTermCardProps) {
  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      basics: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      indicators: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      strategies: 'bg-green-500/20 text-green-400 border-green-500/30',
      risk: 'bg-red-500/20 text-red-400 border-red-500/30',
      fundamentals: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      patterns: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    };
    return colors[category] || colors.basics;
  };

  return (
    <div className="bg-slate-800/50 rounded-lg border border-slate-700/50 overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-700/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className={`px-2 py-0.5 text-xs rounded border ${getCategoryColor(term.category)}`}>
            {term.category.charAt(0).toUpperCase() + term.category.slice(1)}
          </span>
          <span className="font-semibold text-white">{term.term}</span>
          <span className="text-sm text-slate-400 hidden md:inline">— {term.shortDef}</span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        )}
      </button>
      
      {isExpanded && (
        <div className="px-4 pb-4 space-y-4 border-t border-slate-700/50 pt-4">
          {/* Full Explanation */}
          <div>
            <h4 className="text-xs font-medium text-slate-500 uppercase mb-2">What is it?</h4>
            <p className="text-sm text-slate-300">{term.fullExplanation}</p>
          </div>
          
          {/* Formula */}
          {term.formula && (
            <div className="p-3 bg-slate-900/50 rounded-lg border border-slate-700/50">
              <h4 className="text-xs font-medium text-violet-400 uppercase mb-2">Formula</h4>
              <code className="text-sm text-green-400 font-mono">{term.formula}</code>
            </div>
          )}
          
          {/* Why Useful */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-3 bg-green-500/5 rounded-lg border border-green-500/20">
              <h4 className="text-xs font-medium text-green-400 uppercase mb-2 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" /> Why It's Useful
              </h4>
              <p className="text-sm text-slate-300">{term.whyUseful}</p>
            </div>
            
            {term.whyNotUseful && (
              <div className="p-3 bg-red-500/5 rounded-lg border border-red-500/20">
                <h4 className="text-xs font-medium text-red-400 uppercase mb-2 flex items-center gap-1">
                  <TrendingDown className="w-3 h-3" /> Limitations
                </h4>
                <p className="text-sm text-slate-300">{term.whyNotUseful}</p>
              </div>
            )}
          </div>
          
          {/* Example */}
          {term.example && (
            <div className="p-3 bg-blue-500/5 rounded-lg border border-blue-500/20">
              <h4 className="text-xs font-medium text-blue-400 uppercase mb-2">Example</h4>
              <p className="text-sm text-slate-300">{term.example}</p>
            </div>
          )}
          
          {/* XFactor Usage */}
          {term.xfactorUsage && (
            <div className="p-3 bg-violet-500/5 rounded-lg border border-violet-500/20">
              <h4 className="text-xs font-medium text-violet-400 uppercase mb-2 flex items-center gap-1">
                <Zap className="w-3 h-3" /> Used in XFactor
              </h4>
              <p className="text-sm text-slate-300">{term.xfactorUsage}</p>
            </div>
          )}
          
          {/* Related Terms */}
          {term.relatedTerms && term.relatedTerms.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-slate-500 uppercase mb-2">Related Terms</h4>
              <div className="flex flex-wrap gap-2">
                {term.relatedTerms.map((related, i) => (
                  <span key={i} className="px-2 py-1 text-xs bg-slate-700/50 text-slate-400 rounded">
                    {related}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* Visual Indicator */}
          {term.visualType && (
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <LineChart className="w-3 h-3" />
              <span>Best understood with {term.visualType} visualization</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function HelpModal({ isOpen, onClose }: HelpModalProps) {
  const [activeTab, setActiveTab] = useState<'features' | 'quickstart' | 'glossary' | 'changelog'>('features');
  const [glossaryCategory, setGlossaryCategory] = useState<string>('all');
  const [glossarySearch, setGlossarySearch] = useState('');
  const [expandedTerms, setExpandedTerms] = useState<Set<string>>(new Set());

  if (!isOpen) return null;

  const toggleTerm = (term: string) => {
    const newExpanded = new Set(expandedTerms);
    if (newExpanded.has(term)) {
      newExpanded.delete(term);
    } else {
      newExpanded.add(term);
    }
    setExpandedTerms(newExpanded);
  };

  const filteredGlossaryTerms = glossaryTerms.filter(term => {
    const matchesCategory = glossaryCategory === 'all' || term.category === glossaryCategory;
    const matchesSearch = glossarySearch === '' || 
      term.term.toLowerCase().includes(glossarySearch.toLowerCase()) ||
      term.shortDef.toLowerCase().includes(glossarySearch.toLowerCase()) ||
      term.fullExplanation.toLowerCase().includes(glossarySearch.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-slate-900 rounded-xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden border border-slate-700">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700 bg-gradient-to-r from-blue-600/20 to-purple-600/20">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <HelpCircle className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">XFactor Bot Help</h2>
              <p className="text-sm text-slate-400">Version {VERSION} • {RELEASE_DATE}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-700">
          {[
            { id: 'features', label: 'Features', icon: Zap },
            { id: 'quickstart', label: 'Quick Start', icon: Activity },
            { id: 'glossary', label: 'Glossary', icon: Book },
            { id: 'changelog', label: 'Changelog', icon: Calendar }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
                activeTab === tab.id
                  ? 'text-blue-400 border-b-2 border-blue-400 bg-blue-500/10'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[65vh]">
          {activeTab === 'features' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="p-4 bg-slate-800/50 rounded-lg border border-slate-700 hover:border-blue-500/50 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-blue-500/20 rounded-lg shrink-0">
                      <feature.icon className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white mb-1">{feature.title}</h3>
                      <p className="text-sm text-slate-400">{feature.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'quickstart' && (
            <div className="space-y-4">
              <p className="text-slate-300 mb-6">
                Get started with XFactor Bot in 5 simple steps:
              </p>
              {quickStart.map((item) => (
                <div
                  key={item.step}
                  className="flex items-start gap-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700"
                >
                  <div className="w-8 h-8 flex items-center justify-center bg-blue-500 rounded-full text-white font-bold shrink-0">
                    {item.step}
                  </div>
                  <div>
                    <h3 className="font-semibold text-white mb-1">{item.title}</h3>
                    <p className="text-sm text-slate-400">{item.description}</p>
                  </div>
                </div>
              ))}

              <div className="mt-6 p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg">
                <h4 className="font-semibold text-amber-400 mb-2">⚠️ Important Notes</h4>
                <ul className="text-sm text-slate-300 space-y-1">
                  <li>• Always start with Paper trading mode to test strategies</li>
                  <li>• Set appropriate risk limits before enabling Live trading</li>
                  <li>• Monitor bot performance regularly using the Performance Charts</li>
                  <li>• Use Auto-Tune to optimize bot parameters automatically</li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === 'glossary' && (
            <div className="space-y-4">
              {/* Header */}
              <div className="flex flex-col md:flex-row gap-4 mb-6">
                <p className="text-slate-300 flex-1">
                  <span className="text-2xl mr-2">📚</span>
                  <strong>{glossaryTerms.length} terms</strong> covering trading basics, technical indicators, strategies, risk management, and chart patterns used in XFactor.
                </p>
              </div>
              
              {/* Search and Filter */}
              <div className="flex flex-col md:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    placeholder="Search terms..."
                    value={glossarySearch}
                    onChange={(e) => setGlossarySearch(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  {glossaryCategories.map((cat) => (
                    <button
                      key={cat.id}
                      onClick={() => setGlossaryCategory(cat.id)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
                        glossaryCategory === cat.id
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700'
                      }`}
                    >
                      <cat.icon className="w-3 h-3" />
                      {cat.label}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Results count */}
              <div className="text-sm text-slate-500">
                Showing {filteredGlossaryTerms.length} of {glossaryTerms.length} terms
              </div>
              
              {/* Terms List */}
              <div className="space-y-2">
                {filteredGlossaryTerms.map((term) => (
                  <GlossaryTermCard
                    key={term.term}
                    term={term}
                    isExpanded={expandedTerms.has(term.term)}
                    onToggle={() => toggleTerm(term.term)}
                  />
                ))}
              </div>
              
              {filteredGlossaryTerms.length === 0 && (
                <div className="text-center py-12 text-slate-500">
                  <Book className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No terms found matching your search.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'changelog' && (
            <div className="space-y-6">
              {changelog.map((release) => (
                <div key={release.version} className="border-l-2 border-blue-500 pl-4">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-sm font-mono rounded">
                      v{release.version}
                    </span>
                    <span className="text-sm text-slate-400">{release.date}</span>
                  </div>
                  <ul className="space-y-1">
                    {release.changes.map((change, i) => (
                      <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                        <span className="text-green-400 mt-1">•</span>
                        {change}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-700 bg-slate-800/50">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-400">
              © 2025 XFactor Trading • AI-Powered Automated Trading System
            </p>
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded">
                {VERSION}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
