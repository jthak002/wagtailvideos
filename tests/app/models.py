from __future__ import unicode_literals

from django.db import models
from wagtail.core.models import Page

from wagtailvideos.edit_handlers import VideoChooserPanel


class TestPage(Page):
    video_field = models.ForeignKey('wagtailvideos.Video', related_name='+', null=True, blank=True, on_delete=models.SET_NULL)

    content_panels = Page.content_panels + [
        VideoChooserPanel('video_field')
    ]
