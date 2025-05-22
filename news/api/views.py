# ruff: noqa: E501

import html
import re
import time
import uuid
from io import BytesIO
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.search import SearchVector
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from ebooklib import epub
from feedgen.feed import FeedGenerator
from pgvector.django import CosineDistance
from PIL import Image
from rest_framework import mixins
from rest_framework import pagination
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from xhtml2pdf import pisa

import news.translate
import poller
from news.api.serializers import ArticleReadSerializer
from news.api.serializers import ArticleSerializer
from news.api.serializers import ArticleSerializerFull
from news.api.serializers import FeedCreateSerializer
from news.api.serializers import FeedSerializer
from news.api.serializers import FeedSerializerSimple
from news.api.serializers import ProfileSerializer
from news.api.serializers import UserArticleListsSerializer
from news.api.serializers import UserArticleListsSerializerFull
from news.api.serializers import UserFeedSerializer
from news.models import Articles
from news.models import ArticlesCombined
from news.models import FeedIcons
from news.models import Feeds
from news.models import FeedsCombined
from news.models import UserArticleLists
from news.models import UserFeeds
from news.services import TextEmbeddingService


class ArticlePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        # we also allow POST for the new_article page
        if request.method in ("GET", "HEAD", "OPTIONS", "POST"):
            # IsAuthenticated
            return bool(request.user and request.user.is_authenticated)
        # IsAdminUser
        return bool(request.user and request.user.is_staff)


class FeedPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            # IsAuthenticated
            return bool(request.user and request.user.is_authenticated)
        # IsAdminUser
        return bool(request.user and request.user.is_staff)


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 200


def get_epub(articles):
    book = epub.EpubBook()

    # set metadata
    book.set_identifier(str(uuid.uuid4()))
    book.set_title(f"Flash {time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())}")
    base_language = "it"
    book.set_language(base_language)

    book.add_author("flash")

    # create chapters
    cs = []  # chapters
    fs = {}  # chapters grouped by feed_id
    fn = {}  # feed name for each feed_id
    spine = ["nav"]
    i = 1
    for data in articles:
        data["minutes"] = int(data["length"] / 6 / 300)

        if not data["title"] and not data["title_original"]:
            title_combined = "[Senza titolo]"
        elif data["language"] == base_language:
            title_combined = f"{data['title']}"
        elif data["title"]:
            title_combined = f"[{data['title_original']}] {data['title']}"
        else:
            title_combined = f"{data['title_original']}"
        data["title_combined"] = title_combined

        if data["language"] == base_language:
            content_combined = f"<div>{data['content']}</div>"
        elif data["content"]:
            content_combined = f"""<h3>Testo tradotto</h3>
<a href="#native_{data['id']}">Vai al testo in lingua originale</a>
<div>{data['content']}</div>
<br/>
<h3 id="native_{data['id']}">Testo in lingua originale</h3>
<div>{data['content_original']}</div>"""
        else:
            content_combined = f"<div>{data['content_original']}</div>"
        data["content_combined"] = content_combined
        data["aggregator_hostname"] = "notizie.calomelano.it"

        c = epub.EpubHtml(
            title=title_combined,
            file_name=f"chap_{i}.xhtml",
            lang=base_language,
        )
        i += 1
        c.content = f"""<h1>{data['title_combined']}</h1>
<p><strong>Pubblicato</strong>: {data['stamp']}</p>
<p><strong>Di</strong>: {data['author']}</p>
<p><strong>Da</strong>: {data['feed']['title']}</p>
<p><strong>Tempo di lettura stimato</strong>: {data['minutes']} minuti</p>
{data['content_combined']}
<p><strong>Commenta</strong>: <a href="https://{data['aggregator_hostname']}/article/{data['id']}">https://{data['aggregator_hostname']}/article/{data['id']}</a></p>
<p><strong>Vai all'articolo originale</strong>: <a href="{data['url']}">{data['url']}</a></p>"""
        cs.append(c)
        feed_id = data["feed"]["id"]
        if feed_id in fs:
            fs[feed_id] = fs[feed_id] + (c,)
        else:
            fs[feed_id] = (c,)
            fn[feed_id] = data["feed"]["title"]
        # add chapter
        book.add_item(c)
        # add chapter to spine
        spine.append(c)

    # define Table Of Contents
    toc = ()
    for f in list(fs.keys()):
        toc = (*toc, (epub.Section(fn[f]), fs[f]))
    book.toc = toc

    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define CSS style
    style = "BODY {color: white;}"
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style,
    )

    # add CSS file
    book.add_item(nav_css)

    # basic spine
    book.spine = spine
    return book


