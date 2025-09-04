from django.contrib import admin

from . import models


@admin.register(models.CloudinaryImage)
class ClientAdmin(admin.ModelAdmin):
    fields = [
        "public_id",
        "upload_type",
        "resource_type",
        "version",
        "url",
        "width",
        "height",
        "tag_list",
        "created_at",
    ]
    readonly_fields = fields
    list_display = fields
    search_fields = ["public_id"]
    list_filter = ["created_at", "tags"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags")

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
