import re

import cloudinary

CLOUDINARY_FIELD_DB_RE = (
    r"(?:(?P<resource_type>image|raw|video)/(?P<type>upload|private|authenticated)/)?(?:v(?P<version>\d+)/)?(?P<public_id>.*?)(\.(?P<format>[^.]+))?$"  # NOQA
)


class CloudinaryResource(cloudinary.CloudinaryResource):
    @property
    def base_url(self):
        config = cloudinary.config()
        base_url = f"https://res.cloudinary.com/{config.cloud_name}/"
        return f"{base_url}{self.resource_type}/{self.type}"

    @property
    def versioned_public_id(self):
        version = f"v{self.version}/" if self.version else ""  # if '/' not in self.public_id else 'v1/'
        return f"/{version}{self.public_id}"


def str_to_cloudinary_resource(value, resource_type="image", _type="upload"):
    if value == "":
        return None
    m = re.match(CLOUDINARY_FIELD_DB_RE, value)
    resource_type = m.group("resource_type") or resource_type
    upload_type = m.group("type") or _type
    return CloudinaryResource(
        type=upload_type,
        resource_type=resource_type,
        version=m.group("version"),
        public_id=m.group("public_id"),
        format=m.group("format"),
    )
