flash - User Guide
==================

## Features

1. **Filtering** – from the home page, click on the "filter" button (the one with the funnel icon in the top-left) to expand an hidden “off-canvas” sidebar that offers several client-side filtering criteria: by language, date, length and source feed. As the filtering criteria are changed, the article list is updated in (almost) real time, as almost all the filtering is client-side. Finally, full-text search is server-side: once you enter one or more keywords, while you wait for the refreshed data to be loaded from the backend a spinner is shown with a reminder that the current list is filtered. All filtering settings are persisted on the device which means that if you use Flash from two devices you may see different newsfeeds.

2. **Sharing** on social media – from the article detail page, click on the “share” icon and open the link to the article in your favorite social network (Bluesky, Facebook, Linkedin, Mastodon, Reddit, Telegram, Twitter and Whatsapp). You also have the option "Copy link to clipboard" for SMS / email sharing.

3. Saving articles to **lists** – you can create one or more lists then save articles for reading later, bookmarking and exporting. These are managed from the “Saved articles” (heart icon) page.

4. **Algorithmic newsfeed** based on user preferences – a special article list (identified by the “robot” icon) is the "newsfeed" which is automatically updated every hour by the algorithm™ according to your preferences. The newsfeed personalization options are set:

   - languages and whitelisted / blacklisted keywords, from the “Settings” page

   - feeds ratings: up to 5 stars (positive) and down to 5 thumbs-downs (if you rate a feed with 5 thumbs-downs, their articles will disappear from your personalized newsfeed completely!).

5. Exporting lists as **RSS** feeds – all lists (including the automatic newsfeed) can be exported as anonymized and public RSS feeds (accessible without authentication) so that they can be consumed by other news aggregators or published automatically elsewhere: just click on the button with the RSS icon to copy the link to the clipboard. This feature can be used to create element / matrix rooms for each topic, where a "Feed Rss" bot publishes the relevant article links to bootstrap conversations.

6. **TTS** (text-to-speech) – the Flash platform can read aloud single articles or all the articles in a (manual or automatic) article list, using the local voices on your device. This could be useful for accessibility or to create a kind of "synthetic podcast". While the article(s) are read, a light gray background shows the progress. A tiny, green, floating toolbar at the bottom makes it possible to pause, skip forward and backward and stop altogether the reading. Note: for this to work you need to install local voices (it does not work well with "cloud" voices), and disable the automatic screen locking (otherwise the reading stops abruptly when the screen locks).

7. Automatic **translations** – from the article detail page, logged-in users have access to a "Translate" button which requests the translations for the title and content from a service in the cloud (currently Microsoft Translator). The spinner starts spinning, then after a few seconds if the request succeeds, the article reappears, this time the text in the original language is shown side-by-side with the translation in Italian (or, on narrow displays, one after the other). The feature is available only for articles in a language different from the instance base language, which for the currently only live instance notizie.calomelano.it is Italian.

8. **Dowloading** articles – single articles or all the articles in a (manual or automatic) article list can be exported to HTML, PDF (in A5 page size) and EPUB formats. This is useful to send a copy to a friend or to catch up with those long form articles on your ebook reader.

9. Article **similarity** and similarity-based search: the title and content of each article are converted to a vector embedding using the [`use-cmlm-multilingual` sentence transformer](https://huggingface.co/sentence-transformers/use-cmlm-multilingual). This 2020 model is based on LaBSE (Google Language-agnostic BERT sentence embedding model supporting 109 languages), has 472M params, embedding dimension: 768 and size 1.89G (single-precision floating point FP32).

10. **Mastodon Bot** – Flash can automatically post new articles from a user's newsfeed to a specified Mastodon account.

    To enable this feature for a user:
    *   Navigate to the user's Profile in the Django admin interface.
    *   Check the `Is bot user` flag.
    *   Fill in the Mastodon API credentials (go to your Account Preferences -> Development -> New Application, create a new application, fill in Name and Website, with `read`, `profile` and `write:statuses` scopes):
        *   `Mastodon client id`
        *   `Mastodon client secret`
        *   `Mastodon access token`
        *   `Mastodon api base url` (e.g., `https://mastodon.social` or your instance's URL)

    Bot Functionality:
    *   The bot runs automatically every hour via a Celery Beat schedule.
    *   It scans the 'newsfeed' list (`UserArticleLists` named 'newsfeed') of the configured bot user for new (unread) articles.
    *   New articles found are posted to the Mastodon account associated with the provided credentials. The post format is: "New article: {article.title} - {article.url}".
    *   After successfully posting an article, it is marked as 'read' for that user in `UserArticles` to prevent reposting.
    *   To avoid spamming, the bot will post a maximum of 5 articles per hour.

11. **OPML export**: Export the [OPML (Outline Processor Markup Language)](https://en.wikipedia.org/wiki/OPML) file containing the list of aggregated feeds from the public URL `/api/feeds/opml/`. This file can be imported into other RSS readers or aggregators.

## Basic usage

The aggregator presents to the anonymous visitor a restricted list of news items (only articles which some logged-in user has already read):

![Home page](homepage.jpeg)

Clicking on an article opens an interstitial page:

![Article detail](article_detail.jpeg)

which teases the user to log in to read the full text:

![Reserved article detail](res_article_detail.jpeg)

Logged in users also see more information on the home page (for example an extract of the article):

![Reserved home page](res_homepage.jpeg)

Anonymous pages are easy to recognize by the gray color of the header (after logging in the header color changes to "dark" [Mocha Mousse](https://www.pantone.com/eu/it/color-of-the-year/2025)), but they also differ because they are Server-side-rendered by Django, whereas the reserved pages are part of a client-rendered Single Page Application.
