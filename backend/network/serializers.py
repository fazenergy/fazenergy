from rest_framework import serializers
from .models.ScoreReference import ScoreReference


class ScoreReferenceSerializer(serializers.ModelSerializer):
    content_type_app = serializers.SerializerMethodField()
    content_type_model = serializers.SerializerMethodField()

    class Meta:
        model = ScoreReference
        fields = [
            'id',
            'points_amount',
            'status',
            'receiver_licensed',
            'triggering_licensed',
            'content_type_app',
            'content_type_model',
            'object_id',
            'created_at',
        ]

    def get_content_type_app(self, obj):
        return getattr(obj.content_type, 'app_label', None)

    def get_content_type_model(self, obj):
        return getattr(obj.content_type, 'model', None)


