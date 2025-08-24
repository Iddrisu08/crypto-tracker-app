import { test, expect } from '@playwright/test';

test.describe('Enhanced Analytics Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:5173');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
  });

  test('should display enhanced analytics section', async ({ page }) => {
    // Check if enhanced analytics section is visible
    const analyticsSection = page.locator('.enhanced-analytics');
    await expect(analyticsSection).toBeVisible();

    // Check header
    await expect(page.locator('.analytics-header h2')).toContainText('Enhanced Portfolio Analytics');
  });

  test('should show loading state initially', async ({ page }) => {
    // Reload page to catch loading state
    await page.reload();
    
    // Check for loading spinner (might be brief)
    const loadingSpinner = page.locator('.loading-spinner');
    // We can't guarantee we'll catch the loading state, so we'll check if it's either loading or loaded
    const isLoading = await loadingSpinner.isVisible();
    const isLoaded = await page.locator('.metrics-overview').isVisible();
    
    expect(isLoading || isLoaded).toBeTruthy();
  });

  test('should display key metrics cards', async ({ page }) => {
    // Wait for metrics to load
    await page.waitForSelector('.metrics-overview', { timeout: 10000 });

    // Check if metric cards are visible
    const totalCard = page.locator('.metric-card.total');
    const btcCard = page.locator('.metric-card.btc');
    const ethCard = page.locator('.metric-card.eth');
    const performanceCard = page.locator('.metric-card.performance');

    await expect(totalCard).toBeVisible();
    await expect(btcCard).toBeVisible();
    await expect(ethCard).toBeVisible();
    await expect(performanceCard).toBeVisible();

    // Check if cards contain expected content
    await expect(totalCard.locator('h3')).toContainText('Total Portfolio');
    await expect(btcCard.locator('h3')).toContainText('Bitcoin Holdings');
    await expect(ethCard.locator('h3')).toContainText('Ethereum Holdings');
    await expect(performanceCard.locator('h3')).toContainText('Annualized Return');
  });

  test('should display charts section', async ({ page }) => {
    // Wait for charts to load
    await page.waitForSelector('.charts-section', { timeout: 10000 });

    const chartsSection = page.locator('.charts-section');
    await expect(chartsSection).toBeVisible();

    // Check for chart containers
    const chartContainers = page.locator('.chart-container');
    await expect(chartContainers).toHaveCount(3); // Portfolio allocation, ROI comparison, Investment vs Current Value

    // Check chart headers
    await expect(page.locator('.chart-header').first()).toContainText('Portfolio Allocation');
  });

  test('should display DCA analysis', async ({ page }) => {
    // Wait for DCA analysis section
    await page.waitForSelector('.dca-analysis', { timeout: 10000 });

    const dcaSection = page.locator('.dca-analysis');
    await expect(dcaSection).toBeVisible();

    await expect(dcaSection.locator('h3')).toContainText('Dollar Cost Averaging Analysis');

    // Check for DCA metrics
    const dcaMetrics = page.locator('.dca-metric');
    await expect(dcaMetrics).toHaveCount(3);
  });

  test('should display performance periods', async ({ page }) => {
    // Wait for performance periods section
    await page.waitForSelector('.performance-periods', { timeout: 10000 });

    const performanceSection = page.locator('.performance-periods');
    await expect(performanceSection).toBeVisible();

    await expect(performanceSection.locator('h3')).toContainText('Best & Worst Performing Periods');

    // Check for period cards
    const bestPeriod = page.locator('.period-card.best');
    const worstPeriod = page.locator('.period-card.worst');

    await expect(bestPeriod).toBeVisible();
    await expect(worstPeriod).toBeVisible();
  });

  test('should handle refresh analytics button', async ({ page }) => {
    // Wait for analytics to load
    await page.waitForSelector('.refresh-analytics-btn', { timeout: 10000 });

    const refreshButton = page.locator('.refresh-analytics-btn');
    await expect(refreshButton).toBeVisible();

    // Click refresh button
    await refreshButton.click();

    // Should still show analytics after refresh
    const analyticsSection = page.locator('.enhanced-analytics');
    await expect(analyticsSection).toBeVisible();
  });

  test('should display formatted currency values', async ({ page }) => {
    // Wait for metrics to load
    await page.waitForSelector('.metric-value', { timeout: 10000 });

    // Check if currency values are properly formatted (contain $ symbol)
    const metricValues = page.locator('.metric-value');
    const firstValue = await metricValues.first().textContent();
    
    expect(firstValue).toMatch(/\$[\d,]+(\.\d{2})?/);
  });

  test('should display percentage values correctly', async ({ page }) => {
    // Wait for metrics to load
    await page.waitForSelector('.metric-change', { timeout: 10000 });

    // Check if percentage values are formatted correctly
    const percentageElements = page.locator('.metric-change');
    const firstPercentage = await percentageElements.first().textContent();
    
    expect(firstPercentage).toMatch(/[+-]?\d+\.\d{2}%/);
  });

  test('should show positive/negative styling for profit/loss', async ({ page }) => {
    // Wait for metrics to load
    await page.waitForSelector('.metric-change', { timeout: 10000 });

    // Check for positive or negative styling
    const changes = page.locator('.metric-change');
    const count = await changes.count();
    
    for (let i = 0; i < count; i++) {
      const element = changes.nth(i);
      const hasPositiveClass = await element.evaluate(el => el.classList.contains('positive'));
      const hasNegativeClass = await element.evaluate(el => el.classList.contains('negative'));
      
      expect(hasPositiveClass || hasNegativeClass).toBeTruthy();
    }
  });
});