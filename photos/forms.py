from django import forms

from .models import Photo


class EditPhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ["title", "description"]


class UploadPhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ["image", "title", "description"]
