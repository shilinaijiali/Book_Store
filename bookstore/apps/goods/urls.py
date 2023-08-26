from django.urls import re_path
from rest_framework.routers import DefaultRouter

from apps.goods import views

# from goods import views

urlpatterns = [
    # re_path(r'^categories/$', views.GoodsCategoryView.as_view()),
    re_path(r'^goods/$', views.GoodsListView.as_view()),
    re_path(r'^hotsearchs/$', views.HotSearchView.as_view()),
    re_path(r'^indexgoods/$', views.IndexGoodView.as_view()),
    re_path(r'^banners/$', views.BannersView.as_view()),
    re_path(r'^goods/(?P<pk>.*)/$', views.GoodDetailView.as_view()),
]
router = DefaultRouter()
router.register('categories', views.GoodsCategoryView)
urlpatterns += router.urls
