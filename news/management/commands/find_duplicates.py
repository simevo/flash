import json
import logging
from django.core.management.base import BaseCommand, CommandParser
from news.models import Articles
from pgvector.django import CosineDistance

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Finds duplicate articles based on embedding similarity."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--threshold",
            type=float,
            default=0.05,
            help="Similarity threshold for considering articles as duplicates (default: 0.05)",
        )
        parser.add_argument(
            "--min-id",
            type=int,
            default=0,
            help="Minimum article ID to process (default: 0)",
        )

    def handle(self, *args, **options):
        threshold = options["threshold"]
        min_id = options["min_id"]

        logger.info(
            f"Starting duplicate detection with threshold: {threshold} and min_id: {min_id}"
        )

        # Fetch articles with non-null embeddings and ID greater than min_id
        articles_to_process = Articles.objects.filter(
            use_cmlm_multilingual__isnull=False, id__gt=min_id
        ).order_by("id")

        article_count = articles_to_process.count()
        logger.info(f"Found {article_count} articles with embeddings to process.")

        duplicate_sets = []
        processed_article_ids = set()

        for i, source_article in enumerate(articles_to_process):
            if source_article.id in processed_article_ids:
                continue  # Already part of a duplicate set

            logger.info(
                f"Processing article {i+1}/{article_count}: ID {source_article.id}"
            )

            # Find potential duplicates (target articles)
            # Target articles must have ID > source_article.id to avoid redundant checks and self-comparison
            potential_duplicates = (
                Articles.objects.filter(
                    use_cmlm_multilingual__isnull=False, id__gt=source_article.id
                )
                .annotate(
                    distance=CosineDistance(
                        "use_cmlm_multilingual", source_article.use_cmlm_multilingual
                    )
                )
                .filter(distance__lt=threshold)
                .order_by("id")
            )

            if potential_duplicates.exists():
                current_duplicate_set = {source_article.id}
                for target_article in potential_duplicates:
                    logger.info(
                        f"  Found duplicate: Article ID {target_article.id} "
                        f"(Distance: {target_article.distance:.4f})"
                    )
                    current_duplicate_set.add(target_article.id)
                    processed_article_ids.add(target_article.id)
                
                # Check if this set is entirely new or merges with existing sets
                merged = False
                for existing_set in duplicate_sets:
                    if not existing_set.isdisjoint(current_duplicate_set):
                        existing_set.update(current_duplicate_set)
                        merged = True
                        break
                if not merged:
                    duplicate_sets.append(list(current_duplicate_set))
                
                # Add source article to processed_article_ids after its group is formed
                processed_article_ids.add(source_article.id)


        # Consolidate overlapping sets (iterative merge)
        # This is a more robust way to ensure all interconnected duplicates are grouped
        merged_sets = []
        while duplicate_sets:
            first_set = set(duplicate_sets.pop(0))
            merged_this_round = True
            while merged_this_round:
                merged_this_round = False
                remaining_sets_after_merge = []
                for other_set_list in duplicate_sets:
                    other_set = set(other_set_list)
                    if not first_set.isdisjoint(other_set):
                        first_set.update(other_set)
                        merged_this_round = True
                    else:
                        remaining_sets_after_merge.append(other_set_list)
                duplicate_sets = remaining_sets_after_merge
            merged_sets.append(sorted(list(first_set)))


        logger.info(f"Found {len(merged_sets)} duplicate sets.")
        self.stdout.write(json.dumps(merged_sets))
        logger.info("Duplicate detection finished.")
