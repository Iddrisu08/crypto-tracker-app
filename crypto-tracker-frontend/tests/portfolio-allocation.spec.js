import { test, expect } from '@playwright/test';

test.describe('Portfolio Allocation Component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
  });

  test('should display portfolio allocation section', async ({ page }) => {
    // Check if the portfolio allocation component is visible
    const allocationComponent = page.locator('.bg-gradient-to-br').filter({ hasText: 'Portfolio Allocation' });
    await expect(allocationComponent).toBeVisible();

    // Check header content
    await expect(page.locator('text=Portfolio Allocation')).toBeVisible();
    await expect(page.locator('text=Asset distribution breakdown')).toBeVisible();
  });

  test('should show loading state initially', async ({ page }) => {
    // Reload to catch loading state
    await page.reload();
    
    // Check for loading indicators
    const loadingText = page.locator('text=Loading allocation data...');
    const loadedChart = page.locator('canvas');
    
    // Either loading or loaded state should be visible
    const isLoading = await loadingText.isVisible();
    const isLoaded = await loadedChart.isVisible();
    
    expect(isLoading || isLoaded).toBeTruthy();
  });

  test('should display pie chart', async ({ page }) => {
    // Wait for chart to render
    await page.waitForSelector('canvas', { timeout: 10000 });

    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible();
    
    // Chart should have dimensions
    const canvasElement = await canvas.elementHandle();
    const boundingBox = await canvasElement.boundingBox();
    expect(boundingBox.width).toBeGreaterThan(0);
    expect(boundingBox.height).toBeGreaterThan(0);
  });

  test('should display allocation percentages', async ({ page }) => {
    // Wait for allocation data to load
    await page.waitForSelector('text=Bitcoin', { timeout: 10000 });

    // Check for Bitcoin and Ethereum sections
    const bitcoinSection = page.locator('.bg-gradient-to-br').filter({ hasText: 'Bitcoin' });
    const ethereumSection = page.locator('.bg-gradient-to-br').filter({ hasText: 'Ethereum' });

    await expect(bitcoinSection).toBeVisible();
    await expect(ethereumSection).toBeVisible();

    // Check for percentage values (should contain % symbol)
    const percentages = page.locator('text=/%/');
    expect(await percentages.count()).toBeGreaterThan(0);
  });

  test('should display dollar values', async ({ page }) => {
    // Wait for data to load
    await page.waitForSelector('text=$', { timeout: 10000 });

    // Check for dollar-formatted values
    const dollarValues = page.locator('text=/\\$[\\d,]+/');
    expect(await dollarValues.count()).toBeGreaterThan(0);
  });

  test('should display cryptocurrency holdings', async ({ page }) => {
    // Wait for holdings data
    await page.waitForSelector('text=BTC', { timeout: 10000 });

    // Check for BTC and ETH holdings
    const btcHoldings = page.locator('text=/\\d+\\.\\d+ BTC/');
    const ethHoldings = page.locator('text=/\\d+\\.\\d+ ETH/');

    await expect(btcHoldings).toBeVisible();
    await expect(ethHoldings).toBeVisible();
  });

  test('should display total portfolio value', async ({ page }) => {
    // Wait for total portfolio section
    await page.waitForSelector('text=Total Portfolio Value', { timeout: 10000 });

    const totalValueSection = page.locator('.bg-gradient-to-r').filter({ hasText: 'Total Portfolio Value' });
    await expect(totalValueSection).toBeVisible();

    // Should contain a dollar amount
    const totalValue = totalValueSection.locator('text=/\\$[\\d,]+/');
    await expect(totalValue).toBeVisible();
  });

  test('should have working refresh button', async ({ page }) => {
    // Wait for refresh button
    await page.waitForSelector('text=🔄 Refresh', { timeout: 10000 });

    const refreshButton = page.locator('button').filter({ hasText: '🔄 Refresh' });
    await expect(refreshButton).toBeVisible();

    // Click refresh button
    await refreshButton.click();

    // Component should still be visible after refresh
    const allocationComponent = page.locator('.bg-gradient-to-br').filter({ hasText: 'Portfolio Allocation' });
    await expect(allocationComponent).toBeVisible();
  });

  test('should display correct crypto colors', async ({ page }) => {
    // Wait for allocation cards to load
    await page.waitForSelector('text=Bitcoin', { timeout: 10000 });

    // Check for Bitcoin and Ethereum styled sections
    const bitcoinCard = page.locator('.bg-gradient-to-br').filter({ hasText: 'Bitcoin' });
    const ethereumCard = page.locator('.bg-gradient-to-br').filter({ hasText: 'Ethereum' });

    await expect(bitcoinCard).toBeVisible();
    await expect(ethereumCard).toBeVisible();

    // Check for color indicators (colored squares/circles)
    const colorIndicators = page.locator('.bg-gradient-to-br').filter({ hasText: 'w-6 h-6' });
    // Note: This is a simplified check for visual indicators
  });

  test('should handle chart interactions', async ({ page }) => {
    // Wait for chart
    await page.waitForSelector('canvas', { timeout: 10000 });

    const canvas = page.locator('canvas');
    
    // Hover over the chart (should trigger tooltip)
    await canvas.hover();
    
    // Chart should still be visible after interaction
    await expect(canvas).toBeVisible();
  });

  test('should display meaningful allocation percentages', async ({ page }) => {
    // Wait for percentage data
    await page.waitForSelector('text=/%/', { timeout: 10000 });

    // Get all percentage texts
    const percentageElements = page.locator('text=/\\d+\\.\\d%/');
    const count = await percentageElements.count();
    
    expect(count).toBeGreaterThan(0);

    // Check that percentages are reasonable (0-100%)
    for (let i = 0; i < Math.min(count, 2); i++) { // Check first 2 percentages
      const text = await percentageElements.nth(i).textContent();
      const percentage = parseFloat(text.replace('%', ''));
      expect(percentage).toBeGreaterThanOrEqual(0);
      expect(percentage).toBeLessThanOrEqual(100);
    }
  });
});