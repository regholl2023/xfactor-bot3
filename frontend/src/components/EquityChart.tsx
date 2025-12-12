import { useEffect, useRef, useState } from 'react'
import { createChart, ColorType, IChartApi, ISeriesApi, LineData, Time } from 'lightweight-charts'

interface EquityChartProps {
  height?: number
}

// Generate sample equity curve data
function generateEquityData(): LineData[] {
  const data: LineData[] = []
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 90) // 90 days of data
  
  let equity = 100000 // Starting equity
  
  for (let i = 0; i < 90; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)
    
    // Simulate daily returns with slight upward bias
    const dailyReturn = (Math.random() - 0.45) * 0.02 // -0.9% to +1.1% daily
    equity = equity * (1 + dailyReturn)
    
    const dateStr = date.toISOString().split('T')[0]
    data.push({
      time: dateStr as Time,
      value: Math.round(equity * 100) / 100,
    })
  }
  
  return data
}

export function EquityChart({ height = 280 }: EquityChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Area'> | null>(null)
  const [equityData] = useState(() => generateEquityData())
  
  // Calculate stats
  const currentValue = equityData[equityData.length - 1]?.value || 0
  const startValue = equityData[0]?.value || 100000
  const totalReturn = ((currentValue - startValue) / startValue) * 100
  const isPositive = totalReturn >= 0

  useEffect(() => {
    if (!chartContainerRef.current) return

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
    areaSeries.setData(equityData)

    // Fit content
    chart.timeScale().fitContent()

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [equityData, height, isPositive])

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
            <span className="text-muted-foreground">Starting: </span>
            <span className="text-foreground">
              ${startValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </span>
          </div>
        </div>
        <div className={`font-semibold ${isPositive ? 'text-profit' : 'text-loss'}`}>
          {isPositive ? '+' : ''}{totalReturn.toFixed(2)}% Total Return
        </div>
      </div>
      
      {/* Chart */}
      <div ref={chartContainerRef} className="rounded-lg overflow-hidden" />
      
      {/* Time range buttons */}
      <div className="flex items-center gap-2">
        {['1D', '1W', '1M', '3M', 'YTD', 'ALL'].map((range) => (
          <button
            key={range}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              range === '3M'
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

