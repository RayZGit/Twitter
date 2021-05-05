from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import  Response
from django.contrib.auth import (
    logout as django_logout,
    login as django_login,
    authenticate as django_authenticate,
)

# the customized package
from accounts.api.serializers import UserSerializer, LoginSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class AccountViewSet(viewsets.ViewSet):
    serializer_class = LoginSerializer

    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({'success':True})

    @action(methods=['POST'], detail = False)
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check your input",
                "errors": serializer.errors,
            }, status =400)

        #validation of the user authentication
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # check exist of the user ---- optional [Security]
        if not User.objects.filter(username=username).exists():
            return Response({
                "success": False,
                "message": "User doesn't exist",
            }, status = 400)

        # validate the password and username
        user = django_authenticate(username = username, password = password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "username and password doesn't match",
            }, status=400)

        # login
        django_login(request,user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })