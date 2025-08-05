# plans/serializers.py
from rest_framework import serializers
from .models.Plan import Plan
from .models.PlanAdesion import PlanAdesion

class PlanSerializer(serializers.ModelSerializer):
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


class PlanAdesionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanAdesion
        fields = [
            'id',
            'plan',
            'licensed',
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