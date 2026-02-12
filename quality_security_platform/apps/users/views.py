from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from .models import User
from .serializers import *

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
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
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.can_manage_users:
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.validated_data)
        if user:
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
    
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
            return Response({'old_password': '原密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': '密码修改成功'})
