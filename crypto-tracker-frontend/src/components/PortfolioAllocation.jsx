import { useState, useEffect, memo, useMemo, useCallback } from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { fetchPerformanceMetrics } from '../api';

ChartJS.register(ArcElement, Tooltip, Legend);

const PortfolioAllocation = memo(function PortfolioAllocation() {
  const [allocationData, setAllocationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAllocationData();
  }, []);

  const loadAllocationData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const metrics = await fetchPerformanceMetrics();
      
      if (metrics && metrics.btc_metrics && metrics.eth_metrics) {
        setAllocationData({
          btc: {
            allocation: metrics.btc_metrics.allocation_percent,
            value: metrics.btc_metrics.current_value,
            holdings: metrics.btc_metrics.holdings
          },
          eth: {
            allocation: metrics.eth_metrics.allocation_percent,
            value: metrics.eth_metrics.current_value,
            holdings: metrics.eth_metrics.holdings
          },
          total_value: metrics.total_metrics.current_value
        });
      }
    } catch (err) {
      console.error('Error loading allocation data:', err);
      setError('Failed to load portfolio allocation');
    } finally {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-8 shadow-lg border border-gray-600">
        <div className="flex items-center mb-6">
          <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center mr-4 shadow-lg animate-pulse">
            <span className="text-white text-2xl">🥧</span>
          </div>
          <div>
            <h3 className="text-2xl font-bold text-white">Portfolio Allocation</h3>
            <p className="text-indigo-300 text-sm">Asset distribution breakdown</p>
          </div>
        </div>
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <div className="animate-spin w-12 h-12 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full mx-auto mb-4"></div>
            <div className="text-indigo-300">Loading allocation data...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-8 shadow-lg border border-red-500/30">
        <div className="flex items-center mb-6">
          <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center mr-4 shadow-lg">
            <span className="text-white text-2xl">⚠️</span>
          </div>
          <div>
            <h3 className="text-2xl font-bold text-white">Portfolio Allocation</h3>
            <p className="text-red-300 text-sm">Error loading data</p>
          </div>
        </div>
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <div className="text-6xl mb-4">📊</div>
            <div className="text-red-400 font-medium">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  if (!allocationData) {
    return (
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-8 shadow-lg border border-gray-600">
        <div className="flex items-center mb-6">
          <div className="w-16 h-16 bg-gradient-to-br from-gray-500 to-gray-600 rounded-xl flex items-center justify-center mr-4 shadow-lg">
            <span className="text-white text-2xl">📊</span>
          </div>
          <div>
            <h3 className="text-2xl font-bold text-white">Portfolio Allocation</h3>
            <p className="text-gray-300 text-sm">No data available</p>
          </div>
        </div>
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <div className="text-6xl mb-4">📈</div>
            <div className="text-gray-400">No allocation data available</div>
          </div>
        </div>
      </div>
    );
  }

  const chartData = {
    labels: ['Bitcoin (BTC)', 'Ethereum (ETH)'],
    datasets: [
      {
        data: [allocationData.btc.allocation, allocationData.eth.allocation],
        backgroundColor: [
          '#F7931A', // Bitcoin orange
          '#627EEA', // Ethereum blue
        ],
        borderColor: [
          '#F7931A',
          '#627EEA',
        ],
        borderWidth: 2,
        hoverBackgroundColor: [
          '#FF9500',
          '#7089FF',
        ],
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: 'white',
          padding: 20,
          font: {
            size: 14,
          },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.9)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(75, 85, 99, 0.8)',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed;
            const crypto = label.includes('Bitcoin') ? allocationData.btc : allocationData.eth;
            return [
              `${label}: ${value.toFixed(1)}%`,
              `Value: $${crypto.value.toLocaleString()}`,
              `Holdings: ${crypto.holdings.toFixed(6)}`
            ];
          }
        }
      }
    },
  };

  return (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-8 shadow-lg border border-gray-600 hover:border-indigo-500/60 transition-all duration-300">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-6 space-y-4 md:space-y-0">
        <div className="flex items-center">
          <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center mr-4 shadow-lg">
            <span className="text-white text-2xl">🥧</span>
          </div>
          <div>
            <h3 className="text-2xl font-bold text-white">Portfolio Allocation</h3>
            <p className="text-indigo-300 text-sm">Asset distribution breakdown</p>
          </div>
        </div>
        <button
          onClick={loadAllocationData}
          className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-lg hover:from-indigo-700 hover:to-indigo-800 transition-all duration-300 shadow-md hover:shadow-lg transform hover:scale-105 text-sm font-medium"
        >
          🔄 Refresh
        </button>
      </div>
      
      <div className="h-64 mb-4">
        <Pie data={chartData} options={chartOptions} />
      </div>
      
      <div className="grid grid-cols-2 gap-6 mt-6">
        <div className="bg-gradient-to-br from-orange-900/30 to-gray-800/50 rounded-xl p-4 border border-orange-500/30">
          <div className="flex items-center mb-3">
            <div className="w-6 h-6 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg mr-3 shadow-sm"></div>
            <span className="text-orange-300 font-semibold">Bitcoin</span>
          </div>
          <div className="text-3xl font-bold text-white mb-2">
            {allocationData.btc.allocation.toFixed(1)}%
          </div>
          <div className="text-orange-200 text-sm font-medium">
            ${allocationData.btc.value.toLocaleString()}
          </div>
          <div className="text-orange-300/70 text-xs mt-1">
            {allocationData.btc.holdings.toFixed(6)} BTC
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-blue-900/30 to-gray-800/50 rounded-xl p-4 border border-blue-500/30">
          <div className="flex items-center mb-3">
            <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg mr-3 shadow-sm"></div>
            <span className="text-blue-300 font-semibold">Ethereum</span>
          </div>
          <div className="text-3xl font-bold text-white mb-2">
            {allocationData.eth.allocation.toFixed(1)}%
          </div>
          <div className="text-blue-200 text-sm font-medium">
            ${allocationData.eth.value.toLocaleString()}
          </div>
          <div className="text-blue-300/70 text-xs mt-1">
            {allocationData.eth.holdings.toFixed(6)} ETH
          </div>
        </div>
      </div>
      
      <div className="mt-6 pt-6 border-t border-indigo-500/20">
        <div className="text-center bg-gradient-to-r from-indigo-900/20 to-purple-900/20 rounded-lg p-4 border border-indigo-500/30">
          <div className="text-indigo-300 text-sm font-medium mb-1">💎 Total Portfolio Value</div>
          <div className="text-3xl font-bold text-white">
            ${allocationData.total_value.toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
});

export default PortfolioAllocation;