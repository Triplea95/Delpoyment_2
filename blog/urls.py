from django.urls import path
from .views import home, detail


urlpatterns = [
    path("", home, name="home"),
    path("<slug:slug>/", detail, name="detail")
]