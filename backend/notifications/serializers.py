from rest_framework import serializers
from .models.NotifyConfig import NotifyConfig
from .models.NotifyTemplate import NotifyTemplate


class NotifyConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotifyConfig
        fields = [
            'id',
            'smtp_host', 'smtp_port', 'smtp_user', 'smtp_password',
            'use_ssl', 'use_tls', 'default_from_email', 'test_recipient',
        ]


class NotifyTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotifyTemplate
        fields = ['id', 'name', 'subject', 'body', 'active']


