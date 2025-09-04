const ImageChooserFactory =
    window.telepath.constructors["wagtail.images.widgets.ImageChooser"];

class CloudinaryChooserFactory extends ImageChooserFactory {
    // eslint-disable-next-line no-undef
    widgetClass = CloudinaryChooser;
}

window.telepath.register(
    "wagtailcloudinary.widgets.CloudinaryChooser",
    CloudinaryChooserFactory,
);
