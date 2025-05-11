from django.shortcuts import render
from .models import Post

# Create your views here.

def home(request):
    posts = Post.objects.all()
    return render(request, "blog/home.html", {"posts":posts})


def detail(request, slug):
    post = Post.objects.get(slug=slug)
    return render(request, "blog/detail.html", {"post":post})
