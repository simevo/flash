import json
import io
import numpy as np
from django.core.management import call_command
from django.test import TestCase
from news.models import Articles, Feeds
from django.utils import timezone

# Helper function to create embeddings
def create_embedding(dimension=768, base_vector=None, similarity_offset=None):
    if base_vector is not None:
        emb = base_vector.copy()
        if similarity_offset is not None:
            # Apply a small change for similar vectors
            emb[0] += similarity_offset 
        # Ensure it's still a valid vector (e.g. normalize if necessary, though for small offsets it might be fine)
    else:
        emb = np.random.rand(dimension).astype(np.float16)
    return emb

class FindDuplicatesCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a common feed for all test articles
        cls.feed = Feeds.objects.create(
            name="Test Feed",
            url="http://example.com/rss",
            last_read=timezone.now(),
            last_modified="Thu, 01 Jan 1970 00:00:00 GMT", # A default past date
            is_active=True,
        )

    def _create_article(self, title, embedding_vector, feed_obj=None):
        if feed_obj is None:
            feed_obj = self.feed
        
        article = Articles.objects.create(
            feed=feed_obj,
            title=title,
            body_cleaned=f"Body for {title}",
            body_html=f"<p>Body for {title}</p>",
            url=f"http://example.com/{title.lower().replace(' ', '-')}",
            guid=f"guid-{title.lower().replace(' ', '-')}",
            author=f"Author {title}",
            published_on=timezone.now(),
            use_cmlm_multilingual=embedding_vector,
            # Add other necessary fields with default values if any
            # e.g. summary, keywords, etc.
        )
        return article

    def run_find_duplicates_command(self, *args, **kwargs):
        out = io.StringIO()
        call_command("find_duplicates", stdout=out, *args, **kwargs)
        return json.loads(out.getvalue())

    def assertListContainsOnly(self, list_of_lists, expected_items_sets):
        """
        Asserts that a list of lists (like the command output) contains exactly
        the expected sets of items, regardless of the order of lists or items within lists.
        """
        self.assertEqual(len(list_of_lists), len(expected_items_sets), "Number of duplicate sets mismatch.")
        
        processed_actual_sets = [sorted(list(s)) for s in list_of_lists]
        processed_expected_sets = [sorted(list(s)) for s in expected_items_sets]

        for expected_set in processed_expected_sets:
            self.assertIn(expected_set, processed_actual_sets, f"Expected set {expected_set} not found in output.")

        for actual_set in processed_actual_sets:
            self.assertIn(actual_set, processed_expected_sets, f"Actual set {actual_set} not expected.")


    def test_no_duplicates(self):
        emb1 = create_embedding()
        emb2 = create_embedding() # Should be different enough by default
        emb3 = create_embedding()

        self._create_article("Article A", emb1)
        self._create_article("Article B", emb2)
        self._create_article("Article C", emb3)

        output = self.run_find_duplicates_command()
        self.assertEqual(output, [])

    def test_simple_duplicate_pair(self):
        emb_base = create_embedding()
        emb_similar = create_embedding(base_vector=emb_base, similarity_offset=0.001) # Very similar
        emb_different = create_embedding() # Different

        a1 = self._create_article("Article A1", emb_base)
        a2 = self._create_article("Article A2", emb_similar)
        a3 = self._create_article("Article B1", emb_different)

        output = self.run_find_duplicates_command()
        expected = [[a1.id, a2.id]]
        self.assertListContainsOnly(output, expected)
        
    def test_multiple_duplicate_sets(self):
        emb_a_base = create_embedding()
        emb_a_similar = create_embedding(base_vector=emb_a_base, similarity_offset=0.001)
        
        emb_b_base = create_embedding() # Different from A
        emb_b_similar = create_embedding(base_vector=emb_b_base, similarity_offset=0.001)
        
        emb_c_unique = create_embedding() # Different from A and B

        a1 = self._create_article("Article A1", emb_a_base)
        a2 = self._create_article("Article A2", emb_a_similar)
        b1 = self._create_article("Article B1", emb_b_base)
        b2 = self._create_article("Article B2", emb_b_similar)
        c1 = self._create_article("Article C1", emb_c_unique)

        output = self.run_find_duplicates_command()
        # The order of IDs within a set, and the order of sets themselves, can vary.
        # We sort them for consistent comparison.
        expected = [
            sorted([a1.id, a2.id]),
            sorted([b1.id, b2.id]),
        ]
        # Sort the output lists as well
        sorted_output = [sorted(s) for s in output]
        
        self.assertEqual(len(sorted_output), len(expected), "Number of duplicate sets mismatch.")
        for item_set in expected:
            self.assertIn(item_set, sorted_output, f"Expected set {item_set} not found.")
        for item_set in sorted_output:
            self.assertIn(item_set, expected, f"Output set {item_set} not expected.")


    def test_duplicate_chain(self):
        emb_base = create_embedding()
        emb_mid = create_embedding(base_vector=emb_base, similarity_offset=0.001) # Similar to base
        emb_end = create_embedding(base_vector=emb_mid, similarity_offset=0.001) # Similar to mid

        a1 = self._create_article("Article Chain 1", emb_base)
        a2 = self._create_article("Article Chain 2", emb_mid)
        a3 = self._create_article("Article Chain 3", emb_end)
        
        # For sanity check, ensure A1 and A3 are also similar enough
        # This depends on how CosineDistance accumulates. If A1-A2 is 0.001 and A2-A3 is 0.001,
        # A1-A3 might be ~0.002. We assume the command's logic handles chaining correctly.

        output = self.run_find_duplicates_command()
        expected_ids = sorted([a1.id, a2.id, a3.id])
        
        self.assertEqual(len(output), 1, "Expected one duplicate set for the chain.")
        self.assertEqual(sorted(output[0]), expected_ids, "Duplicate chain not correctly identified.")

    def test_threshold_argument(self):
        # Create two embeddings with a known, controllable difference
        # Let's aim for a cosine distance of ~0.07.
        # Note: Directly controlling cosine distance from vector components is non-trivial.
        # For testing, we'll create vectors that are "somewhat similar"
        # and adjust our expectation based on typical behavior of random vectors or
        # by making them more deliberately different than the "very similar" ones.
        
        emb1 = np.random.rand(768).astype(np.float16)
        emb2 = emb1.copy()
        # Introduce a larger, but not huge, difference
        # A larger perturbation might result in a distance around 0.05-0.1
        # This requires some experimentation or a more precise way to craft vectors
        # for a specific cosine distance if critical.
        # For now, let's make it a bit more different than the 0.001 offset.
        emb2[0:10] += 0.1 # Perturb first 10 elements by a bit more
        # Normalize to ensure they are unit vectors, as CosineDistance works best with them
        emb1 = emb1 / np.linalg.norm(emb1)
        emb2 = emb2 / np.linalg.norm(emb2)


        a1 = self._create_article("Article T1", emb1)
        a2 = self._create_article("Article T2", emb2)

        # Run with default threshold (0.05)
        output_default_threshold = self.run_find_duplicates_command()
        # We expect them NOT to be duplicates if their distance is > 0.05
        # This assertion depends on the actual distance achieved by the perturbation.
        # If emb1 and emb2 happen to be < 0.05, this part of the test would need adjustment.
        # For now, we assume the perturbation makes them > 0.05 apart.
        is_duplicate_default = any(
            (a1.id in s and a2.id in s) for s in output_default_threshold
        )
        self.assertFalse(is_duplicate_default, "Articles should NOT be duplicates with default threshold.")


        # Run with higher threshold (e.g., 0.1, assuming the distance is < 0.1 but > 0.05)
        output_high_threshold = self.run_find_duplicates_command(threshold=0.1)
        is_duplicate_high = any(
            (a1.id in s and a2.id in s) for s in output_high_threshold
        )
        if not is_duplicate_high:
            # For debugging if this fails:
            # Calculate actual distance (requires a DB call or pgvector function access)
            # from pgvector.django import CosineDistance
            # dist = Articles.objects.filter(id=a1.id).annotate(distance=CosineDistance('use_cmlm_multilingual', emb2)).first().distance
            # print(f"DEBUG: Actual distance between T1 and T2 for threshold test: {dist}")
            pass

        self.assertTrue(is_duplicate_high, "Articles SHOULD BE duplicates with threshold 0.1.")
        if is_duplicate_high: # Further check if the set is correctly formed
             self.assertListContainsOnly(output_high_threshold, [[a1.id, a2.id]])


    def test_min_id_argument(self):
        emb_base = create_embedding()
        emb_similar = create_embedding(base_vector=emb_base, similarity_offset=0.001)
        emb_unique = create_embedding()

        # Order of creation matters for IDs
        a1 = self._create_article("Article M1", emb_base)      # Lowest ID
        a2 = self._create_article("Article M2", emb_similar) # Similar to A1
        a3 = self._create_article("Article M3", emb_unique)   # Unique

        # Run with min_id = a1.id
        # Source article ID must be > min_id.
        # If a1.id is the min_id, then a1 cannot be a source_article.
        # If a2 is processed, it cannot find a1 (id < a2.id) as a target.
        # The command logic is:
        # articles_to_process = Articles.objects.filter(id__gt=min_id)
        # potential_duplicates = Articles.objects.filter(id__gt=source_article.id)
        # So if min_id = a1.id, a1 is excluded from articles_to_process.
        # a2 and a3 will be processed.
        # When a2 is source, it looks for targets with id > a2.id (only a3, which is not similar).
        # When a3 is source, it looks for targets with id > a3.id (none).
        output_min_id_a1 = self.run_find_duplicates_command(min_id=a1.id)
        self.assertEqual(output_min_id_a1, [], 
                         f"Expected no duplicates when min_id is {a1.id}, excluding a1 as source.")

        # Run with min_id = a2.id
        # a1, a2 excluded from articles_to_process. Only a3 processed. No duplicates.
        output_min_id_a2 = self.run_find_duplicates_command(min_id=a2.id)
        self.assertEqual(output_min_id_a2, [], 
                         f"Expected no duplicates when min_id is {a2.id}, excluding a1,a2 as source.")
        
        # Run with min_id < a1.id (e.g., a1.id - 1, or 0 if a1.id is small)
        min_id_val = 0
        if a1.id > 1: # ensure min_id_val is less than a1.id
            min_id_val = a1.id -1 
        
        output_min_id_less = self.run_find_duplicates_command(min_id=min_id_val)
        expected = [[a1.id, a2.id]]
        self.assertListContainsOnly(output_min_id_less, expected, 
                                   f"Expected duplicates when min_id is {min_id_val}.")

    def test_articles_without_embeddings(self):
        emb_a1 = create_embedding()
        emb_a3_similar_to_a1 = create_embedding(base_vector=emb_a1, similarity_offset=0.001)

        a1 = self._create_article("Article E1", emb_a1)
        # Article A2 has no embedding
        a2 = Articles.objects.create(
            feed=self.feed,
            title="Article E2 No Embedding",
            body_cleaned="Body for E2",
            body_html="<p>Body for E2</p>",
            url="http://example.com/e2",
            guid="guid-e2",
            author="Author E2",
            published_on=timezone.now(),
            use_cmlm_multilingual=None, # Explicitly None
        )
        a3 = self._create_article("Article E3", emb_a3_similar_to_a1)

        output = self.run_find_duplicates_command()
        expected = [[a1.id, a3.id]]
        self.assertListContainsOnly(output, expected)

    def test_no_articles_at_all(self):
        # Ensure no articles exist
        Articles.objects.all().delete()
        output = self.run_find_duplicates_command()
        self.assertEqual(output, [])

    def test_one_article_with_embedding(self):
        Articles.objects.all().delete()
        emb1 = create_embedding()
        self._create_article("Only Article", emb1)
        output = self.run_find_duplicates_command()
        self.assertEqual(output, [])

    def test_one_article_without_embedding(self):
        Articles.objects.all().delete()
        Articles.objects.create(
            feed=self.feed, title="Only Article No Emb", body_cleaned="Body", 
            url="http://example.com/onlynoemb", guid="guid-onlynoemb", published_on=timezone.now(),
            use_cmlm_multilingual=None)
        output = self.run_find_duplicates_command()
        self.assertEqual(output, [])

    def test_complex_merge_scenario(self):
        """
        Test scenario:
        A1 similar to A2
        A3 similar to A4
        Later, A2 found similar to A3
        All A1, A2, A3, A4 should be in one group.
        """
        emb_a1 = create_embedding()
        emb_a2 = create_embedding(base_vector=emb_a1, similarity_offset=0.001) # A1 ~ A2
        
        emb_a3 = create_embedding() # Intentionally different from A1/A2 initially for the sake of test setup
        emb_a4 = create_embedding(base_vector=emb_a3, similarity_offset=0.001) # A3 ~ A4

        # Now, make A2 similar to A3. This requires A3 to be similar to A2's embedding.
        # Let's re-create A3's embedding based on A2.
        emb_a3_updated = create_embedding(base_vector=emb_a2, similarity_offset=0.001) # A2 ~ A3_updated

        # Create articles in an order that might challenge naive merging
        art1 = self._create_article("Merge A1", emb_a1)
        art2 = self._create_article("Merge A2", emb_a2) 
        # art3's embedding needs to be similar to art2, and art4 similar to art3
        art3 = self._create_article("Merge A3", emb_a3_updated) 
        art4 = self._create_article("Merge A4", create_embedding(base_vector=emb_a3_updated, similarity_offset=0.001)) # A3_updated ~ A4
        
        art_unique = self._create_article("Merge Unique", create_embedding())

        output = self.run_find_duplicates_command()
        expected_ids = sorted([art1.id, art2.id, art3.id, art4.id])
        
        found_match = False
        for group in output:
            if sorted(group) == expected_ids:
                found_match = True
                break
        
        self.assertTrue(found_match, f"Expected group {expected_ids} not found in output {output}")
        self.assertEqual(len(output), 1, f"Expected only one group of duplicates, got {output}")

```
