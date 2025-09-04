import collections.abc
import logging

import cloudinary.api
import dateutil.parser

from .models import CloudinaryImage

logger = logging.getLogger(__name__)


class CloudinaryPage(collections.abc.Sequence):
    def __init__(self, items=[], next_cursor=None):
        self.items = items
        self.next_cursor = next_cursor

    def __repr__(self):
        return f"<CloudinaryPage num_items={len(self.items)} next_cursor={self.next_cursor}>"

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        if not isinstance(index, (int, slice)):
            raise TypeError("CloudinaryPage indices must be integers or slices, not %s." % type(index).__name__)
        # The items is converted to a list so that if it was a QuerySet
        # it won't be a database hit per __getitem__.
        if not isinstance(self.items, list):
            self.items = list(self.items)
        return self.items[index]

    def has_next(self):
        return self.next_cursor is not None

    def has_previous(self):
        return False

    def has_other_pages(self):
        return self.has_previous() or self.has_next()

    def next_page_number(self):
        return self.next_cursor

    def previous_page_number(self):
        return None


class CloudinaryBrowser:
    def get_images(self, tag=None, page_size=10, next_cursor=None, alive_only=False):
        # Fetch a page of results from the API
        if alive_only:
            response = (
                cloudinary.Search()
                .expression("status:active")
                .sort_by("created_at", "desc")
                .max_results(page_size)
                .next_cursor(next_cursor or "")
                .with_field("tags")
                .execute()
            )
        else:
            params = {
                "max_results": page_size,
                "tags": True,
            }
            if next_cursor:
                params["next_cursor"] = next_cursor
            if tag:
                response = cloudinary.api.resources_by_tag(tag, **params)
            else:
                response = cloudinary.api.resources(**params)
        # Insert/update API results into the DB
        images = self.insupd_images(response) if len(response["resources"]) > 0 else []
        # Return a page of results
        page = CloudinaryPage(
            items=images,
            next_cursor=response.get("next_cursor"),
        )
        return page

    def insupd_images(self, response):
        """
        Take a Cloudinary API response and insert/update all of the images in
        the response. Returns a list of CloudinaryImage model objects in the
        same order as the resources in the API response.
        """
        resources = {r["public_id"]: r for r in response["resources"]}

        # Find all the rows that already exist and update them with the latest metadata
        existing_objs = [self.update_meta_fields(obj, resources[obj.pk]) for obj in CloudinaryImage.objects.filter(public_id__in=resources.keys()).all()]
        CloudinaryImage.objects.bulk_update(
            existing_objs,
            list(self.get_meta_fields(response["resources"][0]).keys()),
        )

        # Insert any rows that didn't already exist
        nonexisting_ids = set(resources.keys()) - {obj.pk for obj in existing_objs}
        batch = [
            CloudinaryImage(
                public_id=public_id,
                **self.get_meta_fields(resources[public_id]),
            )
            for public_id in nonexisting_ids
        ]
        new_objs = CloudinaryImage.objects.bulk_create(batch)

        # Log what we did
        logger.error(
            "CloudinaryBrowser updated %s rows, inserted %s rows",
            len(existing_objs),
            len(new_objs),
        )

        # Build a combined list of items in the same order the API gave them to us.
        combined_objs = {obj.pk: obj for obj in (list(existing_objs) + list(new_objs))}
        combined_objs = [combined_objs[r["public_id"]] for r in response["resources"]]

        # Update each rows tags (since this m2m update can't be done as a bulk
        # operation like the rest of the metadata fields)
        for obj in combined_objs:
            obj.tags.set(resources[obj.pk]["tags"])

        return combined_objs

    def update_meta_fields(self, obj, data):
        meta = self.get_meta_fields(data)
        for key, value in meta.items():
            setattr(obj, key, value)
        return obj

    def get_meta_fields(self, data):
        meta = {
            "url": data.get("secure_url"),
            "upload_type": data.get("type"),
            "resource_type": data.get("resource_type"),
            "version": data.get("version"),
            "width": data.get("width"),
            "height": data.get("height"),
            "created_at": self.parse_dt(data.get("created_at")),
        }
        return meta

    def parse_dt(self, iso_dt):
        return dateutil.parser.parse(iso_dt) if iso_dt else None
