from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from djoser.views import UserViewSet

from .models import User, Follow
from .serializers import (
    SubscriptionGetSerializer,
    UserGetSerializer,
    UserSerializer
)


class UserViewset(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=['GET'],
        url_path='me',
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        me = get_object_or_404(User, username=request.user)
        serializers = self.get_serializer(me)
        return Response(serializers.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        user_subscriptions = User.objects.filter(following__user=request.user)
        serializer = SubscriptionGetSerializer(
            user_subscriptions,
            context=self.get_serializer_context(),
            many=True
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, *args, **kwargs):
        follower = request.user
        following = get_object_or_404(User, id=self.kwargs['id'])
        if request.method == 'POST':
            serializer_class = SubscriptionGetSerializer
            serializer = serializer_class(
                following,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            if not Follow.objects.filter(
                    user=follower,
                    author=following).exists():
                Follow.objects.create(user=follower, author=following)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
        subscr = get_object_or_404(Follow, user=follower, author=following)
        subscr.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
