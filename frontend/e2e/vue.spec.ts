import { test, expect } from "@playwright/test"

// See here how to get started:
// https://playwright.dev/docs/intro
test("visits the app root url", async ({ page }) => {
  await page.goto("/")
  // Wait for 3 seconds
  await page.waitForTimeout(5000)
  await page.screenshot({ path: "screenshot.png" })
  await expect(page.locator("h1")).toHaveText("o")
})
