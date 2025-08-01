import re
from rest_framework import serializers
from .models.User import User
from .models.Licensed import Licensed

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'is_licensed']
        extra_kwargs = {'password': {'write_only': True}}


class UserProfileSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'image_profile', 'is_superuser', 'groups']


class LicensedSerializer(serializers.ModelSerializer):
    user = UserSerializer() # Coleção de dados do usuário ( username, email, password, first_name, last_name )
    full_name = serializers.CharField(write_only=True)  

    class Meta:
        model = Licensed
        fields = [
            'user',
            'full_name',
            'original_indicator_id',
            'phone',
            'person_type',
            'cpf_cnpj',
            'cep',
            'state_abbr',
            'city_lookup',
            'district',
            'address',
            'number',
            'complement',
            'plan',
            'accept_lgpd',
            'is_root'
        ]

    def validate(self, data):
        # trata caso campos venham mascara
        data['phone'] = re.sub(r'\D', '', data.get('phone', ''))[:14]
        data['cpf_cnpj'] = re.sub(r'\D', '', data.get('cpf_cnpj', ''))
        data['cep'] = re.sub(r'\D', '', data.get('cep', ''))[:8]

        if data.get('is_root') and not data.get('root_network_name'):
            raise serializers.ValidationError("Root network name é obrigatório para root.")
        if data.get('current_career') and not data.get('previous_career'):
            raise serializers.ValidationError(
                "Não é permitido ter carreira atual sem carreira anterior."
            )
        return data
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        full_name = validated_data.pop('full_name', '')
        nomes = full_name.strip().split(' ', 1)
        user_data['first_name'] = nomes[0]
        user_data['last_name'] = nomes[1] if len(nomes) > 1 else ''
        user = User.objects.create_user(**user_data)
        user.is_licensed = True
        user.save()
        licensed = Licensed.objects.create(user=user, **validated_data)
        return licensed

    # def create(self, validated_data):
    #     user_data = validated_data.pop('user')
    #     user = User.objects.create_user(**user_data)
    #     user.is_licensed = True
    #     user.save()
    #     licensed = Licensed.objects.create(user=user, **validated_data)
    #     return licensed
