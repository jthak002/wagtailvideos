from __future__ import unicode_literals

from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase

from tests.utils import create_test_video_file
from wagtailvideos.models import Video


class TestVideoTag(TestCase):
    def setUp(self):
        self.video = Video.objects.create(
            title="Test Video",
            file=create_test_video_file()
        )

    def render_video_tag(self, video, attrs=''):
        temp = Template('{% load wagtailvideos_tags %}{% video video_obj ' + attrs + ' %}')
        context = Context({'video_obj': video})
        return temp.render(context)

    def test_video_tag(self):
        tag = self.render_video_tag(self.video)
        self.assertTrue(self.video.url in tag)

    def test_extra_attributes(self):
        tag = self.render_video_tag(self.video, attrs='controls width=560')
        self.assertTrue('controls' in tag)
        self.assertTrue('width="560"' in tag)

    def test_bad_video(self):
        try:
            self.render_video_tag(None)
        except TemplateSyntaxError as e:
            self.assertEqual(str(e), 'video tag requires a Video object as the first parameter')
