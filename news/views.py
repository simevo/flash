import html
import re

from django.views.generic import ListView
from django.views.generic.detail import DetailView

from news.models import Articles


class ArticleListView(ListView):
    paginate_by = 12
    model = Articles
    queryset = Articles.objects.filter(articlesdata__views__gt="0")
    ordering = "-id"


class ArticleDetailView(DetailView):
    model = Articles
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content = context["object"].content if context["object"].content else context["object"].content_original
        # remove html tags
        content = re.sub(r'<[^>]*>', "", content)
        # convert html entities to unicode
        content = html.unescape(content)
        context["excerpt"] = content[:500]
        return context
