import React from 'react';
import DailyStatCard from './DailyStatCard';
import './DailyProfitLoss.css';
import { FaSync, FaClock } from 'react-icons/fa';

function DailyProfitLoss({ data, onRefresh }) {
  if (!data) return <div className="spinner"></div>;
  if (data.error) return <p>Error fetching data: {data.error}</p>;

  return (
    <div>
      <div className="section-header">
        <h2 className="section-title">
          <FaClock style={{ marginRight: '0.5rem' }} />
          Daily Profit/Loss (24h Change)
        </h2>
        <button 
          onClick={onRefresh} 
          className="btn btn-success btn-sm"
        >
          <FaSync />
          Refresh Daily Data
        </button>
      </div>

      <div className="stats-grid">
        <DailyStatCard
          label="Bitcoin Daily Change"
          value={data.btc_daily_change}
          timestamp={`${data.timestamp_yesterday} → ${data.timestamp_today}`}
        />
        <DailyStatCard
          label="Ethereum Daily Change"
          value={data.eth_daily_change}
          timestamp={`${data.timestamp_yesterday} → ${data.timestamp_today}`}
        />
        <DailyStatCard
          label="Total Daily Change"
          value={data.total_daily_change}
          timestamp={`${data.timestamp_yesterday} → ${data.timestamp_today}`}
        />
      </div>
    </div>
  );
}

export default DailyProfitLoss;
