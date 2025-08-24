import React from 'react';
import StatCard from '../components/StatCard';
import './Portfolio.css';
import { FaSync, FaWallet } from 'react-icons/fa';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

function Portfolio({ data, onRefresh }) {
  if (!data) return <div className="spinner"></div>;

  // Prepare chart data
  const chartData = [
    {
      name: 'BTC',
      Invested: data.btc_invested,
      Value: data.btc_value,
    },
    {
      name: 'ETH',
      Invested: data.eth_invested,
      Value: data.eth_value,
    },
  ];

  return (
    <div>
      <div className="section-header">
        <h2 className="section-title">
          <FaWallet style={{ marginRight: '0.5rem' }} />
          Crypto Portfolio Overview
        </h2>
        <button 
          onClick={onRefresh} 
          className="btn btn-success btn-sm"
        >
          <FaSync />
          Refresh Portfolio
        </button>
      </div>

      <div className="stats-grid">
        <StatCard label="BTC Invested" value={data.btc_invested} prefix="$" type="neutral" />
        <StatCard label="ETH Invested" value={data.eth_invested} prefix="$" type="neutral" />
        <StatCard label="BTC Held" value={data.btc_held} type="neutral" />
        <StatCard label="ETH Held" value={data.eth_held} type="neutral" />
        <StatCard label="BTC Value" value={data.btc_value} type="neutral" />
        <StatCard label="ETH Value" value={data.eth_value} type="neutral" />
        <StatCard label="Total Invested" value={data.total_invested} prefix="$" type="neutral" />
        <StatCard label="Total Value" value={data.total_value} prefix="$" type="neutral" />
        <StatCard
          label="Profit/Loss"
          value={data.profit_loss}
          prefix="$"
          type={data.profit_loss >= 0 ? 'positive' : 'negative'}
        />
        <StatCard
          label="BTC % Change"
          value={data.btc_percent_change}
          suffix="%"
          type={data.btc_percent_change >= 0 ? 'positive' : 'negative'}
        />
        <StatCard
          label="ETH % Change"
          value={data.eth_percent_change}
          suffix="%"
          type={data.eth_percent_change >= 0 ? 'positive' : 'negative'}
        />
        <StatCard
          label="Total % Change"
          value={data.total_percent_change}
          suffix="%"
          type={data.total_percent_change >= 0 ? 'positive' : 'negative'}
        />
      </div>

      {/* Bar Chart for Investment vs Current Value */}
      <div style={{ marginTop: '2rem' }}>
        <h3 className="chart-title">Investment vs Current Value</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="Invested" fill="var(--primary-color)" />
            <Bar dataKey="Value" fill="var(--success-color)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Portfolio;
