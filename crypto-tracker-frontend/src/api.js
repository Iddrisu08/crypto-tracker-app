const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5002';

// Helper function to add cache-busting timestamp
const addCacheBuster = (url) => {
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}_t=${Date.now()}`;
};

export async function fetchPortfolio() {
  const res = await fetch(addCacheBuster(`${API_URL}/portfolio`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  return await res.json();
}

export async function addTransaction(transaction) {
  const res = await fetch(`${API_URL}/add_transaction`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(transaction),
  });
  return await res.json();
}

export async function fetchTransactions() {
  const res = await fetch(addCacheBuster(`${API_URL}/transactions`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  return await res.json();
}

export async function fetchDailyProfitLoss() {
  const res = await fetch(addCacheBuster(`${API_URL}/daily_profit_loss`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  return await res.json();
}

export async function fetchLiveProfitLoss() {
  const res = await fetch(addCacheBuster(`${API_URL}/live_profit_loss`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  if (!res.ok) throw new Error('Failed to fetch live profit/loss data');
  return await res.json();
}

export async function fetchPortfolioHistory(period = '30d') {
  const res = await fetch(addCacheBuster(`${API_URL}/portfolio_history?period=${period}`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  return await res.json();
}

// CSV Export functions
export function downloadPortfolioCSV() {
  const url = `${API_URL}/export/portfolio`;
  const link = document.createElement('a');
  link.href = url;
  link.download = `crypto_portfolio_${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export function downloadTransactionsCSV() {
  const url = `${API_URL}/export/transactions`;
  const link = document.createElement('a');
  link.href = url;
  link.download = `crypto_transactions_${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export function downloadHistoryCSV(days = 90) {
  const url = `${API_URL}/export/history?days=${days}`;
  const link = document.createElement('a');
  link.href = url;
  link.download = `crypto_history_${days}days_${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Price Alert functions
export async function fetchPriceAlerts() {
  const res = await fetch(addCacheBuster(`${API_URL}/alerts`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  return await res.json();
}

export async function createPriceAlert(alert) {
  const res = await fetch(`${API_URL}/alerts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(alert),
  });
  return await res.json();
}

export async function deletePriceAlert(alertId) {
  const res = await fetch(`${API_URL}/alerts/${alertId}`, {
    method: 'DELETE',
  });
  return await res.json();
}

export async function testEmailAlert(email) {
  const res = await fetch(`${API_URL}/alerts/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
  return await res.json();
}

export async function fetchCurrentPrices() {
  const res = await fetch(`${API_URL}/current_prices`, {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  if (!res.ok) throw new Error('Failed to fetch current prices');
  return await res.json();
}

export async function fetchTransactionAnalysis() {
  const res = await fetch(addCacheBuster(`${API_URL}/transaction_analysis`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  if (!res.ok) throw new Error('Failed to fetch transaction analysis');
  return await res.json();
}

export async function fetchPerformanceMetrics() {
  const res = await fetch(`${API_URL}/performance_metrics`, {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  if (!res.ok) throw new Error('Failed to fetch performance metrics');
  return await res.json();
}
