import re
from rest_framework import serializers
from .models.User import User
from .models.Licensed import Licensed
from django.contrib.auth.models import Group, Permission
from django.db import transaction, IntegrityError
from core.models.LicensedDocument import LicensedDocument
from core.choices import DOCUMENT_TYPE_CHOICES, DOCUMENT_STATUS_CHOICES
from notifications.utils import send_email

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class UserProfileSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True)
    # Campos extras do Licensed (aceitam escrita e serão refletidos manualmente na saída)
    phone = serializers.CharField(required=False, allow_blank=True)
    cpf_cnpj = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    number = serializers.CharField(required=False, allow_blank=True)
    complement = serializers.CharField(required=False, allow_blank=True)
    # Somente exibição
    licensed_id = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    plan = serializers.SerializerMethodField()
    # Campos de escrita para Licensed
    cep = serializers.CharField(write_only=True, required=False, allow_blank=True)
    district = serializers.CharField(write_only=True, required=False, allow_blank=True)
    city_lookup = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    # Atualização de senha opcional
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'image_profile',
            'is_superuser', 'groups',
            'phone', 'cpf_cnpj', 'licensed_id', 'city', 'address', 'number', 'complement', 'plan',
            # write-only extras para gravar no Licensed
            'cep', 'district', 'city_lookup',
            'password'
        ]
        extra_kwargs = {
            'image_profile': {'read_only': True},  # upload tratado na view do perfil
        }

    def _get_licensed(self, obj):
        try:
            return Licensed.objects.select_related('plan', 'city_lookup').get(user=obj)
        except Licensed.DoesNotExist:
            return None

    def _get_operator(self, obj):
        try:
            from core.models.Operator import Operator
            return Operator.objects.select_related('city_lookup__state').get(user=obj)
        except Exception:
            return None

    def get_licensed_id(self, obj):
        lic = self._get_licensed(obj)
        return getattr(lic, 'id', None) if lic else None

    def get_city(self, obj):
        # Retorna estrutura com id, name e state {id, uf}, seja de Licensed ou de Operator
        city = None
        lic = self._get_licensed(obj)
        if lic and getattr(lic, 'city_lookup', None):
            city = lic.city_lookup
        else:
            op = self._get_operator(obj)
            if op and getattr(op, 'city_lookup', None):
                city = op.city_lookup
        if not city:
            return None
        try:
            state = getattr(city, 'state', None)
            return {
                'id': getattr(city, 'id', None),
                'name': getattr(city, 'name', None),
                'state': {'id': getattr(state, 'id', None), 'uf': getattr(state, 'uf', None)} if state else None,
            }
        except Exception:
            return {'id': getattr(city, 'id', None), 'name': getattr(city, 'name', None)}

    def get_plan(self, obj):
        lic = self._get_licensed(obj)
        return getattr(getattr(lic, 'plan', None), 'name', None) if lic else None

    def update(self, instance, validated_data):
        # Trata imagem (renomeia para cpf-hash.ext) e senha opcional
        image_file = validated_data.pop('image_profile', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)

        if image_file is not None:
            try:
                lic = Licensed.objects.filter(user=instance).first()
                cpf = getattr(lic, 'cpf_cnpj', '') or ''
                import re as _re, hashlib, os
                from django.core.files.base import ContentFile
                cpf_digits = _re.sub(r'\D', '', str(cpf))
                try:
                    image_file.seek(0)
                except Exception:
                    pass
                file_bytes = image_file.read()
                file_hash = hashlib.sha256(file_bytes).hexdigest()[:16]
                ext = os.path.splitext(getattr(image_file, 'name', ''))[1] or '.jpg'
                new_name = f"{cpf_digits}-{file_hash}{ext}"
                instance.image_profile.save(new_name, ContentFile(file_bytes), save=False)
            except Exception:
                # fallback: mantem arquivo recebido
                instance.image_profile = image_file

        instance.save()
        # Atualiza dados do Licensed/Operator
        try:
            lic = Licensed.objects.select_related('user').get(user=instance)
        except Licensed.DoesNotExist:
            lic = None

        if lic is not None:
            # Pega dados crus para aceitar campos write_only não mapeados para User
            # Usar request.data diretamente (QueryDict/DRF retornam escalar quando único)
            data = {}
            try:
                data = getattr(self.context.get('request'), 'data', self.initial_data or {})
            except Exception:
                data = self.initial_data or {}

            def only_digits(s, max_len=None):
                import re as _re
                if s is None:
                    return None
                v = _re.sub(r'\D', '', str(s))
                return v[:max_len] if max_len else v

            def as_scalar(v):
                # Corrige valores vindos como lista (multipart)
                try:
                    if isinstance(v, (list, tuple)):
                        return v[0] if v else None
                except Exception:
                    pass
                return v

            changed = False
            phone = data.get('phone', None)
            if phone is not None:
                lic.phone = only_digits(phone, 14)
                changed = True
            cpf_cnpj = data.get('cpf_cnpj', None)
            if cpf_cnpj is not None:
                lic.cpf_cnpj = only_digits(cpf_cnpj)
                changed = True
            cep = data.get('cep', None)
            if cep is not None:
                lic.cep = only_digits(cep, 8)
                changed = True
            address = as_scalar(data.get('address', None))
            if address is not None:
                lic.address = address
                changed = True
            number = as_scalar(data.get('number', None))
            if number is not None:
                lic.number = number
                changed = True
            complement = as_scalar(data.get('complement', None))
            if complement is not None:
                lic.complement = complement
                changed = True
            district = as_scalar(data.get('district', None))
            if district is not None:
                lic.district = district
                changed = True
            if 'city_lookup' in data:
                try:
                    from location.models import City
                    cid = as_scalar(data.get('city_lookup'))
                    cid = int(cid) if cid not in (None, '', 'null') else None
                    lic.city_lookup = City.objects.filter(id=cid).first() if cid else None
                    changed = True
                except Exception:
                    pass

            if changed:
                lic.save()

        # Se não houver Licensed, tenta atualizar Operator
        if lic is None:
            try:
                from core.models.Operator import Operator
                op = Operator.objects.select_related('user').get(user=instance)
            except Exception:
                op = None
            if op is not None:
                # Usar request.data diretamente
                data = {}
                try:
                    data = getattr(self.context.get('request'), 'data', self.initial_data or {})
                except Exception:
                    data = self.initial_data or {}

                def only_digits2(s, max_len=None):
                    import re as _re
                    if s is None:
                        return None
                    v = _re.sub(r'\D', '', str(s))
                    return v[:max_len] if max_len else v

                def as_scalar2(v):
                    try:
                        if isinstance(v, (list, tuple)):
                            return v[0] if v else None
                    except Exception:
                        pass
                    return v

                changed = False
                phone = as_scalar2(data.get('phone', None))
                if phone is not None:
                    op.phone = only_digits2(phone, 14)
                    changed = True
                cpf_cnpj = as_scalar2(data.get('cpf_cnpj', None))
                if cpf_cnpj is not None:
                    op.cpf_cnpj = only_digits2(cpf_cnpj)
                    changed = True
                cep = as_scalar2(data.get('cep', None))
                if cep is not None:
                    op.cep = only_digits2(cep, 8)
                    changed = True
                address = as_scalar2(data.get('address', None))
                if address is not None:
                    op.address = address
                    changed = True
                number = as_scalar2(data.get('number', None))
                if number is not None:
                    op.number = number
                    changed = True
                complement = as_scalar2(data.get('complement', None))
                if complement is not None:
                    op.complement = complement
                    changed = True
                district = as_scalar2(data.get('district', None))
                if district is not None:
                    op.district = district
                    changed = True
                if 'city_lookup' in data:
                    try:
                        from location.models import City
                        cid = as_scalar2(data.get('city_lookup'))
                        cid = int(cid) if cid not in (None, '', 'null') else None
                        op.city_lookup = City.objects.filter(id=cid).first() if cid else None
                        changed = True
                    except Exception:
                        pass
                if changed:
                    op.save()

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Corrigir strings salvas como listas serializadas ("['...']")
        def clean_text(v):
            try:
                if isinstance(v, str) and v.startswith("['") and v.endswith("']"):
                    return v[2:-2]
            except Exception:
                pass
            return v
        lic = self._get_licensed(instance)
        if lic:
            rep['phone'] = clean_text(getattr(lic, 'phone', None))
            rep['cpf_cnpj'] = clean_text(getattr(lic, 'cpf_cnpj', None))
            rep['cep'] = clean_text(getattr(lic, 'cep', None))
            rep['district'] = clean_text(getattr(lic, 'district', None))
            rep['address'] = clean_text(getattr(lic, 'address', None))
            rep['number'] = clean_text(getattr(lic, 'number', None))
            rep['complement'] = clean_text(getattr(lic, 'complement', None))
        else:
            # Fallback para Operator (perfil de operador)
            op = self._get_operator(instance)
            if op:
                rep['phone'] = clean_text(getattr(op, 'phone', None))
                rep['cpf_cnpj'] = clean_text(getattr(op, 'cpf_cnpj', None))
                rep['cep'] = clean_text(getattr(op, 'cep', None))
                rep['district'] = clean_text(getattr(op, 'district', None))
                rep['address'] = clean_text(getattr(op, 'address', None))
                rep['number'] = clean_text(getattr(op, 'number', None))
                rep['complement'] = clean_text(getattr(op, 'complement', None))
        return rep


