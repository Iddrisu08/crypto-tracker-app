// DailyStatCard.jsx
import React from 'react';
import './DailyStatCard.css';

function DailyStatCard({ label, value, timestamp }) {
  const color = value >= 0 ? 'green' : 'red';
  const prefix = value >= 0 ? '+' : '';

  return (
    <div className="daily-stat-card">
      <p className="card-label">{label}</p>
      <h3 className="card-value" style={{ color }}>
        {prefix}${value}
      </h3>
      {timestamp && (
        <p className="card-timestamp">{timestamp}</p>
      )}
    </div>
  );
}

export default DailyStatCard;
