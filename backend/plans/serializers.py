# plans/serializers.py
from rest_framework import serializers
from .models.Plan import Plan
from .models.PlanAdesion import PlanAdesion
from .models.PlanCareer import PlanCareer
from .models import Qualification

class PlanSerializer(serializers.ModelSerializer):
    usr_update_username = serializers.SerializerMethodField()
    class Meta:
        model = Plan
        fields = [
            'id',
            'name',
            'image',
            'price',
            'points',
            'bonus_level_1',
            'bonus_level_2',
            'bonus_level_3',
            'bonus_level_4',
            'bonus_level_5',
            'stt_record',
            'usr_record',
            'usr_update',
            'usr_update_username',
            'dtt_record',
            'dtt_update',
        ]
        read_only_fields = ['usr_record', 'usr_update', 'dtt_record', 'dtt_update']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None

        # Se vier imagem, trata via request.FILES
        image = request.FILES.get('image') if request and 'image' in request.FILES else None

        plan = Plan.objects.create(
            name=validated_data.get('name'),
            price=validated_data.get('price'),
            points=validated_data.get('points'),
            bonus_level_1=validated_data.get('bonus_level_1'),
            bonus_level_2=validated_data.get('bonus_level_2'),
            bonus_level_3=validated_data.get('bonus_level_3'),
            bonus_level_4=validated_data.get('bonus_level_4'),
            bonus_level_5=validated_data.get('bonus_level_5'),
            stt_record=validated_data.get('stt_record', True),
            image=image
        )

        if user:
            plan.usr_record = user
            plan.usr_update = user

        plan.save()
        return plan

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user if request else None

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if request and 'image' in request.FILES:
            instance.image = request.FILES['image']

        if user:
            instance.usr_update = user

        instance.save()
        return instance

    def get_usr_update_username(self, obj):
        try:
            return getattr(obj.usr_update, 'username', None)
        except Exception:
            return None


class PlanAdesionSerializer(serializers.ModelSerializer):
    licensed_username = serializers.SerializerMethodField()
    class Meta:
        model = PlanAdesion
        fields = [
            'id',
            'plan',
            'licensed',
            'licensed_username',
            'ind_payment_status',
            'typ_payment',
            'dtt_record',
            'dtt_payment',
            'dtt_cancel',
            'dtt_update',
            'is_courtesy',
            'points_generated',
            'ind_processing',
            'ind_bonus_status',
            'des_cancel_reason',
            'contract_status',
            'contract_token',
        ]
        read_only_fields = ['dtt_record', 'dtt_update', 'dtt_payment', 'dtt_cancel']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None

        adesion = PlanAdesion.objects.create(**validated_data)

        # Garante que quem criou fique registrado como `licensed` se não vier explícito
        if user and not validated_data.get('licensed'):
            adesion.licensed = user
            adesion.save()

        return adesion

    def get_licensed_username(self, obj):
        try:
            return getattr(obj.licensed, 'username', None)
        except Exception:
            return None


class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = ['id', 'licensed', 'plan_career', 'dtt_qualification']
        read_only_fields = ['dtt_qualification']


class PlanCareerSerializer(serializers.ModelSerializer):
    usr_update_username = serializers.SerializerMethodField()
    class Meta:
        model = PlanCareer
        fields = [
            'id',
            'stage_name',
            'reward_description',
            'required_points',
            'required_directs',
            'required_direct_sales',
            'max_pml_per_line',
            'cover_image',
            'usr_record',
            'usr_update',
            'usr_update_username',
            'stt_record',
            'dtt_record',
            'dtt_update',
        ]
        read_only_fields = ['usr_record', 'usr_update', 'dtt_record', 'dtt_update']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        instance = PlanCareer.objects.create(**validated_data)
        if user:
            instance.usr_record = user
            instance.usr_update = user
            instance.save()
        return instance

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if user:
            instance.usr_update = user
        instance.save()
        return instance

    def get_usr_update_username(self, obj):
        try:
            return getattr(obj.usr_update, 'username', None)
        except Exception:
            return None