class LicensedSerializer(serializers.ModelSerializer):
    # Permitir máscaras no input; limpeza é feita em validate()
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    cep = serializers.CharField(required=False, allow_blank=True, max_length=10)
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
        # username vindo do payload (ex.: form.referrer) — sempre remova de data
        ref_username = self.initial_data.get('referrer', None)
        data.pop('referrer', None)

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

        try:
            with transaction.atomic():
                user = User.objects.create_user(**user_data)
                # Adiciona o usuário ao grupo "Licenciado"
                licenciado_group, _ = Group.objects.get_or_create(name='Licenciado')
                user.groups.add(licenciado_group)
                licensed = Licensed.objects.create(user=user, **validated_data)
                return licensed
        except IntegrityError as e:
            # Se algo falhar (ex.: cpf_cnpj duplicado), a transação é revertida (não deixa User órfão)
            raise serializers.ValidationError({
                'non_field_errors': [str(e)]
            })

class LicensedListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    plan = serializers.SerializerMethodField()
    city_lookup = serializers.SerializerMethodField()
    # Campos extras para o grid de licenciados
    stt_document = serializers.CharField(read_only=True)  # status dos documentos
    documents_status = serializers.SerializerMethodField() # status derivado para UI (pending/incomplete/awaiting/approved/rejected)
    stt_record = serializers.BooleanField(read_only=True) # status atual do cadastro (flag administrativo)
    has_paid_adesion = serializers.SerializerMethodField() # pagamento de adesão confirmado?
    is_active = serializers.SerializerMethodField()        # cálculo derivado: payment OK + docs OK
    payment_status = serializers.SerializerMethodField()   # status textual da adesão

    class Meta:
        model = Licensed
        fields = [
            'id', 'user', 'cpf_cnpj', 'phone', 'city_lookup',
            'plan', 'dtt_record',
            # Endereço básico para preencher o modal de edição
            'cep', 'address', 'number', 'complement', 'district',
            # Campos extras para coluna Documentos/Status detalhado no grid
            'stt_document', 'documents_status', 'stt_record', 'has_paid_adesion', 'is_active', 'payment_status'
        ]

    def get_user(self, obj):
        if not getattr(obj, 'user', None):
            return None
        u = obj.user
        full_name = f"{getattr(u, 'first_name', '')} {getattr(u, 'last_name', '')}".strip()
        
        # Tratar o campo de imagem de forma segura
        image_profile = None
        if hasattr(u, 'image_profile') and u.image_profile:
            try:
                # Se for um arquivo, pegar a URL
                if hasattr(u.image_profile, 'url'):
                    image_profile = u.image_profile.url
                else:
                    # Se for uma string/URL, usar diretamente
                    image_profile = str(u.image_profile)
            except (ValueError, UnicodeDecodeError):
                # Se houver erro de codificação, ignorar
                image_profile = None
        
        return {
            'id': getattr(u, 'id', None),
            'username': getattr(u, 'username', None),
            'email': getattr(u, 'email', None),
            'first_name': getattr(u, 'first_name', None),
            'last_name': getattr(u, 'last_name', None),
            'full_name': full_name or None,
            'image_profile': image_profile,
        }

    def get_plan(self, obj):
        return {'name': obj.plan.name} if getattr(obj, 'plan', None) else None

    def get_city_lookup(self, obj):
        # Retorna cidade com UF para exibir no grid "Cidade-UF"
        try:
            if not getattr(obj, 'city_lookup', None):
                return None
            city = obj.city_lookup
            state = getattr(city, 'state', None)
            uf = getattr(state, 'uf', None) if state else None
            # Inclui IDs para pré-preencher o modal de edição
            state_payload = None
            if state:
                state_payload = {'id': getattr(state, 'id', None), 'uf': uf}
            return {'id': getattr(city, 'id', None), 'name': city.name, 'state': state_payload}
        except Exception:
            c = getattr(obj, 'city_lookup', None)
            return {'id': getattr(c, 'id', None), 'name': getattr(c, 'name', None)}

    def get_documents_status(self, obj):
        """Status derivado para UI:
        - 'pending': nenhum documento anexado
        - 'incomplete': existem anexos, mas não todos os tipos obrigatórios
        - 'awaiting': todos os obrigatórios anexados e ao menos 1 pendente
        - 'approved': todos os obrigatórios anexados e aprovados
        - 'rejected': algum obrigatório reprovado (fallback)
        Obrigatórios: definidos por DOCUMENT_TYPE_CHOICES.
        """
        try:
            # Import local para evitar ciclos
            from core.models.LicensedDocument import LicensedDocument
            from core.choices import DOCUMENT_TYPE_CHOICES
            required_types = {key for key, _ in DOCUMENT_TYPE_CHOICES}
            qs = LicensedDocument.objects.filter(licensed=obj)
            if not qs.exists():
                return 'pending'

            present_types = set(qs.values_list('document_type', flat=True))
            has_all_required = required_types.issubset(present_types)

            # Se não enviou todos os obrigatórios
            if not has_all_required:
                return 'incomplete'

            # Tem todos os obrigatórios
            if qs.filter(stt_validate='pending').exists():
                return 'awaiting'
            if qs.filter(stt_validate='rejected').exists():
                return 'rejected'
            # Todos os obrigatórios aprovados
            return 'approved'
        except Exception:
            return getattr(obj, 'stt_document', 'pending') or 'pending'

    def get_has_paid_adesion(self, obj):
        """
        Verdadeiro quando existe uma adesão confirmada para o usuário OU
        quando dtt_payment_received está preenchido no Licensed.
        Mantemos simples e barato para listagem.
        """
        try:
            if getattr(obj, 'dtt_payment_received', None):
                return True
            from plans.models import PlanAdesion
            return PlanAdesion.objects.filter(licensed=obj.user, ind_payment_status='confirmed').exists()
        except Exception:
            return False

    def get_is_active(self, obj):
        """
        Cálculo derivado sugerido: ativo quando pagamento confirmado e documentos aprovados.
        Não altera o flag administrativo (stt_record); apenas expõe para UI/tooltip.
        """
        docs_ok = getattr(obj, 'stt_document', None) == 'approved'
        paid_ok = self.get_has_paid_adesion(obj)
        return bool(docs_ok and paid_ok)

    def get_payment_status(self, obj):
        """
        Retorna status textual da última/mais recente adesão do usuário.
        Possíveis valores: 'confirmed', 'pending', 'canceled'. Se inexistente, retorna 'pending'.
        """
        try:
            from plans.models import PlanAdesion
            last = (
                PlanAdesion.objects
                .filter(licensed=obj.user)
                .order_by('-dtt_record')
                .first()
            )
            return getattr(last, 'ind_payment_status', 'pending') if last else 'pending'
        except Exception:
            return 'pending'


