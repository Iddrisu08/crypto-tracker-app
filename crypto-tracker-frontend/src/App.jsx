import React, { useState, useEffect, useCallback } from 'react';
import Portfolio from './pages/Portfolio';
import PortfolioChart from './components/PortfolioChart';
import TransactionHistory from './components/TransactionHistory';
import DailyProfitLoss from './components/DailyProfitLoss';
import LiveStats from './components/LiveStats';
import AddTransaction from './components/AddTransaction';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import AnalyticsDashboardSimple from './components/AnalyticsDashboardSimple';
import CSVExporter from './components/CSVExporter';
import PriceAlerts from './components/PriceAlerts';
import AdvancedAnalytics from './components/AdvancedAnalytics';
import PWAInstallPrompt, { OfflineIndicator } from './components/PWAInstallPrompt';
import { ToastProvider } from './components/Toast';
import ErrorBoundary, { SectionErrorBoundary } from './components/ErrorBoundary';
import { PortfolioSkeleton, ChartSkeleton, AnalyticsSkeleton } from './components/SkeletonLoader';
// import SimpleEnhancedAnalytics from './components/SimpleEnhancedAnalytics';
// import PortfolioAllocation from './components/PortfolioAllocation';
import { fetchPortfolio, fetchLiveProfitLoss, fetchDailyProfitLoss, fetchTransactions, fetchPortfolioHistory } from './api';
import { FaBitcoin, FaEthereum, FaSun, FaMoon, FaSync } from 'react-icons/fa';
import './App.css';

