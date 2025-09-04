from django.urls import path, reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import View
from wagtail.admin.views.generic.chooser import (
    BaseChooseView,
    ChooseResultsViewMixin,
    ChooseViewMixin,
    ChosenResponseMixin,
    ChosenViewMixin,
    CreateViewMixin,
    CreationFormMixin,
)
from wagtail.admin.viewsets.chooser import ChooserViewSet

from ..api import CloudinaryBrowser
from ..models import CloudinaryImage


class CloudinaryChosenResponseMixin(ChosenResponseMixin):
    def get_chosen_response_data(self, image):
        response_data = super().get_chosen_response_data(image)
        response_data["preview"] = {
            "url": image.url,
            "width": 165,
            "height": 165,
        }
        return response_data


class CloudinaryCreationFormMixin(CreationFormMixin):
    pass


class BaseCloudinaryChooseView(BaseChooseView):
    template_name = "wagtailcloudinary/chooser/chooser.html"
    results_template_name = "wagtailcloudinary/chooser/results.html"
    ordering = "-created_at"

    def get_results_page(self, request):
        cursor = request.GET.get("p")
        tag_filter = request.GET.get("tag")

        browser = CloudinaryBrowser()
        page = browser.get_images(
            tag=tag_filter,
            page_size=25,
            next_cursor=cursor,
            alive_only=(False if tag_filter else True),  # fetching assets by using "resources_by_tag" only returns active images.
        )
        return page

    @cached_property
    def collections(self):
        return None

    def get(self, request):
        self.model = CloudinaryImage
        return super().get(request)


class CloudinaryChooseViewMixin(ChooseViewMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["popular_tags"] = CloudinaryImage.popular_tags(50)
        return context

    def get_response_json_data(self):
        json_data = super().get_response_json_data()
        json_data["tag_autocomplete_url"] = reverse("wagtailadmin_tag_autocomplete")
        return json_data


class CloudinaryChooseView(CloudinaryChooseViewMixin, CloudinaryCreationFormMixin, BaseCloudinaryChooseView):
    pass


class CloudinaryChooseResultsView(ChooseResultsViewMixin, CloudinaryCreationFormMixin, BaseCloudinaryChooseView):
    pass


class CloudinaryChosenView(ChosenViewMixin, CloudinaryChosenResponseMixin, View):
    model = CloudinaryImage

    def get(self, request, *args, pk, **kwargs):
        item = self.get_object(pk)
        return self.get_chosen_response(item)


class CloudinaryUploadViewMixin(CreateViewMixin):
    model = CloudinaryImage

    def post(self, request):
        self.form = self.get_creation_form()

        if self.form.is_valid():
            image = self.save_form(self.form)

            # not specifying a format; return the image details now
            return self.get_chosen_response(image)

        else:  # form is invalid
            return self.get_reshow_creation_form_response()


class CloudinaryUploadView(
    CloudinaryUploadViewMixin,
    CloudinaryCreationFormMixin,
    CloudinaryChosenResponseMixin,
    View,
):
    pass


class CloudinaryChooserViewSet(ChooserViewSet):
    choose_view_class = CloudinaryChooseView
    choose_results_view_class = CloudinaryChooseResultsView
    chosen_view_class = CloudinaryChosenView
    create_view_class = CloudinaryUploadView
    register_widget = False

    icon = "image"
    choose_one_text = _("Choose an image")
    create_action_label = _("Upload")
    create_action_clicked_label = _("Uploading…")

    def get_urlpatterns(self):
        return super().get_urlpatterns() + [
            path("", self.choose_view, name="choose"),
            path("results/", self.choose_results_view, name="choose_results"),
            path("chosen/<path:pk>/", self.chosen_view, name="chosen"),
            path("create/", self.create_view, name="create"),
        ]


viewset = CloudinaryChooserViewSet(
    "wagtailcloudinary_chooser",
    model=CloudinaryImage,
    url_prefix="cloudinary/chooser",
)
