import html
import re

import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from news.models import Articles
from news.models import ArticlesData


class ArticleListView(ListView):
    paginate_by = 12
    model = Articles
    queryset = Articles.objects.filter(articlesdata__views__gt="0")
    ordering = "-id"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/res/")
        return super().get(request, *args, **kwargs)


class ArticleDetailView(DetailView):
    model = Articles
    pk_url_kwarg = "id"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        if request.user.is_authenticated:
            article = context["object"]
            url = f"/res/article/{article.id}"
            return redirect(url)
        if request.GET.get("redirect"):
            article = context["object"]
            ad = ArticlesData.objects.get(id=article.id)
            ad.views += 1
            ad.save()
            url = article.url
            return redirect(url)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content = (
            context["object"].content
            if context["object"].content
            else context["object"].content_original
        )
        if content is None:
            content = ""
        # remove html tags
        content = re.sub(r"<[^>]*>", "", content)
        # convert html entities to unicode
        content = html.unescape(content)
        # remove multiple whitespaces
        content = re.sub(r"[\s]+", " ", content)
        # remove newlines
        content = content.replace("\n", "")
        # trim
        content = content.strip()
        context["excerpt"] = content[:200]
        return context


class ProxyView(LoginRequiredMixin, View):
    def get(self, request, url):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            ),
        }
        response = requests.get(url, headers=headers, timeout=30)
        return HttpResponse(
            response.content,
            content_type=response.headers["Content-Type"],
        )
