flash - User Guide
==================

## Features

1. **Filtering** – from the main article list (e.g., "Tutti") on the homepage, click on the "filter" button (a floating button with a funnel icon, located on the right side of the screen) to expand an off-canvas sidebar. This sidebar offers several client-side filtering criteria: by language, date, and length. As the filtering criteria are changed, the article list is updated in (almost) real time. Full-text search is also available and is server-side: once you enter one or more keywords, while you wait for the refreshed data to be loaded from the backend a spinner is shown with a reminder that the current list is filtered. All filtering settings are persisted on the device, meaning if you use Flash from two devices, you may see different newsfeeds based on your local filter settings.

2. **Sharing** on social media – from the article detail page, click on the “share” icon and open the link to the article in your favorite social network (Bluesky, Facebook, Linkedin, Mastodon, Reddit, Telegram, Twitter and Whatsapp). You also have the option "Copy link to clipboard" for SMS / email sharing.

3. Saving articles to **lists** – you can create one or more lists then save articles for reading later, bookmarking and exporting. These are managed from the “Saved articles” (heart icon) page.

4. Article **similarity**: the title and content of each article are converted to a vector embedding using the [`use-cmlm-multilingual` sentence transformer](https://huggingface.co/sentence-transformers/use-cmlm-multilingual). This 2020 model is based on LaBSE (Google Language-agnostic BERT sentence embedding model supporting 109 languages), has 472M parameters, embedding dimension 768 and size 1.89G (single-precision floating point FP32). The vector embeddings make it possible to suggest related articles (these are shown below the contents in the articles detail page) and to generate a personalized newsfeed (see next item).

5. **Algorithmic newsfeed** – the "Per te" (Personalized Newsfeed) tab of the homepage displays an article list automatically updated every hour by an algorithm based on your preferences. The newsfeed personalization options are: languages and whitelisted / blacklisted keywords, from the “Settings” page. The algorithm is based on the similarity between vector embeddings of the article and of the whitelisted words.

6. **Preferred Feeds** – the "Preferiti" (Favorites) tab of the homepage displays articles from feeds which have been marked with as favorites (heart icon) in the "Feeds" page.

7. **Excluded Feeds** – feeds which have been marked with as hidden (slashed eye icon) in the "Feeds" page are never shown in the main article list (e.g., "Tutti") on the homepage.

8. Exporting lists as **RSS** feeds – all lists (including the automatic newsfeed) can be exported as anonymized and public RSS feeds (accessible without authentication) so that they can be consumed by other news aggregators or published automatically elsewhere: just click on the button with the RSS icon to copy the link to the clipboard. This feature can be used to create element / matrix rooms for each topic, where a "Feed Rss" bot publishes the relevant article links to bootstrap conversations.

9. **TTS** (text-to-speech) – the Flash platform can read aloud single articles or all the articles in a (manual or automatic) article list, using the local voices on your device. This could be useful for accessibility or to create a kind of "synthetic podcast". While the article(s) are read, a light gray background shows the progress. A tiny, green, floating toolbar at the bottom makes it possible to pause, skip forward and backward and stop altogether the reading. Note: for this to work you need to install local voices (it does not work well with "cloud" voices), and disable the automatic screen locking (otherwise the reading stops abruptly when the screen locks).

10. Automatic **translations** – from the article detail page, logged-in users have access to a "Translate" button which requests the translations for the title and content from a service in the cloud (currently Microsoft Translator). The spinner starts spinning, then after a few seconds if the request succeeds, the article reappears, this time the text in the original language is shown side-by-side with the translation in Italian (or, on narrow displays, one after the other). The feature is available only for articles in a language different from the instance base language, which for the currently only live instance notizie.calomelano.it is Italian.

10. **Dowloading** articles – single articles or all the articles in a (manual or automatic) article list can be exported to HTML, PDF (in A5 page size) and EPUB formats. This is useful to send a copy to a friend or to catch up with those long form articles on your ebook reader.

12. **Mastodon Bot** – Flash can automatically post new articles from a user's newsfeed to a specified Mastodon account. To enable this feature for a user:

    *   Navigate to the user's Profile in the Django admin interface.
    *   Check the `Is bot user` flag.
    *   Fill in the Mastodon API credentials (in Mastodon, go to your Account Preferences -> Development -> New Application, create a new application, fill in Name and Website, with `read`, `profile` and `write:statuses` scopes):
        *   `Mastodon client id`
        *   `Mastodon client secret`
        *   `Mastodon access token`
        *   `Mastodon API base url` (e.g., `https://mastodon.social` or your instance's URL)

    Bot Functionality:

    * The bot runs automatically every hour via a Celery Beat schedule.
    * It scans the personalized newsfeed of the configured bot user for new (unread) articles.
    * New articles found are posted to the Mastodon account associated with the provided credentials.
    * After successfully posting an article, it is marked as 'read' for the bot user to prevent reposting.
    * To avoid spamming, the bot will post a maximum of 5 articles per hour.

13. **OPML export**: Export the [OPML (Outline Processor Markup Language)](https://en.wikipedia.org/wiki/OPML) file containing the list of aggregated feeds from the public URL `/api/feeds/opml/`. This file can be imported into other RSS readers or aggregators.

## Basic usage

Flash offers two distinct experiences depending on whether you are logged in or not.

Guest pages are easy to recognize by the gray color of the header. After logging in, the header color changes to "dark" ([Mocha Mousse](https://www.pantone.com/eu/it/color-of-the-year/2025)) for the SPA.

### Guest visitor

The aggregator presents to the anonymous visitor a restricted list of news items (only articles which some logged-in user has already read). This page is server-rendered by Django.

![Home page](homepage.jpeg)

Clicking on an article opens an interstitial page:

![Article detail](article_detail.jpeg)

which teases the user to log in to read the full text.

### Logged-in user

Once logged in, users are presented with a client-rendered Single Page Application (SPA).

The homepage features a tabbed layout for navigating different article views:

![Home page](res_homepage.jpeg)

The primary tabs include:

- **Tutti** (All Articles): Shows all available articles, paginated and filtered (by language, date, length and full-text search).
- **Letti** (Read Articles): Displays articles you have previously read, paginated.
- **Per te** (Personalized Newsfeed): Your algorithmic newsfeed, tailored to your preferences and feed ratings (see Feature 5).
- **Preferiti** (Favorites): Shows articles from your preferred feeds, paginated.

Articles within these tabbed views are displayed as cards, showing:

- The feed's logo (linking to the feed's page/source).
- The article title. If the article has been translated, both original and translated titles might be shown.
- A short excerpt of the article content.
- The author's name (linking to a page showing other articles by the same author).
- The publication time, displayed as a relative time (e.g., "2 hours ago").
- An estimated reading time for the article.

The all articles, read and favorites lists are paginated, and you can load more articles using a "Load more articles" button. 

Clickin on any article leads to the article detail page:

![Reserved article detail](res_article_detail.jpeg)

which shows the full text (if available), the optional translation, and the related articles.
