from rest_framework import serializers
from .models.ScoreReference import ScoreReference
from .models.BonusReference import BonusReference


class ScoreReferenceSerializer(serializers.ModelSerializer):
    content_type_app = serializers.SerializerMethodField()
    content_type_model = serializers.SerializerMethodField()
    receiver_username = serializers.SerializerMethodField()
    origin_label = serializers.SerializerMethodField()

    class Meta:
        model = ScoreReference
        fields = [
            'id',
            'points_amount',
            'status',
            'receiver_licensed',
            'receiver_username',
            'triggering_licensed',
            'content_type_app',
            'content_type_model',
            'origin_label',
            'object_id',
            'created_at',
        ]

    def get_content_type_app(self, obj):
        return getattr(obj.content_type, 'app_label', None)

    def get_content_type_model(self, obj):
        return getattr(obj.content_type, 'model', None)

    def get_receiver_username(self, obj):
        try:
            return getattr(getattr(obj.receiver_licensed, 'user', None), 'username', None)
        except Exception:
            return None

    def get_origin_label(self, obj):
        app = getattr(obj.content_type, 'app_label', None)
        model = getattr(obj.content_type, 'model', None)
        mapping = {
            ('plans', 'planadesion'): 'Adesão',
            ('prospect', 'proposal'): 'Proposta',
        }
        return mapping.get((app, model), f"{app}.{model}" if app and model else None)


class BonusReferenceSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    receiver_username = serializers.SerializerMethodField()

    class Meta:
        model = BonusReference
        fields = [
            'id',
            'product', 'product_name',
            'receiver_licensed', 'receiver_username',
            'amount', 'status', 'created_at'
        ]

    def get_receiver_username(self, obj):
        try:
            return getattr(getattr(obj.receiver_licensed, 'user', None), 'username', None)
        except Exception:
            return None


