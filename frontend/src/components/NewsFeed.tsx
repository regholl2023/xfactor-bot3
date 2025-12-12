import { useState, useEffect } from 'react'
import { 
  RefreshCw, ChevronLeft, ChevronRight, TrendingUp, TrendingDown, 
  Minus, ExternalLink, Clock, Filter, Globe
} from 'lucide-react'

interface NewsItem {
  id: string
  time: string
  timestamp: Date
  ticker: string
  sentiment: number
  headline: string
  source: string
  url?: string
  category: string
  region: string
}

interface NewsFeedProps {
  maxItems?: number
  itemsPerPage?: number
}

// Generate more comprehensive mock news
const generateMockNews = (count: number): NewsItem[] => {
  const tickers = ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'META', 'TSLA', 'AMZN', 'AMD', 'SPY', 'QQQ', 
                   'BABA', 'TSM', 'ASML', 'SAP', 'NVO', 'COIN', 'MSTR', 'PLTR', 'ARM', 'SMCI']
  const sources = ['Reuters', 'Bloomberg', 'WSJ', 'CNBC', 'Financial Times', 'Barrons', 
                   'MarketWatch', 'Yahoo Finance', 'Benzinga', 'Seeking Alpha', 'CNN Business',
                   'Fox Business', 'Caixin', 'Nikkei', 'Handelsblatt', 'The Economist']
  const categories = ['Earnings', 'M&A', 'FDA', 'Fed', 'Macro', 'Tech', 'Crypto', 'Options Flow', 'Insider', 'Analyst']
  const regions = ['US', 'EU', 'Asia', 'Global']
  
  const headlines = [
    { text: '{ticker} beats Q4 earnings expectations by 15%', sentiment: 0.75 },
    { text: '{ticker} announces $10B share buyback program', sentiment: 0.68 },
    { text: 'Breaking: {ticker} in talks for major acquisition', sentiment: 0.55 },
    { text: '{ticker} receives FDA approval for new drug', sentiment: 0.82 },
    { text: 'Analyst upgrades {ticker} to Strong Buy, raises PT to $500', sentiment: 0.71 },
    { text: '{ticker} CEO sells $50M in stock (scheduled sale)', sentiment: -0.15 },
    { text: '{ticker} faces regulatory scrutiny in EU', sentiment: -0.45 },
    { text: '{ticker} warns of supply chain disruptions', sentiment: -0.52 },
    { text: '{ticker} lowers full-year guidance', sentiment: -0.68 },
    { text: 'Unusual options activity detected in {ticker}', sentiment: 0.35 },
    { text: '{ticker} partners with tech giant on AI initiative', sentiment: 0.62 },
    { text: 'Hedge funds increase positions in {ticker}', sentiment: 0.48 },
    { text: '{ticker} launches new product line ahead of schedule', sentiment: 0.58 },
    { text: 'Short interest in {ticker} drops 20%', sentiment: 0.42 },
    { text: '{ticker} expands into emerging markets', sentiment: 0.38 },
    { text: 'Fed comments boost outlook for {ticker} sector', sentiment: 0.45 },
    { text: '{ticker} reports record revenue growth', sentiment: 0.78 },
    { text: 'Insider buying detected at {ticker}', sentiment: 0.55 },
    { text: '{ticker} stock split announced', sentiment: 0.32 },
    { text: 'Major investor takes stake in {ticker}', sentiment: 0.65 },
  ]

  const news: NewsItem[] = []
  const now = new Date()

  for (let i = 0; i < count; i++) {
    const ticker = tickers[Math.floor(Math.random() * tickers.length)]
    const template = headlines[Math.floor(Math.random() * headlines.length)]
    const minutesAgo = i * 3 + Math.floor(Math.random() * 5)
    const timestamp = new Date(now.getTime() - minutesAgo * 60000)
    
    // Add some randomness to sentiment
    const sentimentVariance = (Math.random() - 0.5) * 0.2
    const sentiment = Math.max(-1, Math.min(1, template.sentiment + sentimentVariance))

    news.push({
      id: `news-${i}`,
      time: timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      timestamp,
      ticker,
      sentiment,
      headline: template.text.replace('{ticker}', ticker),
      source: sources[Math.floor(Math.random() * sources.length)],
      category: categories[Math.floor(Math.random() * categories.length)],
      region: regions[Math.floor(Math.random() * regions.length)],
    })
  }

  return news.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
}

