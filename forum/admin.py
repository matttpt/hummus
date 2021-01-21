from django.contrib import admin

from .forms import CommentAdminForm, PostAdminForm
from .models import Comment, Post


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm


class CommentAdmin(admin.ModelAdmin):
    form = CommentAdminForm


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
