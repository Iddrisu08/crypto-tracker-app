import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import {
  PortfolioState,
  PortfolioData,
  PerformanceMetrics,
  Transaction,
  TransactionRequest,
  CurrentPrices
} from '../types';
import { apiService } from '../services/api';

interface PortfolioStore extends PortfolioState {
  // Actions
  refreshPortfolio: () => Promise<void>;
  refreshMetrics: () => Promise<void>;
  refreshPrices: () => Promise<void>;
  refreshTransactions: () => Promise<void>;
  addTransaction: (transaction: TransactionRequest) => Promise<void>;
  refreshAll: () => Promise<void>;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

export const usePortfolioStore = create<PortfolioStore>()(
  subscribeWithSelector(
    (set, get) => ({
      // Initial state
      data: null,
      metrics: null,
      transactions: [],
      currentPrices: null,
      loading: false,
      error: null,
      lastUpdated: null,

      // Actions
      refreshPortfolio: async () => {
        set({ loading: true, error: null });
        try {
          const data = await apiService.fetchPortfolio();
          set({
            data,
            loading: false,
            lastUpdated: new Date().toISOString()
          });
        } catch (error) {
          set({
            loading: false,
            error: error instanceof Error ? error.message : 'Failed to load portfolio'
          });
          throw error;
        }
      },

      refreshMetrics: async () => {
        try {
          const metrics = await apiService.fetchPerformanceMetrics();
          set({ metrics });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to load metrics'
          });
          throw error;
        }
      },

      refreshPrices: async () => {
        try {
          const currentPrices = await apiService.fetchCurrentPrices();
          set({ currentPrices });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to load prices'
          });
          throw error;
        }
      },

      refreshTransactions: async () => {
        try {
          const response = await apiService.fetchTransactions(1, 100);
          set({ transactions: response.transactions });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to load transactions'
          });
          throw error;
        }
      },

      addTransaction: async (transaction: TransactionRequest) => {
        set({ loading: true, error: null });
        try {
          const newTransaction = await apiService.addTransaction(transaction);
          
          // Add to local state
          set(state => ({
            transactions: [newTransaction, ...state.transactions],
            loading: false
          }));

          // Refresh portfolio data after adding transaction
          await get().refreshPortfolio();
          await get().refreshMetrics();
        } catch (error) {
          set({
            loading: false,
            error: error instanceof Error ? error.message : 'Failed to add transaction'
          });
          throw error;
        }
      },

      refreshAll: async () => {
        set({ loading: true, error: null });
        try {
          await Promise.all([
            get().refreshPortfolio(),
            get().refreshMetrics(),
            get().refreshPrices(),
            get().refreshTransactions()
          ]);
          set({ loading: false });
        } catch (error) {
          set({
            loading: false,
            error: error instanceof Error ? error.message : 'Failed to refresh data'
          });
          throw error;
        }
      },

      clearError: () => {
        set({ error: null });
      },

      setLoading: (loading: boolean) => {
        set({ loading });
      }
    })
  )
);

// Auto-refresh functionality
let refreshInterval: NodeJS.Timeout | null = null;

export const startAutoRefresh = (intervalMs = 60000) => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
  
  refreshInterval = setInterval(() => {
    const store = usePortfolioStore.getState();
    if (!store.loading) {
      store.refreshPrices().catch(console.error);
    }
  }, intervalMs);
};

export const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
};