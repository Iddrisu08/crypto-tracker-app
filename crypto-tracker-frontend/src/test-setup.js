/**
 * TEST SETUP CONFIGURATION
 * Sets up the testing environment for all tests.
 * Configures mocks, polyfills, and global test utilities.
 */

import '@testing-library/jest-dom'
import { expect, afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'

// GLOBAL TEST SETUP
// Clean up DOM after each test
afterEach(() => {
  cleanup()
})

// REACT MOCK SETUP
// Mock React if needed for certain components
global.React = require('react')

// DOM MOCKS
// Mock IntersectionObserver (used by some chart libraries)
global.IntersectionObserver = vi.fn(() => ({
  disconnect: vi.fn(),
  observe: vi.fn(),
  unobserve: vi.fn(),
}))

// Mock ResizeObserver (used by chart libraries)
global.ResizeObserver = vi.fn(() => ({
  disconnect: vi.fn(),
  observe: vi.fn(),
  unobserve: vi.fn(),
}))

// WINDOW MOCKS
// Mock window methods that might be used
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.sessionStorage = sessionStorageMock

// NETWORK MOCKS
// Mock fetch for API calls
global.fetch = vi.fn()

// CHART LIBRARY MOCKS
// Mock Chart.js if used
vi.mock('chart.js', () => ({
  Chart: vi.fn(() => ({
    destroy: vi.fn(),
    update: vi.fn(),
    resize: vi.fn(),
  })),
  registerables: [],
}))

// Mock react-chartjs-2 if used
vi.mock('react-chartjs-2', () => ({
  Line: vi.fn(({ data, options }) => (
    <div data-testid="line-chart" data-chart-data={JSON.stringify(data)}>
      Mock Line Chart
    </div>
  )),
  Bar: vi.fn(({ data, options }) => (
    <div data-testid="bar-chart" data-chart-data={JSON.stringify(data)}>
      Mock Bar Chart
    </div>
  )),
  Pie: vi.fn(({ data, options }) => (
    <div data-testid="pie-chart" data-chart-data={JSON.stringify(data)}>
      Mock Pie Chart
    </div>
  )),
}))

// CRYPTO LIBRARY MOCKS
// Mock any crypto-related libraries if used
vi.mock('crypto-js', () => ({
  SHA256: vi.fn(() => ({
    toString: vi.fn(() => 'mocked-hash')
  }))
}))

// DATE MOCKS
// Mock Date if consistent dates are needed for tests
const mockDate = new Date('2024-01-15T10:00:00Z')
vi.setSystemTime(mockDate)

// CONSOLE MOCKS
// Suppress console warnings in tests (optional)
const originalConsoleError = console.error
const originalConsoleWarn = console.warn

console.error = (...args) => {
  // Suppress React warnings in tests
  if (args[0]?.includes?.('Warning:')) {
    return
  }
  originalConsoleError.call(console, ...args)
}

console.warn = (...args) => {
  // Suppress development warnings in tests
  if (args[0]?.includes?.('Warning:')) {
    return
  }
  originalConsoleWarn.call(console, ...args)
}

// CUSTOM TEST UTILITIES
// Add custom matchers or utilities here
expect.extend({
  toBeWithinRange(received, floor, ceiling) {
    const pass = received >= floor && received <= ceiling
    if (pass) {
      return {
        message: () => `expected ${received} not to be within range ${floor} - ${ceiling}`,
        pass: true,
      }
    } else {
      return {
        message: () => `expected ${received} to be within range ${floor} - ${ceiling}`,
        pass: false,
      }
    }
  },
})

// GLOBAL TEST HELPERS
global.testHelpers = {
  // Helper to create mock user data
  createMockUser: (overrides = {}) => ({
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    ...overrides
  }),
  
  // Helper to create mock transaction data
  createMockTransaction: (overrides = {}) => ({
    id: 1,
    crypto_symbol: 'BTC',
    amount: 0.5,
    price_usd: 45000,
    transaction_type: 'buy',
    timestamp: '2024-01-15T10:00:00Z',
    ...overrides
  }),
  
  // Helper to create mock portfolio data
  createMockPortfolio: (overrides = {}) => ({
    total_value: 47500,
    total_invested: 45000,
    profit_loss: 2500,
    profit_loss_percentage: 5.56,
    holdings: [
      {
        crypto_symbol: 'BTC',
        amount: 0.75,
        current_value: 33750,
        profit_loss: 2250
      }
    ],
    ...overrides
  })
}

// ASYNC TEST HELPERS
global.waitForNextTick = () => new Promise(resolve => setTimeout(resolve, 0))
global.wait = (ms) => new Promise(resolve => setTimeout(resolve, ms))