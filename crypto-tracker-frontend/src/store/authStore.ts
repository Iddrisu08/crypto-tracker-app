import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AuthState, User, AuthTokens, LoginRequest, RegisterRequest } from '../types';
import { apiService } from '../services/api';

interface AuthStore extends AuthState {
  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      tokens: null,
      isAuthenticated: false,
      loading: false,
      error: null,

      // Actions
      login: async (credentials: LoginRequest) => {
        set({ loading: true, error: null });
        try {
          const { user, tokens } = await apiService.login(credentials);
          set({
            user,
            tokens,
            isAuthenticated: true,
            loading: false,
            error: null
          });
        } catch (error) {
          set({
            loading: false,
            error: error instanceof Error ? error.message : 'Login failed',
            isAuthenticated: false
          });
          throw error;
        }
      },

      register: async (data: RegisterRequest) => {
        set({ loading: true, error: null });
        try {
          const { user, tokens } = await apiService.register(data);
          set({
            user,
            tokens,
            isAuthenticated: true,
            loading: false,
            error: null
          });
        } catch (error) {
          set({
            loading: false,
            error: error instanceof Error ? error.message : 'Registration failed',
            isAuthenticated: false
          });
          throw error;
        }
      },

      logout: () => {
        apiService.logout();
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
          loading: false,
          error: null
        });
      },

      refreshToken: async () => {
        try {
          const tokens = await apiService.refreshToken();
          set({ tokens });
        } catch (error) {
          // If refresh fails, logout the user
          get().logout();
          throw error;
        }
      },

      checkAuth: async () => {
        const { tokens } = get();
        if (!tokens?.access_token) {
          set({ isAuthenticated: false });
          return;
        }

        set({ loading: true });
        try {
          const user = await apiService.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            loading: false,
            error: null
          });
        } catch (error) {
          // Try to refresh token
          try {
            await get().refreshToken();
            const user = await apiService.getCurrentUser();
            set({
              user,
              isAuthenticated: true,
              loading: false,
              error: null
            });
          } catch (refreshError) {
            get().logout();
            set({ loading: false });
          }
        }
      },

      clearError: () => {
        set({ error: null });
      }
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);