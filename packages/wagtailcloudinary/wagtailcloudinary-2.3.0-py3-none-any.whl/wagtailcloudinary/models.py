from django.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from taggit.models import Tag, TaggedItemBase

from .utils import CloudinaryResource


class TaggedCloudinaryImage(TaggedItemBase):
    content_object = models.ForeignKey("CloudinaryImage", on_delete=models.CASCADE)


class CloudinaryImage(models.Model):
    public_id = models.CharField(max_length=250, primary_key=True)

    url = models.URLField(max_length=1000, null=True, blank=True)
    upload_type = models.CharField(max_length=100, null=True, blank=True)
    resource_type = models.CharField(max_length=100, null=True, blank=True)
    version = models.PositiveIntegerField(null=True, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    tags = TaggableManager(
        through=TaggedCloudinaryImage,
        help_text=None,
        blank=True,
        verbose_name=_("tags"),
    )

    class Meta:
        verbose_name = _("Cloudinary Image")
        verbose_name_plural = _("Cloudinary Images")
        ordering = ["-created_at"]

    @classmethod
    def popular_tags(cls, count=10):
        """Return a queryset of the most frequently used tags used on this model class"""
        return (
            Tag.objects.filter(wagtailcloudinary_taggedcloudinaryimage_items__isnull=False)
            .annotate(item_count=Count("wagtailcloudinary_taggedcloudinaryimage_items"))
            .order_by("-item_count")[:count]
        )

    def __str__(self):
        return self.public_id

    def as_resource(self):
        return CloudinaryResource(
            type=self.upload_type,
            resource_type=self.resource_type,
            version=self.version,
            public_id=self.pk,
        )
