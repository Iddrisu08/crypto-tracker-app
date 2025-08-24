import { useState, useEffect, memo, useCallback } from 'react';

const AnalyticsDashboardSimple = memo(function AnalyticsDashboardSimple() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('AnalyticsDashboardSimple: Fetching performance metrics...');
      
      const response = await fetch('http://localhost:5001/api/v1/performance-metrics', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('AnalyticsDashboardSimple: Received data:', data);
      
      if (!data) {
        throw new Error('No data received from API');
      }
      
      setMetrics(data);
    } catch (err) {
      console.error('AnalyticsDashboardSimple: Error loading metrics:', err);
      if (err.message.includes('fetch')) {
        setError('Network error: Unable to connect to the analytics service');
      } else if (err.message.includes('JSON')) {
        setError('Data error: Invalid response format');
      } else {
        setError(`Failed to load analytics data: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="bg-gradient-to-r from-gray-800 to-gray-700 rounded-xl p-8 shadow-2xl border border-gray-600">
          <div className="flex items-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mr-4 shadow-lg animate-pulse">
              <span className="text-white text-2xl">🚀</span>
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Portfolio Analytics (Simplified)</h2>
              <p className="text-gray-300">Loading enhanced insights without authentication...</p>
            </div>
          </div>
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <div className="animate-spin w-16 h-16 border-4 border-green-500/30 border-t-green-500 rounded-full mx-auto mb-6"></div>
              <div className="text-green-300 text-lg font-medium">Loading analytics...</div>
              <div className="text-gray-400 text-sm mt-2">Fetching from simplified backend (no auth required)</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-8">
        <div className="bg-gradient-to-r from-red-800/50 to-gray-700 rounded-xl p-8 shadow-2xl border border-red-500/50">
          <div className="flex items-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center mr-4 shadow-lg">
              <span className="text-white text-2xl">⚠️</span>
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Portfolio Analytics (Simplified)</h2>
              <p className="text-red-300">Error loading analytics data</p>
            </div>
          </div>
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <div className="text-8xl mb-6">📊</div>
              <div className="text-red-400 text-lg font-medium">{error}</div>
              <div className="text-gray-400 text-sm mt-2">Simplified backend (no authentication required)</div>
              <button
                onClick={loadMetrics}
                className="mt-4 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="space-y-8">
        <div className="bg-gradient-to-r from-gray-800 to-gray-700 rounded-xl p-8 shadow-2xl border border-gray-600">
          <div className="flex items-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-gray-500 to-gray-600 rounded-xl flex items-center justify-center mr-4 shadow-lg">
              <span className="text-white text-2xl">📈</span>
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Portfolio Analytics (Simplified)</h2>
              <p className="text-gray-300">No data available</p>
            </div>
          </div>
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <div className="text-8xl mb-6">📊</div>
              <div className="text-gray-400 text-lg">No analytics data available</div>
              <div className="text-gray-500 text-sm mt-2">Simplified backend returned no data</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value) => {
    const color = value >= 0 ? 'text-green-400' : 'text-red-400';
    const sign = value >= 0 ? '+' : '';
    return <span className={color}>{sign}{value.toFixed(2)}%</span>;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-700 rounded-xl p-8 shadow-2xl border border-gray-600">
        <div className="flex flex-col md:flex-row md:justify-between md:items-center space-y-4 md:space-y-0">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">Portfolio Analytics (Simplified) 🚀</h2>
            <p className="text-gray-300">Enhanced backend without authentication complexity</p>
          </div>
          <button
            onClick={loadMetrics}
            className="px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 font-medium"
          >
            Refresh Analytics
          </button>
        </div>
      </div>

      {/* Connection Status */}
      <div className="bg-gradient-to-r from-green-900/30 to-gray-800 rounded-xl p-6 shadow-lg border border-green-500/30">
        <h3 className="text-xl font-bold text-white mb-4">✅ Enhanced Backend Connection</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-400">API Endpoint:</span>
            <span className="text-white ml-2">http://localhost:5001/api/v1/performance-metrics</span>
          </div>
          <div>
            <span className="text-gray-400">Authentication:</span>
            <span className="text-green-400 ml-2">❌ None Required (Simplified)</span>
          </div>
          <div>
            <span className="text-gray-400">Database:</span>
            <span className="text-green-400 ml-2">✅ SQLite Enhanced</span>
          </div>
          <div>
            <span className="text-gray-400">Features:</span>
            <span className="text-green-400 ml-2">✅ Caching, Rate Limiting, Logging</span>
          </div>
        </div>
        
        {metrics && (
          <div className="mt-4">
            <span className="text-gray-400">Raw Response Structure:</span>
            <div className="text-xs text-green-400 mt-2 p-3 bg-gray-800 rounded">
              Available sections: {Object.keys(metrics).join(', ')}
            </div>
          </div>
        )}
      </div>

      {/* Key Metrics Cards */}
      {metrics && metrics.total_metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 shadow-lg border border-gray-600 hover:border-blue-500 transition-all duration-300 hover:shadow-xl">
            <div className="flex items-center mb-3">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white text-xl">💰</span>
              </div>
              <h3 className="text-gray-300 text-sm font-semibold uppercase tracking-wide">Total Investment</h3>
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              {formatCurrency(metrics.total_metrics.invested)}
            </div>
            <div className="text-blue-400 text-sm">
              📅 {metrics.total_metrics.days_invested} days invested
            </div>
          </div>

          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 shadow-lg border border-gray-600 hover:border-green-500 transition-all duration-300 hover:shadow-xl">
            <div className="flex items-center mb-3">
              <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white text-xl">📈</span>
              </div>
              <h3 className="text-gray-300 text-sm font-semibold uppercase tracking-wide">Current Value</h3>
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              {formatCurrency(metrics.total_metrics.current_value)}
            </div>
            <div className="text-sm">
              {formatPercent(metrics.total_metrics.roi_percent)}
            </div>
          </div>

          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 shadow-lg border border-gray-600 hover:border-purple-500 transition-all duration-300 hover:shadow-xl">
            <div className="flex items-center mb-3">
              <div className={`w-12 h-12 ${metrics.total_metrics.profit_loss >= 0 ? 'bg-green-600' : 'bg-red-600'} rounded-lg flex items-center justify-center mr-3`}>
                <span className="text-white text-xl">{metrics.total_metrics.profit_loss >= 0 ? '📊' : '📉'}</span>
              </div>
              <h3 className="text-gray-300 text-sm font-semibold uppercase tracking-wide">Total P&L</h3>
            </div>
            <div className={`text-3xl font-bold mb-2 ${metrics.total_metrics.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {formatCurrency(metrics.total_metrics.profit_loss)}
            </div>
            <div className="text-gray-400 text-sm">
              💡 Unrealized gains/losses
            </div>
          </div>

          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 shadow-lg border border-gray-600 hover:border-yellow-500 transition-all duration-300 hover:shadow-xl">
            <div className="flex items-center mb-3">
              <div className={`w-12 h-12 ${metrics.total_metrics.annualized_return >= 0 ? 'bg-yellow-600' : 'bg-red-600'} rounded-lg flex items-center justify-center mr-3`}>
                <span className="text-white text-xl">⚡</span>
              </div>
              <h3 className="text-gray-300 text-sm font-semibold uppercase tracking-wide">Annualized Return</h3>
            </div>
            <div className={`text-3xl font-bold mb-2 ${metrics.total_metrics.annualized_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {metrics.total_metrics.annualized_return.toFixed(2)}%
            </div>
            <div className="text-gray-400 text-sm">
              📅 Annual performance
            </div>
          </div>
        </div>
      )}

      {/* Individual Crypto Performance */}
      {metrics && metrics.btc_metrics && metrics.eth_metrics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Bitcoin Metrics */}
          <div className="bg-gradient-to-br from-orange-900/20 to-gray-900 rounded-xl p-8 shadow-lg border border-orange-500/30 hover:border-orange-500/60 transition-all duration-300">
            <div className="flex items-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center mr-4 shadow-lg">
                <span className="text-white font-bold text-2xl">₿</span>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">Bitcoin Performance</h3>
                <p className="text-orange-300 text-sm">BTC Investment Analysis</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-6 mb-6">
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                <div className="text-orange-300 text-sm font-medium mb-1">💰 Invested</div>
                <div className="text-white font-bold text-xl">{formatCurrency(metrics.btc_metrics.invested)}</div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                <div className="text-orange-300 text-sm font-medium mb-1">📈 Current Value</div>
                <div className="text-white font-bold text-xl">{formatCurrency(metrics.btc_metrics.current_value)}</div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                <div className="text-orange-300 text-sm font-medium mb-1">📊 P&L</div>
                <div className={`font-bold text-xl ${metrics.btc_metrics.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {formatCurrency(metrics.btc_metrics.profit_loss)}
                </div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                <div className="text-orange-300 text-sm font-medium mb-1">⚡ ROI</div>
                <div className="font-bold text-xl">
                  {formatPercent(metrics.btc_metrics.roi_percent)}
                </div>
              </div>
            </div>
          </div>

          {/* Ethereum Metrics */}
          <div className="bg-gradient-to-br from-blue-900/20 to-gray-900 rounded-xl p-8 shadow-lg border border-blue-500/30 hover:border-blue-500/60 transition-all duration-300">
            <div className="flex items-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mr-4 shadow-lg">
                <span className="text-white font-bold text-2xl">Ξ</span>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">Ethereum Performance</h3>
                <p className="text-blue-300 text-sm">ETH Investment Analysis</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-6 mb-6">
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                <div className="text-blue-300 text-sm font-medium mb-1">💰 Invested</div>
                <div className="text-white font-bold text-xl">{formatCurrency(metrics.eth_metrics.invested)}</div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                <div className="text-blue-300 text-sm font-medium mb-1">📈 Current Value</div>
                <div className="text-white font-bold text-xl">{formatCurrency(metrics.eth_metrics.current_value)}</div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                <div className="text-blue-300 text-sm font-medium mb-1">📊 P&L</div>
                <div className={`font-bold text-xl ${metrics.eth_metrics.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {formatCurrency(metrics.eth_metrics.profit_loss)}
                </div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                <div className="text-blue-300 text-sm font-medium mb-1">⚡ ROI</div>
                <div className="font-bold text-xl">
                  {formatPercent(metrics.eth_metrics.roi_percent)}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Success Message */}
      <div className="bg-gradient-to-r from-green-900/40 to-gray-800 rounded-xl p-6 shadow-lg border border-green-500/50">
        <div className="flex items-center">
          <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center mr-4">
            <span className="text-white text-xl">🎉</span>
          </div>
          <div>
            <h3 className="text-green-300 font-bold text-lg">Enhanced Backend Working!</h3>
            <p className="text-green-200 text-sm">
              Successfully connected to simplified enhanced backend with database, caching, rate limiting, and performance improvements - all without authentication complexity!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
});

export default AnalyticsDashboardSimple;