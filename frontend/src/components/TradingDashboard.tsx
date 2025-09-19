import React from 'react';
import { PortfolioHeader } from './PortfolioHeader';
import { RecommendationCard } from './RecommendationCard';
import { MarketSidebar } from './MarketSidebar';

// TypeScript interfaces
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

interface AIRecommendation {
  id: string;
  action: 'buy' | 'sell' | 'hold';
  ticker: string;
  quantity: number;
  currentPrice: number;
  confidence: 'high' | 'medium' | 'low';
  reasoning: string;
  estimatedValue: number;
  urgency: 'high' | 'normal';
}

// Mock data for demonstration
const mockPortfolio: Portfolio = {
  totalValue: 125750.50,
  dailyChange: 2340.25,
  dailyChangePercent: 1.89,
  topHoldings: [
    { ticker: "AAPL", value: 25600.00, change: 434.50, changePercent: 1.72, sparklineData: [150, 152, 148, 155, 158] },
    { ticker: "MSFT", value: 18900.00, change: -234.25, changePercent: -1.23, sparklineData: [200, 198, 195, 192, 189] },
    { ticker: "GOOGL", value: 15300.00, change: 567.80, changePercent: 3.85, sparklineData: [120, 125, 130, 128, 135] }
  ],
  lastUpdated: "2025-09-19T15:42:33Z"
};

const mockRecommendations: AIRecommendation[] = [
  {
    id: "1",
    action: "sell",
    ticker: "NVDA", 
    quantity: 100,
    currentPrice: 180.25,
    confidence: "high",
    reasoning: "Trim position to reduce risk before earnings volatility",
    estimatedValue: 18025.00,
    urgency: "high"
  },
  {
    id: "2", 
    action: "buy",
    ticker: "META",
    quantity: 50,
    currentPrice: 245.80,
    confidence: "medium",
    reasoning: "Rotate into undervalued tech with growth potential",
    estimatedValue: 12290.00,
    urgency: "normal"
  }
];

const TradingDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState('opportunities');

  const tabs = [
    { id: 'opportunities', label: 'Opportunities' },
    { id: 'portfolio', label: 'Portfolio' },
    { id: 'history', label: 'History' },
    { id: 'settings', label: 'Settings' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-3 space-y-6">
            {/* Portfolio Header */}
            <PortfolioHeader portfolio={mockPortfolio} />
            
            {/* Today's Opportunities */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold text-gray-900">Today's Opportunities</h2>
                <button className="text-sm text-blue-600 hover:text-blue-700 transition-colors duration-200">
                  Refresh Analysis
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {mockRecommendations.map((recommendation) => (
                  <RecommendationCard 
                    key={recommendation.id} 
                    recommendation={recommendation} 
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Market Sidebar - Desktop Only */}
          <div className="hidden lg:block">
            <MarketSidebar />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingDashboard;