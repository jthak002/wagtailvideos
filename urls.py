from django.conf.urls import url

from wagtailvideos.views import chooser, multiple, videos

app_name = 'wagtailvideos'
urlpatterns = [
    url(r'^$', videos.index, name='index'),
    url(r'^(\d+)/$', videos.edit, name='edit'),
    url(r'^(\d+)/delete/$', videos.delete, name='delete'),
    url(r'^(\d+)/create_transcode/$', videos.create_transcode, name='create_transcode'),

    url(r'^add/$', videos.add, name='add'),
    url(r'^usage/(\d+)/$', videos.usage, name='video_usage'),

    url(r'^multiple/add/$', multiple.add, name='add_multiple'),
    url(r'^multiple/(\d+)/$', multiple.edit, name='edit_multiple'),
    url(r'^multiple/(\d+)/delete/$', multiple.delete, name='delete_multiple'),

    url(r'^chooser/$', chooser.chooser, name='chooser'),
    url(r'^chooser/(\d+)/$', chooser.video_chosen, name='video_chosen'),
    url(r'^chooser/upload/$', chooser.chooser_upload, name='chooser_upload'),
]
