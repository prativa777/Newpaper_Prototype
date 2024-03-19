from ctypes.wintypes import tagSIZE
from typing import Any, Dict
from django.db import models
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, TemplateView, View, DetailView
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
from newspaper_app.forms import ContactForm, CommentForm, NewsletterForm
from newspaper_app.models import Category, Post, Tag
from django.core.paginator import Paginator, PageNotAnInteger
from django.db.models import Q


# Create your views here.
class HomeView(ListView):
    model = Post
    template_name = "aznews/home.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(
        published_at__isnull=False, status="active"
    ).order_by("-published_at")[:4]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trending_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-views_count")[:3]

        context["featured_post"] = (
            Post.objects.filter(published_at__isnull=False, status="active")
            .order_by("-views_count")
            .first()
        )

        context["featured_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-views_count")[1:4]

        one_week_ago = timezone.now() - timedelta(days=7)
        context["weekly_top_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active", published_at__gte=one_week_ago
        ).order_by
        ("-published_at", "-views_count")[:7]

        context["recent_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-published_at")[:4]

        context["categories"] = Category.objects.all()[:4]
        context["tags"] = Tag.objects.all()[:10]

        return context


class AboutView(TemplateView):
    template_name = "aznews/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trending_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-views_count")[:3]
        context["categories"] = Category.objects.all()[:5]
        context["tags"] = Tag.objects.all()[:10]

        return context


class ContactView(View):
    template_name = "aznews/contact.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Successfully submitted your query. We will contact you soon!"
            )
            return redirect("contact")
        else:
            messages.error(
                request,
                "Cannot submit your query. Please make sure all fiels are valid",
            )
            return render(
                request,
                self.template_name,
                {"form": form},
            )


class PostListView(ListView):
    model = Post
    template_name = "aznews/list/list.html"
    context_object_name = "posts"
    paginate_by = 1

    def get_queryset(self):
        return Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-published_at")


class PostDetailView(DetailView):
    model = Post
    template_name = "aznews/detail/detail.html"
    context_object_name = "posts"

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(published_at__isnull=False, status="active")
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        obj.views_count += 1
        obj.save()

        context["previous_post"] = (
            Post.objects.filter(
                published_at__isnull=False, status="active", id__lt=obj.id
            )
            .order_by("-id")
            .first()
        )
        context["next_post"] = (
            Post.objects.filter(
                published_at__isnull=False, status="active", id__gt=obj.id
            )
            .order_by("-id")
            .first()
        )

        return context


class PostByCategoryView(ListView):
    model = Post
    template_name = "aznews/list/list.html"
    context_object_name = "posts"

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(
            published_at__isnull=False,
            status="active",
            category_id=self.kwargs["category_id"],
        ).order_by("-published_at")
        return query


class PostByTagView(ListView):
    model = Post
    template_name = "aznews/list/list.html"
    context_object_name = "posts"
    paginate_by = 1

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(
            published_at__isnull=False,
            status="active",
            category_id=self.kwargs["tag_id"],
        ).order_by("-published_at")
        return query


class CommentView(View):
    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        post_id = request.POST["post"]
        if form.is_valid():
            form.save()
            return redirect("post-detail", post_id)
        else:
            post = Post.objects.get(pk=post_id)
            return render(
                request, "aznews/main/detail/detail.html", {"post": post, "form": form}
            )


class PostSearchView(View):
    template_name = "aznews/list/search.html"

    def get(self, request, *args, **kwargs):
        query = request.GET["query"]
        post_list = Post.objects.filter(
            (Q(title__icontains=query) | Q(content__icontains=query))
            & Q(status="active")
            & Q(published_at__isnull=False)
        ).order_by("-published_at")

        # pagination start
        page = request.GET.get("page", 1)
        paginate_by = 1
        paginator = Paginator(post_list, paginate_by)
        try:
            posts = paginator.page(page)

        except PageNotAnInteger:
            posts = paginator.page(1)

        # pagination end
        return render(
            request,
            self.template_name,
            {"page_obj": posts, "query": query},
        )
    
class NewsletterView(View):
    def post(self, request):
        is_ajax=request.headers.get("x-requested-with")
        if is_ajax=='XMLHttpRequest':
            form = NewsletterForm(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse(
                {
                    "success": True,
                    "message": "Successfully subscribed to the newsletter.",
                },
                status=200,
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Cannot subscribe to the newsletter.",
                    },
                    status=484,
                )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Cannot process. Must be an AJAX XMLHttpRequest",
                },
                status=400,
            )
            


