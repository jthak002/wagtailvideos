import json

from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from wagtail.admin.widgets import AdminChooser

from wagtailvideos.models import Video


class AdminVideoChooser(AdminChooser):
    choose_one_text = _('Choose a video')
    choose_another_text = _('Choose another video')
    link_to_chosen_text = _('Edit this video')

    def __init__(self, **kwargs):
        super(AdminVideoChooser, self).__init__(**kwargs)
        self.video_model = Video

    def render_html(self, name, value, attrs):
        instance, value = self.get_instance_and_id(self.video_model, value)
        original_field_html = super(AdminVideoChooser, self).render_html(name, value, attrs)

        return render_to_string("wagtailvideos/widgets/video_chooser.html", {
            'widget': self,
            'original_field_html': original_field_html,
            'attrs': attrs,
            'value': value,
            'video': instance,
        })

    def render_js_init(self, id_, name, value):
        return "createVideoChooser({0});".format(json.dumps(id_))
