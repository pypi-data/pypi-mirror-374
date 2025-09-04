import json

from django import forms
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.staticfiles import versioned_static
from wagtail.admin.widgets import BaseChooser
from wagtail.telepath import register
from wagtail.widget_adapters import WidgetAdapter

from .models import CloudinaryImage


class AdminCloudinaryChooser(BaseChooser):
    choose_one_text = _("Choose an image")
    template_name = "wagtailcloudinary/widgets/cloudinary_chooser.html"
    choose_another_text = _("Change image")
    chooser_modal_url_name = "wagtailcloudinary_chooser:choose"
    icon = "media"
    classname = "image-chooser"
    model = CloudinaryImage

    def get_value_data_from_instance(self, instance):
        data = super().get_value_data_from_instance(instance)
        data["preview"] = {
            "url": instance.url,
            "width": 165,
            "height": 165,
        }
        return data

    def get_context(self, name, value_data, attrs):
        context = super().get_context(name, value_data, attrs)
        context["preview"] = value_data.get("preview", {})
        return context

    def render_js_init(self, id_, name, value_data):
        return f"new CloudinaryChooser({json.dumps(id_)});"

    @property
    def media(self):
        return forms.Media(
            js=[
                versioned_static("wagtailimages/js/image-chooser-modal.js"),
                versioned_static("wagtailimages/js/image-chooser.js"),
                versioned_static("wagtailcloudinary/js/cloudinary-chooser.js"),
            ]
        )


class CloudinaryChooserAdapter(WidgetAdapter):
    js_constructor = "wagtailcloudinary.widgets.CloudinaryChooser"

    @cached_property
    def media(self):
        return forms.Media(
            js=[
                versioned_static("wagtailimages/js/image-chooser-telepath.js"),
                versioned_static("wagtailcloudinary/js/cloudinary-chooser-telepath.js"),
            ]
        )


register(CloudinaryChooserAdapter(), AdminCloudinaryChooser)
