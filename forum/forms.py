from django import forms

from .models import Comment, Post


class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]
        labels = {"content": "Your post"}


class EditCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        labels = {"content": "Your comment"}
