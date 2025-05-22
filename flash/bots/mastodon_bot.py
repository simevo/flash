import logging
import os
import sys

import django
from mastodon import Mastodon

# Configure Django settings
# This assumes your project is named 'flash' and is in the parent directory
# Adjust as necessary for your project structure
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from news.models import Articles, Profile, UserArticleLists, UserArticles  # noqa: E402

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MAX_ARTICLES_PER_RUN = 5


def main(user_id):
    """
    Main function for the Mastodon bot.
    Fetches unread articles for a user and posts them to Mastodon.
    """
    try:
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)
    except User.DoesNotExist:
        logging.error(f"User with ID {user_id} not found.")
        return
    except Profile.DoesNotExist:
        logging.error(f"Profile for user {user.username} not found.")
        return

    # Retrieve Mastodon API credentials
    client_id = profile.mastodon_client_id
    client_secret = profile.mastodon_client_secret
    access_token = profile.mastodon_access_token
    api_base_url = profile.mastodon_api_base_url

    if not all([client_id, client_secret, access_token, api_base_url]):
        logging.error(f"Mastodon API credentials not fully configured for user {user.username}.")
        return

    # Initialize Mastodon API client
    try:
        mastodon_client = Mastodon(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            api_base_url=api_base_url,
        )
        mastodon_client.account_verify_credentials()  # Verify credentials
    except Exception as e:
        logging.error(f"Failed to initialize Mastodon API client for user {user.username}: {e}")
        return

    logging.info(f"Successfully initialized Mastodon client for user {user.username}")

    # Fetch Unread Articles
    try:
        newsfeed_list = UserArticleLists.objects.get(user=user, name="newsfeed")
        all_articles_in_list = newsfeed_list.articles.all().order_by("-stamp")  # newest first
    except UserArticleLists.DoesNotExist:
        logging.info(f"No 'newsfeed' list found for user {user.username}.")
        return
    except Exception as e:
        logging.error(f"Error fetching newsfeed for user {user.username}: {e}")
        return

    unread_articles = []
    for article in all_articles_in_list:
        user_article_status, created = UserArticles.objects.get_or_create(
            user=user, article=article
        )
        if not user_article_status.read:
            unread_articles.append(article)

    if not unread_articles:
        logging.info(f"No unread articles found for user {user.username}.")
        return

    logging.info(f"Found {len(unread_articles)} unread articles for user {user.username}.")

    # Post to Mastodon and Mark as Read (up to MAX_ARTICLES_PER_RUN)
    articles_to_post = unread_articles[:MAX_ARTICLES_PER_RUN]

    for article in articles_to_post:
        post_content = f"New article: {article.title} - {article.url}"
        try:
            mastodon_client.status_post(post_content)
            logging.info(f"Successfully posted to Mastodon for user {user.username}: {article.title}")

            # Mark as read
            user_article_status, _ = UserArticles.objects.get_or_create(
                user=user, article=article
            )
            user_article_status.read = True
            user_article_status.save()
            logging.info(f"Marked article as read for user {user.username}: {article.title}")

        except Exception as e:
            logging.error(
                f"Error posting article to Mastodon for user {user.username} (article: {article.title}): {e}"
            )
    logging.info(f"Finished processing articles for user {user.username}.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mastodon_bot.py <user_id>")
        sys.exit(1)

    try:
        user_id_arg = int(sys.argv[1])
        main(user_id_arg)
    except ValueError:
        print("Error: user_id must be an integer.")
        sys.exit(1)
