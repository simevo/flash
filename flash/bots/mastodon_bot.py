import logging
import os
import sys
import time
from pathlib import Path

import django
from mastodon import Mastodon

# Configure Django settings
# This assumes your project is named 'flash' and is in the parent directory
# Adjust as necessary for your project structure
path = Path(__file__).parent / ".." / ".."
sys.path.append(str(path))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from news.models import Profile  # noqa: E402
from news.models import UserArticleLists  # noqa: E402
from news.models import UserArticles  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Configuration constants
MAX_ARTICLES_PER_RUN = 5  # Maximum number of articles to post in a single run
POST_DELAY_SECONDS = 2  # Delay between posts to avoid flooding
MAX_POST_LENGTH = 500  # Maximum length for a Mastodon post


def get_user_and_profile(user_id):
    """
    Retrieve user and profile information.

    Args:
        user_id: The ID of the user to process articles for

    Returns:
        tuple: (user, profile) if successful, (None, None) if not
    """
    try:
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)
    except User.DoesNotExist:
        logging.exception(f"User with ID {user_id} not found.")
        return None, None
    except Profile.DoesNotExist:
        logging.exception(f"Profile for user {user.username} not found.")
        return None, None
    return user, profile


def initialize_mastodon_client(user, profile):
    """
    Initialize and verify Mastodon API client.

    Args:
        user: User object
        profile: Profile object with Mastodon credentials

    Returns:
        Mastodon client if successful, None if not
    """
    # Retrieve Mastodon API credentials
    client_id = profile.mastodon_client_id
    client_secret = profile.mastodon_client_secret
    access_token = profile.mastodon_access_token
    api_base_url = profile.mastodon_api_base_url

    if not all([client_id, client_secret, access_token, api_base_url]):
        logging.error(
            f"Mastodon API credentials not fully configured for user {user.username}.",
        )
        return None

    # Initialize Mastodon API client
    try:
        mastodon_client = Mastodon(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            api_base_url=api_base_url,
        )
        mastodon_client.account_verify_credentials()  # Verify credentials
        logging.info(
            f"Successfully initialized Mastodon client for user {user.username}",
        )
    except Exception:
        msg = f"Failed to initialize Mastodon API client for user {user.username}"
        logging.exception(msg)
        return None
    return mastodon_client


def get_unread_articles(user):
    """
    Fetch unread articles for a user.

    Args:
        user: User object

    Returns:
        list: List of unread articles if successful, empty list if not
    """
    try:
        newsfeed_list = UserArticleLists.objects.get(user=user, name="newsfeed")
        all_articles_in_list = newsfeed_list.articles.all().order_by(
            "-stamp",
        )  # newest first
    except UserArticleLists.DoesNotExist:
        logging.info(f"No 'newsfeed' list found for user {user.username}.")
        return []
    except Exception:
        msg = f"Error fetching newsfeed for user {user.username}"
        logging.exception(msg)
        return []

    unread_articles = []
    for article in all_articles_in_list:
        user_article_status, created = UserArticles.objects.get_or_create(
            user=user,
            article=article,
        )
        if not user_article_status.read:
            unread_articles.append(article)

    if not unread_articles:
        logging.info(f"No unread articles found for user {user.username}.")
    else:
        logging.info(
            f"Found {len(unread_articles)} unread articles for user {user.username}.",
        )

    return unread_articles


def create_post_content(article):
    """
    Create formatted post content for an article.

    Args:
        article: Article object

    Returns:
        str: Formatted post content
    """
    # Create a richer post content with date if available
    post_date = ""
    if hasattr(article, "stamp") and article.stamp:
        post_date = f"[{article.stamp.strftime('%Y-%m-%d')}] "

    # Create the post content
    post_content = f"NEW: {post_date}{article.title}\n\n"

    # Add source if available
    if hasattr(article, "feed") and article.feed and hasattr(article.feed, "name"):
        post_content += f"Source: {article.feed.name}\n\n"

    # Add URL and hashtags
    post_content += f"{article.url}"

    # Ensure the post doesn't exceed Mastodon's character limit
    if len(post_content) > MAX_POST_LENGTH:
        # Truncate the title if needed
        overflow = len(post_content) - MAX_POST_LENGTH + 3  # +3 for ellipsis
        title_length = len(article.title)
        if overflow < title_length:
            truncated_title = article.title[: (title_length - overflow)] + "..."
            post_content = post_content.replace(article.title, truncated_title)

    return post_content