function App() {
  const [portfolioData, setPortfolioData] = useState(null);
  const [liveStatsData, setLiveStatsData] = useState(null);
  const [dailyProfitData, setDailyProfitData] = useState(null);
  const [transactionsData, setTransactionsData] = useState(null);
  const [portfolioHistoryData, setPortfolioHistoryData] = useState(null);
  const [currentPrices, setCurrentPrices] = useState({ btc: 0, eth: 0 });
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Toggle dark mode
  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', JSON.stringify(newMode));
    document.documentElement.setAttribute('data-theme', newMode ? 'dark' : 'light');
  };

  // Set theme on mount
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  // Extract current prices from portfolio data
  useEffect(() => {
    if (portfolioData) {
      const btcPrice = portfolioData.btc_held > 0 ? portfolioData.btc_value / portfolioData.btc_held : 0;
      const ethPrice = portfolioData.eth_held > 0 ? portfolioData.eth_value / portfolioData.eth_held : 0;
      setCurrentPrices({ btc: btcPrice, eth: ethPrice });
    }
  }, [portfolioData]);

  // Global refresh function that updates all data
  const refreshAllData = useCallback(async () => {
    setIsRefreshing(true);
    setLoading(true);
    try {
      const [portfolio, liveStats, dailyProfit, transactions, portfolioHistory] = await Promise.all([
        fetchPortfolio(),
        fetchLiveProfitLoss(),
        fetchDailyProfitLoss(),
        fetchTransactions(),
        fetchPortfolioHistory()
      ]);
      
      setPortfolioData(portfolio);
      setLiveStatsData(liveStats);
      setDailyProfitData(dailyProfit);
      setTransactionsData(transactions);
      setPortfolioHistoryData(portfolioHistory);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  // Load all data when app first mounts
  useEffect(() => {
    refreshAllData();
    
    // Set up automatic refresh every 5 minutes for more real-time data
    const interval = setInterval(() => {
      refreshAllData();
    }, 300000); // 5 minutes

    return () => clearInterval(interval);
  }, [refreshAllData]);

  if (loading && !portfolioData) {
    return (
      <ToastProvider>
        <div className="App">
          <OfflineIndicator />
          
          {/* Header Skeleton - matches real header structure */}
          <header className="app-header">
            <div className="header-content">
              <h1 className="app-title">Crypto Investment Tracker</h1>
              <div className="header-controls">
                <div className="current-prices">
                  <div className="price-item">
                    <span style={{ color: '#f7931a' }}>₿</span>
                    <span className="price-value">$---,---</span>
                  </div>
                  <div className="price-item">
                    <span style={{ color: '#627eea' }}>Ξ</span>
                    <span className="price-value">$---,---</span>
                  </div>
                </div>
                <button className="btn btn-primary global-refresh" disabled>
                  <FaSync />
                  Loading...
                </button>
                <button className="theme-toggle" disabled>
                  {darkMode ? <FaSun /> : <FaMoon />}
                </button>
              </div>
            </div>
          </header>

          {/* Main Content Skeleton */}
          <main className="main-content">
            <section className="section fade-in">
              <PortfolioSkeleton />
            </section>
            <section className="section fade-in">
              <ChartSkeleton />
            </section>
            <section className="section fade-in">
              <AnalyticsSkeleton />
            </section>
          </main>
        </div>
      </ToastProvider>
    );
  }

  return (
    <ErrorBoundary>
      <ToastProvider>
        <div className="App">
      {/* PWA Components */}
      <OfflineIndicator />
      <PWAInstallPrompt />
      
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">Crypto Investment Tracker</h1>
          
          <div className="header-controls">
            {/* Current Prices */}
            <div className="current-prices">
              <div className="price-item">
                <FaBitcoin className="price-icon" style={{ color: '#f7931a' }} />
                <span className="price-value">${currentPrices.btc.toLocaleString()}</span>
              </div>
              <div className="price-item">
                <FaEthereum className="price-icon" style={{ color: '#627eea' }} />
                <span className="price-value">${currentPrices.eth.toLocaleString()}</span>
              </div>
            </div>

            {/* Global Refresh Button */}
            <button 
              onClick={refreshAllData} 
              className={`btn btn-primary global-refresh ${isRefreshing ? 'pulse' : ''}`}
              disabled={isRefreshing}
            >
              <FaSync className={isRefreshing ? 'fa-spin' : ''} />
              {isRefreshing ? 'Refreshing...' : 'Refresh All Data'}
            </button>

            {/* Theme Toggle */}
            <button 
              onClick={toggleDarkMode}
              className="theme-toggle"
              title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {darkMode ? <FaSun /> : <FaMoon />}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Live Stats Section */}
        <SectionErrorBoundary sectionName="Live Stats">
          <section className="section fade-in">
            <LiveStats data={liveStatsData} onRefresh={refreshAllData} />
          </section>
        </SectionErrorBoundary>

        {/* Daily Profit/Loss Section */}
        <SectionErrorBoundary sectionName="Daily Profit/Loss">
          <section className="section fade-in">
            <DailyProfitLoss data={dailyProfitData} onRefresh={refreshAllData} />
          </section>
        </SectionErrorBoundary>

        {/* Portfolio Section */}
        <SectionErrorBoundary sectionName="Portfolio">
          <section className="section fade-in">
            <Portfolio data={portfolioData} onRefresh={refreshAllData} />
          </section>
        </SectionErrorBoundary>

        {/* Enhanced Analytics Section - Temporarily Disabled */}
        {/* 
        <section className="section fade-in">
          <SimpleEnhancedAnalytics />
        </section>

        <section className="section fade-in">
          <PortfolioAllocation />
        </section>
        */}

        {/* Charts Section */}
        <section className="section fade-in">
          <div className="section-header">
            <h2 className="section-title">Historical Charts</h2>
            <button 
              onClick={refreshAllData} 
              className="btn btn-success btn-sm"
              disabled={isRefreshing}
            >
              <FaSync className={isRefreshing ? 'fa-spin' : ''} />
              Refresh Charts
            </button>
          </div>
          <div className="charts-container">
            <div className="chart-section">
              <h3 className="chart-title">Portfolio Value Over Time</h3>
              <PortfolioChart data={portfolioHistoryData} onRefresh={refreshAllData} />
            </div>
            <div className="chart-section">
              <h3 className="chart-title">Profit/Loss Trend</h3>
              <PortfolioChart data={portfolioHistoryData} onRefresh={refreshAllData} />
            </div>
          </div>
        </section>

        {/* Manual Transaction Section */}
        <section className="section fade-in">
          <div className="section-header">
            <h2 className="section-title">Manual Transactions</h2>
            <p className="section-description">
              Add buy/sell transactions to track your manual trades with real-time profit/loss calculations
            </p>
          </div>
          <AddTransaction onRefresh={refreshAllData} />
        </section>

        {/* Transaction History Section */}
        <section className="section fade-in">
          <div className="section-header">
            <h2 className="section-title">Transaction History</h2>
            <button 
              onClick={refreshAllData} 
              className="btn btn-success btn-sm"
              disabled={isRefreshing}
            >
              <FaSync className={isRefreshing ? 'fa-spin' : ''} />
              Refresh History
            </button>
          </div>
          <div className="table-container">
            <TransactionHistory data={transactionsData} onRefresh={refreshAllData} />
          </div>
        </section>

        {/* Price Alerts Section */}
        <section className="section fade-in">
          <PriceAlerts />
        </section>

        {/* Advanced Analytics Section */}
        <SectionErrorBoundary sectionName="Advanced Analytics">
          <section className="section fade-in">
            <AdvancedAnalytics />
          </section>
        </SectionErrorBoundary>

        {/* CSV Export Section */}
        <SectionErrorBoundary sectionName="CSV Export">
          <section className="section fade-in">
            <CSVExporter />
          </section>
        </SectionErrorBoundary>
      </main>
    </div>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
