from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<feedrun_pk>[0-9]+)/notify/$', views.notify, name='notify'),
]