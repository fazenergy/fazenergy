from rest_framework import serializers
from .models import ContractConfig, ContractTemplate


class ContractConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractConfig
        fields = [
            'id', 'lexio_url', 'lexio_token',
            'signer_name_partner', 'signer_mail_partner',
            'signer_name_testmon', 'signer_mail_testmon'
        ]


class ContractTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractTemplate
        fields = ['id', 'name', 'description', 'body', 'mapping_info', 'active']


