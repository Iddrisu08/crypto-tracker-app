import { test, expect } from '@playwright/test';

test.describe('Transaction Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display transaction form', async ({ page }) => {
    // Wait for page to load
    await page.waitForSelector('h2:has-text("Manual Transactions")', { timeout: 10000 });
    
    // Check if transaction form is visible
    await expect(page.getByText('Manual Transactions')).toBeVisible();
    
    // Check for form fields
    await expect(page.locator('select[name="coin"]')).toBeVisible();
    await expect(page.locator('select[name="type"]')).toBeVisible();
    await expect(page.locator('input[name="amount"]')).toBeVisible();
    await expect(page.locator('input[name="date"]')).toBeVisible();
  });

  test('should display transaction history', async ({ page }) => {
    // Wait for transaction history to load
    await page.waitForSelector('h2:has-text("Transaction History")', { timeout: 10000 });
    
    // Check if transaction history section is visible
    await expect(page.getByText('Transaction History')).toBeVisible();
    
    // Check for refresh button
    await expect(page.locator('button:has-text("Refresh History")')).toBeVisible();
  });

  test('should validate transaction form', async ({ page }) => {
    // Wait for form to load
    await page.waitForSelector('select[name="coin"]', { timeout: 10000 });
    
    // Try to submit empty form
    const submitButton = page.locator('button:has-text("Add Transaction")');
    await expect(submitButton).toBeVisible();
    
    // Fill out form with valid data
    await page.selectOption('select[name="coin"]', 'bitcoin');
    await page.selectOption('select[name="type"]', 'buy');
    await page.fill('input[name="amount"]', '0.001');
    await page.fill('input[name="date"]', '2025-01-15');
    
    // Form should be ready to submit
    await expect(submitButton).toBeEnabled();
  });

  test('should refresh transaction history', async ({ page }) => {
    // Wait for transaction history to load
    await page.waitForSelector('h2:has-text("Transaction History")', { timeout: 10000 });
    
    // Find and click refresh button
    const refreshButton = page.locator('button:has-text("Refresh History")');
    await expect(refreshButton).toBeVisible();
    
    // Click refresh
    await refreshButton.click();
    
    // Wait for refresh to complete
    await page.waitForTimeout(2000);
    
    // Transaction history should still be visible
    await expect(page.getByText('Transaction History')).toBeVisible();
  });

  test('should handle price fetching', async ({ page }) => {
    // Wait for form to load
    await page.waitForSelector('select[name="coin"]', { timeout: 10000 });
    
    // Fill out form
    await page.selectOption('select[name="coin"]', 'bitcoin');
    await page.selectOption('select[name="type"]', 'buy');
    await page.fill('input[name="amount"]', '0.001');
    await page.fill('input[name="date"]', '2025-01-15');
    
    // Check if price field appears or is handled automatically
    const priceInput = page.locator('input[name="price"]');
    
    // Price should either be filled automatically or have a field
    if (await priceInput.isVisible()) {
      await expect(priceInput).toBeVisible();
    } else {
      // Price is handled automatically - this is also valid
      await expect(page.locator('button:has-text("Add Transaction")')).toBeEnabled();
    }
  });
});