import React from 'react';
import { FaBitcoin, FaEthereum, FaPlus, FaMinus } from 'react-icons/fa';

function TransactionHistory({ data: transactions, onRefresh }) {
  if (!transactions || !transactions.length) return <p>No manual transactions found.</p>;

  const getTransactionIcon = (type) => {
    return type === 'buy' ? 
      <FaPlus style={{ color: '#28a745', marginRight: '4px' }} /> : 
      <FaMinus style={{ color: '#dc3545', marginRight: '4px' }} />;
  };

  const getCoinIcon = (coin) => {
    return coin === 'bitcoin' ? 
      <FaBitcoin style={{ color: '#f7931a', marginRight: '4px' }} /> : 
      <FaEthereum style={{ color: '#627eea', marginRight: '4px' }} />;
  };

  const formatCoinName = (coin) => {
    return coin.charAt(0).toUpperCase() + coin.slice(1);
  };

  const formatAmount = (amount, coin) => {
    const decimals = coin === 'bitcoin' ? 8 : 6;
    return parseFloat(amount).toFixed(decimals);
  };

  const formatPrice = (price) => {
    return parseFloat(price).toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  const getTransactionValue = (amount, price) => {
    return (parseFloat(amount) * parseFloat(price)).toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  return (
    <div className="fade-in">
      <h2>Transaction History</h2>
      
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

      <div className="table-container">
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Date</th>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Type</th>
              <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>Coin</th>
              <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #e2e8f0' }}>Amount</th>
              <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #e2e8f0' }}>Price (USD)</th>
              <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #e2e8f0' }}>Value (USD)</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx, index) => (
              <tr key={index} style={{ borderBottom: '1px solid #e2e8f0' }}>
                <td style={{ padding: '12px' }}>{tx.date}</td>
                <td style={{ padding: '12px' }}>
                  <span style={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    color: tx.type === 'buy' ? '#28a745' : '#dc3545',
                    fontWeight: '600'
                  }}>
                    {getTransactionIcon(tx.type || 'buy')}
                    {(tx.type || 'buy').toUpperCase()}
                  </span>
                </td>
                <td style={{ padding: '12px' }}>
                  <span style={{ display: 'flex', alignItems: 'center' }}>
                    {getCoinIcon(tx.coin)}
                    {formatCoinName(tx.coin)}
                  </span>
                </td>
                <td style={{ padding: '12px', textAlign: 'right', fontFamily: 'monospace' }}>
                  {formatAmount(tx.amount, tx.coin)}
                </td>
                <td style={{ padding: '12px', textAlign: 'right', fontFamily: 'monospace' }}>
                  {formatPrice(tx.price)}
                </td>
                <td style={{ 
                  padding: '12px', 
                  textAlign: 'right', 
                  fontFamily: 'monospace',
                  fontWeight: '600',
                  color: tx.type === 'buy' ? '#28a745' : '#dc3545'
                }}>
                  {getTransactionValue(tx.amount, tx.price)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TransactionHistory;
