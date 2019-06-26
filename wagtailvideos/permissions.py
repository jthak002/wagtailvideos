from wagtail.core.permission_policies.collections import (
    CollectionOwnershipPermissionPolicy)

from wagtailvideos.models import Video

permission_policy = CollectionOwnershipPermissionPolicy(
    Video,
    auth_model=Video,
    owner_field_name='uploaded_by_user'
)
