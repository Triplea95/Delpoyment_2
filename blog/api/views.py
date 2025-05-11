import re
from rest_framework import serializers
from rest_framework import  status
from rest_framework.decorators import api_view, permission_classes
from blog.models import Post
from rest_framework.permissions import IsAuthenticated
from .serializers import PostSerializer, RegistrationSerializer, UserPropertiesSerializer
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter

@api_view(["GET"])
def api_list_view(request):
    try:
        posts = Post.objects.all()
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def api_detail_view(request, slug):
    try:
        post = Post.objects.get(slug=slug)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = PostSerializer(post)
        return Response(serializer.data)


@api_view(["PUT"])
@permission_classes((IsAuthenticated,))
def api_update_view(request, slug):
    try:
        post = Post.objects.get(slug=slug)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if post.author != user:
        return Response({"Response": "You cannot edit a post you didn't create"})

    if request.method == "PUT":
        serializer = PostSerializer(post, data=request.data)
        data = {}
        if serializer.is_valid():
            new_post = serializer.save()
            data["success"] = "update successful"
            data["title"] = new_post.title
            data["content"] = new_post.content
            data["slug"] = new_post.slug
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def api_delete_view(request, slug):
    try:
        post = Post.objects.get(slug=slug)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if post.author != user:
        return Response({"Response": "You cannot delete a post you didn't create"})


    if request.method == "DELETE":
        data = {}
        operation = post.delete()
        if operation:
            data["success"] = "Post deleted successfully!"
        else:
            data["failure"] = "Post delete failed"
        return Response(data=data)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def api_create_view(request):
    user = request.user
    post = Post(author=user)

    if request.method == "POST":
        serializer = PostSerializer(post, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def registration_view(request):
    if request.method == "POST":
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.save()
            data["Response"] = "Successfully registered a new user"
            data["email"] = user.email
            data["username"] = user.username
            token = Token.objects.get(user=user).key
            data["token"] = token
        else:
            data = serializer.errors
        return Response(data)


class PostListView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("title", "content", "slug", "author__username")
    

@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def account_properties_view(request):
    try:
        user = request.user
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = UserPropertiesSerializer(user)
        return Response(serializer.data)



@api_view(["PUT"])
@permission_classes((IsAuthenticated,))
def update_user_view(request):
    try:
        user = request.user
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = UserPropertiesSerializer(user, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data["response"] = "Account update success"
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

