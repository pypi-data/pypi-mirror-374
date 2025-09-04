from django.core.management.base import BaseCommand

from wagtailcloudinary.api import CloudinaryBrowser
from wagtailcloudinary.models import CloudinaryImage


class Command(BaseCommand):
    help = "Import all images from Cloudinary"

    def handle(self, *args, **options):
        browser = CloudinaryBrowser()
        kwargs = {
            "page_size": 100,
        }
        i = 0
        # Import all of the images from cloudinary
        imported_pks = set()
        while True:
            i += 1
            # Import a page of images
            page = browser.get_images(**kwargs)
            for img in page.items:
                imported_pks.add(img.pk)
            self.stdout.write(self.style.SUCCESS("Imported page %s" % i))
            # Continue to next page, if one exists.
            if page.next_cursor:
                kwargs["next_cursor"] = page.next_cursor
            else:
                kwargs.pop("next_cursor", None)

            if "next_cursor" not in kwargs:
                break
        # Delete any images from our DB that were missing form cloudinary
        deleted = CloudinaryImage.objects.exclude(pk__in=imported_pks).all().delete()
        self.stdout.write(self.style.SUCCESS(f"Done. Imported {len(imported_pks)} rows and deleted {deleted[0]} rows"))
