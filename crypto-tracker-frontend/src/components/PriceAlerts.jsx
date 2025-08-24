import React, { useState, useEffect } from 'react';
import { FaBell, FaPlus, FaTrash, FaEnvelope, FaSpinner, FaBitcoin, FaEthereum } from 'react-icons/fa';
import { fetchPriceAlerts, createPriceAlert, deletePriceAlert, testEmailAlert } from '../api';
import { useToast } from './Toast';
import './PriceAlerts.css';

const PriceAlerts = () => {
  const { showSuccess, showError, showWarning, showInfo } = useToast();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [testingEmail, setTestingEmail] = useState(false);
  const [newAlert, setNewAlert] = useState({
    coin: 'bitcoin',
    target_price: '',
    condition: 'above',
    email: '',
    description: ''
  });

  // Load alerts on component mount
  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const response = await fetchPriceAlerts();
      setAlerts(response.alerts || []);
    } catch (error) {
      console.error('Error loading price alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAlert = async (e) => {
    e.preventDefault();
    
    if (!newAlert.target_price || !newAlert.email) {
      showWarning('Please fill in all required fields');
      return;
    }

    try {
      setCreating(true);
      const response = await createPriceAlert({
        ...newAlert,
        target_price: parseFloat(newAlert.target_price)
      });
      
      if (response.alert) {
        setAlerts(prev => [...prev, response.alert]);
        setNewAlert({
          coin: 'bitcoin',
          target_price: '',
          condition: 'above',
          email: '',
          description: ''
        });
        setShowForm(false);
        showSuccess('Price alert created successfully!');
      } else {
        showError(response.error || 'Failed to create alert');
      }
    } catch (error) {
      console.error('Error creating alert:', error);
      showError('Failed to create alert. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteAlert = async (alertId) => {
    if (!window.confirm('Are you sure you want to delete this alert?')) {
      return;
    }

    try {
      const response = await deletePriceAlert(alertId);
      if (response.message) {
        setAlerts(prev => prev.filter(alert => alert.id !== alertId));
        showSuccess('Alert deleted successfully');
      } else {
        showError(response.error || 'Failed to delete alert');
      }
    } catch (error) {
      console.error('Error deleting alert:', error);
      showError('Failed to delete alert. Please try again.');
    }
  };

  const handleTestEmail = async () => {
    if (!newAlert.email) {
      showWarning('Please enter an email address first');
      return;
    }

    try {
      setTestingEmail(true);
      const response = await testEmailAlert(newAlert.email);
      if (response.message) {
        showSuccess('Test email sent successfully! Check your inbox.');
      } else {
        showError(response.error || 'Failed to send test email');
      }
    } catch (error) {
      console.error('Error sending test email:', error);
      showError('Failed to send test email. Please check your email configuration.');
    } finally {
      setTestingEmail(false);
    }
  };

  const getCoinIcon = (coin) => {
    return coin === 'bitcoin' ? <FaBitcoin color="#f7931a" /> : <FaEthereum color="#627eea" />;
  };

  const getCoinName = (coin) => {
    return coin === 'bitcoin' ? 'Bitcoin' : 'Ethereum';
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  if (loading) {
    return (
      <div className="price-alerts loading">
        <FaSpinner className="fa-spin" />
        <p>Loading price alerts...</p>
      </div>
    );
  }

  return (
    <div className="price-alerts">
      <div className="price-alerts-header">
        <div className="header-left">
          <FaBell className="header-icon" />
          <div>
            <h3>Price Alerts</h3>
            <p>Get notified when crypto prices hit your targets</p>
          </div>
        </div>
        <button 
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          <FaPlus /> New Alert
        </button>
      </div>

      {showForm && (
        <div className="alert-form-card">
          <h4>Create New Price Alert</h4>
          <form onSubmit={handleCreateAlert} className="alert-form">
            <div className="form-row">
              <div className="form-group">
                <label>Cryptocurrency</label>
                <select
                  value={newAlert.coin}
                  onChange={(e) => setNewAlert(prev => ({ ...prev, coin: e.target.value }))}
                  required
                >
                  <option value="bitcoin">Bitcoin (BTC)</option>
                  <option value="ethereum">Ethereum (ETH)</option>
                </select>
              </div>

              <div className="form-group">
                <label>Condition</label>
                <select
                  value={newAlert.condition}
                  onChange={(e) => setNewAlert(prev => ({ ...prev, condition: e.target.value }))}
                  required
                >
                  <option value="above">Price Goes Above</option>
                  <option value="below">Price Goes Below</option>
                </select>
              </div>

              <div className="form-group">
                <label>Target Price ($)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={newAlert.target_price}
                  onChange={(e) => setNewAlert(prev => ({ ...prev, target_price: e.target.value }))}
                  placeholder="Enter target price"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Email Address *</label>
                <div className="email-input-group">
                  <input
                    type="email"
                    value={newAlert.email}
                    onChange={(e) => setNewAlert(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="your@email.com"
                    required
                  />
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={handleTestEmail}
                    disabled={testingEmail || !newAlert.email}
                  >
                    {testingEmail ? <FaSpinner className="fa-spin" /> : <FaEnvelope />}
                    Test
                  </button>
                </div>
              </div>
            </div>

            <div className="form-group">
              <label>Description (Optional)</label>
              <input
                type="text"
                value={newAlert.description}
                onChange={(e) => setNewAlert(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Optional description for this alert"
              />
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowForm(false)}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={creating}
              >
                {creating ? <FaSpinner className="fa-spin" /> : <FaPlus />}
                {creating ? 'Creating...' : 'Create Alert'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="alerts-list">
        {alerts.length === 0 ? (
          <div className="no-alerts">
            <FaBell size={48} opacity={0.3} />
            <h4>No Price Alerts</h4>
            <p>Create your first alert to get notified when prices change</p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowForm(true)}
            >
              <FaPlus /> Create Alert
            </button>
          </div>
        ) : (
          alerts.map(alert => (
            <div key={alert.id} className="alert-card">
              <div className="alert-info">
                <div className="alert-header">
                  <div className="coin-info">
                    {getCoinIcon(alert.coin)}
                    <span className="coin-name">{getCoinName(alert.coin)}</span>
                  </div>
                  <div className="alert-condition">
                    <span className={`condition ${alert.condition}`}>
                      {alert.condition === 'above' ? '↗' : '↘'} {alert.condition}
                    </span>
                    <span className="target-price">{formatPrice(alert.target_price)}</span>
                  </div>
                </div>
                
                <div className="alert-details">
                  <p className="alert-description">
                    {alert.description || `Notify when ${getCoinName(alert.coin)} goes ${alert.condition} ${formatPrice(alert.target_price)}`}
                  </p>
                  <div className="alert-meta">
                    <span>📧 {alert.email}</span>
                    <span>📅 {new Date(alert.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
              
              <button
                className="delete-btn"
                onClick={() => handleDeleteAlert(alert.id)}
                title="Delete Alert"
              >
                <FaTrash />
              </button>
            </div>
          ))
        )}
      </div>

      <div className="alert-info-note">
        <p><strong>📧 Email Configuration Required:</strong> Price alerts require email configuration in your environment. Set the following environment variables:</p>
        <code>EMAIL_ALERTS_ENABLED=true, EMAIL_USER, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT</code>
      </div>
    </div>
  );
};

export default PriceAlerts;