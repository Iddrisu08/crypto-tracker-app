import React, { useState } from 'react';
import { FaDownload, FaSpinner } from 'react-icons/fa';
import { downloadPortfolioCSV, downloadTransactionsCSV, downloadHistoryCSV } from '../api';
import './CSVExporter.css';

const CSVExporter = () => {
  const [loading, setLoading] = useState({});

  const handleExport = async (type, downloadFunc, params = null) => {
    setLoading(prev => ({ ...prev, [type]: true }));
    
    try {
      if (params) {
        await downloadFunc(...params);
      } else {
        await downloadFunc();
      }
    } catch (error) {
      console.error(`Error exporting ${type}:`, error);
      alert(`Failed to export ${type}. Please try again.`);
    } finally {
      setLoading(prev => ({ ...prev, [type]: false }));
    }
  };

  const exportOptions = [
    {
      key: 'portfolio',
      label: 'Portfolio Summary',
      description: 'Current holdings, investments, and P&L',
      action: () => handleExport('portfolio', downloadPortfolioCSV)
    },
    {
      key: 'transactions',
      label: 'Transaction History',
      description: 'All manual buy/sell transactions',
      action: () => handleExport('transactions', downloadTransactionsCSV)
    },
    {
      key: 'history30',
      label: '30-Day History',
      description: 'Portfolio value over last 30 days',
      action: () => handleExport('history30', downloadHistoryCSV, [30])
    },
    {
      key: 'history90',
      label: '90-Day History',
      description: 'Portfolio value over last 90 days',
      action: () => handleExport('history90', downloadHistoryCSV, [90])
    },
    {
      key: 'history365',
      label: 'Full Year History',
      description: 'Portfolio value over last 365 days',
      action: () => handleExport('history365', downloadHistoryCSV, [365])
    }
  ];

  return (
    <div className="csv-exporter">
      <div className="csv-exporter-header">
        <h3>Export Data</h3>
        <p>Download your portfolio data as CSV files for spreadsheet analysis</p>
      </div>
      
      <div className="export-grid">
        {exportOptions.map(option => (
          <div key={option.key} className="export-option">
            <div className="export-info">
              <h4>{option.label}</h4>
              <p>{option.description}</p>
            </div>
            <button
              onClick={option.action}
              disabled={loading[option.key]}
              className={`export-btn ${loading[option.key] ? 'loading' : ''}`}
            >
              {loading[option.key] ? (
                <FaSpinner className="fa-spin" />
              ) : (
                <FaDownload />
              )}
              {loading[option.key] ? 'Exporting...' : 'Download CSV'}
            </button>
          </div>
        ))}
      </div>
      
      <div className="export-note">
        <p><strong>Note:</strong> CSV files can be opened in Excel, Google Sheets, or any spreadsheet application.</p>
      </div>
    </div>
  );
};

export default CSVExporter;