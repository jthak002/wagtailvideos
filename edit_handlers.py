from wagtail.admin.edit_handlers import BaseChooserPanel

from .widgets import AdminVideoChooser


class VideoChooserPanel(BaseChooserPanel):
    model = None
    field_name = None
    _target_model = None

    object_type_name = "video"

    def widget_overrides(self):
        return {self.field_name: AdminVideoChooser}
