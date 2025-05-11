
from rest_framework import serializers
from blog.models import Post
from django.contrib.auth.models import User

class PostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField("get_username_from_author")
    class Meta:
        model = Post

        fields = ["id", "title", "content", "date_posted", "slug", "username"]

    
    def get_username_from_author(self, post):
        username = post.author.username
        return username


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]
        exra_kwargs = {
            "password": {"write_only": True}
        }

    def save(self):
        user = User(
            email=self.validated_data["email"],
            username=self.validated_data["username"]
        )
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise serializers.ValidationError({"Response": "Passwords must match"})
        user.set_password(password)
        user.save()
        return user


class UserPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = ["pk", "email", "username"]