class ArticlesFilter(filters.FilterSet):
    search_author = filters.CharFilter(
        method="filter_search_author",
        field_name="author",
    )
    read = filters.BooleanFilter(
        method="filter_read",
        label="Articoli letti",
    )
    ids = filters.BaseInFilter(
        field_name="id",
    )
    query = filters.CharFilter(
        method="filter_query",
        label="Cerca",
    )

    def filter_search_author(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("author")).filter(search=value)

    def filter_read(self, queryset, name, value):
        if value:
            return queryset.filter(views__gt=0)
        return queryset

    def filter_query(self, queryset, name, value):
        return queryset.extra(
            where=[
                "articles_combined.tsv @@ plainto_tsquery('pg_catalog.simple', %s)",
            ],
            params=[value],
        )

    class Meta:
        model = ArticlesCombined
        fields = ["feed_id", "url"]


def clean_html(raw_html):
    # Remove HTML tags
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text()
    # Convert HTML entities to characters
    return html.unescape(text)


class ArticlesView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = ArticlesCombined.objects.all().order_by("-id")
    permission_classes = [ArticlePermissions]
    filterset_class = ArticlesFilter
    pagination_class = StandardResultsSetPagination

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return ArticleReadSerializer
        return ArticleSerializer

    @extend_schema(
        responses={200: ArticleSerializerFull},
    )
    def retrieve(self, request, pk=None):
        queryset = ArticlesCombined.objects
        article = get_object_or_404(queryset, pk=pk)
        serializer = ArticleSerializerFull(article, context={"request": request})
        user = request.user
        user_articles = user.userarticles_set.filter(article_id=article.id)
        if user_articles.exists():
            user_article = user_articles.first()
            user_article.read = True
            user_article.save()
        else:
            user.userarticles_set.create(article_id=article.id, read=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        queryset = Articles.objects
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        instance = get_object_or_404(queryset, **filter_kwargs)
        serializer = ArticleSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def translate(self, request, pk=None):
        queryset = Articles.objects
        article = get_object_or_404(queryset, pk=pk)
        token = news.translate.get_token()
        if token != "":
            language_original = article.language
            content_original = article.content_original
            title_original = article.title_original
            (title, content) = news.translate.translate(
                token,
                language_original,
                title_original,
                content_original,
            )
            if title and content:
                article.title = title
                article.content = content
                article.save()
                return Response(
                    {
                        "language": article.language,
                    },
                    status=status.HTTP_200_OK,
                )
        return Response(
            {"error": "Translation failed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True)
    def html(self, request, pk=None):
        queryset = ArticlesCombined.objects
        article = get_object_or_404(queryset, pk=pk)
        return render(request, "article.html", {"article": article})

    @action(detail=True)
    def pdf(self, request, pk=None):
        queryset = ArticlesCombined.objects
        article = get_object_or_404(queryset, pk=pk)
        html = render(request, "article.html", {"article": article})
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="article_{article.id}.pdf"'
        )

        html_content = html.content.decode("utf-8")
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_content.encode("utf-8")), result)

        if not pdf.err:
            response.write(result.getvalue())
            return response
        return Response(
            {"error": "PDF generation failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @action(detail=True)
    def epub(self, request, pk=None):
        queryset = ArticlesCombined.objects
        article = get_object_or_404(queryset, pk=pk)
        serializer = ArticleSerializerFull(article)
        articles = [serializer.data]
        book = get_epub(articles)
        response = HttpResponse(content_type="application/epub+zip")
        response["Content-Disposition"] = (
            f'attachment; filename="article_{article.id}.epub"'
        )
        epub.write_epub(response, book, {})
        return response

    @action(detail=True)
    def related(self, request, pk=None):
        queryset = ArticlesCombined.objects
        article = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(
            queryset.order_by(
                CosineDistance(
                    "use_cmlm_multilingual",
                    article.use_cmlm_multilingual,
                ),
            )[1:100],
            many=True,
        )
        results = sorted(serializer.data, key=lambda x: x["id"], reverse=True)[:10]
        return Response(results)

    @action(detail=True, methods=["get"])
    def search(self, request, pk=None):
        queryset = self.get_queryset()
        embedding_service = TextEmbeddingService()
        q_embedding = embedding_service.get_embedding(pk)
        queryset = queryset.order_by(
            CosineDistance(
                "use_cmlm_multilingual",
                q_embedding,
            ),
        )
        # Paginate the results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FeedsView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = (
        FeedsCombined.objects.all()
        .order_by("id")
        .values(
            "id",
            "homepage",
            "url",
            "language",
            "title",
            "license",
            "active",
            "last_polled",
            "tags",
            "last_polled_epoch",
            "article_count",
            "average_time_from_last_post",
            "incomplete",
            "salt_url",
            "cookies",
            "exclude",
            "main",
            "script",
            "frequency",
            "image",
        )
    )
    serializer_class = FeedSerializer
    permission_classes = [FeedPermissions]

    @extend_schema(
        responses=FeedSerializerSimple,
    )
    @action(detail=False, methods=["GET"])
    def simple(self, request, *args, **kwargs):
        queryset = FeedsCombined.objects.all().values("id", "title", "image", "license")
        serializer = FeedSerializerSimple(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = Feeds.objects.get(pk=kwargs["pk"])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        feed_icon = FeedIcons.objects.filter(feed_id=kwargs["pk"]).first()
        if feed_icon:
            feed_icon.image = request.data["image"]
            feed_icon.save()
        else:
            FeedIcons.objects.create(image=request.data["image"], feed=instance)
        return Response(serializer.data)

    @extend_schema(
        responses={201: FeedCreateSerializer},
    )
    def create(self, request, *args, **kwargs):
        serializer = FeedCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @action(detail=True, methods=["POST"])
    def refresh(self, request, pk=None):
        queryset = Feeds.objects
        feed = get_object_or_404(queryset, pk=pk)
        p = poller.Poller(feed)
        p.poll()
        data = {
            "retrieved": p.retrieved,
            "failed": p.failed,
            "stored": p.stored,
        }
        return Response(
            data,
            status=status.HTTP_201_CREATED,
        )


class ProfileView(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile


class UserFeedsView(viewsets.ModelViewSet):
    queryset = UserFeeds.objects.all()
    serializer_class = UserFeedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        feed_id = request.data["feed"]
        rating = request.data["rating"]
        uf = UserFeeds.objects.filter(user_id=user_id, feed_id=feed_id).first()
        if uf:
            uf.rating = rating
            uf.save()
            return Response(uf.id, status=status.HTTP_200_OK)
        uf = UserFeeds.objects.create(user_id=user_id, feed_id=feed_id, rating=rating)
        return Response(uf.id, status=status.HTTP_201_CREATED)


class UserArticleListsView(viewsets.ModelViewSet):
    queryset = UserArticleLists.objects.all()
    serializer_class = UserArticleListsSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["GET"])
    def me(self, request, *args, **kwargs):
        data = (
            UserArticleLists.objects.filter(
                user_id=request.user.id,
            )
            .order_by("-automatic")
            .annotate(articles_set=ArrayAgg("articles"))
            .values("id", "name", "automatic", "articles_set", "user")
        )
        for d in data:
            d["articles"] = d.pop("articles_set")
        return Response(data)

    @extend_schema(
        responses={200: UserArticleListsSerializerFull},
    )
    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = UserArticleListsSerializerFull(
            instance,
            context={"request": request},
        )
        return Response(serializer.data)

    @extend_schema(
        responses={201: UserArticleListsSerializerFull},
    )
    def create(self, request, *args, **kwargs):
        data = request.data
        data["user"] = request.user.id
        serializer = UserArticleListsSerializerFull(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @action(detail=True, methods=["PUT"])
    def add_article(self, request, pk=None):
        instance = self.get_object()
        if instance.user_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        article = request.data["article"]
        instance.articles.add(article)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["DELETE"])
    def remove_article(self, request, pk=None):
        instance = self.get_object()
        if instance.user_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        article = request.data["article"]
        instance.articles.remove(article)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"], permission_classes=[permissions.AllowAny])
    def rss(self, request, pk=None):
        instance = self.get_object()
        articles = instance.articles.all()
        fg = FeedGenerator()
        fg.id(instance.id)
        fg.title(instance.name)
        fg.description(
            "Powered by flash - An open-source news platform with aggregation and ranking",
        )
        fg.link(href=request.build_absolute_uri())
        for article in articles:
            fe = fg.add_entry()
            fe.id(str(article.id))
            title = article.title_original or article.title
            fe.title(title)
            fe.link(href=f"https://notizie.calomelano.it/article/{article.id}")
            content = article.content_original or article.content
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
            excerpt = content[:200]
            fe.description(excerpt)
            fe.published(article.stamp)

        response = fg.rss_str(pretty=True)
        return HttpResponse(response, content_type="application/rss+xml")

    @action(detail=True)
    def html(self, request, pk=None):
        queryset = UserArticleLists.objects.filter(
            user_id=request.user.id,
        )
        article_list = get_object_or_404(queryset, pk=pk)
        full_article_list = article_list.articles.all()
        return render(request, "list.html", {"list": full_article_list})

    @action(detail=True)
    def pdf(self, request, pk=None):
        queryset = UserArticleLists.objects.filter(
            user_id=request.user.id,
        )
        user_list = get_object_or_404(queryset, pk=pk)
        article_list = user_list.articles.all()
        html = render(request, "list.html", {"list": article_list})
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="list_{user_list.name}.pdf"'
        )
        html_content = html.content.decode("utf-8")
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_content.encode("utf-8")), result)

        if not pdf.err:
            response.write(result.getvalue())
            return response
        return Response(
            {"error": "PDF generation failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @action(detail=True)
    def epub(self, request, pk=None):
        queryset = UserArticleLists.objects.filter(
            user_id=request.user.id,
        )
        user_list = get_object_or_404(queryset, pk=pk)
        serializer = UserArticleListsSerializerFull(user_list)
        article_list = serializer.data["articles"]
        full_article_list = ArticlesCombined.objects.filter(id__in=article_list)
        serializer = ArticleSerializerFull(full_article_list, many=True)
        book = get_epub(serializer.data)
        response = HttpResponse(content_type="application/epub+zip")
        response["Content-Disposition"] = (
            f'attachment; filename="list_{user_list.name}.epub"'
        )
        epub.write_epub(response, book, {})
        return response


class OPMLExportView(APIView):
    """
    Exports all feeds as an OPML file using ElementTree.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        feeds = Feeds.objects.all()

        opml_element = ET.Element("opml", version="2.0")
        head_element = ET.SubElement(opml_element, "head")
        title_element = ET.SubElement(head_element, "title")
        title_element.text = "Flash Feeds"
        body_element = ET.SubElement(opml_element, "body")

        for feed in feeds:
            ET.SubElement(
                body_element,
                "outline",
                text=feed.title,  # Use direct keyword argument for text
                type="rss",  # Use direct keyword argument for type
                xmlUrl=feed.url,  # Use direct keyword argument for xmlUrl
            )

        xml_string = ET.tostring(
            opml_element,
            encoding="utf-8",
            xml_declaration=True,
        )
        return HttpResponse(xml_string, content_type="application/xml; charset=utf-8")


class ImageUploadView(APIView):
    def post(self, request):
        # Get the uploaded file
        file = request.FILES.get("image")

        if not file:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if file.name.lower().endswith(".svg"):
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(file.name, file)
        else:
            img = Image.open(file)
            min_size = 16
            max_size = 200
            max_square_deviation = 0.1
            current_width, current_height = img.size
            if current_width < min_size or current_height < min_size:
                return Response(
                    {
                        "error": f"Immagine troppo piccola, dimensione minima: {min_size} pixel",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if (
                abs(current_width - current_height) / (current_width + current_height)
                > 2 * max_square_deviation
            ):
                return Response(
                    {"error": "Immagine non quadrata: differenza tra i lati > 10%"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if current_width > max_size or current_height > max_size:
                resized_img = img.resize((max_size, max_size), Image.Resampling.LANCZOS)
                buffer = BytesIO()
                resized_img.save(buffer, format=img.format or "PNG")
                buffer.seek(0)
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                filename = fs.save(f"{file.name}", buffer)
            else:
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                filename = fs.save(file.name, file)

        uploaded_file_url = f"{settings.MEDIA_URL}{filename}"

        return Response(
            {
                "fileUrl": uploaded_file_url,
                "filename": filename,
            },
            status=status.HTTP_200_OK,
        )
