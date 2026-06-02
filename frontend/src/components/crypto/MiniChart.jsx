import { useMemo } from 'react';

/**
 * MiniChart - simple sparkline chart for crypto price history
 * @param {{
 *   data: Array<[timestamp, price]>,
 *   positive?: boolean,
 *   height?: number
 * }} props
 */
export default function MiniChart({ data, positive, height = 40 }) {
  const pathData = useMemo(() => {
    if (!data || data.length < 2) return '';
    
    const prices = data.map((d) => d[1]);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const range = max - min || 1;
    
    // Generate simple SVG path
    const width = 100;
    const stepX = width / (prices.length - 1);
    
    const points = prices.map((price, i) => {
      const x = i * stepX;
      const y = height - ((price - min) / range) * height;
      return `${x},${y}`;
    });
    
    return `M ${points.join(' L ')}`;
  }, [data, height]);

  const color = positive ? '#22c55e' : '#ef4444';

  if (!data || data.length < 2) {
    return (
      <div 
        className="w-full bg-[var(--bg-elevated)] rounded animate-pulse" 
        style={{ height }} 
      />
    );
  }

  return (
    <svg 
      className="w-full" 
      viewBox={`0 0 100 ${height}`} 
      preserveAspectRatio="none"
    >
      <path
        d={pathData}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}