import re

from django.forms.models import model_to_dict
from django.utils.functional import cached_property
from wagtail.blocks import ChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from .utils import CloudinaryResource, str_to_cloudinary_resource


class CloudinaryImageBlock(ChooserBlock):
    class Meta:
        icon = "image"

    def __init__(self, required=True, help_text=None, **kwargs):
        self.field_options = {
            "required": required,
            "help_text": help_text,
        }
        super().__init__(required, help_text, **kwargs)

    @cached_property
    def target_model(self):
        from .models import CloudinaryImage

        return CloudinaryImage

    @cached_property
    def widget(self):
        from .widgets import AdminCloudinaryChooser

        return AdminCloudinaryChooser()

    def to_python(self, value):
        value = self.prep_image_pk(value)
        return super().to_python(value)

    def bulk_to_python(self, values):
        values = [self.prep_image_pk(value) for value in values]
        return super().bulk_to_python(values)

    def prep_image_pk(self, value):
        return re.sub(r"^image\/upload\/v\d+\/", "", value or "", count=1)

    def get_prep_value(self, value):
        return getattr(value, "public_id", value)

    def get_api_representation(self, value, context=None):
        # Treat "" as None
        if value == "":
            value = None
        elif value is not None:
            value = getattr(value, "public_id", None) or str_to_cloudinary_resource(value).public_id
        return super().get_api_representation(value, context)


class CloudinarySnippetChooserBlock(SnippetChooserBlock):
    """
    Use this snippet chooser block when you have a snippet that contains a
    CloudinaryField AND you must display the details of the snippet in the
    Wagtail API (http://docs.wagtail.io/en/v2.4/advanced_topics/api/).
    """

    def get_api_representation(self, value, context=None):
        snippet_dict = model_to_dict(value)
        for key, value in snippet_dict.items():
            if type(value) is CloudinaryResource:
                snippet_dict[key] = value.public_id
        return snippet_dict
