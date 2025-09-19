import React from 'react';

interface Portfolio {
  totalValue: number;
  dailyChange: number;
  dailyChangePercent: number;
  topHoldings: Array<{
    ticker: string;
    value: number;
    change: number;
    changePercent: number;
    sparklineData: number[];
  }>;
  lastUpdated: string;
}

interface PortfolioHeaderProps {
  portfolio: Portfolio;
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(value);
};

const formatPercent = (value: number): string => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
};

const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    timeZoneName: 'short'
  });
};

const MiniSparkline: React.FC<{ data: number[]; isPositive: boolean }> = ({ data, isPositive }) => {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min;
  
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * 60;
    const y = 20 - ((value - min) / range) * 20;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width="60" height="24" className="inline-block">
      <polyline
        points={points}
        fill="none"
        stroke={isPositive ? "#34A853" : "#EA4335"}
        strokeWidth="1.5"
        className="transition-all duration-200"
      />
    </svg>
  );
};

export const PortfolioHeader: React.FC<PortfolioHeaderProps> = ({ portfolio }) => {
  const isPositiveChange = portfolio.dailyChange >= 0;

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      {/* Header with timestamp */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-semibold text-gray-900 mb-2">
            Portfolio Overview
          </h1>
          <p className="text-sm text-gray-500">
            Last updated: {formatTimestamp(portfolio.lastUpdated)}
          </p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-mono font-bold text-gray-900">
            {formatCurrency(portfolio.totalValue)}
          </div>
          <div className={`text-lg font-mono font-medium ${
            isPositiveChange ? 'text-green-600' : 'text-red-600'
          }`}>
            {formatCurrency(portfolio.dailyChange)} ({formatPercent(portfolio.dailyChangePercent)})
          </div>
        </div>
      </div>

      {/* Top Holdings */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Top Holdings</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {portfolio.topHoldings.map((holding) => {
            const isHoldingPositive = holding.change >= 0;
            
            return (
              <div key={holding.ticker} className="bg-gray-50 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <span className="font-medium text-gray-900 text-lg">
                    {holding.ticker}
                  </span>
                  <MiniSparkline 
                    data={holding.sparklineData} 
                    isPositive={isHoldingPositive}
                  />
                </div>
                <div className="space-y-1">
                  <div className="font-mono font-semibold text-gray-900">
                    {formatCurrency(holding.value)}
                  </div>
                  <div className={`font-mono text-sm ${
                    isHoldingPositive ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatCurrency(holding.change)} ({formatPercent(holding.changePercent)})
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};