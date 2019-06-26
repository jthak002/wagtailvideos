from django.apps import AppConfig
from django.core.checks import Warning, register

from wagtailvideos import ffmpeg


def ffmpeg_check(app_configs, **kwargs):
    messages = []
    if not ffmpeg.installed():
        messages.append(
            Warning(
                'ffmpeg could not be found on your system. Transcoding will be disabled',
                hint=None,
                id='wagtailvideos.W001',
            )
        )
    return messages


class WagtailVideosApp(AppConfig):
    name = 'wagtailvideos'
    label = 'wagtailvideos'
    verbose_name = 'Wagtail Videos'

    def ready(self):
        register(ffmpeg_check)
