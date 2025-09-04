from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet

from wagtailcloudinary.fields import CloudinaryField
from wagtailcloudinary.widgets import AdminCloudinaryChooser


@register_snippet
class ImageSnippet(models.Model):
    image = CloudinaryField()

    panels = [
        FieldPanel("image", widget=AdminCloudinaryChooser),
    ]
