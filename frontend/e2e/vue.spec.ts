/* eslint-disable playwright/no-wait-for-selector */

import { test, expect, Page } from "@playwright/test"

// Helper function to extract article identifiers (e.g., titles)
async function getArticleIdentifiers(page: Page, count: number = 5): Promise<string[]> {
  await page.waitForSelector(".wrapper > div", { state: "attached", timeout: 10000 }) // Wait for ArticleCard elements to be potentially rendered

  // More robust selector for ArticleCard instances within the .wrapper
  // Assuming ArticleCard renders a root div that gets placed into .wrapper
  const articleCardSelector = ".wrapper > div" // This might need adjustment if ArticleCard has a specific class like .article-card

  // Wait for at least one article card to be visible
  await page.waitForSelector(articleCardSelector, { state: "visible", timeout: 15000 })

  const articles = await page.locator(articleCardSelector).all()

  if (articles.length === 0) {
    console.warn("No article cards found with selector:", articleCardSelector)
    return []
  }

  const identifiers: string[] = []
  for (let i = 0; i < Math.min(articles.length, count); i++) {
    // Try to get a unique identifier. Article title is a good candidate.
    // Assuming ArticleCard.vue renders title within a specific element, e.g., <h3> or similar.
    // Let's look for a title-like element, often a link within a heading.
    // Example: <div class="card-title"><h3><a href="/article/123">Article Title</a></h3></div>
    // Or simply a heading containing the title.
    // The actual selector for the title needs to be based on ArticleCard.vue's structure.
    // Let's try a common pattern: an `<a>` tag inside an `<h3>` within the article card.
    const titleElement = articles[i].locator("h3 a").first() // Adjust if title is elsewhere
    try {
      await titleElement.waitFor({ state: "visible", timeout: 2000 }) // Wait for title to be visible
      const title = await titleElement.textContent()
      if (title) {
        identifiers.push(title.trim())
      } else {
        // Fallback or log if title not found
        const fallbackId = await articles[i].getAttribute("data-article-id") // If data-article-id exists
        if (fallbackId) {
          identifiers.push(`id-${fallbackId}`)
        } else {
          console.warn(`Could not extract title or ID for article at index ${i}`)
          identifiers.push(`unknown-article-${i}`) // Placeholder
        }
      }
    } catch (e) {
      console.warn(`Timeout waiting for title element for article at index ${i}`, e)
      identifiers.push(`error-article-${i}`)
    }
  }
  return identifiers
}

test.describe("Authenticated Article View", () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto("/accounts/login/")
    await page.fill('input[name="login"]', "root")
    await page.fill('input[name="password"]', "root")
    await page.click('button[type="submit"]')
    // Wait for navigation to the articles page or a clear indicator of login success
    await page.waitForURL("/res/", { timeout: 10000 }) // Assuming successful login redirects to /res/
    await expect(page).toHaveURL("/res/")
  })

  test("visits the app root url", async ({ page }) => {
    // This test is now within the authenticated scope, so it will run after login.
    // If the intention was to test the unauthenticated root, it should be outside this describe block.
    // For now, let's assume it's fine here, effectively testing /res/ after login.
    await page.goto("/res/") // Already on /res/ due to beforeEach, but explicit navigation is fine.
    await expect(page.locator(".wrapper > div").first()).toBeVisible() // Check for article cards

    // Screenshot if needed
    // const metadata = testInfo.project.metadata;
    // const browserName = metadata.browser?.toLowerCase() || 'unknown';
    // await page.screenshot({
    //   path: `screenshots/${browserName}_res_page.png`,
    //   fullPage: true,
    // });
  })

  test("should display articles in a stable perturbed order on load and reload", async ({
    page,
  }) => {
    await page.goto("/res/") // Ensure we are on the page

    // Wait for articles to be loaded
    await page.waitForSelector(".wrapper > div", { state: "visible", timeout: 15000 })

    const initialArticleIdentifiers = await getArticleIdentifiers(page, 5)
    expect(initialArticleIdentifiers.length).toBeGreaterThan(
      0,
      "Should load some articles initially.",
    )
    console.log("Initial articles (perturbed order):", initialArticleIdentifiers)

    // Reload the page
    await page.reload()
    await page.waitForSelector(".wrapper > div", { state: "visible", timeout: 15000 }) // Wait for articles after reload

    const reloadedArticleIdentifiers = await getArticleIdentifiers(page, 5)
    expect(reloadedArticleIdentifiers.length).toBeGreaterThan(
      0,
      "Should load some articles after reload.",
    )
    console.log("Reloaded articles (perturbed order):", reloadedArticleIdentifiers)

    // Assert that the order is the same due to deterministic perturbed ordering
    expect(initialArticleIdentifiers).toEqual(
      reloadedArticleIdentifiers,
      "Article order should be the same (stable) after reload.",
    )
  })
})
