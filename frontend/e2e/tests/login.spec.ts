import { test, expect } from '@playwright/test';

test.describe('Login Page', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the login page before each test
    await page.goto('/login');
    // Wait for the login form to be visible
    await expect(page.getByRole('heading', { name: 'Sign in to DoMD' })).toBeVisible();
  });

  test('should display login form', async ({ page }) => {
    // Check if the login form is visible
    await expect(page.getByLabel('Username')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('should show validation errors for empty form', async ({ page }) => {
    // Submit the form without filling any fields
    await page.getByRole('button', { name: /sign in/i }).click();

    // Check for validation error messages
    await expect(page.getByText('Username is required')).toBeVisible();
    await expect(page.getByText('Password is required')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Fill in the form with invalid credentials
    await page.getByLabel('Username').fill('invaliduser');
    await page.getByLabel('Password').fill('wrongpassword');

    // Mock the API response for login failure
    await page.route('**/api/auth/login', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'error',
          message: 'Invalid credentials'
        })
      });
    });

    // Submit the form
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Check for error message
    await expect(page.getByText('Invalid username or password. Please try again.')).toBeVisible();
  });

  test('should successfully log in with valid credentials', async ({ page }) => {
    // Fill in the form with valid credentials
    await page.getByLabel('Username').fill('admin');
    await page.getByLabel('Password').fill('admin');

    // Mock the API response for successful login
    await page.route('**/api/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'success',
          message: 'Login successful',
          data: {
            token: 'test-token-123',
            user: {
              username: 'admin',
              roles: ['admin']
            }
          }
        })
      });
    });

    // Submit the form
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Check if redirected to the home page after successful login
    await expect(page).toHaveURL('/');
  });

  test('should toggle password visibility', async ({ page }) => {
    // Password field should be of type 'password' initially
    const passwordInput = page.getByLabel('Password');
    await expect(passwordInput).toHaveAttribute('type', 'password');

    // Click the toggle button (using the eye icon)
    await page.locator('button[aria-label="toggle password visibility"]').click();

    // Password field should now be of type 'text'
    await expect(passwordInput).toHaveAttribute('type', 'text');
  });
});