class LicensedDocumentSerializer(serializers.ModelSerializer):
    licensed = serializers.PrimaryKeyRelatedField(read_only=True)
    licensed_username = serializers.SerializerMethodField()

    class Meta:
        model = LicensedDocument
        fields = [
            'id', 'licensed', 'licensed_username', 'document_type', 'file', 'observation',
            'stt_validate', 'rejection_reason', 'dtt_record', 'dtt_update'
        ]
        read_only_fields = ['dtt_record', 'dtt_update']

    def create(self, validated_data):
        instance = super().create(validated_data)
        # Disparo de e-mail para operadores ao anexar conjunto de docs
        try:
            user = instance.licensed.user
            # Operadores: grupo Operador
            from django.contrib.auth import get_user_model
            User = get_user_model()
            operators = User.objects.filter(groups__name='Operador').values_list('email', flat=True)
            recipients = [e for e in operators if e]
            if recipients:
                send_email(
                    'LicensedDocsSubmitted',
                    {
                        'nome': user.get_full_name() or user.username,
                        'username': user.username,
                    },
                    recipients
                )
        except Exception:
            pass
        return instance

    def get_licensed_username(self, obj):
        try:
            return getattr(getattr(obj.licensed, 'user', None), 'username', None)
        except Exception:
            return None


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


# --------------------------- Admin Serializers ---------------------------
class AdminPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']


class AdminGroupSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True, required=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']


class AdminUserSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)
    user_permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser', 'image_profile', 'groups', 'user_permissions', 'last_login', 'date_joined', 'password']
        extra_kwargs = { 'password': { 'write_only': True, 'required': False } }

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        perms = validated_data.pop('user_permissions', [])
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        if groups:
            user.groups.set(groups)
        if perms:
            user.user_permissions.set(perms)
        return user

    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', None)
        perms = validated_data.pop('user_permissions', None)
        password = validated_data.pop('password', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        if groups is not None:
            instance.groups.set(groups)
        if perms is not None:
            instance.user_permissions.set(perms)
        return instance
