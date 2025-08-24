import React, { useState, useEffect } from 'react';
import './AdvancedAnalytics.css';

const AdvancedAnalytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [benchmarks, setBenchmarks] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // For now, create mock data until backend is fully ready
      const mockAnalytics = {
        risk_metrics: {
          volatility: 15.4,
          annualized_volatility: 89.2,
          sharpe_ratio: 1.85,
          max_drawdown: 8.7,
          value_at_risk_95: -2.3,
          value_at_risk_dollar: -150.50
        },
        performance_metrics: {
          daily_return_avg: 0.45,
          annualized_return: 164.25,
          total_return: 42.8,
          days_tracked: 30
        },
        portfolio_composition: {
          btc_allocation: 65.5,
          eth_allocation: 34.5,
          diversification_score: 0.452
        },
        market_data: {
          portfolio_value: 8963.14,
          total_invested: 6300.00,
          unrealized_pnl: 2663.14
        }
      };

      const mockBenchmarks = {
        portfolio_performance: {
          return_percent: 42.8,
          start_value: 6300.00,
          end_value: 8963.14,
          period_days: 30
        },
        btc_benchmark: {
          return_percent: 38.2,
          outperformance: 4.6,
          start_price: 75000,
          end_price: 103650
        },
        eth_benchmark: {
          return_percent: 28.9,
          outperformance: 13.9,
          start_price: 2800,
          end_price: 3609
        },
        balanced_benchmark: {
          return_percent: 33.55,
          outperformance: 9.25,
          description: '50% BTC / 50% ETH'
        }
      };

      // Enhanced Analytics - Performance Insights
      const mockInsights = {
        coin_performance: {
          best_performer: {
            coin: 'BTC',
            return_percent: 38.2,
            profit_amount: 1750.30,
            days_held: 30
          },
          worst_performer: {
            coin: 'ETH', 
            return_percent: 28.9,
            profit_amount: 912.84,
            days_held: 30
          }
        },
        time_analysis: {
          best_day: {
            date: '2025-01-18',
            return_percent: 8.4,
            profit_amount: 420.15,
            reason: 'BTC surge to $105K'
          },
          worst_day: {
            date: '2025-01-12', 
            return_percent: -3.2,
            loss_amount: -180.45,
            reason: 'Market correction'
          },
          best_week: {
            week: 'Jan 15-21, 2025',
            return_percent: 15.6,
            profit_amount: 980.25
          },
          current_streak: {
            type: 'winning',
            days: 5,
            return_percent: 12.3
          }
        },
        investment_efficiency: {
          avg_buy_price_btc: 89750,
          current_price_btc: 117484,
          price_improvement: 30.9,
          avg_buy_price_eth: 3200,
          current_price_eth: 3771,
          eth_price_improvement: 17.8,
          cost_average_score: 8.2, // out of 10
          timing_score: 7.5 // out of 10
        },
        recommendations: [
          {
            type: 'rebalance',
            message: 'Consider rebalancing: BTC is now 65.5% of portfolio (target: 60%)',
            action: 'Sell $150 BTC or buy $100 ETH',
            impact: 'Reduce concentration risk'
          },
          {
            type: 'opportunity',
            message: 'ETH showing strong momentum (+5.2% this week)',
            action: 'Consider increasing ETH allocation',
            impact: 'Potential upside capture'
          },
          {
            type: 'risk',
            message: 'Portfolio volatility is high (89.2% annualized)',
            action: 'Consider dollar-cost averaging',
            impact: 'Reduce timing risk'
          }
        ]
      };

      setAnalytics(mockAnalytics);
      setBenchmarks(mockBenchmarks);
      setInsights(mockInsights);
      
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const getRiskLevel = (sharpe) => {
    if (sharpe > 2) return { level: 'Excellent', color: '#28a745' };
    if (sharpe > 1) return { level: 'Good', color: '#ffc107' };
    if (sharpe > 0) return { level: 'Fair', color: '#fd7e14' };
    return { level: 'Poor', color: '#dc3545' };
  };

  const getPerformanceColor = (value) => {
    return value >= 0 ? '#28a745' : '#dc3545';
  };

  if (loading) {
    return (
      <div className="advanced-analytics loading">
        <div className="loading-spinner"></div>
        <p>Calculating advanced analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="advanced-analytics error">
        <span>⚠️</span>
        <p>{error}</p>
        <button onClick={fetchAnalytics} className="retry-btn">
          Retry
        </button>
      </div>
    );
  }

  const riskLevel = getRiskLevel(analytics.risk_metrics.sharpe_ratio);

  return (
    <div className="advanced-analytics">
      <div className="analytics-header">
        <span className="header-icon">📊</span>
        <div>
          <h3>Advanced Portfolio Analytics</h3>
          <p>Professional risk metrics and performance analysis</p>
        </div>
        <button onClick={fetchAnalytics} className="refresh-btn">
          📈 Refresh
        </button>
      </div>

      <div className="analytics-grid">
        {/* Risk Metrics */}
        <div className="analytics-card risk-metrics">
          <h4>⚠️ Risk Metrics</h4>
          <div className="metrics-grid">
            <div className="metric">
              <span className="metric-label">Daily Volatility</span>
              <span className="metric-value">{analytics.risk_metrics.volatility}%</span>
            </div>
            <div className="metric">
              <span className="metric-label">Annual Volatility</span>
              <span className="metric-value">{analytics.risk_metrics.annualized_volatility}%</span>
            </div>
            <div className="metric">
              <span className="metric-label">Sharpe Ratio</span>
              <span className="metric-value" style={{ color: riskLevel.color }}>
                {analytics.risk_metrics.sharpe_ratio}
              </span>
              <span className="metric-note">{riskLevel.level}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Max Drawdown</span>
              <span className="metric-value risk">{analytics.risk_metrics.max_drawdown}%</span>
            </div>
            <div className="metric">
              <span className="metric-label">Value at Risk (95%)</span>
              <span className="metric-value risk">
                {analytics.risk_metrics.value_at_risk_95}% 
                (${analytics.risk_metrics.value_at_risk_dollar})
              </span>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="analytics-card performance-metrics">
          <h4>📈 Performance Analysis</h4>
          <div className="metrics-grid">
            <div className="metric">
              <span className="metric-label">Avg Daily Return</span>
              <span className="metric-value" style={{ 
                color: getPerformanceColor(analytics.performance_metrics.daily_return_avg) 
              }}>
                {analytics.performance_metrics.daily_return_avg}%
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Annualized Return</span>
              <span className="metric-value" style={{ 
                color: getPerformanceColor(analytics.performance_metrics.annualized_return) 
              }}>
                {analytics.performance_metrics.annualized_return}%
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Total Return</span>
              <span className="metric-value" style={{ 
                color: getPerformanceColor(analytics.performance_metrics.total_return) 
              }}>
                {analytics.performance_metrics.total_return}%
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Tracking Period</span>
              <span className="metric-value">{analytics.performance_metrics.days_tracked} days</span>
            </div>
          </div>
        </div>

        {/* Portfolio Composition */}
        <div className="analytics-card portfolio-composition">
          <h4>⚖️ Portfolio Allocation</h4>
          <div className="allocation-chart">
            <div className="allocation-bar">
              <div 
                className="btc-allocation" 
                style={{ width: `${analytics.portfolio_composition.btc_allocation}%` }}
              >
                BTC {analytics.portfolio_composition.btc_allocation}%
              </div>
              <div 
                className="eth-allocation" 
                style={{ width: `${analytics.portfolio_composition.eth_allocation}%` }}
              >
                ETH {analytics.portfolio_composition.eth_allocation}%
              </div>
            </div>
          </div>
          <div className="metrics-grid">
            <div className="metric">
              <span className="metric-label">Diversification Score</span>
              <span className="metric-value">{analytics.portfolio_composition.diversification_score}</span>
              <span className="metric-note">Higher is better (max: 0.5)</span>
            </div>
          </div>
        </div>

        {/* Benchmark Comparison */}
        <div className="analytics-card benchmark-comparison">
          <h4>🎯 Benchmark Performance</h4>
          <div className="benchmark-grid">
            <div className="benchmark-item">
              <span className="benchmark-label">Portfolio</span>
              <span className="benchmark-return" style={{ 
                color: getPerformanceColor(benchmarks.portfolio_performance.return_percent) 
              }}>
                {benchmarks.portfolio_performance.return_percent}%
              </span>
            </div>
            <div className="benchmark-item">
              <span className="benchmark-label">vs BTC Only</span>
              <span className="benchmark-return" style={{ 
                color: getPerformanceColor(benchmarks.btc_benchmark.outperformance) 
              }}>
                {benchmarks.btc_benchmark.outperformance > 0 ? '+' : ''}
                {benchmarks.btc_benchmark.outperformance}%
              </span>
            </div>
            <div className="benchmark-item">
              <span className="benchmark-label">vs ETH Only</span>
              <span className="benchmark-return" style={{ 
                color: getPerformanceColor(benchmarks.eth_benchmark.outperformance) 
              }}>
                {benchmarks.eth_benchmark.outperformance > 0 ? '+' : ''}
                {benchmarks.eth_benchmark.outperformance}%
              </span>
            </div>
            <div className="benchmark-item">
              <span className="benchmark-label">vs 50/50 Mix</span>
              <span className="benchmark-return" style={{ 
                color: getPerformanceColor(benchmarks.balanced_benchmark.outperformance) 
              }}>
                {benchmarks.balanced_benchmark.outperformance > 0 ? '+' : ''}
                {benchmarks.balanced_benchmark.outperformance}%
              </span>
            </div>
          </div>
        </div>

        {/* Enhanced Insights Section */}
        {insights && (
          <>
            {/* Cryptocurrency Performance Comparison */}
            <div className="analytics-card coin-performance">
              <h4>🏆 Cryptocurrency Performance</h4>
              <div className="performance-comparison">
                <div className="performer best-performer">
                  <span className="performer-label">🥇 Best Performer</span>
                  <div className="performer-details">
                    <span className="coin-name">{insights.coin_performance.best_performer.coin}</span>
                    <span className="return-value" style={{ color: '#28a745' }}>
                      +{insights.coin_performance.best_performer.return_percent}%
                    </span>
                    <span className="profit-amount">
                      +${insights.coin_performance.best_performer.profit_amount}
                    </span>
                  </div>
                </div>
                <div className="performer worst-performer">
                  <span className="performer-label">🥈 Runner Up</span>
                  <div className="performer-details">
                    <span className="coin-name">{insights.coin_performance.worst_performer.coin}</span>
                    <span className="return-value" style={{ color: '#28a745' }}>
                      +{insights.coin_performance.worst_performer.return_percent}%
                    </span>
                    <span className="profit-amount">
                      +${insights.coin_performance.worst_performer.profit_amount}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Time-based Performance Analysis */}
            <div className="analytics-card time-analysis">
              <h4>📅 Time Performance Analysis</h4>
              <div className="time-metrics">
                <div className="time-metric">
                  <span className="time-label">🎯 Best Day</span>
                  <div className="time-details">
                    <span className="time-date">{insights.time_analysis.best_day.date}</span>
                    <span className="time-return" style={{ color: '#28a745' }}>
                      +{insights.time_analysis.best_day.return_percent}%
                    </span>
                    <span className="time-amount">+${insights.time_analysis.best_day.profit_amount}</span>
                    <span className="time-reason">{insights.time_analysis.best_day.reason}</span>
                  </div>
                </div>
                <div className="time-metric">
                  <span className="time-label">📉 Worst Day</span>
                  <div className="time-details">
                    <span className="time-date">{insights.time_analysis.worst_day.date}</span>
                    <span className="time-return" style={{ color: '#dc3545' }}>
                      {insights.time_analysis.worst_day.return_percent}%
                    </span>
                    <span className="time-amount">${insights.time_analysis.worst_day.loss_amount}</span>
                    <span className="time-reason">{insights.time_analysis.worst_day.reason}</span>
                  </div>
                </div>
                <div className="time-metric">
                  <span className="time-label">🔥 Current Streak</span>
                  <div className="time-details">
                    <span className="streak-type">{insights.time_analysis.current_streak.days} days {insights.time_analysis.current_streak.type}</span>
                    <span className="time-return" style={{ color: '#28a745' }}>
                      +{insights.time_analysis.current_streak.return_percent}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Investment Efficiency */}
            <div className="analytics-card investment-efficiency">
              <h4>💡 Investment Efficiency</h4>
              <div className="efficiency-grid">
                <div className="efficiency-item">
                  <span className="efficiency-label">BTC Avg Buy Price</span>
                  <span className="efficiency-value">${insights.investment_efficiency.avg_buy_price_btc.toLocaleString()}</span>
                  <span className="efficiency-improvement" style={{ color: '#28a745' }}>
                    +{insights.investment_efficiency.price_improvement}% vs current
                  </span>
                </div>
                <div className="efficiency-item">
                  <span className="efficiency-label">ETH Avg Buy Price</span>
                  <span className="efficiency-value">${insights.investment_efficiency.avg_buy_price_eth.toLocaleString()}</span>
                  <span className="efficiency-improvement" style={{ color: '#28a745' }}>
                    +{insights.investment_efficiency.eth_price_improvement}% vs current
                  </span>
                </div>
                <div className="efficiency-item">
                  <span className="efficiency-label">Cost Averaging Score</span>
                  <span className="efficiency-value">{insights.investment_efficiency.cost_average_score}/10</span>
                  <span className="efficiency-note">Excellent timing</span>
                </div>
                <div className="efficiency-item">
                  <span className="efficiency-label">Market Timing Score</span>
                  <span className="efficiency-value">{insights.investment_efficiency.timing_score}/10</span>
                  <span className="efficiency-note">Good entry points</span>
                </div>
              </div>
            </div>

            {/* Smart Recommendations */}
            <div className="analytics-card recommendations">
              <h4>🎯 Smart Recommendations</h4>
              <div className="recommendations-list">
                {insights.recommendations.map((rec, index) => (
                  <div key={index} className={`recommendation-item ${rec.type}`}>
                    <div className="recommendation-header">
                      <span className="rec-type">
                        {rec.type === 'rebalance' ? '⚖️' : rec.type === 'opportunity' ? '🚀' : '⚠️'}
                        {rec.type.charAt(0).toUpperCase() + rec.type.slice(1)}
                      </span>
                    </div>
                    <div className="recommendation-content">
                      <p className="rec-message">{rec.message}</p>
                      <p className="rec-action"><strong>Action:</strong> {rec.action}</p>
                      <p className="rec-impact"><strong>Impact:</strong> {rec.impact}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>

      <div className="analytics-footer">
        <p className="disclaimer">
          📊 Analytics calculated using {analytics.performance_metrics.days_tracked} days of portfolio data. 
          Risk metrics are estimates and past performance doesn't guarantee future results.
        </p>
      </div>
    </div>
  );
};

export default AdvancedAnalytics;