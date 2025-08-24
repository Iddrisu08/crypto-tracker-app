import { useState, useEffect, memo, useCallback } from 'react';
import { fetchPerformanceMetrics } from '../api';
import PortfolioAllocation from './PortfolioAllocation';

const AnalyticsDashboard = memo(function AnalyticsDashboard() {
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
      console.log('AnalyticsDashboard: Fetching performance metrics...');
      
      const data = await fetchPerformanceMetrics();
      console.log('AnalyticsDashboard: Received data:', data);
      
      if (!data) {
        throw new Error('No data received from API');
      }
      
      if (!data.total_metrics || !data.btc_metrics || !data.eth_metrics) {
        throw new Error('Incomplete data structure received');
      }
      
      setMetrics(data);
    } catch (err) {
      console.error('AnalyticsDashboard: Error loading metrics:', err);
      // More detailed error message
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

  // Remove unused processedMetrics to avoid any potential issues

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="bg-gradient-to-r from-gray-800 to-gray-700 rounded-xl p-8 shadow-2xl border border-gray-600">
          <div className="flex items-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mr-4 shadow-lg animate-pulse">
              <span className="text-white text-2xl">📊</span>
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Portfolio Analytics</h2>
              <p className="text-gray-300">Loading comprehensive insights...</p>
            </div>
          </div>
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <div className="animate-spin w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full mx-auto mb-6"></div>
              <div className="text-blue-300 text-lg font-medium">Loading analytics...</div>
              <div className="text-gray-400 text-sm mt-2">Calculating performance metrics</div>
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
              <h2 className="text-3xl font-bold text-white mb-2">Portfolio Analytics</h2>
              <p className="text-red-300">Error loading analytics data</p>
            </div>
          </div>
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <div className="text-8xl mb-6">📊</div>
              <div className="text-red-400 text-lg font-medium">{error}</div>
              <div className="text-gray-400 text-sm mt-2">Please try refreshing the page</div>
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
              <h2 className="text-3xl font-bold text-white mb-2">Portfolio Analytics</h2>
              <p className="text-gray-300">No data available</p>
            </div>
          </div>
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <div className="text-8xl mb-6">📊</div>
              <div className="text-gray-400 text-lg">No analytics data available</div>
              <div className="text-gray-500 text-sm mt-2">Check your portfolio data and try again</div>
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
            <h2 className="text-3xl font-bold text-white mb-2">Portfolio Analytics</h2>
            <p className="text-gray-300">Comprehensive performance insights and metrics</p>
          </div>
          <button
            onClick={loadMetrics}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 font-medium"
          >
            Refresh Analytics
          </button>
        </div>
      </div>

      {/* Key Metrics Cards */}
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

      {/* Individual Crypto Performance */}
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
          
          <div className="border-t border-orange-500/20 pt-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="flex justify-between items-center py-2">
                <span className="text-orange-300 text-sm">🪙 Holdings:</span>
                <span className="text-white font-semibold">{metrics.btc_metrics.holdings.toFixed(6)} BTC</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-orange-300 text-sm">💲 Avg Price:</span>
                <span className="text-white font-semibold">{formatCurrency(metrics.btc_metrics.avg_purchase_price)}</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-orange-300 text-sm">📊 Current Price:</span>
                <span className="text-white font-semibold">{formatCurrency(metrics.btc_metrics.current_price)}</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-orange-300 text-sm">🥧 Allocation:</span>
                <span className="text-white font-semibold">{metrics.btc_metrics.allocation_percent.toFixed(1)}%</span>
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
          
          <div className="border-t border-blue-500/20 pt-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="flex justify-between items-center py-2">
                <span className="text-blue-300 text-sm">🪙 Holdings:</span>
                <span className="text-white font-semibold">{metrics.eth_metrics.holdings.toFixed(6)} ETH</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-blue-300 text-sm">💲 Avg Price:</span>
                <span className="text-white font-semibold">{formatCurrency(metrics.eth_metrics.avg_purchase_price)}</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-blue-300 text-sm">📊 Current Price:</span>
                <span className="text-white font-semibold">{formatCurrency(metrics.eth_metrics.current_price)}</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-blue-300 text-sm">🥧 Allocation:</span>
                <span className="text-white font-semibold">{metrics.eth_metrics.allocation_percent.toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* DCA Analysis and Portfolio Allocation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* DCA Analysis */}
        <div className="bg-gradient-to-br from-purple-900/20 to-gray-900 rounded-xl p-8 shadow-lg border border-purple-500/30 hover:border-purple-500/60 transition-all duration-300">
          <div className="flex items-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mr-4 shadow-lg">
              <span className="text-white text-2xl">📊</span>
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">DCA Strategy Analysis</h3>
              <p className="text-purple-300 text-sm">Dollar-Cost Averaging Performance</p>
            </div>
          </div>
          
          <div className="space-y-4 mb-6">
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="flex justify-between items-center">
                <span className="text-purple-300 font-medium">📈 DCA vs Lump Sum</span>
                <span className={`font-bold text-lg ${metrics.dca_analysis.dca_vs_lump_sum_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {metrics.dca_analysis.dca_vs_lump_sum_percent >= 0 ? '+' : ''}{metrics.dca_analysis.dca_vs_lump_sum_percent.toFixed(2)}%
                </span>
              </div>
            </div>
            
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="flex justify-between items-center">
                <span className="text-purple-300 font-medium">💰 Weekly Average</span>
                <span className="text-white font-bold text-lg">
                  {formatCurrency(metrics.dca_analysis.weekly_avg_investment)}
                </span>
              </div>
            </div>
            
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="flex justify-between items-center">
                <span className="text-purple-300 font-medium">📅 Investment Period</span>
                <span className="text-white font-bold text-lg">
                  {metrics.dca_analysis.total_weeks_invested} weeks
                </span>
              </div>
            </div>
          </div>
          
          <div className={`p-4 rounded-lg border ${metrics.dca_analysis.dca_vs_lump_sum_percent >= 0 ? 'bg-green-900/30 border-green-500/50' : 'bg-blue-900/30 border-blue-500/50'}`}>
            <div className={`${metrics.dca_analysis.dca_vs_lump_sum_percent >= 0 ? 'text-green-300' : 'text-blue-300'} text-sm font-medium mb-2 flex items-center`}>
              <span className="mr-2">{metrics.dca_analysis.dca_vs_lump_sum_percent >= 0 ? '🎉' : '💡'}</span>
              DCA Strategy Insight
            </div>
            <div className={`${metrics.dca_analysis.dca_vs_lump_sum_percent >= 0 ? 'text-green-100' : 'text-blue-100'} text-sm`}>
              {metrics.dca_analysis.dca_vs_lump_sum_percent >= 0 
                ? 'Your DCA strategy has outperformed a lump sum investment! Great job timing the market with regular purchases.' 
                : 'A lump sum investment would have performed better, but DCA reduces risk and provides emotional stability in volatile markets.'}
            </div>
          </div>
        </div>

        {/* Portfolio Allocation Chart */}
        <PortfolioAllocation />
      </div>

      {/* Performance Periods */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-8 shadow-lg border border-gray-600">
        <div className="flex items-center mb-6">
          <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center mr-4 shadow-lg">
            <span className="text-white text-2xl">📈</span>
          </div>
          <div>
            <h3 className="text-2xl font-bold text-white">Performance Periods</h3>
            <p className="text-indigo-300 text-sm">Best and worst weekly returns</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-gradient-to-br from-green-900/40 to-green-800/20 border-2 border-green-500/40 rounded-xl p-6 hover:border-green-500/60 transition-all duration-300 shadow-lg">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center mr-3 shadow-md">
                <span className="text-white text-xl">🏆</span>
              </div>
              <h4 className="text-green-300 font-bold text-lg">Best Week</h4>
            </div>
            {metrics.performance_periods.best_week.date ? (
              <>
                <div className="text-white font-bold text-3xl mb-2 flex items-center">
                  <span className="text-green-400 mr-2">+</span>
                  {metrics.performance_periods.best_week.return_percent.toFixed(2)}%
                </div>
                <div className="text-green-200 text-sm bg-green-900/30 rounded-lg px-3 py-2 border border-green-500/30">
                  📅 Week of {new Date(metrics.performance_periods.best_week.date).toLocaleDateString()}
                </div>
              </>
            ) : (
              <div className="text-gray-400 text-center py-4">
                <span className="text-2xl">📊</span>
                <div className="mt-2">No data available</div>
              </div>
            )}
          </div>
          
          <div className="bg-gradient-to-br from-red-900/40 to-red-800/20 border-2 border-red-500/40 rounded-xl p-6 hover:border-red-500/60 transition-all duration-300 shadow-lg">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-red-500 rounded-lg flex items-center justify-center mr-3 shadow-md">
                <span className="text-white text-xl">📉</span>
              </div>
              <h4 className="text-red-300 font-bold text-lg">Worst Week</h4>
            </div>
            {metrics.performance_periods.worst_week.date ? (
              <>
                <div className="text-white font-bold text-3xl mb-2 flex items-center">
                  <span className="text-red-400 mr-2"></span>
                  {metrics.performance_periods.worst_week.return_percent.toFixed(2)}%
                </div>
                <div className="text-red-200 text-sm bg-red-900/30 rounded-lg px-3 py-2 border border-red-500/30">
                  📅 Week of {new Date(metrics.performance_periods.worst_week.date).toLocaleDateString()}
                </div>
              </>
            ) : (
              <div className="text-gray-400 text-center py-4">
                <span className="text-2xl">📊</span>
                <div className="mt-2">No data available</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});

export default AnalyticsDashboard;