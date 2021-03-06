from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework import exceptions

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class UserSerializerForTweet(serializers.HyperlinkedModelSerializer):
     class Meta:
        model = User
        fields = ('id', 'username',)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields =  ('username', 'password', 'email')

    # will be called when is_valid() is called
    # validate function is to change make the data not sensitive to upper case
    def validate(self, data):
        if User.objects.filter(username = data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This username has been occupied.'
            })
        if User.objects.filter(email = data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This email address has been occupied.'
            })
        return data

    def create(self, validated_data):
        username =  validated_data['username'].lower()
        password = validated_data['password']
        email = validated_data['email'].lower()

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        return user



