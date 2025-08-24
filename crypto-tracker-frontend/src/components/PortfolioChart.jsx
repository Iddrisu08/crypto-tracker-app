import React from 'react';
import LineChart from './LineChart';

function PortfolioChart({ data: portfolioData, onRefresh }) {
  // Handle the API response structure - extract history array
  const history = portfolioData?.history || portfolioData || [];
  
  if (!history || !history.length) return <p>Loading chart...</p>;

  const labels = history.map(item => item.date);
  const values = history.map(item => item.total_value);
  const profitLoss = history.map(item => item.profit_loss);

  return (
    <div>
      <h2>Portfolio Total Value Over Time</h2>
      
      {/* Individual refresh button for this component */}
      <button 
        onClick={onRefresh} 
        style={{ 
          marginBottom: '1rem', 
          padding: '8px 16px',
          backgroundColor: '#28a745',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '14px'
        }}
      >
        🔄 Refresh
      </button>

      <LineChart labels={labels} dataPoints={values} label="Total Value ($)" />

      <h2>Profit / Loss Over Time</h2>
      <LineChart labels={labels} dataPoints={profitLoss} label="Profit/Loss ($)" />
    </div>
  );
}

export default PortfolioChart;
