from django.core.management.base import BaseCommand
from flash.news.models import Articles, ArticlesData

class Command(BaseCommand):
    help = 'Makes an article public and updates its view count.'

    def add_arguments(self, parser):
        parser.add_argument('article_id', type=int, help='The ID of the article to make public.')

    def handle(self, *args, **options):
        article_id = options['article_id']
        try:
            article = Articles.objects.get(pk=article_id)
            
            article_data, created = ArticlesData.objects.get_or_create(
                article=article,
                defaults={
                    'views': 1,
                    'rating': 0,
                    'to_reads': 0,
                    'length': len(article.content_original or article.content or "")
                }
            )

            if not created:
                article_data.views += 1
                article_data.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully made article {article_id} public. Views: {article_data.views}'))

        except Articles.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Article with ID {article_id} does not exist.'))