def post_article_to_mastodon(user, article, mastodon_client, delay_seconds=None):
    """
    Post an article to Mastodon and mark it as read.

    Args:
        user: User object
        article: Article object
        mastodon_client: Mastodon client
        delay_seconds: Optional delay seconds between posts

    Returns:
        bool: True if successful, False if not
    """
    post_content = create_post_content(article)

    try:
        mastodon_client.status_post(post_content)
        msg = f"Posted article [{article.title}] for user {user.username}"
        logging.info(msg)

        # Mark as read
        user_article_status, _ = UserArticles.objects.get_or_create(
            user=user,
            article=article,
        )
        user_article_status.read = True
        user_article_status.save()
        logging.info(
            f"Marked article [{article.title}] as read for user {user.username}",
        )
    except Exception:
        msg = f"Error posting article [{article.title}] for user {user.username}"
        logging.exception(msg)
        return False
    return True


def main(user_id, max_articles=None, delay_seconds=None):
    """
    Main function for the Mastodon bot.
    Fetches unread articles for a user and posts them to Mastodon.

    Args:
        user_id: The ID of the user to process articles for
        max_articles: Optional override for MAX_ARTICLES_PER_RUN
        delay_seconds: Optional override for POST_DELAY_SECONDS
    """
    # Get user and profile
    user, profile = get_user_and_profile(user_id)
    if not user or not profile:
        return

    # Initialize Mastodon client
    mastodon_client = initialize_mastodon_client(user, profile)
    if not mastodon_client:
        return

    # Get unread articles
    unread_articles = get_unread_articles(user)
    if not unread_articles:
        return

    # Post to Mastodon and Mark as Read (up to MAX_ARTICLES_PER_RUN or custom limit)
    max_to_post = max_articles if max_articles is not None else MAX_ARTICLES_PER_RUN
    articles_to_post = unread_articles[:max_to_post]

    successfully_posted = 0
    failed_posts = 0

    for i, article in enumerate(articles_to_post):
        is_last_article = i == len(articles_to_post) - 1
        success = post_article_to_mastodon(user, article, mastodon_client)

        if success:
            successfully_posted += 1
        else:
            failed_posts += 1

        # Add delay between posts to avoid flooding the timeline
        post_delay = delay_seconds if delay_seconds is not None else POST_DELAY_SECONDS
        if post_delay > 0 and not is_last_article:  # Don't delay after the last article
            time.sleep(post_delay)

    # Log summary
    logging.info(
        f"Summary for user {user.username}: "
        f"{successfully_posted} new articles posted successfully, "
        f"{failed_posts} failed posts, "
        f"{len(unread_articles) - len(articles_to_post)} new articles queued.",
    )


if __name__ == "__main__":
    min_args = 2
    if len(sys.argv) < min_args:
        print("Usage: python mastodon_bot.py <user_id> [max_articles] [delay_seconds]")  # noqa: T201
        print("  max_articles: Maximum number of articles to post (default: 5)")  # noqa: T201
        print("  delay_seconds: Delay between posts in seconds (default: 2)")  # noqa: T201
        sys.exit(1)

    try:
        user_id_arg = int(sys.argv[1])

        # Parse optional arguments
        max_articles_arg = None
        if len(sys.argv) > min_args:
            max_articles_arg = int(sys.argv[min_args])

        delay_seconds_arg = None
        if len(sys.argv) > min_args + 1:
            delay_seconds_arg = int(sys.argv[min_args + 1])

        main(user_id_arg, max_articles_arg, delay_seconds_arg)
    except ValueError:
        print("Error: Arguments must be integers.")  # noqa: T201
        sys.exit(1)
