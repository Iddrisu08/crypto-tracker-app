import { test, expect } from '@playwright/test';

test.describe('Analytics Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display Portfolio Analytics section', async ({ page }) => {
    // Wait for analytics to load
    await page.waitForSelector('h2:has-text("Portfolio Analytics")', { timeout: 15000 });
    
    // Check if analytics header is visible
    await expect(page.getByRole('heading', { name: 'Portfolio Analytics' })).toBeVisible();
    
    // Check if refresh button is present
    await expect(page.locator('button:has-text("Refresh Analytics")')).toBeVisible();
  });

  test('should display key metrics cards', async ({ page }) => {
    // Wait for analytics to load
    await page.waitForSelector('h2:has-text("Portfolio Analytics")', { timeout: 15000 });
    
    // Check for metric cards
    await expect(page.getByText('Total Investment')).toBeVisible();
    await expect(page.getByText('Current Value')).toBeVisible();
    await expect(page.getByText('Total P&L')).toBeVisible();
    await expect(page.getByText('Annualized Return')).toBeVisible();
  });

  test('should display Bitcoin performance metrics', async ({ page }) => {
    // Wait for analytics to load
    await page.waitForSelector('h2:has-text("Portfolio Analytics")', { timeout: 15000 });
    
    // Check for Bitcoin section
    await expect(page.getByText('Bitcoin Performance')).toBeVisible();
    
    // Check for BTC metrics
    await expect(page.getByText('BTC Investment Analysis')).toBeVisible();
  });

  test('should display Ethereum performance metrics', async ({ page }) => {
    // Wait for analytics to load
    await page.waitForSelector('h2:has-text("Portfolio Analytics")', { timeout: 15000 });
    
    // Check for Ethereum section
    await expect(page.getByText('Ethereum Performance')).toBeVisible();
    
    // Check for ETH metrics
    await expect(page.getByText('ETH Investment Analysis')).toBeVisible();
  });

  test('should display DCA strategy analysis', async ({ page }) => {
    // Wait for analytics to load
    await page.waitForSelector('h2:has-text("Portfolio Analytics")', { timeout: 15000 });
    
    // Check for DCA section
    await expect(page.getByText('DCA Strategy Analysis')).toBeVisible();
    await expect(page.getByText('Dollar-Cost Averaging Performance')).toBeVisible();
    
    // Check for DCA metrics
    await expect(page.getByText('DCA vs Lump Sum')).toBeVisible();
    await expect(page.getByText('Weekly Average')).toBeVisible();
  });

  test('should display portfolio allocation pie chart', async ({ page }) => {
    // Wait for analytics to load
    await page.waitForSelector('h2:has-text("Portfolio Analytics")', { timeout: 15000 });
    
    // Check for allocation section
    await expect(page.getByText('Portfolio Allocation')).toBeVisible();
    await expect(page.getByText('Asset distribution breakdown')).toBeVisible();
    
    // Check for pie chart canvas
    await expect(page.locator('canvas')).toBeVisible();
  });

  test('should display performance periods', async ({ page }) => {
    // Wait for analytics to load
    await page.waitForSelector('h2:has-text("Portfolio Analytics")', { timeout: 15000 });
    
    // Check for performance periods section
    await expect(page.getByText('Performance Periods')).toBeVisible();
    await expect(page.getByText('Best and worst weekly returns')).toBeVisible();
    
    // Check for best/worst week cards
    await expect(page.getByText('Best Week')).toBeVisible();
    await expect(page.getByText('Worst Week')).toBeVisible();
  });

  test('should refresh analytics data', async ({ page }) => {
    // Wait for analytics to load
    await page.waitForSelector('h2:has-text("Portfolio Analytics")', { timeout: 15000 });
    
    // Find and click refresh button
    const refreshButton = page.locator('button:has-text("Refresh Analytics")');
    await expect(refreshButton).toBeVisible();
    
    // Click refresh
    await refreshButton.click();
    
    // Wait for refresh to complete
    await page.waitForTimeout(3000);
    
    // Analytics should still be visible
    await expect(page.getByRole('heading', { name: 'Portfolio Analytics' })).toBeVisible();
  });

  test('should handle loading states', async ({ page }) => {
    // Go to page and immediately check for loading indicators
    await page.goto('/');
    
    // Check if loading state is shown initially
    const loadingText = page.getByText('Loading analytics...');
    
    // Either loading text should be visible or content should load quickly
    try {
      await expect(loadingText).toBeVisible({ timeout: 2000 });
    } catch {
      // If loading is too fast, that's also okay
      await expect(page.getByRole('heading', { name: 'Portfolio Analytics' })).toBeVisible();
    }
  });
});