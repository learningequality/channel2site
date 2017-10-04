from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<requestpath>.*)$', views.render, name='render'),
]
