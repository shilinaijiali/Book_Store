from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from goods.filters import GoodsFilter
from goods.models import GoodsCategory, Goods, HotSearchWords, Banner
from goods.serializers import GoodsCategorySer, GoodsSerializer, HotSearchSerializer, IndexCategorySerializer, \
    BannerSerializer, GoodsDetailSerializer


# class GoodsCategoryView(ListAPIView):
#     queryset = GoodsCategory.objects.all()
#     serializer_class = GoodsCategorySer

class GoodsCategoryView(ReadOnlyModelViewSet):
    queryset = GoodsCategory.objects.all()
    serializer_class = GoodsCategorySer


class GoodsPagination(PageNumberPagination):
    page_size = 12   # 表示每页多少条数据
    # 向后台要多少条
    page_size_query_param = 'page_size'  # 分页数参数名
    # 定制多少页的参数
    page_query_param = "page"
    max_page_size = 100     # 最大分为多少页，此处为100页


class GoodsListView(ListAPIView):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ('name', 'goods_brief', 'goods_desc')
    ordering_fields = ('sold_num', 'shop_price')
    filter_class = GoodsFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # print(queryset)

        page = self.paginate_queryset(queryset)
        print(request.GET.get('search'))
        if page is not None:
            if request.GET.get('search'):
                data = HotSearchWords.objects.filter(keywords=request.GET.get('search'))
                ins = data.first()
                if data:
                    ins.index += 1
                    ins.save()
                else:
                    HotSearchWords.objects.create(keywords=request.GET.get('search'), index=1)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class HotSearchView(ListAPIView):
    queryset = HotSearchWords.objects.all().order_by('-index')
    serializer_class = HotSearchSerializer


class IndexGoodView(ListAPIView):
    queryset = GoodsCategory.objects.filter(is_tab=True, name__in=['文学类', '工学类'])
    serializer_class = IndexCategorySerializer


class BannersView(ListAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer


class GoodDetailView(ListAPIView):
    queryset = Goods.objects.all()
    serializer_class = GoodsDetailSerializer

    def list(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        good = self.get_queryset().filter(id=int(pk)).first()
        serializer = self.get_serializer(good)
        res = serializer.data
        res['images'] = ['https://django07lq.oss-cn-beijing.aliyuncs.com/media/goods/images/sq1.jpg',
                         'https://django07lq.oss-cn-beijing.aliyuncs.com/media/goods/images/sq1.jpg',
                         'https://django07lq.oss-cn-beijing.aliyuncs.com/media/goods/images/sq1.jpg']
        print(res.get('images'))
        print(res)
        return Response(res)
