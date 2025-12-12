import { useEffect, useRef, useState, useMemo } from 'react'
import { createChart, ColorType, IChartApi, ISeriesApi, LineData, Time } from 'lightweight-charts'
import { LineChart } from 'lucide-react'

interface EquityChartProps {
  height?: number
}

type TimeRange = '1D' | '1W' | '1M' | '3M' | 'YTD' | 'ALL'

function filterDataByRange(data: LineData[], range: TimeRange): LineData[] {
  if (data.length === 0) return data
  
  const now = new Date()
  let cutoffDate: Date
  
  switch (range) {
    case '1D':
      cutoffDate = new Date(now)
      cutoffDate.setDate(cutoffDate.getDate() - 1)
      break
    case '1W':
      cutoffDate = new Date(now)
      cutoffDate.setDate(cutoffDate.getDate() - 7)
      break
    case '1M':
      cutoffDate = new Date(now)
      cutoffDate.setMonth(cutoffDate.getMonth() - 1)
      break
    case '3M':
      cutoffDate = new Date(now)
      cutoffDate.setMonth(cutoffDate.getMonth() - 3)
      break
    case 'YTD':
      cutoffDate = new Date(now.getFullYear(), 0, 1)
      break
    case 'ALL':
    default:
      return data
  }
  
  const cutoffStr = cutoffDate.toISOString().split('T')[0]
  return data.filter(d => (d.time as string) >= cutoffStr)
}

export function EquityChart({ height = 280 }: EquityChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Area'> | null>(null)
  const [fullData, setFullData] = useState<LineData[]>([])
  const [selectedRange, setSelectedRange] = useState<TimeRange>('3M')
  const [loading, setLoading] = useState(true)
  
  // Filter data based on selected range
  const filteredData = useMemo(() => {
    return filterDataByRange(fullData, selectedRange)
  }, [fullData, selectedRange])
  
  // Calculate stats for filtered data
  const currentValue = filteredData[filteredData.length - 1]?.value || 0
  const startValue = filteredData[0]?.value || 0
  const totalReturn = startValue > 0 ? ((currentValue - startValue) / startValue) * 100 : 0
  const isPositive = totalReturn >= 0
  
  // Check if we should show empty state
  const showEmptyState = !loading && fullData.length === 0
  
  // Fetch equity data from API
  useEffect(() => {
    const fetchEquityData = async () => {
      try {
        const res = await fetch('/api/positions/equity-history')
        if (res.ok) {
          const data = await res.json()
          if (data.history && data.history.length > 0) {
            setFullData(data.history.map((d: any) => ({
              time: d.date as Time,
              value: d.value,
            })))
          }
        }
      } catch (e) {
        console.error('Failed to fetch equity history:', e)
      }
      setLoading(false)
    }
    
    fetchEquityData()
  }, [])

  // Update chart when data or range changes
  useEffect(() => {
    // Don't create chart if no data or showing empty state
    if (showEmptyState || !chartContainerRef.current || filteredData.length === 0) {
      return
    }

    // Clean up existing chart safely
    if (chartRef.current) {
      try {
        chartRef.current.remove()
      } catch (e) {
        // Chart may already be disposed, ignore error
      }
      chartRef.current = null
      seriesRef.current = null
    }

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#9ca3af',
        fontFamily: "'JetBrains Mono', monospace",
      },
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
      },
      width: chartContainerRef.current.clientWidth,
      height: height,
      rightPriceScale: {
        borderColor: 'rgba(255, 255, 255, 0.1)',
        scaleMargins: {
          top: 0.1,
          bottom: 0.1,
        },
      },
      timeScale: {
        borderColor: 'rgba(255, 255, 255, 0.1)',
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        vertLine: {
          color: 'rgba(139, 92, 246, 0.3)',
          width: 1,
          style: 2,
        },
        horzLine: {
          color: 'rgba(139, 92, 246, 0.3)',
          width: 1,
          style: 2,
        },
      },
    })

    chartRef.current = chart

    // Create area series for equity curve
    const areaSeries = chart.addAreaSeries({
      lineColor: isPositive ? '#22c55e' : '#ef4444',
      topColor: isPositive ? 'rgba(34, 197, 94, 0.4)' : 'rgba(239, 68, 68, 0.4)',
      bottomColor: isPositive ? 'rgba(34, 197, 94, 0.0)' : 'rgba(239, 68, 68, 0.0)',
      lineWidth: 2,
      priceFormat: {
        type: 'custom',
        formatter: (price: number) => '$' + price.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }),
      },
    })

    seriesRef.current = areaSeries
    areaSeries.setData(filteredData)

    // Fit content
    chart.timeScale().fitContent()

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        try {
          chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth })
        } catch (e) {
          // Chart may be disposed during resize, ignore
        }
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      if (chartRef.current) {
        try {
          chartRef.current.remove()
        } catch (e) {
          // Chart may already be disposed, ignore error
        }
        chartRef.current = null
        seriesRef.current = null
      }
    }
  }, [filteredData, height, isPositive, showEmptyState])

  const handleRangeChange = (range: TimeRange) => {
    setSelectedRange(range)
  }

  // Get period label
  const getPeriodLabel = () => {
    switch (selectedRange) {
      case '1D': return 'Today'
      case '1W': return 'Past Week'
      case '1M': return 'Past Month'
      case '3M': return 'Past 3 Months'
      case 'YTD': return 'Year to Date'
      case 'ALL': return 'All Time'
    }
  }

  // Show empty state
  if (showEmptyState) {
    return (
      <div 
        className="flex flex-col items-center justify-center text-muted-foreground rounded-lg border border-dashed border-border bg-secondary/20"
        style={{ height }}
      >
        <LineChart className="h-12 w-12 mb-3 opacity-30" />
        <div className="text-sm font-medium">No Equity Data</div>
        <div className="text-xs mt-1">Connect a broker to see your portfolio performance</div>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* Stats row */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-4">
          <div>
            <span className="text-muted-foreground">Current: </span>
            <span className="font-semibold text-foreground">
              ${currentValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </span>
          </div>
          <div>
            <span className="text-muted-foreground">{getPeriodLabel()} Start: </span>
            <span className="text-foreground">
              ${startValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </span>
          </div>
        </div>
        <div className={`font-semibold ${isPositive ? 'text-profit' : 'text-loss'}`}>
          {isPositive ? '+' : ''}{totalReturn.toFixed(2)}% {getPeriodLabel()}
        </div>
      </div>
      
      {/* Chart */}
      <div ref={chartContainerRef} className="rounded-lg overflow-hidden" />
      
      {/* Time range buttons */}
      <div className="flex items-center gap-2">
        {(['1D', '1W', '1M', '3M', 'YTD', 'ALL'] as TimeRange[]).map((range) => (
          <button
            key={range}
            onClick={() => handleRangeChange(range)}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              range === selectedRange
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary/50 text-muted-foreground hover:bg-secondary hover:text-foreground'
            }`}
          >
            {range}
          </button>
        ))}
      </div>
    </div>
  )
}
