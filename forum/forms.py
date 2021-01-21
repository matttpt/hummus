from django import forms
from django.contrib import admin

from .models import Comment, Post


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {"content": admin.widgets.AdminTextareaWidget()}
        fields = "__all__"


class CommentAdminForm(forms.ModelForm):
    class Meta:
        model = Comment
        widgets = {"content": admin.widgets.AdminTextareaWidget()}
        fields = "__all__"


class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]
        widgets = {"content": forms.Textarea()}
        labels = {"content": "Your post"}


class EditCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {"content": forms.Textarea()}
        labels = {"content": "Your comment"}
