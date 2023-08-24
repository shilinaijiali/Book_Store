from django.urls import re_path
from users import views
from rest_framework_jwt.views import obtain_jwt_token
from goods.urls import router
# 一个项目中只能定义一个DefaultRouter

urlpatterns = [
    re_path(r'^code/$', views.SmscodeView.as_view()),    # 发送短信
    re_path(r'^users/$', views.RegisView.as_view()),
    re_path(r'^login/$', obtain_jwt_token),
    # re_path(r'^userfavs/(?P<pk>.*)/$', views.UserFavViewset.as_view({"delete": 'destroy'}))
]
router.register('userfavs', views.UserFavViewset, basename='userfavs')
urlpatterns += router.urls