import argparse
import html
import logging
import os
import re
import sys
import time
from pathlib import Path

import django
from django.contrib.auth import get_user_model
from mastodon import Mastodon

# Configure Django settings
# This assumes your project is named 'flash' and is in the parent directory
# Adjust as necessary for your project structure
path = Path(__file__).parent / ".." / ".."
sys.path.append(str(path))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from news.models import Articles  # noqa: E402
from news.models import ArticlesCombined  # noqa: E402
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
DRY_RUN = False  # When True, don't actually post to Mastodon, just simulate it


def get_user_and_profile(user_id):
    """
    Retrieve user and profile information.

    Args:
        user_id: The ID of the user to process articles for

    Returns:
        tuple: (user, profile) if successful, (None, None) if not
    """
    try:
        user = get_user_model().objects.get(id=user_id)
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


def get_unpublished_articles(user):
    """
    Fetch not-yet-published articles for a user.

    Args:
        user: User object

    Returns:
        list: List of unpublished articles if successful, empty list if not
    """
    try:
        profile = Profile.objects.get(user=user)
        list_name = profile.mastodon_list_name
        if not list_name:  # Default to "newsfeed" if blank
            list_name = "newsfeed"
            logging.info(
                f"mastodon_list_name not set for user {user.username}, "
                f"defaulting to '{list_name}'.",
            )
        else:
            logging.info(
                f"Using mastodon_list_name '{list_name}' for user {user.username}.",
            )
    except Profile.DoesNotExist:
        logging.warning(
            f"Profile not found for user {user.username}. "
            f"Cannot determine Mastodon list name, defaulting to 'newsfeed'.",
        )
        list_name = "newsfeed"  # Default in case profile is missing

    try:
        article_list = UserArticleLists.objects.get(user=user, name=list_name)
        all_articles_in_list = article_list.articles.all().order_by(
            "-stamp",
        )
    except UserArticleLists.DoesNotExist:
        logging.exception(
            f"No '{list_name}' list found for user {user.username}",
        )
        return []
    except Exception:
        msg = f"Error fetching article list for user {user.username}"
        logging.exception(msg)
        return []

    unpublished_articles = []
    for article in all_articles_in_list:
        user_article = UserArticles.objects.filter(
            user=user,
            article=article,
        ).first()
        if user_article is None or not user_article.published:
            article_combined = ArticlesCombined.objects.get(pk=article.id)
            unpublished_articles.append(article_combined)

    if not unpublished_articles:
        logging.info(f"No unpublished articles found for user {user.username}.")
    else:
        lupa = len(unpublished_articles)
        logging.info(
            f"Found {lupa} unpublished articles for user {user.username}.",
        )

    return unpublished_articles


def create_post_content(article):
    """
    Create formatted post content for an article.

    Args:
        article: Article object

    Returns:
        str: Formatted post content
    """
    # Create the post content
    title = article.title_original if article.title_original else article.title
    excerpt = article.excerpt
    # remove html tags
    excerpt = re.sub(r"<[^>]*>", "", excerpt)
    # convert html entities to unicode
    excerpt = html.unescape(excerpt)
    # remove multiple whitespaces
    excerpt = re.sub(r"[\s]+", " ", excerpt)
    # remove newlines
    excerpt = excerpt.replace("\n", "")
    # trim
    excerpt = excerpt.strip()[:300]

    link = f"https://notizie.calomelano.it/article/{article.id}"
    post_content = f"{title}\n\n{excerpt} ...\n\n{link}"

    if len(post_content) > MAX_POST_LENGTH:
        post_content = f"{title}\n\n{link}"

    if len(post_content) > MAX_POST_LENGTH:
        # Truncate the title if needed
        overflow = len(post_content) - MAX_POST_LENGTH + 3  # +3 for ellipsis
        title_length = len(title)
        link_length = 23  # links are counted as 23 characters regardless of length
        available_length = title_length + link_length - overflow
        if available_length > 0:
            truncated_title = article.title[:available_length]
            post_content = f"{truncated_title}\n\n{link}"
        else:
            post_content = f"{link}"

    return post_content


def post_article_to_mastodon(user, article, mastodon_client, delay_seconds=None):
    """
    Post an article to Mastodon and mark it as published.

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
        if DRY_RUN:
            msg = f"DRY RUN: post article {article.id} for user {user.username}"
            logging.info(msg)
            logging.info(f"DRY RUN: Post content would be: {post_content}")
        else:
            mastodon_client.status_post(status=post_content, language=article.language)
            msg = f"Posted article {article.id} for user {user.username}"
            logging.info(msg)

        # Mark as published (even in dry run mode)
        article_simple = Articles.objects.get(pk=article.id)
        user_article_status, _ = UserArticles.objects.get_or_create(
            user=user,
            article=article_simple,
        )
        user_article_status.published = True
        user_article_status.save()
        logging.info(
            f"Marked article {article.id} as published for user {user.username}",
        )
    except Exception:
        msg = f"Error posting article {article.id} for user {user.username}"
        logging.exception(msg)
        return False
    return True


def main(user_id, max_articles=None, delay_seconds=None):
    """
    Main function for the Mastodon bot.
    Fetches unpublished articles for a user and posts them to Mastodon.

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
    mastodon_client = None
    if not DRY_RUN:
        mastodon_client = initialize_mastodon_client(user, profile)
        if not mastodon_client:
            return

    # Get unpublished articles
    unpublished_articles = get_unpublished_articles(user)
    if not unpublished_articles:
        return

    # Post to Mastodon and Mark as published
    # (up to MAX_ARTICLES_PER_RUN or custom limit)
    max_to_post = max_articles if max_articles is not None else MAX_ARTICLES_PER_RUN
    articles_to_post = unpublished_articles[:max_to_post]

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
    dry_run_prefix = "DRY RUN: " if DRY_RUN else ""
    action_verb = "would be" if DRY_RUN else "were"
    logging.info(
        f"{dry_run_prefix}Summary for user {user.username}: "
        f"{successfully_posted} new articles {action_verb} posted successfully, "
        f"{failed_posts} failed posts, "
        f"{len(unpublished_articles) - len(articles_to_post)} new articles queued.",
    )


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Mastodon bot for posting unpublished articles to Mastodon",
    )

    # Add arguments
    parser.add_argument(
        "user_id",
        type=int,
        help="ID of the user to process articles for",
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=None,
        help=f"Maximum number of articles to post (default: {MAX_ARTICLES_PER_RUN})",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=None,
        dest="delay_seconds",
        help=f"Delay between posts in seconds (default: {POST_DELAY_SECONDS})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry run mode (no actual posting)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Set dry run flag if specified
    if args.dry_run:
        DRY_RUN = True
        print("Running in DRY RUN mode - no posts will be sent to Mastodon")  # noqa: T201

    # Run main function with parsed arguments
    main(args.user_id, args.max_articles, args.delay_seconds)
