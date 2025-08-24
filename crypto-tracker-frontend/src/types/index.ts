// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
  status?: number;
}

// User Types
export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
  is_active: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

// Portfolio Types
export interface PortfolioData {
  btc_invested: number;
  eth_invested: number;
  btc_held: number;
  eth_held: number;
  btc_value: number;
  eth_value: number;
  total_invested: number;
  total_value: number;
  profit_loss: number;
  btc_percent_change: number;
  eth_percent_change: number;
  total_percent_change: number;
  last_updated: string;
}

// Transaction Types
export interface Transaction {
  id: number;
  coin: 'bitcoin' | 'ethereum';
  type: 'buy' | 'sell';
  amount: number;
  price_usd: number;
  total_value_usd: number;
  transaction_date: string;
  created_at: string;
}

export interface TransactionRequest {
  coin: 'bitcoin' | 'ethereum';
  type: 'buy' | 'sell';
  amount: number;
  price: number;
  date: string;
}

export interface TransactionResponse {
  transactions: Transaction[];
  total: number;
  pages: number;
  current_page: number;
  per_page: number;
}

// Performance Metrics Types
export interface TotalMetrics {
  invested: number;
  current_value: number;
  profit_loss: number;
  roi_percent: number;
  annualized_return: number;
  days_invested: number;
}

export interface CryptoMetrics {
  invested: number;
  current_value: number;
  profit_loss: number;
  roi_percent: number;
  holdings: number;
  avg_purchase_price: number;
  current_price: number;
  allocation_percent: number;
}

export interface DCAAnalysis {
  dca_vs_lump_sum_percent: number;
  total_weeks_invested: number;
  weekly_avg_investment: number;
}

export interface PerformancePeriod {
  date: string;
  return_percent: number;
}

export interface PerformancePeriods {
  best_week: PerformancePeriod;
  worst_week: PerformancePeriod;
}

export interface PerformanceMetrics {
  total_metrics: TotalMetrics;
  btc_metrics: CryptoMetrics;
  eth_metrics: CryptoMetrics;
  dca_analysis: DCAAnalysis;
  performance_periods: PerformancePeriods;
}

// Price Types
export interface CurrentPrices {
  bitcoin: number;
  ethereum: number;
}

// Chart Types
export interface ChartDataPoint {
  date: string;
  value: number;
  invested?: number;
  profit_loss?: number;
}

// Component Props Types
export interface LoadingState {
  loading: boolean;
  error: string | null;
}

export interface RefreshableComponent {
  onRefresh?: () => void;
}

// State Management Types
export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export interface PortfolioState {
  data: PortfolioData | null;
  metrics: PerformanceMetrics | null;
  transactions: Transaction[];
  currentPrices: CurrentPrices | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

// API Configuration
export interface ApiConfig {
  baseURL: string;
  timeout: number;
  retries: number;
}

// Error Types
export interface ApiError extends Error {
  status?: number;
  data?: any;
}

// Hook Return Types
export interface UseApiReturn<T> extends LoadingState {
  data: T | null;
  refetch: () => Promise<void>;
}

export interface UseAuthReturn extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export interface UsePortfolioReturn extends PortfolioState {
  refreshPortfolio: () => Promise<void>;
  refreshMetrics: () => Promise<void>;
  refreshPrices: () => Promise<void>;
  addTransaction: (transaction: TransactionRequest) => Promise<void>;
}