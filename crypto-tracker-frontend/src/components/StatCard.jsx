import React, { useState, useEffect, useRef } from 'react';
import { FaBitcoin, FaEthereum, FaChartLine, FaPercentage } from 'react-icons/fa';
import './StatCard.css';

function StatCard({ label, value, prefix = '', suffix = '', icon = null, type = 'neutral' }) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [displayValue, setDisplayValue] = useState(value);
  const prevValueRef = useRef(value);

  // Detect value changes and trigger animation
  useEffect(() => {
    if (prevValueRef.current !== value) {
      setIsUpdating(true);
      const timer = setTimeout(() => {
        setDisplayValue(value);
        setIsUpdating(false);
      }, 300);
      
      prevValueRef.current = value;
      return () => clearTimeout(timer);
    }
  }, [value]);

  // Determine card type based on label and value
  const getCardType = () => {
    if (type !== 'neutral') return type;
    
    const lowerLabel = label.toLowerCase();
    if (lowerLabel.includes('profit') || lowerLabel.includes('loss')) {
      return value >= 0 ? 'positive' : 'negative';
    }
    if (lowerLabel.includes('change') && lowerLabel.includes('%')) {
      return value >= 0 ? 'positive' : 'negative';
    }
    return 'neutral';
  };

  // Get appropriate icon based on label
  const getIcon = () => {
    if (icon) return icon;
    
    const lowerLabel = label.toLowerCase();
    if (lowerLabel.includes('btc') || lowerLabel.includes('bitcoin')) {
      return <FaBitcoin className="bitcoin" />;
    }
    if (lowerLabel.includes('eth') || lowerLabel.includes('ethereum')) {
      return <FaEthereum className="ethereum" />;
    }
    if (lowerLabel.includes('%') || lowerLabel.includes('percent')) {
      return <FaPercentage />;
    }
    return <FaChartLine />;
  };

  // Format value for display
  const formatValue = (val) => {
    if (typeof val === 'number') {
      if (prefix === '$') {
        return val.toLocaleString('en-US', { 
          minimumFractionDigits: 2, 
          maximumFractionDigits: 2 
        });
      }
      if (suffix === '%') {
        return val.toFixed(2);
      }
      return val.toLocaleString();
    }
    return val;
  };

  const cardType = getCardType();

  return (
    <div className={`stat-card ${cardType} fade-in`}>
      <div className="stat-icon-label">
        <span className="stat-icon">
          {getIcon()}
        </span>
        <p className="stat-label">{label}</p>
      </div>
      <h3 className={`stat-value ${isUpdating ? 'updating' : ''}`}>
        {prefix}{formatValue(displayValue)}{suffix}
      </h3>
    </div>
  );
}

export default StatCard;
