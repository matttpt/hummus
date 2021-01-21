import bleach
import markdown
from django.contrib.auth.models import User
from django.db import models


# TODO: consider what else might be allowed (look at the Markdown spec)
BLEACH_ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS + ["p", "img"]
BLEACH_ALLOWED_ATTRIBUTES = dict(bleach.sanitizer.ALLOWED_ATTRIBUTES)
BLEACH_ALLOWED_ATTRIBUTES["img"] = ["src", "alt"]


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    edited = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_edited = models.DateTimeField(auto_now_add=True)
    time_active = models.DateTimeField(auto_now_add=True)

    def toplevel_comments(self):
        return self.comment_set.filter(parent=None).order_by("time_created")

    def content_as_markdown(self):
        return bleach.clean(
            markdown.markdown(self.content),
            tags=BLEACH_ALLOWED_TAGS,
            attributes=BLEACH_ALLOWED_ATTRIBUTES,
            strip=True,
        )

    def __str__(self):
        return 'Post {} ("{}")'.format(self.pk, self.title)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    edited = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_edited = models.DateTimeField(auto_now_add=True)

    def content_as_markdown(self):
        return bleach.clean(
            markdown.markdown(self.content),
            tags=BLEACH_ALLOWED_TAGS,
            attributes=BLEACH_ALLOWED_ATTRIBUTES,
            strip=True,
        )

    def sorted_comment_set(self):
        return self.comment_set.order_by("time_created")

    def __str__(self):
        if self.parent:
            return "Comment {} (reply to comment {} on post {})".format(
                self.pk, self.parent.pk, self.post.pk
            )
        else:
            return "Comment {} (top-level on post {})".format(self.pk, self.post.pk)
