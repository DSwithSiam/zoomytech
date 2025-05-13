from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from accounts.models import CustomUser, CompanyDetails

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Password and Confirm Password do not match.")
        
        try:
            password_validation.validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        user = User.objects.create_user(
            full_name=validated_data.get('full_name', ''),
            email=validated_data['email'],
            username=validated_data['email'].split('@')[0], 
            password=validated_data['password']
        )
        return user
    

class CompanyDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model = CompanyDetails
        fields = "__all__"
        read_only_fields = ["id", 'user']