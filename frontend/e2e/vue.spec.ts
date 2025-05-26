import { test, expect, Page } from "@playwright/test";

// Helper function to extract article identifiers (e.g., titles)
async function getArticleIdentifiers(page: Page, count: number = 5): Promise<string[]> {
  await page.waitForSelector(".wrapper > div", { state: "attached", timeout: 10000 }); // Wait for ArticleCard elements to be potentially rendered
  
  // More robust selector for ArticleCard instances within the .wrapper
  // Assuming ArticleCard renders a root div that gets placed into .wrapper
  const articleCardSelector = ".wrapper > div"; // This might need adjustment if ArticleCard has a specific class like .article-card

  // Wait for at least one article card to be visible
  await page.waitForSelector(articleCardSelector, { state: "visible", timeout: 15000 });

  const articles = await page.locator(articleCardSelector).all();
  
  if (articles.length === 0) {
    console.warn("No article cards found with selector:", articleCardSelector);
    return [];
  }

  const identifiers: string[] = [];
  for (let i = 0; i < Math.min(articles.length, count); i++) {
    // Try to get a unique identifier. Article title is a good candidate.
    // Assuming ArticleCard.vue renders title within a specific element, e.g., <h3> or similar.
    // Let's look for a title-like element, often a link within a heading.
    // Example: <div class="card-title"><h3><a href="/article/123">Article Title</a></h3></div>
    // Or simply a heading containing the title.
    // The actual selector for the title needs to be based on ArticleCard.vue's structure.
    // Let's try a common pattern: an `<a>` tag inside an `<h3>` within the article card.
    const titleElement = articles[i].locator("h3 a").first(); // Adjust if title is elsewhere
    try {
      await titleElement.waitFor({ state: "visible", timeout: 2000}); // Wait for title to be visible
      const title = await titleElement.textContent();
      if (title) {
        identifiers.push(title.trim());
      } else {
        // Fallback or log if title not found
        const fallbackId = await articles[i].getAttribute("data-article-id"); // If data-article-id exists
        if (fallbackId) {
          identifiers.push(`id-${fallbackId}`);
        } else {
          console.warn(`Could not extract title or ID for article at index ${i}`);
          identifiers.push(`unknown-article-${i}`); // Placeholder
        }
      }
    } catch (e) {
      console.warn(`Timeout waiting for title element for article at index ${i}`, e);
      identifiers.push(`error-article-${i}`);
    }
  }
  return identifiers;
}


