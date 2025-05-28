/* eslint-disable playwright/no-wait-for-selector */

import { test, expect, Page, Dialog } from "@playwright/test"

// Helper function to extract article identifiers (e.g., titles)
async function getArticleIds(page: Page): Promise<number[]> {
  const articleCardSelector = ".wrapper > div" // This might need adjustment if ArticleCard has a specific class like .article-card

  // Wait for ArticleCard elements to be potentially rendered
  await page.waitForSelector(articleCardSelector, { state: "attached", timeout: 10000 })

  // Wait for at least one article card to be visible
  await page.waitForSelector(articleCardSelector, { state: "visible", timeout: 15000 })

  const articles = await page.locator(articleCardSelector).all()

  if (articles.length === 0) {
    console.warn("No article cards found with selector:", articleCardSelector)
    return []
  }

  const identifiers: number[] = []
  for (let i = 0; i < articles.length; i++) {
    const anchor = articles[i].locator("a:nth-child(2)").first()
    try {
      await anchor.waitFor({ state: "visible", timeout: 2000 }) // Wait for title to be visible
      const href = await anchor.getAttribute("href")
      if (href) {
        const id = Number(href.split("/")[3])
        identifiers.push(id)
      }
    } catch (e) {
      console.warn(`Timeout waiting for title element for article at index ${i}`, e)
    }
  }
  return identifiers
}

async function refresh_feed(page: Page, feed_id: number) {
  console.log(`start refreshing feed ${feed_id}`)
  await expect(page.getByRole('button', { name: 'rss iconFonti' })).toBeVisible();
  await page.getByRole('button', { name: 'rss iconFonti' }).click();
  // await page.click('button[id="feeds"]')
  await expect(page.locator('h1')).toContainText('Fonti');
  await expect(page.locator(`#feed_${feed_id}`).getByRole('button', { name: 'Aggiorna la fonte' })).toBeVisible();

  const dialogPromise = new Promise<void>((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('Alert did not appear within 15 seconds'));
    }, 15000);

    const handleDialog = async (dialog: Dialog) => {
      clearTimeout(timeout);
      try {
        expect(dialog.type()).toContain('alert');
        await dialog.dismiss();
        await page.off('dialog', handleDialog);
        resolve();
      } catch (error) {
        reject(error);
      }
    };
    page.on('dialog', handleDialog);
  });

  await page.locator(`#feed_${feed_id}`).getByRole('button', { name: 'Aggiorna la fonte' }).click();
  await dialogPromise;
  console.log(`done refreshing feed ${feed_id}`)
}

test.describe("Authenticated Article View", () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto("/accounts/login/")
    await page.fill('input[name="login"]', "root")
    await page.fill('input[name="password"]', "root")
    await page.click('button[type="submit"]')
    // Wait for navigation to the reserved home page
    await page.waitForURL("/res/", { timeout: 10000 })
    await expect(page).toHaveURL("/res/")
  })

  test("populate articles table", async ({ page }) => {
    await refresh_feed(page, 1)
    await refresh_feed(page, 2)
    await refresh_feed(page, 3)
    await refresh_feed(page, 4)
  })

  test("visits the app root url", async ({ page }) => {
    // Wait for articles to be loaded
    await page.waitForSelector(".wrapper > div", { state: "visible", timeout: 15000 })

    const articleIds = await getArticleIds(page)
    console.log(`article identifiers = ${articleIds}`)
    expect(articleIds.length).toBeGreaterThan(0)
  })
})
