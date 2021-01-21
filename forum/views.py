from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import EditCommentForm, EditPostForm
from .models import Comment, Post


@login_required
def index(request):
    # TODO pagination
    # TODO configurable max depth
    latest_posts = Post.objects.order_by("-time_active")
    render_args = {
        "title": "Forum",
        "latest_posts": latest_posts,
        "max_depth": 8,
        "post_count": Post.objects.all().count(),
        "comment_count": Comment.objects.all().count(),
    }
    return render(request, "forum/index.html", render_args)


@login_required
def post(request, post_id):
    # TODO configurable max depth
    post = get_object_or_404(Post, pk=post_id)
    render_args = {"title": post.title, "post": post, "max_depth": 8}
    return render(request, "forum/post.html", render_args)


@login_required
def comment(request, comment_id):
    # TODO configurable max depth
    comment = get_object_or_404(Comment, pk=comment_id)
    render_args = {
        "title": "Comment {}".format(comment.pk),
        "comment_list": [comment],
        "max_depth": 8,
    }
    return render(request, "forum/comments.html", render_args)


@login_required
def new_post(request):
    render_args = {}
    if request.method == "POST":
        form = EditPostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            action = request.POST.get("action")
            if action == "submit":
                new_post.save()
                return redirect("post", new_post.pk)
            elif action == "preview":
                render_args["preview"] = new_post
            else:
                return HttpResponse("Invalid action specified", status=400)
    else:
        form = EditPostForm()
    render_args["title"] = "New post"
    render_args["form"] = form
    render_args["form_action"] = reverse("new-post")
    return render(request, "forum/post_form.html", render_args)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    render_args = {}
    if request.user != post.user:
        return HttpResponse("You are not authorized to edit this post.", status=403)
    elif request.method == "POST":
        form = EditPostForm(request.POST, instance=post)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.edited = True
            edited_post.time_edited = timezone.now()
            action = request.POST.get("action")
            if action == "submit":
                edited_post.save()
                return redirect("post", post.pk)
            elif action == "preview":
                render_args["preview"] = edited_post
            else:
                return HttpResponse("Invalid action specified", status=400)
    else:
        form = EditPostForm(instance=post)
    render_args["title"] = "Edit post {}".format(post.pk)
    render_args["form"] = form
    render_args["form_action"] = reverse("edit-post", args=[post_id])
    return render(request, "forum/post_form.html", render_args)


@login_required
def new_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    render_args = {}
    if request.method == "POST":
        form = EditCommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.parent = None
            new_comment.user = request.user
            action = request.POST.get("action")
            if action == "submit":
                with transaction.atomic():
                    new_comment.save()
                    post.time_active = new_comment.time_created
                    post.save()
                return redirect("post", post.pk)
            elif action == "preview":
                render_args["preview"] = new_comment
            else:
                return HttpResponse("Invalid action specified", status=400)
    else:
        form = EditCommentForm()
    render_args["title"] = "New comment on “{}”".format(post.title)
    render_args["form"] = form
    render_args["form_action"] = reverse("new-comment", args=[post_id])
    return render(request, "forum/comment_form.html", render_args)


@login_required
def reply(request, comment_id):
    parent_comment = get_object_or_404(Comment, pk=comment_id)
    render_args = {}
    if request.method == "POST":
        form = EditCommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = parent_comment.post
            new_comment.parent = parent_comment
            new_comment.user = request.user
            action = request.POST.get("action")
            if action == "submit":
                with transaction.atomic():
                    new_comment.save()
                    new_comment.post.time_active = new_comment.time_created
                    new_comment.post.save()
                return redirect("post", new_comment.post.pk)
            elif action == "preview":
                render_args["preview"] = new_comment
            else:
                return HttpResponse("Invalid action specified", status=400)
    else:
        form = EditCommentForm()
    render_args["title"] = "Reply to comment {}".format(parent_comment.pk)
    render_args["parent_comment"] = parent_comment
    render_args["form"] = form
    render_args["form_action"] = reverse("reply", args=[comment_id])
    return render(request, "forum/comment_form.html", render_args)


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.user:
        return HttpResponse("You are not authorized to edit this comment.", status=403)
    render_args = {}
    if request.method == "POST":
        form = EditCommentForm(request.POST, instance=comment)
        if form.is_valid():
            edited_comment = form.save(commit=False)
            edited_comment.edited = True
            edited_comment.time_edited = timezone.now()
            action = request.POST.get("action")
            if action == "submit":
                edited_comment.save()
                return redirect("post", edited_comment.post.pk)
            elif action == "preview":
                render_args["preview"] = edited_comment
            else:
                return HttpResponse("Invalid action specified", status=400)
    else:
        form = EditCommentForm(instance=comment)
    render_args["title"] = "Edit comment {}".format(comment.pk)
    render_args["form"] = form
    render_args["form_action"] = reverse("edit-comment", args=[comment_id])
    return render(request, "forum/comment_form.html", render_args)
