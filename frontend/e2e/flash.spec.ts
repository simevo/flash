import { test, expect } from "@playwright/test";

test.describe("Flash app", () => {
  test("unauthenticated access to public news items", async ({ page }) => {
    // Navigate to / (public articles list)
    await page.goto("/");

    // Verify that the list is initially empty
    // Assuming the articles are in a list with class "items-list"
    // and each item has class "article-item"
    // Adjust the selector based on the actual HTML structure
    const articles = await page.locator(".article-item").count();
    expect(articles).toBe(0);

    // Alternatively, check for a message indicating no articles
    // Adjust the selector and text based on the actual HTML structure
    await expect(page.locator(".alert-warning")).toHaveText("Non ci sono articoli da visualizzare.");
  });

  test("authenticated access and redirection", async ({ page }) => {
    // Log in as a regular user
    await page.goto("/accounts/login/"); // Assuming this is the login page URL
    await page.fill('input[name="login"]', "testuser"); // Adjust selectors and credentials
    await page.fill('input[name="password"]', "testpassword");
    await page.click('button[type="submit"]');

    // Verify redirection to /res/ (restricted-access section)
    await expect(page).toHaveURL("/res/");

    // Verify that the list of articles in /res/ is initially empty
    // Adjust the selector based on the actual HTML structure
    const articles = await page.locator(".article-item").count();
    expect(articles).toBe(0);

    // Alternatively, check for a message indicating no articles
    // Adjust the selector and text based on the actual HTML structure
    await expect(page.locator(".alert-warning")).toHaveText("Non ci sono articoli da visualizzare.");
  });

  test("poller functionality", async ({ page, request }) => {
    // Log in as a regular user (assuming this is required to access /res/)
    await page.goto("/accounts/login/");
    await page.fill('input[name="login"]', "testuser");
    await page.fill('input[name="password"]', "testpassword");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/res/");

    // Launch the poller
    // This is an assumption, replace with actual poller trigger mechanism
    await request.post("/api/poller/run/"); 

    // Verify that the list of articles in /res/ is now non-empty
    // Adjust the selector based on the actual HTML structure
    await expect(page.locator(".article-item")).not.toHaveCount(0);
  });

  test("public visibility of articles after read", async ({ page, request }) => {
    // Log in as a regular user
    await page.goto("/accounts/login/");
    await page.fill('input[name="login"]', "testuser");
    await page.fill('input[name="password"]', "testpassword");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/res/");

    // Ensure poller has run and there are articles
    await request.post("/api/poller/run/"); // Assuming this triggers poller
    await expect(page.locator(".article-item").first()).toBeVisible(); // Wait for articles to load

    // As a logged-in user, read an article
    // Adjust the selector based on the actual HTML structure
    const articleLink = page.locator(".article-item a").first();
    const articleUrl = await articleLink.getAttribute("href");
    await articleLink.click();

    // Verify that the article is marked as public
    // This is an assumption, replace with actual verification mechanism
    // For example, check for a specific class, an API response, or a UI element
    // If articles have a unique ID, we can use that to check its status via an API call
    // For now, let's assume a class "is-public" is added to the article item
    if (articleUrl) {
      await page.goto("/res/"); // Go back to the list
      const articleId = articleUrl.split("/").pop(); // Extract ID from URL like /res/article/123
      await expect(page.locator(`.article-item[data-article-id="${articleId}"]`)).toHaveClass(/is-public/); // Placeholder selector
    } else {
      throw new Error("Article URL not found");
    }
  });

  test("non-authenticated access to public news items after read", async ({ page, request }) => {
    // This test depends on a previous test marking an article as public.
    // For robustness, it would be better to:
    // 1. Create a specific user and article for this test.
    // 2. Log in as that user.
    // 3. Read the specific article.
    // 4. Log out.
    // 5. Then perform the check as an unauthenticated user.

    // For now, let's assume an article was made public by a previous test run or setup.
    // First, ensure at least one article is made public by a logged-in user.
    // This setup part is similar to the previous test.
    await page.goto("/accounts/login/");
    await page.fill('input[name="login"]', "testuser"); // Use a dedicated test user if possible
    await page.fill('input[name="password"]', "testpassword");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/res/");
    await request.post("/api/poller/run/"); // Ensure articles exist
    await expect(page.locator(".article-item").first()).toBeVisible();
    const articleLink = page.locator(".article-item a").first();
    const articleHref = await articleLink.getAttribute("href");
    if (!articleHref) throw new Error("Failed to get article href for setup");
    const articleIdToMakePublic = articleHref.split("/").pop();
    await articleLink.click(); // Read the article
    // Assuming reading marks it public. We might need an explicit API call or UI interaction here.

    // Log out (important for the next step)
    // Assuming there's a logout button/link. Adjust selector as needed.
    // If direct navigation to logout is possible: await page.goto("/accounts/logout/");
    // Or find a logout button:
    const logoutButton = page.locator('a[href="/accounts/logout/"]'); // Placeholder
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      await expect(page).toHaveURL("/"); // Assuming logout redirects to home or login page
    } else {
      // Fallback or error if logout mechanism isn't straightforward
      console.warn("Logout mechanism not found or not visible. Proceeding as if logged out.");
      // Forcing a new context might be an option in some test setups,
      // but here we'll just navigate away and hope session is cleared or not used for public page.
      await page.goto("/"); // Go to public page
    }


    // Navigate to / (public articles list) as a non-authenticated user
    await page.goto("/");

    // Verify that the list now shows the single read article
    // Adjust the selector based on the actual HTML structure and how public articles are identified
    // This selector assumes the public article will also have 'article-item' and a way to identify it.
    const publicArticleSelector = `.article-item[data-article-id="${articleIdToMakePublic}"]`; // Placeholder
    await expect(page.locator(publicArticleSelector)).toBeVisible();
    await expect(page.locator(".article-item")).toHaveCount(1); // Ensure only one article is public as per test logic
  });
});
