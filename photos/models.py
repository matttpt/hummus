from datetime import datetime

import PIL.ExifTags
import PIL.Image
from django.contrib.auth.models import User
from django.db import models

from hummus.markdown import process_markdown


class Photo(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to="photos/%Y/%m")
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    time_created = models.DateTimeField(auto_now_add=True)

    def aspect_ratio(self):
        return self.width / self.height

    def description_as_markdown(self):
        return process_markdown(self.description)

    def save(self, *args, **kwargs):
        image = PIL.Image.open(self.image)
        dimensions_reversed = False
        timestamp = None

        if image.format == "JPEG":
            # Read the EXIF data to determine if the image is rotated by
            # 90 or 270 degrees, so that we can swap the width and
            # height in those cases
            orientation_tags = [
                v
                for (t, v) in image.getexif().items()
                if t in PIL.ExifTags.TAGS and PIL.ExifTags.TAGS[t] == "Orientation"
            ]
            if orientation_tags:
                value = orientation_tags[0]
                if value >= 5 and value <= 8:
                    dimensions_reversed = True

            # Extract the timestamp from the EXIF data, if present
            datetime_tags = [
                v
                for (t, v) in image.getexif().items()
                if t in PIL.ExifTags.TAGS and PIL.ExifTags.TAGS[t] == "DateTime"
            ]
            if datetime_tags:
                value = datetime_tags[0]
                try:
                    timestamp = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    # Ignore the invalid data
                    pass

        if dimensions_reversed:
            self.height, self.width = image.size
        else:
            self.width, self.height = image.size
        self.timestamp = timestamp

        super(Photo, self).save(*args, **kwargs)
