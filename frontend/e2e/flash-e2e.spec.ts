import { test, expect } from '@playwright/test';
import { loginUser, logoutUser, triggerPoller, makeArticlePublic } from './utils';

/**
 * @file E2E tests for the Flash application.
 * 
 * Prerequisites for running these tests:
 * 1. A running backend server for the Flash application.
 * 2. A test user account with credentials 'testuser' / 'testpassword'.
 * 3. A feed configured in the backend with ID=1 (TEST_FEED_ID) that will yield articles when its poller is triggered.
 * 4. The `makeArticlePublic` helper function in `utils.ts` is currently a placeholder.
 *    For tests relying on it to truly affect public visibility, its backend implementation is required.
 */

// Assume a TEST_FEED_ID is available. This would ideally come from test setup or environment.
const TEST_FEED_ID = 1; // Replace with a real feed ID configured for testing in the backend

test.describe('Flash E2E Tests', () => {

  // beforeEach hook to ensure a clean state for each test
  test.beforeEach(async ({ page }) => {
    // Clear cookies and local storage to ensure no session data persists between tests
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
    // Navigate to a neutral starting point, e.g., the public home page.
    // Some tests might immediately navigate away, but this ensures a consistent start.
    await page.goto('/'); 
  });

  test('should display an empty list of news items for a non-authenticated user on the public home page', async ({ page }) => {
    // Navigate to the public home page (already done by beforeEach, but explicit for clarity if beforeEach changes)
    await page.goto('/');

    // Verify the list of news items is empty by checking for the "empty state" message.
    // Selector based on flash/templates/pages/home.html
    const emptyMessage = page.locator('div.alert.alert-warning.text-center');
    await expect(emptyMessage).toBeVisible();
    await expect(emptyMessage).toHaveText('Non ci sono articoli da visualizzare.');

    // Additionally, verify that no article items are rendered.
    // Articles are <li class="card mb-3"> within <ul class="ps-0">.
    const articleItems = page.locator('ul.ps-0 li.card.mb-3');
    await expect(articleItems).toHaveCount(0);

    // The template shows an {% if page_obj.paginator.count == 0 %} block for the empty message,
    // and an {% else %} block for the list. So the <ul> should not exist if empty.
    const articleListContainer = page.locator('ul.ps-0');
    await expect(articleListContainer).toHaveCount(0);
  });

  test('should redirect a logged-in user to /res/ and display an empty article list', async ({ page }) => {
    // Log in user
    await loginUser(page, 'testuser', 'testpassword'); 

    // loginUser helper already waits for /res/ URL.
    // Verify current URL is /res/
    await expect(page).toHaveURL(/\/res\//, { timeout: 15000 }); 

    // Verify the article list in /res/ (Vue app) is initially empty.
    // Selectors based on frontend/src/views/HomeView.vue
    const resEmptyMessage = page.locator('div.alert.alert-warning.text-center:has-text("Non ci sono articoli da visualizzare.")');
    // Wait for the loading indicators in HomeView.vue to resolve and the empty message to appear.
    await expect(resEmptyMessage).toBeVisible({ timeout: 10000 }); 

    // Verify that the container for ArticleCard components is not present.
    const resArticlesContainer = page.locator('div.wrapper');
    await expect(resArticlesContainer).toHaveCount(0);
  });

  test('should display articles in /res/ for a logged-in user after poller runs', async ({ page }) => {
    // Log in user
    await loginUser(page, 'testuser', 'testpassword');
    await expect(page).toHaveURL(/\/res\//, { timeout: 10000 }); // Ensure user is on /res/

    // Trigger poller for the test feed
    await triggerPoller(page, TEST_FEED_ID);

    // Reload the page to force the Vue app to re-fetch articles.
    await page.reload({ waitUntil: 'domcontentloaded', timeout: 10000 }); 

    // Wait for articles to load: empty message should disappear or article container should appear.
    // In HomeView.vue, content is shown when count_fetch == 0.
    await expect(
        page.locator('div.alert.alert-warning.text-center:has-text("Non ci sono articoli da visualizzare.")').or(page.locator('div.wrapper'))
    ).toBeVisible({timeout:15000}); // Wait for either state to be visible

    // Verify article list in /res/ is not empty
    const emptyStateMessage = page.locator('div.alert.alert-warning.text-center:has-text("Non ci sono articoli da visualizzare.")');
    await expect(emptyStateMessage).toHaveCount(0); // Empty state should NOT be visible

    const articlesContainer = page.locator('div.wrapper'); // Container of articles
    await expect(articlesContainer).toBeVisible(); // Article container should BE visible

    // Verify at least one ArticleCard component is rendered.
    const articleItems = articlesContainer.locator('> *'); // Direct children of div.wrapper
    await expect(articleItems.first()).toBeVisible({ timeout: 10000 }); 
    const count = await articleItems.count();
    expect(count).toBeGreaterThan(0); 
  });

  test('should still display an empty public list for a non-authenticated user after poller runs', async ({ page }) => {
    // This test verifies that articles fetched by the poller do not appear on the public page
    // unless explicitly made public.

    // Log in to trigger the poller (as it might require authentication).
    await loginUser(page, 'testuser', 'testpassword'); 
    await triggerPoller(page, TEST_FEED_ID);
    await logoutUser(page); // Log out to check public page as a non-authenticated user.

    // Navigate to public home page.
    await page.goto('/');

    // Verify the public list of news items is still empty.
    const emptyMessage = page.locator('div.alert.alert-warning.text-center');
    await expect(emptyMessage).toBeVisible();
    await expect(emptyMessage).toHaveText('Non ci sono articoli da visualizzare.');

    const articleItems = page.locator('ul.ps-0 li.card.mb-3');
    await expect(articleItems).toHaveCount(0);

    const articleListContainer = page.locator('ul.ps-0');
    await expect(articleListContainer).toHaveCount(0); 
  });

  test('should allow a logged-in user to navigate to an article detail page in /res/', async ({ page }) => {
    // Log in user
    await loginUser(page, 'testuser', 'testpassword');

    // Ensure articles are present in /res/
    // loginUser should land on /res/, if not, explicitly navigate.
    if (!page.url().includes('/res/')) {
        await page.goto('/res/');
    }
    await triggerPoller(page, TEST_FEED_ID);
    await page.reload({ waitUntil: 'domcontentloaded', timeout: 10000 });
    
    // Wait for articles to be loaded (empty message gone or wrapper visible)
     await expect(
        page.locator('div.alert.alert-warning.text-center:has-text("Non ci sono articoli da visualizzare.")').or(page.locator('div.wrapper'))
    ).toBeVisible({timeout:15000});
    await expect(page.locator('div.alert.alert-warning.text-center:has-text("Non ci sono articoli da visualizzare.")')).toHaveCount(0);

    // Find and click the first article link in the /res/ list
    const articlesContainer = page.locator('div.wrapper');
    await expect(articlesContainer).toBeVisible();
    
    // Selector for the link within ArticleCard.vue that navigates to the detail page
    const firstArticleLink = articlesContainer.locator('div.card.m-1 a[href^="/article/"]').first();
    await expect(firstArticleLink).toBeVisible({ timeout: 5000 }); 
    await firstArticleLink.click();

    // Verify navigation to the article detail page (Vue router uses hash mode: /res/#/article/ID)
    await expect(page).toHaveURL(/\/res\/#\/article\/\d+$/, { timeout: 10000 }); 

    // Verify key elements on the article detail page are visible (ArticleView.vue)
    // Wait for loading spinner to disappear (count_fetch === 0 in ArticleView.vue)
    const detailPageContainer = page.locator('div.container.my-3:not(:has(.spinner-border))');
    await expect(detailPageContainer).toBeVisible({ timeout: 10000 });

    const articleTitle = detailPageContainer.locator('div.title h1'); 
    await expect(articleTitle).toBeVisible();
    await expect(articleTitle).not.toBeEmpty(); 

    const articleContent = detailPageContainer.locator('div#content_tts'); 
    await expect(articleContent).toBeVisible();
  });

  test('should display a read article on the public list for a non-authenticated user after it is made public', async ({ page }) => {
    // Log in user
    await loginUser(page, 'testuser', 'testpassword');
    
    // Ensure user is on /res/ and articles are loaded
    if (!page.url().includes('/res/')) {
        await page.goto('/res/');
    }
    await triggerPoller(page, TEST_FEED_ID);
    await page.reload({ waitUntil: 'domcontentloaded', timeout: 10000 });
    
    // Wait for articles to be loaded in /res/
    await expect(
        page.locator('div.alert.alert-warning.text-center:has-text("Non ci sono articoli da visualizzare.")').or(page.locator('div.wrapper'))
    ).toBeVisible({timeout:15000});
    await expect(page.locator('div.alert.alert-warning.text-center:has-text("Non ci sono articoli da visualizzare.")')).toHaveCount(0);

    // Get the ID of the first article in the /res/ list
    const articlesContainer = page.locator('div.wrapper');
    await expect(articlesContainer).toBeVisible();
    const firstArticleCardLink = articlesContainer.locator('div.card.m-1 a[href^="/article/"]').first();
    await expect(firstArticleCardLink).toBeVisible({ timeout: 10000 });

    const articleHref = await firstArticleCardLink.getAttribute('href'); // e.g., #/article/123
    let articleId: string | undefined;
    if (articleHref) {
        const parts = articleHref.split('/');
        articleId = parts.pop(); // Get the last part, which should be the ID
    }
    if (!articleId) {
      throw new Error('Could not extract article ID from href: ' + articleHref);
    }
    
    // Use the (placeholder) helper to make the article public
    await makeArticlePublic(page, articleId); 

    // Log out and check the public page
    await logoutUser(page);
    await page.goto('/');
    // A page reload might be necessary if the public page caches or if makeArticlePublic is slow
    await page.reload({ waitUntil: 'domcontentloaded', timeout: 10000 }); 

    // Verify the public list is not empty
    const emptyStateMessage = page.locator('div.alert.alert-warning.text-center:has-text("Non ci sono articoli da visualizzare.")');
    await expect(emptyStateMessage).toHaveCount(0); 

    const publicArticleItems = page.locator('ul.ps-0 li.card.mb-3'); 
    await expect(publicArticleItems.first()).toBeVisible({ timeout: 10000 }); 
    const count = await publicArticleItems.count();
    expect(count).toBeGreaterThan(0);

    // Verify the specific article is now on the public page
    // Public page Django template generates links like /article/<id>/
    const specificArticleLinkOnPublicPage = page.locator(`li.card.mb-3 a[href="/article/${articleId}/"]`);
    await expect(specificArticleLinkOnPublicPage.first()).toBeVisible({ timeout: 10000 });
  });

});
