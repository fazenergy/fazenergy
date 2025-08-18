import re
from rest_framework import serializers
from .models.User import User
from .models.Licensed import Licensed
from django.contrib.auth.models import Group

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class UserProfileSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True)
    # Campos extras do Licensed
    phone = serializers.SerializerMethodField()
    cpf_cnpj = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    number = serializers.SerializerMethodField()
    complement = serializers.SerializerMethodField()
    plan = serializers.SerializerMethodField()
    # Atualização de senha opcional
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'image_profile',
            'is_superuser', 'groups',
            'phone', 'cpf_cnpj', 'city', 'address', 'number', 'complement', 'plan',
            'password'
        ]

    def _get_licensed(self, obj):
        try:
            return Licensed.objects.select_related('plan', 'city_lookup').get(user=obj)
        except Licensed.DoesNotExist:
            return None

    def get_phone(self, obj):
        lic = self._get_licensed(obj)
        return getattr(lic, 'phone', None) if lic else None

    def get_cpf_cnpj(self, obj):
        lic = self._get_licensed(obj)
        return getattr(lic, 'cpf_cnpj', None) if lic else None

    def get_city(self, obj):
        lic = self._get_licensed(obj)
        return getattr(getattr(lic, 'city_lookup', None), 'name', None) if lic else None

    def get_address(self, obj):
        lic = self._get_licensed(obj)
        return getattr(lic, 'address', None) if lic else None

    def get_number(self, obj):
        lic = self._get_licensed(obj)
        return getattr(lic, 'number', None) if lic else None

    def get_complement(self, obj):
        lic = self._get_licensed(obj)
        return getattr(lic, 'complement', None) if lic else None

    def get_plan(self, obj):
        lic = self._get_licensed(obj)
        return getattr(getattr(lic, 'plan', None), 'name', None) if lic else None

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class LicensedSerializer(serializers.ModelSerializer):
    user = UserSerializer() # Coleção de dados do usuário ( username, email, password, first_name, last_name )
    full_name = serializers.CharField(write_only=True)  
    referrer = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Licensed
        fields = [
            'user',
            'full_name',
            'referrer',
            'original_indicator_id',
            'phone',
            'person_type',
            'cpf_cnpj',
            'cep',
            'city_lookup',
            'district',
            'address',
            'number',
            'complement',
            'plan',
            'accept_lgpd',
            'is_root',
            'root_network_name',
            'dtt_activation',
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
        # Resolve indicador (original_indicator)
        request = self.context.get('request')
        # username vindo do payload (ex.: form.referrer)
        ref_username = self.initial_data.get('referrer') or data.pop('referrer', None)

        indicator = None
        if request and request.user and request.user.is_authenticated:
            try:
                indicator = Licensed.objects.get(user=request.user)
            except Licensed.DoesNotExist:
                indicator = None
        if not indicator and ref_username:
            try:
                # procura licenciado pelo username (case-insensitive)
                indicator = Licensed.objects.get(user__username__iexact=ref_username)
            except Licensed.DoesNotExist:
                raise serializers.ValidationError({
                    'referrer': 'Usuário indicador inválido.'
                })

        if indicator:
            data['original_indicator_id'] = indicator.id

        return data
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        full_name = validated_data.pop('full_name', '')
        nomes = full_name.strip().split(' ', 1)
        user_data['first_name'] = nomes[0]
        user_data['last_name'] = nomes[1] if len(nomes) > 1 else ''
        user = User.objects.create_user(**user_data)

        # Adiciona o usuário ao grupo "Licenciado"
        licenciado_group, _ = Group.objects.get_or_create(name='Licenciado')
        user.groups.add(licenciado_group)

        licensed = Licensed.objects.create(user=user, **validated_data)
        return licensed

class LicensedListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    plan = serializers.SerializerMethodField()
    city_lookup = serializers.SerializerMethodField()

    class Meta:
        model = Licensed
        fields = [
            'id', 'user', 'cpf_cnpj', 'phone', 'city_lookup',
            'plan', 'dtt_record'
        ]

    def get_user(self, obj):
        return {'username': obj.user.username} if getattr(obj, 'user', None) else None

    def get_plan(self, obj):
        return {'name': obj.plan.name} if getattr(obj, 'plan', None) else None

    def get_city_lookup(self, obj):
        return {'name': obj.city_lookup.name} if getattr(obj, 'city_lookup', None) else None


class DownlineListSerializer(LicensedListSerializer):
    level = serializers.SerializerMethodField()
    upline = serializers.SerializerMethodField()

    class Meta(LicensedListSerializer.Meta):
        fields = LicensedListSerializer.Meta.fields + ['level', 'upline']

    def get_level(self, obj):
        return (self.context.get('levels') or {}).get(obj.id, None)

    def get_upline(self, obj):
        uname = (self.context.get('uplines') or {}).get(obj.id, None)
        return {'username': uname} if uname else None
