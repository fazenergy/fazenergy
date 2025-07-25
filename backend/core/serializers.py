from rest_framework import serializers
from .models.user_manager import User, Affiliate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class UserProfileSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'image_profile', 'is_superuser', 'groups']


class AffiliateSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Affiliate
        fields = [
            'id', 'user', 'cpf', 'address',
            'is_root', 'root_network_name',
            'dynamic_compression', 'annual_plan_paid',
            'parent'
        ]

    def validate(self, data):
        if data.get('is_root') and not data.get('root_network_name'):
            raise serializers.ValidationError("Root network name é obrigatório para root.")
        if data.get('current_career') and not data.get('previous_career'):
            raise serializers.ValidationError(
                "Não é permitido ter carreira atual sem carreira anterior."
            )
        return data

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        user.is_affiliate = True
        user.save()
        affiliate = Affiliate.objects.create(user=user, **validated_data)
        return affiliate
