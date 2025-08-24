import { test, expect } from '@playwright/test';

test.describe('Crypto Tracker Integration Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
  });

  test('should load main application', async ({ page }) => {
    // Check if main title is visible
    await expect(page.locator('text=Crypto Investment Tracker')).toBeVisible();

    // Check if main sections are present
    await expect(page.locator('.main-content')).toBeVisible();
  });

  test('should display all major sections', async ({ page }) => {
    // Wait for content to load
    await page.waitForSelector('.section', { timeout: 15000 });

    // Check for main sections
    const sections = page.locator('.section');
    const sectionCount = await sections.count();
    
    expect(sectionCount).toBeGreaterThan(3); // Should have multiple sections

    // Check specific section headers
    await expect(page.locator('text=Enhanced Portfolio Analytics')).toBeVisible();
    await expect(page.locator('text=Portfolio Allocation')).toBeVisible();
  });

  test('should have working global refresh button', async ({ page }) => {
    // Wait for refresh button in header
    await page.waitForSelector('text=Refresh All Data', { timeout: 10000 });

    const globalRefreshBtn = page.locator('button').filter({ hasText: 'Refresh All Data' });
    await expect(globalRefreshBtn).toBeVisible();

    // Click refresh
    await globalRefreshBtn.click();

    // App should still be functional after refresh
    await expect(page.locator('text=Crypto Investment Tracker')).toBeVisible();
  });

  test('should display current crypto prices in header', async ({ page }) => {
    // Wait for price displays
    await page.waitForSelector('.current-prices', { timeout: 10000 });

    const pricesSection = page.locator('.current-prices');
    await expect(pricesSection).toBeVisible();

    // Should show Bitcoin and Ethereum prices
    const bitcoinPrice = pricesSection.locator('.price-item').first();
    const ethereumPrice = pricesSection.locator('.price-item').last();

    await expect(bitcoinPrice).toBeVisible();
    await expect(ethereumPrice).toBeVisible();
  });

  test('should have working theme toggle', async ({ page }) => {
    // Look for theme toggle button
    const themeToggle = page.locator('.theme-toggle');
    
    if (await themeToggle.isVisible()) {
      // Click theme toggle
      await themeToggle.click();
      
      // App should still be functional
      await expect(page.locator('text=Crypto Investment Tracker')).toBeVisible();
    }
  });

  test('should display enhanced analytics with real data', async ({ page }) => {
    // Wait for analytics to load with data
    await page.waitForSelector('.metric-value', { timeout: 15000 });

    const metricValues = page.locator('.metric-value');
    const valueCount = await metricValues.count();
    
    expect(valueCount).toBeGreaterThan(0);

    // Check that we have actual dollar values (not $0.00)
    const firstValue = await metricValues.first().textContent();
    expect(firstValue).not.toBe('$0.00');
    expect(firstValue).toMatch(/\$[\d,]+/);
  });

  test('should display portfolio allocation with real data', async ({ page }) => {
    // Wait for allocation data
    await page.waitForSelector('canvas', { timeout: 15000 });

    // Check for allocation percentages
    const btcSection = page.locator('text=/Bitcoin/').first();
    const ethSection = page.locator('text=/Ethereum/').first();

    await expect(btcSection).toBeVisible();
    await expect(ethSection).toBeVisible();

    // Check for non-zero percentages
    const percentages = page.locator('text=/\\d+\\.\\d%/');
    const percentageCount = await percentages.count();
    expect(percentageCount).toBeGreaterThan(0);
  });

  test('should handle backend API errors gracefully', async ({ page }) => {
    // This test checks error handling by looking for error states
    // We can't easily simulate network errors, so we check if error handling exists

    // Wait for initial load
    await page.waitForTimeout(5000);

    // Check if any error states are visible (shouldn't be under normal conditions)
    const errorMessages = page.locator('text=/error|Error|failed|Failed/i');
    const errorCount = await errorMessages.count();

    // If there are errors, they should be handled gracefully
    if (errorCount > 0) {
      // Should show retry buttons or helpful error messages
      const retryButtons = page.locator('button').filter({ hasText: /retry|Retry/i });
      expect(await retryButtons.count()).toBeGreaterThan(0);
    }
  });

  test('should display consistent data across components', async ({ page }) => {
    // Wait for all components to load
    await page.waitForSelector('.metric-value', { timeout: 15000 });
    await page.waitForSelector('canvas', { timeout: 15000 });

    // Get portfolio value from analytics
    const analyticsValue = page.locator('.metric-card.total .metric-value').first();
    const analyticsText = await analyticsValue.textContent();

    // Get total value from allocation component
    const totalValue = page.locator('text=Total Portfolio Value').locator('..').locator('.text-3xl');
    
    if (await totalValue.isVisible()) {
      const totalText = await totalValue.textContent();
      
      // Values should be consistent (same dollar amount)
      const analyticsAmount = analyticsText.replace(/[^\\d.,]/g, '');
      const totalAmount = totalText.replace(/[^\\d.,]/g, '');
      
      expect(analyticsAmount).toBe(totalAmount);
    }
  });

  test('should be responsive on different screen sizes', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);

    // Main content should still be visible
    await expect(page.locator('text=Crypto Investment Tracker')).toBeVisible();
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);

    await expect(page.locator('.enhanced-analytics')).toBeVisible();

    // Test desktop viewport
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.waitForTimeout(1000);

    await expect(page.locator('.charts-section')).toBeVisible();
  });

  test('should load and display charts', async ({ page }) => {
    // Wait for charts to render
    await page.waitForSelector('canvas', { timeout: 15000 });

    const canvasElements = page.locator('canvas');
    const chartCount = await canvasElements.count();

    expect(chartCount).toBeGreaterThan(0);

    // Check that charts have content (non-zero dimensions)
    for (let i = 0; i < Math.min(chartCount, 3); i++) {
      const canvas = canvasElements.nth(i);
      const boundingBox = await canvas.boundingBox();
      expect(boundingBox.width).toBeGreaterThan(50);
      expect(boundingBox.height).toBeGreaterThan(50);
    }
  });

  test('should show meaningful portfolio data', async ({ page }) => {
    // Wait for data to load
    await page.waitForSelector('.metric-value', { timeout: 15000 });

    // Check for meaningful investment amounts
    const investedAmounts = page.locator('text=/Invested.*\\$[\\d,]+/');
    expect(await investedAmounts.count()).toBeGreaterThan(0);

    // Check for holdings data
    const btcHoldings = page.locator('text=/\\d+\\.\\d+ BTC/');
    const ethHoldings = page.locator('text=/\\d+\\.\\d+ ETH/');

    expect(await btcHoldings.count()).toBeGreaterThan(0);
    expect(await ethHoldings.count()).toBeGreaterThan(0);
  });
});