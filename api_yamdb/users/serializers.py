from django.contrib.auth import get_user_model
from rest_framework import serializers
from .validators import ValidateUsername

User = get_user_model()


# class CreateUserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = ('username', 'email')
    
#     def validate_username(self, value):
#         if value.lower() == 'me':
#             raise serializers.ValidationError(
#                 'Имя пользователя "me" не разрешено'
#             )
#         return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

    def validate_role(self, role):
        req_user = self.context['request'].user
        user = User.objects.get(username=req_user)
        if user.is_user:
            role = user.role
        return role


class RegistrationSerializer(serializers.Serializer, ValidateUsername):
    """Сериализатор регистрации User"""

    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)


class TokenSerializer(serializers.Serializer, ValidateUsername):
    """Сериализатор токена"""

    username = serializers.CharField(required=True, max_length=150)
    confirmation_code = serializers.CharField(required=True)