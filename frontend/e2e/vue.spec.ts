import { test, expect } from "@playwright/test"

test("visits the app root url", async ({ page }, testInfo) => {
  await page.goto("/")
  const metadata = testInfo.project.metadata
  const browserName = metadata.browser.toLowerCase()
  await expect(page.getByRole("link", { name: "view icon Sign In" })).toBeVisible()
  await page.screenshot({
    path: `screenshots/${browserName}.png`,
    fullPage: true,
  })
})
