import { useEffect, useRef, useState, useMemo } from 'react'
import { createChart, ColorType, IChartApi, ISeriesApi, LineData, Time } from 'lightweight-charts'

interface EquityChartProps {
  height?: number
}

type TimeRange = '1D' | '1W' | '1M' | '3M' | 'YTD' | 'ALL'

// Generate sample equity curve data for the full year
function generateFullEquityData(): LineData[] {
  const data: LineData[] = []
  const now = new Date()
  const startOfYear = new Date(now.getFullYear(), 0, 1)
  const startDate = new Date(startOfYear)
  startDate.setDate(startDate.getDate() - 30) // Start 30 days before year start
  
  const totalDays = Math.ceil((now.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))
  
  let equity = 100000 // Starting equity
  
  for (let i = 0; i <= totalDays; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)
    
    // Simulate daily returns with slight upward bias
    const volatility = 0.015 + Math.random() * 0.01 // 1.5-2.5% daily volatility
    const trend = 0.0003 // Slight upward bias
    const dailyReturn = (Math.random() - 0.48) * volatility + trend
    equity = equity * (1 + dailyReturn)
    
    const dateStr = date.toISOString().split('T')[0]
    data.push({
      time: dateStr as Time,
      value: Math.round(equity * 100) / 100,
    })
  }
  
  return data
}

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
  const [fullData] = useState(() => generateFullEquityData())
  const [selectedRange, setSelectedRange] = useState<TimeRange>('3M')
  
  // Filter data based on selected range
  const filteredData = useMemo(() => {
    return filterDataByRange(fullData, selectedRange)
  }, [fullData, selectedRange])
  
  // Calculate stats for filtered data
  const currentValue = filteredData[filteredData.length - 1]?.value || 0
  const startValue = filteredData[0]?.value || 100000
  const totalReturn = ((currentValue - startValue) / startValue) * 100
  const isPositive = totalReturn >= 0

  // Update chart when data or range changes
  useEffect(() => {
    if (!chartContainerRef.current) return

    // Remove existing chart
    if (chartRef.current) {
      chartRef.current.remove()
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
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [filteredData, height, isPositive])

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
