from django.urls import re_path
# from goods.urls import router

from . import views
from apps.goods.urls import router

urlpatterns = [
    re_path(r'^shoppingCart/clear$', views.ShoppingCartDelView.as_view()),
    re_path(r'^alipay/return/$', views.AlipayView.as_view()),
]

router.register('shopcarts', views.ShoppingCartViewSet, basename='shopcarts')
router.register('orders', views.OrderViewSet, basename='orders')
urlpatterns += router.urls
