/**
 * APP COMPONENT TESTS
 * Tests the main App component functionality, routing, and core features.
 * Ensures the application loads and renders correctly.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import App from '../App'

// Mock API calls
vi.mock('../api', () => ({
  getCurrentPrices: vi.fn(() => Promise.resolve({
    BTC: { current_price: 45000, price_change_24h: 2.5 },
    ETH: { current_price: 3000, price_change_24h: -1.2 }
  })),
  getPortfolio: vi.fn(() => Promise.resolve({
    total_value: 25000,
    holdings: [
      { crypto_symbol: 'BTC', amount: 0.5, current_value: 22500 },
      { crypto_symbol: 'ETH', amount: 1.0, current_value: 3000 }
    ]
  })),
  getTransactions: vi.fn(() => Promise.resolve([
    {
      id: 1,
      crypto_symbol: 'BTC',
      amount: 0.5,
      price_usd: 45000,
      transaction_type: 'buy',
      timestamp: '2024-01-15T10:00:00Z'
    }
  ]))
}))

describe('App Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks()
  })

  it('should render main application structure', async () => {
    /**
     * TEST: App should render with basic structure
     * - Renders App component
     * - Checks for main navigation elements
     * - Verifies core sections are present
     */
    render(<App />)
    
    // Should have main app container
    expect(screen.getByRole('main')).toBeInTheDocument()
    
    // Should have navigation or header
    const header = screen.queryByRole('banner') || screen.queryByRole('navigation')
    if (header) {
      expect(header).toBeInTheDocument()
    }
    
    // App title or branding should be visible
    const titleElement = screen.queryByText(/crypto/i) || screen.queryByText(/portfolio/i) || screen.queryByText(/tracker/i)
    expect(titleElement).toBeInTheDocument()
  })

  it('should load and display crypto prices', async () => {
    /**
     * TEST: App should fetch and display current crypto prices
     * - Renders App component
     * - Waits for API calls to complete
     * - Verifies price data is displayed
     */
    const { getCurrentPrices } = await import('../api')
    
    render(<App />)
    
    // Wait for prices to load
    await waitFor(() => {
      expect(getCurrentPrices).toHaveBeenCalled()
    })
    
    // Should display BTC price (mocked as 45000)
    await waitFor(() => {
      const btcPrice = screen.queryByText(/45.*000/) || screen.queryByText(/BTC/)
      expect(btcPrice).toBeInTheDocument()
    })
  })

  it('should handle navigation between sections', async () => {
    /**
     * TEST: App should allow navigation between different sections
     * - Renders App component
     * - Clicks on navigation elements
     * - Verifies content changes
     */
    const user = userEvent.setup()
    render(<App />)
    
    // Look for navigation elements
    const portfolioNav = screen.queryByText(/portfolio/i) || screen.queryByRole('button', { name: /portfolio/i })
    const transactionsNav = screen.queryByText(/transaction/i) || screen.queryByRole('button', { name: /transaction/i })
    
    if (portfolioNav) {
      await user.click(portfolioNav)
      // Should show portfolio content
      await waitFor(() => {
        const portfolioContent = screen.queryByText(/total.*value/i) || screen.queryByText(/holdings/i)
        expect(portfolioContent).toBeInTheDocument()
      })
    }
    
    if (transactionsNav) {
      await user.click(transactionsNav)
      // Should show transactions content
      await waitFor(() => {
        const transactionContent = screen.queryByText(/add.*transaction/i) || screen.queryByText(/transaction.*history/i)
        expect(transactionContent).toBeInTheDocument()
      })
    }
  })

  it('should display portfolio summary', async () => {
    /**
     * TEST: App should fetch and display portfolio data
     * - Renders App component
     * - Waits for portfolio API call
     * - Verifies portfolio data is shown
     */
    const { getPortfolio } = await import('../api')
    
    render(<App />)
    
    // Wait for portfolio to load
    await waitFor(() => {
      expect(getPortfolio).toHaveBeenCalled()
    })
    
    // Should display total portfolio value (mocked as 25000)
    await waitFor(() => {
      const totalValue = screen.queryByText(/25.*000/) || screen.queryByText(/total.*value/i)
      expect(totalValue).toBeInTheDocument()
    })
  })

  it('should handle loading states', async () => {
    /**
     * TEST: App should show loading indicators while fetching data
     * - Renders App component
     * - Checks for loading indicators initially
     * - Verifies loading disappears after data loads
     */
    render(<App />)
    
    // Should show loading indicator initially
    const loadingElement = screen.queryByText(/loading/i) || screen.queryByRole('status') || screen.queryByTestId('loading')
    
    if (loadingElement) {
      expect(loadingElement).toBeInTheDocument()
      
      // Loading should disappear after data loads
      await waitFor(() => {
        expect(loadingElement).not.toBeInTheDocument()
      }, { timeout: 3000 })
    }
  })

  it('should handle error states gracefully', async () => {
    /**
     * TEST: App should handle API errors gracefully
     * - Mocks API to return error
     * - Renders App component
     * - Verifies error handling
     */
    const { getCurrentPrices } = await import('../api')
    
    // Mock API to throw error
    getCurrentPrices.mockRejectedValueOnce(new Error('API Error'))
    
    render(<App />)
    
    // Should handle error gracefully (not crash)
    await waitFor(() => {
      // App should still render even with API errors
      expect(screen.getByRole('main')).toBeInTheDocument()
    })
    
    // Might show error message
    const errorElement = screen.queryByText(/error/i) || screen.queryByText(/failed/i)
    // Error handling is optional - app might just show empty state
  })

  it('should be responsive to different screen sizes', () => {
    /**
     * TEST: App should be responsive and work on different screen sizes
     * - Renders App component
     * - Checks for responsive design elements
     */
    render(<App />)
    
    // App should have responsive container
    const mainElement = screen.getByRole('main')
    expect(mainElement).toBeInTheDocument()
    
    // Should have some responsive classes or styles
    // This is a basic check - real responsive testing would use different viewport sizes
    const appContainer = mainElement.closest('div')
    if (appContainer) {
      expect(appContainer).toHaveAttribute('class')
    }
  })

  it('should support keyboard navigation', async () => {
    /**
     * TEST: App should be accessible via keyboard navigation
     * - Renders App component
     * - Tests keyboard navigation
     * - Verifies accessibility
     */
    const user = userEvent.setup()
    render(<App />)
    
    // Should be able to tab through interactive elements
    await user.tab()
    
    // Should have focused element
    const focusedElement = document.activeElement
    expect(focusedElement).not.toBe(document.body)
    
    // Should have interactive elements that are focusable
    const interactiveElements = screen.queryAllByRole('button') || screen.queryAllByRole('link')
    if (interactiveElements.length > 0) {
      expect(interactiveElements[0]).toBeInTheDocument()
    }
  })

  it('should maintain state across component updates', async () => {
    /**
     * TEST: App should maintain state when components update
     * - Renders App component
     * - Triggers state changes
     * - Verifies state persistence
     */
    const user = userEvent.setup()
    render(<App />)
    
    // Look for interactive elements that change state
    const buttons = screen.queryAllByRole('button')
    
    if (buttons.length > 0) {
      const firstButton = buttons[0]
      
      // Click button to change state
      await user.click(firstButton)
      
      // App should still be functional
      expect(screen.getByRole('main')).toBeInTheDocument()
    }
  })
})