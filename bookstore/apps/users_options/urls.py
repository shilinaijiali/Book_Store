from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^users/(?P<pk>.*)/$', views.UserUpdateView.as_view()),
    re_path(r'^messages/$', views.MessageView.as_view()),
    re_path(r'^messages/(?P<id>.*)/$', views.MessageView.as_view()),
    re_path(r'^address/$', views.ReceiveView.as_view()),
    re_path(r'^address/(?P<pk>.*)/$', views.ReceiveView.as_view()),
]