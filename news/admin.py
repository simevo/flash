from django.contrib import admin

from .models import Feeds
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_bot_user", "newsletter", "list_frequency")
    list_filter = ("is_bot_user", "newsletter")
    search_fields = ("user__username", "user__email")
    fieldsets = (
        (
            None,
            {
                "fields": ("user", "is_bot_user", "newsletter", "last_access"),
            },
        ),
        (
            "Email List Settings",
            {
                "fields": (
                    "list_email",
                    "list_frequency",
                    "list_news",
                    "list_format",
                    "list_hour",
                    "list_fulltext",
                ),
            },
        ),
        (
            "Content Preferences",
            {
                "fields": (
                    "whitelist",
                    "whitelist_authors",
                    "blacklist",
                    "blacklist_authors",
                    "tags",
                    "languages",
                ),
            },
        ),
        (
            "Ranking Settings",
            {
                "fields": (
                    "sociality_weight",
                    "gravity",
                    "age_divider",
                    "feed_weight",
                    "list_weight",
                ),
            },
        ),
        (
            "Mastodon Integration",
            {
                "fields": (
                    "mastodon_api_base_url",
                    "mastodon_client_id",
                    "mastodon_client_secret",
                    "mastodon_access_token",
                ),
            },
        ),
    )


admin.site.register(Feeds)
