import {
  ApiResponse,
  User,
  AuthTokens,
  LoginRequest,
  RegisterRequest,
  PortfolioData,
  Transaction,
  TransactionRequest,
  TransactionResponse,
  PerformanceMetrics,
  CurrentPrices,
  ApiConfig,
  ApiError
} from '../types';

class ApiService {
  private config: ApiConfig;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5001';
    this.config = {
      baseURL: this.baseURL,
      timeout: 30000,
      retries: 3
    };
  }

  // Helper method for making requests with enhanced error handling
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const token = this.getAuthToken();
    
    const defaultHeaders: HeadersInit = {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    };

    if (token) {
      defaultHeaders.Authorization = `Bearer ${token}`;
    }

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);
      
      const response = await fetch(url, {
        ...config,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { error: `HTTP ${response.status}: ${response.statusText}` };
        }
        
        const error = new Error(errorData.error || `HTTP ${response.status}`) as ApiError;
        error.status = response.status;
        error.data = errorData;
        throw error;
      }

      // Handle empty responses
      const text = await response.text();
      if (!text) return {} as T;
      
      try {
        return JSON.parse(text) as T;
      } catch {
        return text as unknown as T;
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    }
  }

  // Auth token management
  private getAuthToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private setAuthTokens(tokens: AuthTokens): void {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
  }

  private clearAuthTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  // Authentication endpoints
  async login(credentials: LoginRequest): Promise<{ user: User; tokens: AuthTokens }> {
    const response = await this.makeRequest<{
      user: User;
      access_token: string;
      refresh_token: string;
    }>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    });

    const tokens = {
      access_token: response.access_token,
      refresh_token: response.refresh_token
    };

    this.setAuthTokens(tokens);
    return { user: response.user, tokens };
  }

  async register(data: RegisterRequest): Promise<{ user: User; tokens: AuthTokens }> {
    const response = await this.makeRequest<{
      user: User;
      access_token: string;
      refresh_token: string;
    }>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(data)
    });

    const tokens = {
      access_token: response.access_token,
      refresh_token: response.refresh_token
    };

    this.setAuthTokens(tokens);
    return { user: response.user, tokens };
  }

  async refreshToken(): Promise<AuthTokens> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.makeRequest<{ access_token: string }>('/api/v1/auth/refresh', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${refreshToken}`
      }
    });

    const tokens = {
      access_token: response.access_token,
      refresh_token: refreshToken
    };

    this.setAuthTokens(tokens);
    return tokens;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.makeRequest<{ user: User }>('/api/v1/auth/me');
    return response.user;
  }

  logout(): void {
    this.clearAuthTokens();
  }

  // Portfolio endpoints
  async fetchPortfolio(): Promise<PortfolioData> {
    return this.makeRequest<PortfolioData>('/api/v1/portfolio');
  }

  async fetchPerformanceMetrics(): Promise<PerformanceMetrics> {
    return this.makeRequest<PerformanceMetrics>('/api/v1/performance-metrics');
  }

  // Transaction endpoints
  async fetchTransactions(page = 1, perPage = 20): Promise<TransactionResponse> {
    return this.makeRequest<TransactionResponse>(
      `/api/v1/transactions?page=${page}&per_page=${perPage}`
    );
  }

  async addTransaction(transaction: TransactionRequest): Promise<Transaction> {
    const response = await this.makeRequest<{ transaction: Transaction }>('/api/v1/transactions', {
      method: 'POST',
      body: JSON.stringify(transaction)
    });
    return response.transaction;
  }

  // Legacy endpoints for backward compatibility
  async fetchCurrentPrices(): Promise<CurrentPrices> {
    return this.makeRequest<CurrentPrices>('/current_prices');
  }

  async fetchDailyProfitLoss(): Promise<any> {
    return this.makeRequest<any>('/daily_profit_loss');
  }

  async fetchLiveProfitLoss(): Promise<any> {
    return this.makeRequest<any>('/live_profit_loss');
  }

  async fetchPortfolioHistory(): Promise<any> {
    return this.makeRequest<any>('/portfolio_history?frequency=daily');
  }

  async fetchTransactionAnalysis(): Promise<any> {
    return this.makeRequest<any>('/transaction_analysis');
  }

  // Utility methods
  isAuthenticated(): boolean {
    return !!this.getAuthToken();
  }

  async healthCheck(): Promise<{ status: string; timestamp: string; version: string }> {
    return this.makeRequest<{ status: string; timestamp: string; version: string }>('/api/v1/health');
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Export individual methods for backward compatibility
export const {
  login,
  register,
  logout,
  refreshToken,
  getCurrentUser,
  fetchPortfolio,
  fetchPerformanceMetrics,
  fetchTransactions,
  addTransaction,
  fetchCurrentPrices,
  fetchDailyProfitLoss,
  fetchLiveProfitLoss,
  fetchPortfolioHistory,
  fetchTransactionAnalysis,
  isAuthenticated,
  healthCheck
} = apiService;