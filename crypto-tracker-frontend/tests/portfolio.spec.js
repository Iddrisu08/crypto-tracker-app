import { test, expect } from '@playwright/test';

test.describe('Portfolio Features', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Wait for the application to load
    await page.waitForLoadState('networkidle');
  });

  test('should display portfolio overview', async ({ page }) => {
    // Wait for portfolio data to load
    await page.waitForSelector('h2:has-text("Crypto Portfolio Overview")', { timeout: 10000 });
    
    // Check if portfolio section is visible
    await expect(page.getByText('Crypto Portfolio Overview')).toBeVisible();
    
    // Check if portfolio stats are displayed
    await expect(page.getByText('Total Invested')).toBeVisible();
    await expect(page.getByText('Total Value')).toBeVisible();
    await expect(page.getByText('Profit/Loss')).toBeVisible();
  });

  test('should refresh portfolio data', async ({ page }) => {
    // Wait for initial load
    await page.waitForSelector('h2:has-text("Crypto Portfolio Overview")', { timeout: 10000 });
    
    // Find and click refresh button
    const refreshButton = page.locator('button:has-text("Refresh Portfolio")');
    await expect(refreshButton).toBeVisible();
    
    // Click refresh and wait for response
    await refreshButton.click();
    
    // Verify the data refreshes (spinner or updated timestamp)
    await page.waitForTimeout(2000);
    
    // Portfolio should still be visible after refresh
    await expect(page.getByText('Crypto Portfolio Overview')).toBeVisible();
  });

  test('should display BTC and ETH holdings', async ({ page }) => {
    // Wait for portfolio data to load
    await page.waitForSelector('h2:has-text("Crypto Portfolio Overview")', { timeout: 10000 });
    
    // Check for BTC related elements
    await expect(page.getByText('BTC Invested')).toBeVisible();
    await expect(page.getByText('BTC Held')).toBeVisible();
    await expect(page.getByText('BTC Value')).toBeVisible();
    
    // Check for ETH related elements
    await expect(page.getByText('ETH Invested')).toBeVisible();
    await expect(page.getByText('ETH Held')).toBeVisible();
    await expect(page.getByText('ETH Value')).toBeVisible();
  });

  test('should display portfolio chart', async ({ page }) => {
    // Wait for chart to load
    await page.waitForSelector('h3:has-text("Investment vs Current Value")', { timeout: 10000 });
    
    // Check if chart title is visible
    await expect(page.getByText('Investment vs Current Value')).toBeVisible();
    
    // Check if chart container exists (look for any chart-related elements)
    await expect(page.locator('application')).toBeVisible();
  });

  test('should handle portfolio data errors gracefully', async ({ page }) => {
    // This test would require mocking API failures
    // For now, just ensure the page doesn't crash
    await page.goto('/');
    
    // Wait a bit and ensure basic structure is there
    await page.waitForTimeout(5000);
    
    // The app title should always be visible
    await expect(page.getByText('Crypto Investment Tracker')).toBeVisible();
  });
});