export function NewsFeed({ maxItems = 100, itemsPerPage = 10 }: NewsFeedProps) {
  const [allNews, setAllNews] = useState<NewsItem[]>([])
  const [currentPage, setCurrentPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [filter, setFilter] = useState<'all' | 'bullish' | 'bearish'>('all')
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  useEffect(() => {
    loadNews()
  }, [])

  const loadNews = () => {
    setLoading(true)
    // Simulate API call
    setTimeout(() => {
      setAllNews(generateMockNews(maxItems))
      setLastUpdate(new Date())
      setLoading(false)
      setCurrentPage(1)
    }, 500)
  }

  // Filter news
  const filteredNews = allNews.filter(item => {
    if (filter === 'bullish') return item.sentiment > 0.2
    if (filter === 'bearish') return item.sentiment < -0.2
    return true
  })

  // Pagination
  const totalPages = Math.ceil(filteredNews.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const displayedNews = filteredNews.slice(startIndex, startIndex + itemsPerPage)

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.3) return 'text-profit'
    if (sentiment < -0.3) return 'text-loss'
    return 'text-yellow-500'
  }

  const getSentimentBg = (sentiment: number) => {
    if (sentiment > 0.3) return 'bg-profit/10'
    if (sentiment < -0.3) return 'bg-loss/10'
    return 'bg-yellow-500/10'
  }

  const getSentimentIcon = (sentiment: number) => {
    if (sentiment > 0.2) return <TrendingUp className="h-4 w-4 text-profit" />
    if (sentiment < -0.2) return <TrendingDown className="h-4 w-4 text-loss" />
    return <Minus className="h-4 w-4 text-yellow-500" />
  }

  return (
    <div className="space-y-4">
      {/* Header Controls */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          {/* Filter buttons */}
          <div className="flex rounded-lg overflow-hidden border border-border">
            <button
              onClick={() => { setFilter('all'); setCurrentPage(1) }}
              className={`px-3 py-1.5 text-xs transition-colors ${
                filter === 'all' ? 'bg-xfactor-teal text-white' : 'bg-secondary hover:bg-secondary/80'
              }`}
            >
              All ({allNews.length})
            </button>
            <button
              onClick={() => { setFilter('bullish'); setCurrentPage(1) }}
              className={`px-3 py-1.5 text-xs transition-colors border-l border-border ${
                filter === 'bullish' ? 'bg-profit text-white' : 'bg-secondary hover:bg-secondary/80'
              }`}
            >
              Bullish
            </button>
            <button
              onClick={() => { setFilter('bearish'); setCurrentPage(1) }}
              className={`px-3 py-1.5 text-xs transition-colors border-l border-border ${
                filter === 'bearish' ? 'bg-loss text-white' : 'bg-secondary hover:bg-secondary/80'
              }`}
            >
              Bearish
            </button>
          </div>
          
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Globe className="h-3 w-3" />
            <span>Global Sources</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Last update */}
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>Updated: {lastUpdate.toLocaleTimeString()}</span>
          </div>
          
          {/* Refresh button */}
          <button
            onClick={loadNews}
            disabled={loading}
            className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors"
            title="Refresh news"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* News List */}
      <div className="space-y-2">
        {displayedNews.map((news) => (
          <div
            key={news.id}
            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 border border-border/50 hover:border-xfactor-teal/50 transition-colors ${getSentimentBg(news.sentiment)}`}
          >
            {/* Time */}
            <span className="text-xs text-muted-foreground w-14 shrink-0">
              [{news.time}]
            </span>
            
            {/* Ticker */}
            <span className="font-bold text-foreground w-14 shrink-0">
              {news.ticker}
            </span>
            
            {/* Sentiment */}
            <div className={`flex items-center gap-1 w-16 shrink-0 ${getSentimentColor(news.sentiment)}`}>
              {getSentimentIcon(news.sentiment)}
              <span className="text-sm font-medium">
                {news.sentiment > 0 ? '+' : ''}{news.sentiment.toFixed(2)}
              </span>
            </div>
            
            {/* Category badge */}
            <span className="text-xs px-2 py-0.5 rounded bg-secondary text-muted-foreground shrink-0">
              {news.category}
            </span>
            
            {/* Headline */}
            <span className="flex-1 text-sm truncate" title={news.headline}>
              "{news.headline}"
            </span>
            
            {/* Source & Region */}
            <div className="flex items-center gap-2 shrink-0">
              <span className="text-xs text-muted-foreground">
                {news.source}
              </span>
              <span className="text-xs px-1.5 py-0.5 rounded bg-xfactor-teal/20 text-xfactor-teal">
                {news.region}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between pt-2 border-t border-border">
        <div className="text-sm text-muted-foreground">
          Showing {startIndex + 1}-{Math.min(startIndex + itemsPerPage, filteredNews.length)} of {filteredNews.length} items
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          
          <div className="flex items-center gap-1">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum: number
              if (totalPages <= 5) {
                pageNum = i + 1
              } else if (currentPage <= 3) {
                pageNum = i + 1
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i
              } else {
                pageNum = currentPage - 2 + i
              }
              
              return (
                <button
                  key={pageNum}
                  onClick={() => setCurrentPage(pageNum)}
                  className={`w-8 h-8 rounded-lg text-sm transition-colors ${
                    currentPage === pageNum
                      ? 'bg-xfactor-teal text-white'
                      : 'bg-secondary hover:bg-secondary/80'
                  }`}
                >
                  {pageNum}
                </button>
              )
            })}
            {totalPages > 5 && currentPage < totalPages - 2 && (
              <>
                <span className="text-muted-foreground">...</span>
                <button
                  onClick={() => setCurrentPage(totalPages)}
                  className="w-8 h-8 rounded-lg text-sm bg-secondary hover:bg-secondary/80 transition-colors"
                >
                  {totalPages}
                </button>
              </>
            )}
          </div>
          
          <button
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
