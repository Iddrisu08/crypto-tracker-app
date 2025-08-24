import { useState, useEffect, memo, useCallback } from 'react';
import { useAuthStore } from '../store/authStore';
import SimpleLogin from './SimpleLogin';

const AnalyticsDashboardV2 = memo(function AnalyticsDashboardV2() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user, tokens, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) {
      loadMetrics();
    } else {
      setError('Please log in to view analytics');
      setLoading(false);
    }
  }, [isAuthenticated]);

  const loadMetrics = useCallback(async () => {
    if (!tokens?.access_token) {
      setError('Authentication required');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      console.log('AnalyticsDashboardV2: Fetching performance metrics...');
      
      const response = await fetch('http://localhost:5001/api/v1/performance-metrics', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please log in again.');
        }
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('AnalyticsDashboardV2: Received data:', data);
      
      if (!data) {
        throw new Error('No data received from API');
      }
      
      setMetrics(data);
    } catch (err) {
      console.error('AnalyticsDashboardV2: Error loading metrics:', err);
      if (err.message.includes('Authentication')) {
        setError('Authentication required. Please log in to view analytics.');
      } else if (err.message.includes('fetch')) {
        setError('Network error: Unable to connect to the analytics service');
      } else if (err.message.includes('JSON')) {
        setError('Data error: Invalid response format');
      } else {
        setError(`Failed to load analytics data: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  }, [tokens]);

  if (!isAuthenticated) {
    return (
      <div className="space-y-8">
        <div className="bg-gradient-to-r from-yellow-800/50 to-gray-700 rounded-xl p-8 shadow-2xl border border-yellow-500/50">
          <div className="flex items-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl flex items-center justify-center mr-4 shadow-lg">
              <span className="text-white text-2xl">🔒</span>
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Portfolio Analytics V2</h2>
              <p className="text-yellow-300">Authentication Required</p>
            </div>
          </div>
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <div className="text-8xl mb-6">🔐</div>
              <div className="text-yellow-400 text-lg font-medium">Please log in to view analytics</div>
              <div className="text-gray-400 text-sm mt-2">Enhanced backend requires authentication</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="bg-gradient-to-r from-gray-800 to-gray-700 rounded-xl p-8 shadow-2xl border border-gray-600">
          <div className="flex items-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mr-4 shadow-lg animate-pulse">
              <span className="text-white text-2xl">📊</span>
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Portfolio Analytics V2</h2>
              <p className="text-gray-300">Loading enhanced insights...</p>
            </div>
          </div>
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <div className="animate-spin w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full mx-auto mb-6"></div>
              <div className="text-blue-300 text-lg font-medium">Loading analytics...</div>
              <div className="text-gray-400 text-sm mt-2">Fetching from enhanced backend</div>
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
              <h2 className="text-3xl font-bold text-white mb-2">Portfolio Analytics V2</h2>
              <p className="text-red-300">Error loading analytics data</p>
            </div>
          </div>
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <div className="text-8xl mb-6">📊</div>
              <div className="text-red-400 text-lg font-medium">{error}</div>
              <div className="text-gray-400 text-sm mt-2">Enhanced backend authentication required</div>
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
              <h2 className="text-3xl font-bold text-white mb-2">Portfolio Analytics V2</h2>
              <p className="text-gray-300">No data available</p>
            </div>
          </div>
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <div className="text-8xl mb-6">📊</div>
              <div className="text-gray-400 text-lg">No analytics data available</div>
              <div className="text-gray-500 text-sm mt-2">Enhanced backend returned no data</div>
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
            <h2 className="text-3xl font-bold text-white mb-2">Portfolio Analytics V2 🚀</h2>
            <p className="text-gray-300">Enhanced backend with authentication • Welcome {user?.username}</p>
          </div>
          <button
            onClick={loadMetrics}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 font-medium"
          >
            Refresh Analytics
          </button>
        </div>
      </div>

      {/* Login Component */}
      <SimpleLogin />

      {/* Debug Info */}
      <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-6 shadow-lg border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">Debug Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-400">User:</span>
            <span className="text-white ml-2">{user?.username || 'Not logged in'}</span>
          </div>
          <div>
            <span className="text-gray-400">Token:</span>
            <span className="text-white ml-2">{tokens?.access_token ? '✅ Present' : '❌ Missing'}</span>
          </div>
          <div>
            <span className="text-gray-400">Authenticated:</span>
            <span className="text-white ml-2">{isAuthenticated ? '✅ Yes' : '❌ No'}</span>
          </div>
          <div>
            <span className="text-gray-400">API Endpoint:</span>
            <span className="text-white ml-2">http://localhost:5001/api/v1/performance-metrics</span>
          </div>
        </div>
        
        {metrics && (
          <div className="mt-4">
            <span className="text-gray-400">Raw Response:</span>
            <pre className="text-xs text-green-400 mt-2 p-3 bg-gray-800 rounded overflow-x-auto">
              {JSON.stringify(metrics, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* Simple metrics display */}
      {metrics && (
        <div className="bg-gradient-to-r from-green-900/30 to-gray-800 rounded-xl p-8 shadow-lg border border-green-500/30">
          <h3 className="text-2xl font-bold text-white mb-6">📈 Raw Data Display</h3>
          <div className="text-white">
            <p>Successfully connected to enhanced backend!</p>
            <p className="mt-2">Data structure: {typeof metrics === 'object' ? 'Object' : typeof metrics}</p>
            <p className="mt-2">Keys available: {Object.keys(metrics || {}).join(', ')}</p>
          </div>
        </div>
      )}
    </div>
  );
});

export default AnalyticsDashboardV2;