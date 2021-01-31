from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="photos"),
    path("by-user/", views.by_user_index, name="photos-by-user-index"),
    path("by-user/<int:user_id>", views.by_user, name="photos-by-user"),
    path("photo/<int:photo_id>", views.photo, name="photo"),
    path("photo/<int:photo_id>/edit", views.edit_photo, name="edit-photo"),
    path("upload", views.upload, name="upload-photo"),
]
