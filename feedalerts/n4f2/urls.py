from django.conf.urls import url

from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<feedrun_pk>[0-9]+)/notify/$', views.notify, name='notify'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)