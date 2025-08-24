import { useState, useEffect } from 'react';
import { FaBitcoin, FaEthereum, FaTrendingUp, FaCalendarAlt } from 'react-icons/fa';

const SimpleEnhancedAnalytics = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('http://localhost:5001/performance_metrics');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      setError(`Failed to load analytics: ${err.message}`);
      console.error('Analytics fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value, showSign = true) => {
    const sign = showSign && value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div style={{ 
        padding: '2rem', 
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', 
        borderRadius: '16px', 
        color: 'white',
        textAlign: 'center'
      }}>
        <h2>🚀 Enhanced Portfolio Analytics</h2>
        <div style={{ padding: '2rem' }}>
          <div style={{ marginBottom: '1rem' }}>Loading analytics...</div>
          <div className="spinner" style={{ 
            width: '40px', 
            height: '40px', 
            border: '4px solid rgba(255,255,255,0.1)', 
            borderTop: '4px solid #667eea', 
            borderRadius: '50%', 
            animation: 'spin 1s linear infinite',
            margin: '0 auto'
          }}></div>
        </div>
        <style>
          {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        padding: '2rem', 
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', 
        borderRadius: '16px', 
        color: 'white',
        textAlign: 'center'
      }}>
        <h2>📊 Enhanced Portfolio Analytics</h2>
        <p style={{ color: '#f56565', margin: '1rem 0' }}>{error}</p>
        <button 
          onClick={fetchAnalytics}
          style={{
            background: 'linear-gradient(45deg, #667eea, #764ba2)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          Retry Analysis
        </button>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div style={{ 
        padding: '2rem', 
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', 
        borderRadius: '16px', 
        color: 'white',
        textAlign: 'center'
      }}>
        <h2>📊 Enhanced Portfolio Analytics</h2>
        <p>No data available</p>
      </div>
    );
  }

  return (
    <div style={{ 
      padding: '2rem', 
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', 
      borderRadius: '16px', 
      color: 'white'
    }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h2 style={{ 
          fontSize: '2.5rem', 
          marginBottom: '0.5rem',
          background: 'linear-gradient(45deg, #ff6b6b, #4ecdc4)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          🚀 Enhanced Portfolio Analytics
        </h2>
        <p style={{ color: '#a0aec0', fontSize: '1.1rem' }}>
          Comprehensive insights into your crypto investments
        </p>
        <button 
          onClick={fetchAnalytics}
          style={{
            background: 'linear-gradient(45deg, #667eea, #764ba2)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            cursor: 'pointer',
            marginTop: '1rem'
          }}
        >
          <FaTrendingUp style={{ marginRight: '0.5rem' }} />
          Refresh Analytics
        </button>
      </div>

      {/* Key Metrics Overview */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
        gap: '1.5rem', 
        marginBottom: '3rem'
      }}>
        {/* Total Portfolio */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '12px',
          padding: '2rem',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderTop: '3px solid #22c55e'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>💰</div>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', opacity: 0.9 }}>
            Total Portfolio
          </h3>
          <div style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '0.5rem' }}>
            {formatCurrency(metrics.total_metrics.current_value)}
          </div>
          <div style={{ color: '#22c55e', fontSize: '1rem', fontWeight: '600' }}>
            {formatPercent(metrics.total_metrics.roi_percent)} 
            ({formatCurrency(metrics.total_metrics.profit_loss)})
          </div>
        </div>

        {/* Bitcoin */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '12px',
          padding: '2rem',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderTop: '3px solid #f7931a'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '1rem', color: '#f7931a' }}>
            <FaBitcoin />
          </div>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', opacity: 0.9 }}>
            Bitcoin Holdings
          </h3>
          <div style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '0.5rem' }}>
            {formatCurrency(metrics.btc_metrics.current_value)}
          </div>
          <div style={{ 
            color: metrics.btc_metrics.roi_percent >= 0 ? '#22c55e' : '#f56565',
            fontSize: '1rem',
            fontWeight: '600',
            marginBottom: '0.25rem'
          }}>
            {formatPercent(metrics.btc_metrics.roi_percent)}
          </div>
          <div style={{ color: '#a0aec0', fontSize: '0.9rem' }}>
            {metrics.btc_metrics.holdings.toFixed(6)} BTC
          </div>
        </div>

        {/* Ethereum */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '12px',
          padding: '2rem',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderTop: '3px solid #627eea'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '1rem', color: '#627eea' }}>
            <FaEthereum />
          </div>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', opacity: 0.9 }}>
            Ethereum Holdings
          </h3>
          <div style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '0.5rem' }}>
            {formatCurrency(metrics.eth_metrics.current_value)}
          </div>
          <div style={{ 
            color: metrics.eth_metrics.roi_percent >= 0 ? '#22c55e' : '#f56565',
            fontSize: '1rem',
            fontWeight: '600',
            marginBottom: '0.25rem'
          }}>
            {formatPercent(metrics.eth_metrics.roi_percent)}
          </div>
          <div style={{ color: '#a0aec0', fontSize: '0.9rem' }}>
            {metrics.eth_metrics.holdings.toFixed(6)} ETH
          </div>
        </div>

        {/* Performance */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '12px',
          padding: '2rem',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderTop: '3px solid #667eea'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '1rem', color: '#667eea' }}>📈</div>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', opacity: 0.9 }}>
            Annualized Return
          </h3>
          <div style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '0.5rem' }}>
            {formatPercent(metrics.total_metrics.annualized_return, false)}
          </div>
          <div style={{ color: '#a0aec0', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FaCalendarAlt /> {metrics.total_metrics.days_invested} days invested
          </div>
        </div>
      </div>

      {/* DCA Analysis */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.03)',
        borderRadius: '12px',
        padding: '2rem',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        marginBottom: '2rem'
      }}>
        <h3 style={{ fontSize: '1.3rem', marginBottom: '1.5rem' }}>
          📊 Dollar Cost Averaging Analysis
        </h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '1.5rem'
        }}>
          <div style={{ textAlign: 'center', padding: '1rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '8px' }}>
            <div style={{ color: '#a0aec0', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
              Weekly Average Investment
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: '700' }}>
              {formatCurrency(metrics.dca_analysis.weekly_avg_investment)}
            </div>
          </div>
          <div style={{ textAlign: 'center', padding: '1rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '8px' }}>
            <div style={{ color: '#a0aec0', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
              Total Weeks Invested
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: '700' }}>
              {metrics.dca_analysis.total_weeks_invested}
            </div>
          </div>
          <div style={{ textAlign: 'center', padding: '1rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '8px' }}>
            <div style={{ color: '#a0aec0', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
              DCA vs Lump Sum
            </div>
            <div style={{ 
              fontSize: '1.4rem', 
              fontWeight: '700',
              color: metrics.dca_analysis.dca_vs_lump_sum_percent >= 0 ? '#22c55e' : '#f56565'
            }}>
              {formatPercent(metrics.dca_analysis.dca_vs_lump_sum_percent)}
            </div>
          </div>
        </div>
      </div>

      {/* Performance Periods */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.03)',
        borderRadius: '12px',
        padding: '2rem',
        border: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <h3 style={{ fontSize: '1.3rem', marginBottom: '1.5rem', textAlign: 'center' }}>
          🎯 Best & Worst Performing Periods
        </h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '1.5rem'
        }}>
          <div style={{
            textAlign: 'center',
            padding: '1.5rem',
            borderRadius: '10px',
            border: '2px solid rgba(34, 197, 94, 0.3)',
            background: 'rgba(255, 255, 255, 0.02)'
          }}>
            <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>🚀 Best Week</h4>
            <div style={{ color: '#a0aec0', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
              {metrics.performance_periods.best_week.date || 'N/A'}
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#22c55e' }}>
              {formatPercent(metrics.performance_periods.best_week.return_percent)}
            </div>
          </div>
          
          <div style={{
            textAlign: 'center',
            padding: '1.5rem',
            borderRadius: '10px',
            border: '2px solid rgba(245, 101, 101, 0.3)',
            background: 'rgba(255, 255, 255, 0.02)'
          }}>
            <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>📉 Worst Week</h4>
            <div style={{ color: '#a0aec0', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
              {metrics.performance_periods.worst_week.date || 'N/A'}
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#f56565' }}>
              {formatPercent(metrics.performance_periods.worst_week.return_percent)}
            </div>
          </div>
        </div>
      </div>

      {/* Success Message */}
      <div style={{
        background: 'linear-gradient(90deg, rgba(34, 197, 94, 0.1), rgba(16, 185, 129, 0.05))',
        borderRadius: '12px',
        padding: '1.5rem',
        border: '1px solid rgba(34, 197, 94, 0.3)',
        marginTop: '2rem',
        display: 'flex',
        alignItems: 'center'
      }}>
        <div style={{ fontSize: '3rem', marginRight: '1rem' }}>🎉</div>
        <div>
          <h3 style={{ color: '#22c55e', fontSize: '1.2rem', marginBottom: '0.5rem' }}>
            Enhanced Analytics Working!
          </h3>
          <p style={{ color: '#a0aec0', fontSize: '0.9rem', margin: 0 }}>
            Successfully displaying your portfolio performance with comprehensive metrics and insights!
          </p>
        </div>
      </div>
    </div>
  );
};

export default SimpleEnhancedAnalytics;