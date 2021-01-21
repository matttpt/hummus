from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="forum"),
    path("new-post", views.new_post, name="new-post"),
    path("post/<int:post_id>", views.post, name="post"),
    path("post/<int:post_id>/edit", views.edit_post, name="edit-post"),
    path("post/<int:post_id>/new-comment", views.new_comment, name="new-comment"),
    path("comment/<int:comment_id>", views.comment, name="comment"),
    path("comment/<int:comment_id>/reply", views.reply, name="reply"),
    path("comment/<int:comment_id>/edit", views.edit_comment, name="edit-comment"),
]
