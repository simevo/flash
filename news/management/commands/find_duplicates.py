import json
import logging

from django.core.management.base import BaseCommand
from django.core.management.base import CommandParser
from pgvector.django import CosineDistance

from news.models import Articles

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Finds duplicate articles based on embedding similarity."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--threshold",
            type=float,
            default=0.05,
            help="Similarity threshold to mark articles as duplicates (default: 0.05)",
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
            f"Starting detection with threshold: {threshold} and min_id: {min_id}",
        )

        articles_to_process = self._get_articles_to_process(min_id)
        article_count = articles_to_process.count()
        logger.info(f"Found {article_count} articles with embeddings to process.")

        duplicate_sets = self._find_initial_duplicate_sets(
            articles_to_process,
            threshold,
        )
        merged_sets = self._consolidate_duplicate_sets(duplicate_sets)

        logger.info(f"Found {len(merged_sets)} duplicate sets.")
        self.stdout.write(json.dumps(merged_sets))
        logger.info("Duplicate detection finished.")

    def _get_articles_to_process(self, min_id):
        """Fetch articles with non-null embeddings and ID greater than min_id."""
        return Articles.objects.filter(
            use_cmlm_multilingual__isnull=False,
            id__gt=min_id,
        ).order_by("id")

    def _find_potential_duplicates(self, source_article, threshold):
        """Find articles similar to source_article based on embedding similarity."""
        return (
            Articles.objects.filter(
                use_cmlm_multilingual__isnull=False,
                id__gt=source_article.id,
            )
            .annotate(
                distance=CosineDistance(
                    "use_cmlm_multilingual",
                    source_article.use_cmlm_multilingual,
                ),
            )
            .filter(distance__lt=threshold)
            .order_by("id")
        )

    def _find_initial_duplicate_sets(self, articles_to_process, threshold):
        """
        Process articles to find initial duplicate sets.
        Returns a list of sets, where each set contains IDs of duplicate articles.
        """
        duplicate_sets = []
        processed_article_ids = set()
        article_count = articles_to_process.count()

        for i, source_article in enumerate(articles_to_process):
            if source_article.id in processed_article_ids:
                continue  # Already part of a duplicate set

            logger.info(
                f"Processing article {i+1}/{article_count}: ID {source_article.id}",
            )

            potential_duplicates = self._find_potential_duplicates(
                source_article,
                threshold,
            )

            if potential_duplicates.exists():
                current_duplicate_set = self._process_duplicates(
                    source_article,
                    potential_duplicates,
                    duplicate_sets,
                    processed_article_ids,
                )

                # Check if this set is entirely new or merges with existing sets
                merged = self._try_merge_with_existing_sets(
                    current_duplicate_set,
                    duplicate_sets,
                )
                if not merged:
                    duplicate_sets.append(current_duplicate_set)

                # Add source article to processed_article_ids after its group is formed
                processed_article_ids.add(source_article.id)

        return duplicate_sets

    def _process_duplicates(
        self,
        source_article,
        potential_duplicates,
        duplicate_sets,
        processed_article_ids,
    ):
        """Process found duplicate articles and create a new duplicate set."""
        current_duplicate_set = {source_article.id}

        for target_article in potential_duplicates:
            logger.info(
                f"  Found duplicate: Article ID {target_article.id} "
                f"(Distance: {target_article.distance:.4f})",
            )
            current_duplicate_set.add(target_article.id)
            processed_article_ids.add(target_article.id)

        return current_duplicate_set

    def _try_merge_with_existing_sets(self, current_duplicate_set, duplicate_sets):
        """Try to merge the current duplicate set with existing sets if they overlap."""
        for existing_set in duplicate_sets:
            if not existing_set.isdisjoint(current_duplicate_set):
                existing_set.update(current_duplicate_set)
                return True
        return False

    def _consolidate_duplicate_sets(self, duplicate_sets):
        """
        Consolidate overlapping sets through iterative merging.
        Ensures all interconnected duplicates are grouped together.
        """
        # Convert list entries to sets if they aren't already
        duplicate_sets = [
            set(s) if not isinstance(s, set) else s for s in duplicate_sets
        ]

        merged_sets = []
        while duplicate_sets:
            first_set = duplicate_sets.pop(0)
            merged_set = self._merge_overlapping_sets(first_set, duplicate_sets)
            merged_sets.append(sorted(merged_set))

        return merged_sets

    def _merge_overlapping_sets(self, first_set, remaining_sets):
        """
        Iteratively merge all sets that overlap with the first_set.
        Updates remaining_sets in place to remove merged sets.
        """
        merged_this_round = True

        while merged_this_round:
            merged_this_round = False
            remaining_after_merge = []

            for other_set in remaining_sets:
                if not first_set.isdisjoint(other_set):
                    first_set.update(other_set)
                    merged_this_round = True
                else:
                    remaining_after_merge.append(other_set)

            remaining_sets.clear()
            remaining_sets.extend(remaining_after_merge)

        return first_set
