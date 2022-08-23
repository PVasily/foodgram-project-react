# from django.shortcuts import get_object_or_404
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.decorators import action

# from .models import User
# from .serializers import UserSerializer

# class UserViewset(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     @action(
#         detail=False,
#         methods=['GET'],
#         url_path='me'
#     )
#     def me(self, request):
#         me = get_object_or_404(User, username=request.user)
#         serializers = self.get_serializer(me)
#         return Response(serializers.data, status=status.HTTP_200_OK)
