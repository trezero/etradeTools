import React from 'react';

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

interface RecommendationCardProps {
  recommendation: AIRecommendation;
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(value);
};

const getActionColor = (action: string): string => {
  switch (action) {
    case 'buy':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'sell':
      return 'bg-red-100 text-red-800 border-red-200';
    case 'hold':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

const getConfidenceBadge = (confidence: string): string => {
  switch (confidence) {
    case 'high':
      return 'bg-green-100 text-green-700';
    case 'medium':
      return 'bg-yellow-100 text-yellow-700';
    case 'low':
      return 'bg-red-100 text-red-700';
    default:
      return 'bg-gray-100 text-gray-700';
  }
};

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation }) => {
  const handleViewDetails = () => {
    // TODO: Open detail modal
    console.log('View details for:', recommendation.id);
  };

  const handleExecuteTrade = () => {
    // TODO: Open trade execution flow
    console.log('Execute trade for:', recommendation.id);
  };

  return (
    <div className={`bg-white border rounded-lg p-6 shadow-sm hover:shadow-md transition-all duration-200 ${
      recommendation.urgency === 'high' ? 'border-l-4 border-l-orange-400' : 'border-gray-200'
    }`}>
      {/* Header with action and confidence */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center space-x-3">
          <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getActionColor(recommendation.action)}`}>
            {recommendation.action.toUpperCase()}
          </span>
          <span className="text-2xl font-bold text-gray-900">
            {recommendation.ticker}
          </span>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceBadge(recommendation.confidence)}`}>
          {recommendation.confidence} confidence
        </span>
      </div>

      {/* Trade details */}
      <div className="space-y-3 mb-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-sm text-gray-500">Quantity</span>
            <div className="font-mono font-semibold text-gray-900">
              {recommendation.quantity.toLocaleString()} shares
            </div>
          </div>
          <div>
            <span className="text-sm text-gray-500">Current Price</span>
            <div className="font-mono font-semibold text-gray-900">
              {formatCurrency(recommendation.currentPrice)}
            </div>
          </div>
        </div>
        
        <div>
          <span className="text-sm text-gray-500">Estimated Value</span>
          <div className="font-mono font-bold text-lg text-gray-900">
            {formatCurrency(recommendation.estimatedValue)}
          </div>
        </div>
      </div>

      {/* AI Reasoning */}
      <div className="mb-6">
        <span className="text-sm text-gray-500 block mb-1">AI Analysis</span>
        <p className="text-sm text-gray-700 leading-relaxed">
          {recommendation.reasoning}
        </p>
      </div>

      {/* Action buttons */}
      <div className="flex space-x-3">
        <button
          onClick={handleViewDetails}
          className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md font-medium hover:bg-blue-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          View Details
        </button>
        <button
          onClick={handleExecuteTrade}
          className={`flex-1 px-4 py-2 rounded-md font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 ${
            recommendation.action === 'buy'
              ? 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500'
              : recommendation.action === 'sell'
              ? 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500'
              : 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500'
          }`}
        >
          Execute Trade
        </button>
      </div>

      {/* Urgency indicator */}
      {recommendation.urgency === 'high' && (
        <div className="mt-4 p-2 bg-orange-50 border border-orange-200 rounded-md">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-4 w-4 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-2">
              <p className="text-sm text-orange-700">
                High priority recommendation - consider acting soon
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};