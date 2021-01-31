import itertools
import math

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import EditPhotoForm, UploadPhotoForm
from .models import Photo


########################################################################
# Gallery and GalleryRow classes, which compute how to fit images into #
# rows when displayed                                                  #
########################################################################


class Gallery:
    def __init__(self, photos=[]):
        self.current_row = GalleryRow()
        self.finished_rows = []
        for photo in photos:
            self.append(photo)

    def append(self, photo):
        if not self.current_row.try_append(photo):
            # The current row is non-empty and full. We finish the row
            # and start a new one. The second try_append must succeed,
            # since the new row is empty.
            self.finished_rows.append(self.current_row)
            self.current_row = GalleryRow()
            self.current_row.try_append(photo)

    def finish(self):
        if not self.current_row.empty():
            self.finished_rows.append(self.current_row)
        return self.finished_rows


class GalleryRow:
    # NOTE: WIDTH and IMAGE_GAP are in pixels and should match the
    # templates and CSS. The width of the row might not actually be
    # WIDTH pixels if the window is too narrow; in this case, the CSS is
    # set up so that the images will scale down proportionally.
    WIDTH = 720
    IMAGE_GAP = 5
    MIN_HEIGHT = 160
    THUMBNAIL_LEVELS = [WIDTH / 4, WIDTH / 2, WIDTH]

    def __init__(self):
        self.photos = []

    def aspect_ratio(self):
        return sum(p.aspect_ratio() for p in self.photos)

    def empty(self):
        return not self.photos

    def height(self, additional_photo=None):
        if additional_photo:
            number_of_gaps = len(self.photos)
            aspect_ratio = self.aspect_ratio() + additional_photo.aspect_ratio()
        else:
            number_of_gaps = len(self.photos) - 1
            aspect_ratio = self.aspect_ratio()

        width_of_photos = GalleryRow.WIDTH - GalleryRow.IMAGE_GAP * number_of_gaps
        return width_of_photos / aspect_ratio

    def photos_with_sizes(self):
        return [(p, self.thumb_size_str(p)) for p in self.photos]

    def thumb_size_str(self, photo):
        width = self.height() * photo.aspect_ratio()
        suitable_levels = itertools.dropwhile(
            lambda w: w < width, GalleryRow.THUMBNAIL_LEVELS
        )
        return str(math.ceil(next(suitable_levels, GalleryRow.WIDTH)))

    def try_append(self, photo):
        # If we are empty, then we always add the photo. This allows
        # high-aspect-ratio photos that cannot possibly fit into a row
        # (even alone) with a height of at least MIN_HEIGHT to appear in
        # the gallery.
        if self.empty() or self.height(photo) >= GalleryRow.MIN_HEIGHT:
            self.photos.append(photo)
            return True
        else:
            return False


########################################################################
# Views                                                                #
########################################################################


@login_required
def index(request):
    photo_count = Photo.objects.count()
    latest_photos = Photo.objects.order_by("-time_created")
    gallery = Gallery(latest_photos)
    render_args = {
        "photo_count": photo_count,
        "gallery": gallery.finish(),
    }
    return render(request, "photos/index.html", render_args)


@login_required
def by_user_index(request):
    users = User.objects.order_by("last_name", "first_name")
    users_with_photo_data = []

    for user in users:
        query_set = Photo.objects.filter(user=user).order_by("-time_created")
        users_with_photo_data.append((user, query_set.first(), query_set.count()))

    render_args = {
        "users_with_photo_data": users_with_photo_data,
    }
    return render(request, "photos/by_user_index.html", render_args)


@login_required
def by_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    photos = Photo.objects.filter(user=user).order_by("-time_created")
    gallery = Gallery(photos)
    render_args = {
        "user": user,
        "gallery": gallery.finish(),
    }
    return render(request, "photos/by_user.html", render_args)


@login_required
def photo(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)

    # Get the size on disk and compute the size string
    size = photo.image.size
    if size >= 1024 * 1024:
        size_str = "{:.1f} MiB".format(size / 1024 / 1024)
    elif size >= 1024:
        size_str = "{:.0f} KiB".format(size / 1024)
    else:
        size_str = "{} bytes".format(size)

    render_args = {
        "photo": photo,
        "size_str": size_str,
    }
    return render(request, "photos/photo.html", render_args)


@login_required
def edit_photo(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)

    if request.user != photo.user:
        return HttpResponse("You are not authorized to edit this photo.", status=403)
    elif request.method == "POST":
        form = EditPhotoForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            return redirect(reverse("photo", args=[photo_id]))
    else:
        form = EditPhotoForm(instance=photo)

    render_args = {
        "form": form,
        "form_action": reverse("edit-photo", args=[photo_id]),
        "title": "Edit photo {}".format(photo_id),
    }
    return render(request, "photos/photo_form.html", render_args)


@login_required
def upload(request):
    if request.method == "POST":
        form = UploadPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            new_photo = form.save(commit=False)
            new_photo.user = request.user
            new_photo.save()
            return redirect(reverse("photo", args=[new_photo.pk]))
    else:
        form = UploadPhotoForm()

    render_args = {
        "form": form,
        "form_action": reverse("upload-photo"),
        "title": "Upload photo",
    }
    return render(request, "photos/photo_form.html", render_args)
