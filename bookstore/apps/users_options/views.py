from rest_framework.generics import UpdateAPIView, CreateAPIView, ListAPIView, DestroyAPIView, ListCreateAPIView
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

# get_user_model 用户获取可验证的用户模型类
from rest_framework.response import Response

from users_options.models import UserLeavingMessage, UserAddress
from users_options.seriazliers import UserUpdateSerializer, LeavingSerializer, AddressSerializer

User = get_user_model()     # 获取用户模型类


class UserUpdateView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

    def get_object(self):
        # 不管传入的id是多少，都只返回当前的请求用户
        return self.request.user


class MessageView(CreateAPIView, ListAPIView, DestroyAPIView):
    queryset = UserLeavingMessage.objects.all()
    serializer_class = LeavingSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        message_id = kwargs.get('id')
        self.queryset.filter(id=message_id).delete()
        return Response(status=204)


class ReceiveView(ListCreateAPIView, UpdateAPIView, DestroyAPIView):
    queryset = UserAddress.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        id_ = kwargs.get('pk')
        data = request.data
        print(request.data)
        # filter查询取出的是所有满足条件的数据
        # exclude查询取出的是所有与当前过滤条件相反的数据
        addr_obj = self.get_queryset().filter()
        # instance表示要修改的对象实例
        serializer = self.get_serializer(data=data, instance=addr_obj.first())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # print(addr_obj)
        return Response({"message": "收货地址更新成功"})

    def destroy(self, request, *args, **kwargs):
        """使用jwt验证的时候，后端服务器运行前后的token需要保持同步，"""
        id_ = kwargs.get('pk')
        addr_obj = self.get_queryset().filter(id=id_).delete()
        print(addr_obj)
        return Response({"message": "删除成功"}, status=204)

    """
        desdroy重写之前，指定了当前的视图类返回的对象一直为请求用户对象，结合DestroyAPIView底层方法来看，
        其删除的对象为get_object方法的返回值，由于将get_object方法的返回值返回的为请求的用户，所以在进行删除的时候，
        将当前请求的用户删除，并级联删除掉了该用户的收货地址等信息
    """
