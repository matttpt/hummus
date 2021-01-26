import bleach
import markdown


# TODO: consider what else might be allowed (look at the Markdown spec)
BLEACH_ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS + ["p", "img"]
BLEACH_ALLOWED_ATTRIBUTES = dict(bleach.sanitizer.ALLOWED_ATTRIBUTES)
BLEACH_ALLOWED_ATTRIBUTES["img"] = ["src", "alt"]


def process_markdown(source):
    return bleach.clean(
        markdown.markdown(source),
        tags=BLEACH_ALLOWED_TAGS,
        attributes=BLEACH_ALLOWED_ATTRIBUTES,
        strip=True,
    )
