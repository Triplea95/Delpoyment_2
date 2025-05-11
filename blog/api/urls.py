from .views import api_list_view, api_detail_view, api_update_view, api_create_view, api_delete_view, registration_view, PostListView, account_properties_view, update_user_view
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("", api_list_view, name="list"),
    path('properties', account_properties_view, name="properties"),
    path("properties/update", update_user_view, name="properties-update"),
    path("create/", api_create_view, name="create"),
    path("<slug:slug>/", api_detail_view, name="detail"),
    path("<slug:slug>/update", api_update_view, name="update"),
    path("<slug:slug>/delete", api_delete_view, name='delete'),
    path("register", registration_view, name="register"),
    path("login", obtain_auth_token, name="login"),
    path("list", PostListView.as_view(), name="list")
 
]