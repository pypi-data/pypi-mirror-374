from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html
from wagtail import hooks

from .views.chooser import viewset as cloudinary_viewset


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', static("wagtailcloudinary/css/main.css"))


@hooks.register("insert_editor_js")
def editor_js():
    return format_html(
        """
        <script>
            window.chooserUrls.cloudinaryChooser = '{0}';
        </script>
        """,
        reverse("wagtailcloudinary_chooser:choose"),
    )


@hooks.register("register_admin_viewset")
def register_cloudinary_chooser_viewset():
    return cloudinary_viewset
