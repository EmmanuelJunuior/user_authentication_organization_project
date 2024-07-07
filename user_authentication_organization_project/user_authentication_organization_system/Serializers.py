from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Organisation
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'password', 'phone']

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class OrganisationSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Organisation
        fields = ['id', 'name', 'description', 'users']

from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise serializers.ValidationError('Invalid login credentials.')
        else:
            raise serializers.ValidationError('Both "email" and "password" are required.')

        refresh = RefreshToken.for_user(user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = {
            'user_id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }
        return data

