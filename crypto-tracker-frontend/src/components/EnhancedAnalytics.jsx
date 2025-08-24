import { useState, useEffect } from 'react';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';
import { FaBitcoin, FaEthereum, FaChartPie, FaChartLine, FaTrendingUp, FaCalendarAlt } from 'react-icons/fa';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

const EnhancedAnalytics = () => {
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

  // Portfolio Allocation Pie Chart
  const getAllocationChartData = () => {
    if (!metrics) return null;

    return {
      labels: ['Bitcoin (BTC)', 'Ethereum (ETH)'],
      datasets: [
        {
          data: [
            metrics.btc_metrics.allocation_percent,
            metrics.eth_metrics.allocation_percent
          ],
          backgroundColor: [
            '#f7931a', // Bitcoin orange
            '#627eea'  // Ethereum blue
          ],
          borderColor: [
            '#e6820a',
            '#5a6fd8'
          ],
          borderWidth: 2,
          hoverBackgroundColor: [
            '#ff9f33',
            '#7289f0'
          ]
        }
      ]
    };
  };

  // ROI Comparison Bar Chart
  const getROIChartData = () => {
    if (!metrics) return null;

    return {
      labels: ['Bitcoin', 'Ethereum', 'Total Portfolio'],
      datasets: [
        {
          label: 'ROI %',
          data: [
            metrics.btc_metrics.roi_percent,
            metrics.eth_metrics.roi_percent,
            metrics.total_metrics.roi_percent
          ],
          backgroundColor: [
            'rgba(247, 147, 26, 0.8)',
            'rgba(98, 126, 234, 0.8)',
            'rgba(34, 197, 94, 0.8)'
          ],
          borderColor: [
            '#f7931a',
            '#627eea',
            '#22c55e'
          ],
          borderWidth: 2
        }
      ]
    };
  };

  // Investment vs Current Value Comparison
  const getValueComparisonData = () => {
    if (!metrics) return null;

    return {
      labels: ['Bitcoin', 'Ethereum'],
      datasets: [
        {
          label: 'Amount Invested',
          data: [metrics.btc_metrics.invested, metrics.eth_metrics.invested],
          backgroundColor: 'rgba(156, 163, 175, 0.8)',
          borderColor: '#9ca3af',
          borderWidth: 2
        },
        {
          label: 'Current Value',
          data: [metrics.btc_metrics.current_value, metrics.eth_metrics.current_value],
          backgroundColor: 'rgba(34, 197, 94, 0.8)',
          borderColor: '#22c55e',
          borderWidth: 2
        }
      ]
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#ffffff',
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#374151',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#9ca3af'
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.2)'
        }
      },
      y: {
        ticks: {
          color: '#9ca3af'
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.2)'
        }
      }
    }
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#ffffff',
          padding: 20,
          font: {
            size: 14
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#374151',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            return `${context.label}: ${context.parsed.toFixed(1)}%`;
          }
        }
      }
    }
  };

  if (loading) {
    return (
      <div className="enhanced-analytics">
        <div className="analytics-header">
          <h2>🚀 Enhanced Portfolio Analytics</h2>
          <p>Loading comprehensive insights...</p>
        </div>
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Analyzing your portfolio performance...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="enhanced-analytics">
        <div className="analytics-header error">
          <h2>📊 Enhanced Portfolio Analytics</h2>
          <p className="error-message">{error}</p>
          <button onClick={fetchAnalytics} className="retry-btn">
            Retry Analysis
          </button>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="enhanced-analytics">
        <div className="analytics-header">
          <h2>📊 Enhanced Portfolio Analytics</h2>
          <p>No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="enhanced-analytics">
      {/* Header */}
      <div className="analytics-header">
        <h2>🚀 Enhanced Portfolio Analytics</h2>
        <p>Comprehensive insights into your crypto investments</p>
        <button onClick={fetchAnalytics} className="refresh-analytics-btn">
          <FaTrendingUp /> Refresh Analytics
        </button>
      </div>

      {/* Key Metrics Overview */}
      <div className="metrics-overview">
        <div className="metric-card total">
          <div className="metric-icon">💰</div>
          <div className="metric-info">
            <h3>Total Portfolio</h3>
            <div className="metric-value">{formatCurrency(metrics.total_metrics.current_value)}</div>
            <div className="metric-change positive">
              {formatPercent(metrics.total_metrics.roi_percent)} 
              ({formatCurrency(metrics.total_metrics.profit_loss)})
            </div>
          </div>
        </div>

        <div className="metric-card btc">
          <div className="metric-icon"><FaBitcoin /></div>
          <div className="metric-info">
            <h3>Bitcoin Holdings</h3>
            <div className="metric-value">{formatCurrency(metrics.btc_metrics.current_value)}</div>
            <div className={`metric-change ${metrics.btc_metrics.roi_percent >= 0 ? 'positive' : 'negative'}`}>
              {formatPercent(metrics.btc_metrics.roi_percent)}
            </div>
            <div className="metric-details">
              {metrics.btc_metrics.holdings.toFixed(6)} BTC
            </div>
          </div>
        </div>

        <div className="metric-card eth">
          <div className="metric-icon"><FaEthereum /></div>
          <div className="metric-info">
            <h3>Ethereum Holdings</h3>
            <div className="metric-value">{formatCurrency(metrics.eth_metrics.current_value)}</div>
            <div className={`metric-change ${metrics.eth_metrics.roi_percent >= 0 ? 'positive' : 'negative'}`}>
              {formatPercent(metrics.eth_metrics.roi_percent)}
            </div>
            <div className="metric-details">
              {metrics.eth_metrics.holdings.toFixed(6)} ETH
            </div>
          </div>
        </div>

        <div className="metric-card performance">
          <div className="metric-icon">📈</div>
          <div className="metric-info">
            <h3>Annualized Return</h3>
            <div className="metric-value">{formatPercent(metrics.total_metrics.annualized_return, false)}</div>
            <div className="metric-details">
              <FaCalendarAlt /> {metrics.total_metrics.days_invested} days invested
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        {/* Portfolio Allocation */}
        <div className="chart-container">
          <div className="chart-header">
            <h3><FaChartPie /> Portfolio Allocation</h3>
            <p>Distribution of your crypto investments</p>
          </div>
          <div className="chart-wrapper pie-chart">
            <Pie data={getAllocationChartData()} options={pieOptions} />
          </div>
        </div>

        {/* ROI Comparison */}
        <div className="chart-container">
          <div className="chart-header">
            <h3><FaChartLine /> ROI Comparison</h3>
            <p>Return on investment by asset</p>
          </div>
          <div className="chart-wrapper">
            <Bar data={getROIChartData()} options={chartOptions} />
          </div>
        </div>

        {/* Investment vs Current Value */}
        <div className="chart-container full-width">
          <div className="chart-header">
            <h3><FaTrendingUp /> Investment vs Current Value</h3>
            <p>Compare your initial investment to current market value</p>
          </div>
          <div className="chart-wrapper">
            <Bar data={getValueComparisonData()} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* DCA Analysis */}
      <div className="dca-analysis">
        <h3>📊 Dollar Cost Averaging Analysis</h3>
        <div className="dca-metrics">
          <div className="dca-metric">
            <label>Weekly Average Investment</label>
            <value>{formatCurrency(metrics.dca_analysis.weekly_avg_investment)}</value>
          </div>
          <div className="dca-metric">
            <label>Total Weeks Invested</label>
            <value>{metrics.dca_analysis.total_weeks_invested}</value>
          </div>
          <div className="dca-metric">
            <label>DCA vs Lump Sum</label>
            <value className={metrics.dca_analysis.dca_vs_lump_sum_percent >= 0 ? 'positive' : 'negative'}>
              {formatPercent(metrics.dca_analysis.dca_vs_lump_sum_percent)}
            </value>
          </div>
        </div>
      </div>

      {/* Performance Periods */}
      <div className="performance-periods">
        <h3>🎯 Best & Worst Performing Periods</h3>
        <div className="periods-grid">
          <div className="period-card best">
            <h4>🚀 Best Week</h4>
            <div className="period-date">{metrics.performance_periods.best_week.date || 'N/A'}</div>
            <div className="period-return positive">
              {formatPercent(metrics.performance_periods.best_week.return_percent)}
            </div>
          </div>
          <div className="period-card worst">
            <h4>📉 Worst Week</h4>
            <div className="period-date">{metrics.performance_periods.worst_week.date || 'N/A'}</div>
            <div className="period-return negative">
              {formatPercent(metrics.performance_periods.worst_week.return_percent)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedAnalytics;