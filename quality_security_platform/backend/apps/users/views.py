from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from .models import User
from .serializers import *
from apps.base.viewsets import BaseModelViewSet
class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update'] and not self.request.user.is_superuser:
            return UserUpdateSerializer
        if self.action == 'change_password':
            return PasswordChangeSerializer
        if self.action == 'login':
            return UserLoginSerializer
        return UserSerializer
    def get_permissions(self):
        if self.action == 'login':
            return [AllowAny()]
        return super().get_permissions()
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.validated_data)
        if user:
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response({'error': '用户名或密码错误'}, status=401)
    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': '退出成功'})
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': '原密码错误'}, status=400)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': '密码修改成功'})
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