test.describe("Authenticated Article View", () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto("/accounts/login/");
    await page.fill('input[name="username"]', "testuser");
    await page.fill('input[name="password"]', "testpassword");
    await page.click('button[type="submit"]');
    // Wait for navigation to the articles page or a clear indicator of login success
    await page.waitForURL("/res/", { timeout: 10000 }); // Assuming successful login redirects to /res/
    await expect(page).toHaveURL("/res/");
  });

  test("visits the app root url", async ({ page }, testInfo) => {
    // This test is now within the authenticated scope, so it will run after login.
    // If the intention was to test the unauthenticated root, it should be outside this describe block.
    // For now, let's assume it's fine here, effectively testing /res/ after login.
    await page.goto("/res/"); // Already on /res/ due to beforeEach, but explicit navigation is fine.
    await expect(page.locator(".wrapper > div").first()).toBeVisible(); // Check for article cards

    // Screenshot if needed
    // const metadata = testInfo.project.metadata;
    // const browserName = metadata.browser?.toLowerCase() || 'unknown';
    // await page.screenshot({
    //   path: `screenshots/${browserName}_res_page.png`,
    //   fullPage: true,
    // });
  });

  test("should display articles in random order on load and reload", async ({ page }) => {
    await page.goto("/res/"); // Ensure we are on the page

    // Wait for articles to be loaded
    await page.waitForSelector(".wrapper > div", { state: "visible", timeout: 15000 });

    const initialArticleIdentifiers = await getArticleIdentifiers(page, 5);
    expect(initialArticleIdentifiers.length).toBeGreaterThan(0, "Should load some articles initially.");
    console.log("Initial articles:", initialArticleIdentifiers);


    // Reload the page
    await page.reload();
    await page.waitForSelector(".wrapper > div", { state: "visible", timeout: 15000 }); // Wait for articles after reload

    const reloadedArticleIdentifiers = await getArticleIdentifiers(page, 5);
    expect(reloadedArticleIdentifiers.length).toBeGreaterThan(0, "Should load some articles after reload.");
    console.log("Reloaded articles:", reloadedArticleIdentifiers);

    // Assert that the order is different
    // This has a small chance of failing if the random order is the same,
    // but with enough articles and a decent shuffle, it's unlikely for the top 5.
    expect(initialArticleIdentifiers).not.toEqual(reloadedArticleIdentifiers, "Article order should be different after reload.");
  });

  test("should load more articles and maintain randomization", async ({ page }) => {
    await page.goto("/res/");
    await page.waitForSelector(".wrapper > div", { state: "visible", timeout: 15000 });

    const initialPage1Articles = await getArticleIdentifiers(page, 5);
    expect(initialPage1Articles.length).toBeGreaterThan(0);
    console.log("Initial page 1 articles (first 5):", initialPage1Articles);

    const initialArticleElements = await page.locator(".wrapper > div").count();
    expect(initialArticleElements).toBeGreaterThan(0);

    // Find and click the 'load more' button
    const loadMoreButton = page.locator('button:has-text("Carica altri articoli")');
    await expect(loadMoreButton).toBeVisible({ timeout: 10000 });
    await loadMoreButton.click();

    // Wait for new articles to be loaded
    // Option 1: Wait for a specific network response if applicable (e.g., next page of API call)
    // Option 2: Wait for the number of article cards to increase
    await page.waitForFunction((initialCount) => {
      return document.querySelectorAll(".wrapper > div").length > initialCount;
    }, initialArticleElements, { timeout: 15000 });

    const articlesAfterLoadMore = await page.locator(".wrapper > div").count();
    expect(articlesAfterLoadMore).toBeGreaterThan(initialArticleElements, "More articles should be loaded.");
    console.log(`Articles loaded: initial=${initialArticleElements}, after_load_more=${articlesAfterLoadMore}`);

    // (Optional) Check that the newly loaded articles are different from the first set.
    // This requires identifying which articles are "new".
    // If page size is known (e.g. 200 from backend), we can try to get articles from the "second page" part.
    // For simplicity here, we'll just re-get the first 5. Due to backend randomization on *each*
    // API call (which `fetchMoreArticles` does for `next.value`), the whole list's order
    // might not be stable in the way `order_by("?")` would be.
    // The current backend implementation shuffles IDs *then* paginates.
    // So, clicking "load more" fetches the *next* chunk of those *already shuffled* IDs.
    // The test for randomization is primarily on page reload.
    // However, if `fetchMoreArticles` somehow triggered a full re-fetch and re-shuffle of page 1 too,
    // then initialPage1Articles might change. Let's verify this.

    const page1ArticlesAfterLoadMore = await getArticleIdentifiers(page, 5);
    console.log("Page 1 articles after load more (first 5):", page1ArticlesAfterLoadMore);
    
    // In the current backend implementation, the initial set of articles (page 1)
    // should NOT change just by loading more articles for page 2.
    // The randomization happens when the initial queryset for the view is prepared.
    // Subsequent 'load more' operations fetch the next pages of that *same* randomized queryset.
    // If they *were* different, it would imply page 1 is re-shuffling on load more, which is not the design.
    expect(initialPage1Articles).toEqual(page1ArticlesAfterLoadMore, "First page articles should remain the same after loading more.");

    // To verify new articles are different, we'd need to get identifiers for articles
    // beyond the initial set. For example, if 200 articles are on page 1, get articles 201-205.
    // This requires knowing the page size accurately on the frontend.
    // For now, we've confirmed more articles load.
  });
});
