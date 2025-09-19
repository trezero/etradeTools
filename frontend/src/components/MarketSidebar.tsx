import React from 'react';

interface MarketIndex {
  name: string;
  symbol: string;
  value: number;
  change: number;
  changePercent: number;
}

// Mock market data
const mockMarketData: MarketIndex[] = [
  { name: "S&P 500", symbol: "SPX", value: 4485.50, change: 23.75, changePercent: 0.53 },
  { name: "NASDAQ", symbol: "IXIC", value: 13945.20, change: -45.30, changePercent: -0.32 },
  { name: "Dow Jones", symbol: "DJI", value: 34756.80, change: 156.20, changePercent: 0.45 }
];

const mockVIX = {
  value: 18.45,
  change: -1.20,
  changePercent: -6.11
};

const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

const formatPercent = (value: number): string => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
};

const getMarketStatus = (): { status: string; color: string; message: string } => {
  const now = new Date();
  const hour = now.getHours();
  const isWeekend = now.getDay() === 0 || now.getDay() === 6;
  
  if (isWeekend) {
    return { status: "Closed", color: "text-gray-500", message: "Markets closed - Weekend" };
  }
  
  if (hour >= 9 && hour < 16) {
    return { status: "Open", color: "text-green-600", message: "Markets are open" };
  } else if (hour >= 16 && hour < 20) {
    return { status: "After Hours", color: "text-yellow-600", message: "After hours trading" };
  } else {
    return { status: "Closed", color: "text-gray-500", message: "Markets closed" };
  }
};

export const MarketSidebar: React.FC = () => {
  const marketStatus = getMarketStatus();
  const isVIXHigh = mockVIX.value > 25;

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
      {/* Market Status */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3">Market Status</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Status</span>
            <span className={`font-medium ${marketStatus.color}`}>
              {marketStatus.status}
            </span>
          </div>
          <p className="text-xs text-gray-500">{marketStatus.message}</p>
        </div>
      </div>

      {/* Major Indices */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3">Major Indices</h3>
        <div className="space-y-3">
          {mockMarketData.map((index) => {
            const isPositive = index.change >= 0;
            
            return (
              <div key={index.symbol} className="border-b border-gray-100 pb-3 last:border-b-0">
                <div className="flex justify-between items-start mb-1">
                  <div>
                    <div className="font-medium text-gray-900 text-sm">
                      {index.name}
                    </div>
                    <div className="text-xs text-gray-500">
                      {index.symbol}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-mono text-sm font-semibold text-gray-900">
                      {formatNumber(index.value)}
                    </div>
                    <div className={`font-mono text-xs ${
                      isPositive ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {isPositive ? '+' : ''}{formatNumber(index.change)}
                    </div>
                  </div>
                </div>
                <div className={`text-xs font-mono ${
                  isPositive ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatPercent(index.changePercent)}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* VIX Volatility */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3">Volatility (VIX)</h3>
        <div className={`p-3 rounded-lg ${
          isVIXHigh ? 'bg-red-50 border border-red-200' : 'bg-gray-50'
        }`}>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600">VIX</span>
            {isVIXHigh && (
              <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">
                High Volatility
              </span>
            )}
          </div>
          <div className="space-y-1">
            <div className={`font-mono text-lg font-bold ${
              isVIXHigh ? 'text-red-700' : 'text-gray-900'
            }`}>
              {formatNumber(mockVIX.value)}
            </div>
            <div className={`font-mono text-sm ${
              mockVIX.change >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {mockVIX.change >= 0 ? '+' : ''}{formatNumber(mockVIX.change)} ({formatPercent(mockVIX.changePercent)})
            </div>
          </div>
          {isVIXHigh && (
            <p className="text-xs text-red-600 mt-2">
              Elevated market volatility detected
            </p>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3">Quick Actions</h3>
        <div className="space-y-2">
          <button className="w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-md transition-colors duration-200">
            Refresh All Data
          </button>
          <button className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-md transition-colors duration-200">
            View Market News
          </button>
          <button className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-md transition-colors duration-200">
            Economic Calendar
          </button>
        </div>
      </div>
    </div>
  );
};