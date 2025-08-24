import React from 'react';
import StatCard from './StatCard';
import './LiveStats.css';
import { FaSync } from 'react-icons/fa';

function LiveStats({ data: stats, onRefresh }) {
  if (!stats) return <div className="spinner"></div>;

  return (
    <div>
      <div className="section-header">
        <h2 className="section-title">Live Profit/Loss (Real-time)</h2>
        <button 
          onClick={onRefresh} 
          className="btn btn-success btn-sm"
        >
          <FaSync />
          Refresh Live Data
        </button>
      </div>

      <div className="stats-grid">
        <StatCard
          label="BTC Profit/Loss"
          value={stats.profit_btc}
          prefix="$"
          type={stats.profit_btc >= 0 ? 'positive' : 'negative'}
        />
        <StatCard
          label="ETH Profit/Loss"
          value={stats.profit_eth}
          prefix="$"
          type={stats.profit_eth >= 0 ? 'positive' : 'negative'}
        />
        <StatCard
          label="Total Profit/Loss"
          value={stats.profit_total}
          prefix="$"
          type={stats.profit_total >= 0 ? 'positive' : 'negative'}
        />
        <StatCard
          label="Total Profit/Loss %"
          value={stats.profit_percent}
          suffix="%"
          type={stats.profit_percent >= 0 ? 'positive' : 'negative'}
        />
      </div>
    </div>
  );
}

export default LiveStats;
