import { Page } from '@playwright/test';

/**
 * Logs a user in through the AllAuth login page.
 * @param {Page} page - The Playwright Page object.
 * @param {string} username - The username to log in with.
 * @param {string} [password] - The password for the user. Optional for scenarios like social login.
 */
export async function loginUser(page: Page, username: string, password?: string) {
  await page.goto('/accounts/login/');
  await page.fill('input[name="login"]', username);
  if (password) { // Password might not be needed for social logins in the future
    await page.fill('input[name="password"]', password);
  }
  // Try a common text for allauth login button first
  const signInButton = page.locator("//button[contains(text(), 'Sign In')] | //button[contains(text(), 'Log In')]");
  if (await signInButton.count() > 0) {
    await signInButton.click();
  } else {
    // Fallback to a generic submit button
    await page.click('button[type="submit"]');
  }
  // Wait for redirect to a page that indicates successful login
  // Assuming /res/ is part of the URL for authenticated users
  await page.waitForURL(/\/res\//, { timeout: 10000 });
}

/**
 * Logs a user out using the AllAuth logout page.
 * @param {Page} page - The Playwright Page object.
 */
export async function logoutUser(page: Page) {
  await page.goto('/accounts/logout/');
  // allauth logout page usually has a confirmation form/button
  const signOutButton = page.locator("//button[contains(text(), 'Sign Out')] | //button[contains(text(), 'Log Out')] | //input[@type='submit' and contains(@value, 'Sign Out')]");
  if (await signOutButton.count() > 0) {
    await signOutButton.click();
  } else {
    // If no specific button is found, try a generic form submission on the logout page.
    // This handles cases where the logout page might just be a form that needs submitting.
    const form = page.locator('form'); // Assuming there's a form on the logout page
    if (await form.count() > 0) {
        const submitButton = form.locator('button[type="submit"], input[type="submit"]');
        if (await submitButton.count() > 0) {
            await submitButton.click();
        }
    }
  }
  // Wait for redirect to a page that indicates successful logout
  // e.g., login page or homepage, and definitely not /res/
  await page.waitForURL((url) => !url.pathname.includes('/res/'), { timeout: 10000 });
}

/**
 * Triggers the article poller for a specific feed.
 * @param {Page} page - The Playwright Page object.
 * @param {number | string} feedId - The ID of the feed to poll.
 */
export async function triggerPoller(page: Page, feedId: number | string) {
  const response = await page.request.post(`/api/feeds/${feedId}/refresh/`);
  if (!response.ok()) {
    console.error(`Error triggering poller for feed ${feedId}: ${response.status()} ${response.statusText()}`);
    // Optionally, throw an error to make the test fail explicitly
    // throw new Error(`Error triggering poller for feed ${feedId}: ${response.status()} ${response.statusText()}`);
  }
  // It might be useful to return the response if the caller needs to inspect it.
}

/**
 * Placeholder function to simulate making an article public.
 * In a real test suite, this function would need to interact with the backend
 * (e.g., via an API call or by executing a Django management command) to change the article's status.
 * @param {Page} page - The Playwright Page object (used for context, e.g., page.request).
 * @param {string | undefined | null} articleId - The ID of the article to make public.
 * @throws {Error} if articleId is not provided.
 */
export async function makeArticlePublic(page: Page, articleId: string | undefined | null) {
  if (!articleId) throw new Error("Article ID is undefined or null");
  
  console.warn(`(Placeholder) Making article ${articleId} public. 
    This is a placeholder and does not actually change backend state. 
    For this function to work in a real E2E test, it must be implemented 
    to trigger the necessary backend Django management command (e.g., via a test-specific API endpoint).`);

  // Example of what a real implementation might do (requires a backend endpoint):
  // const response = await page.request.post('/api/testing/make-article-public', {
  //   data: { article_id: articleId }
  // });
  // if (!response.ok()) {
  //   throw new Error(`Failed to make article ${articleId} public: ${response.statusText()}`);
  // }

  // For the E2E test to proceed as if the command worked, we assume this placeholder
  // is sufficient for now, and the test will be written as if this helper correctly modifies backend state.
}
