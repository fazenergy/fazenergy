import re
from rest_framework import serializers
from .models import Prospect, Proposal, ProposalResult


class ProspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prospect
        fields = '__all__'
        read_only_fields = ['dtt_record', 'dtt_update']

    def validate(self, data):
        # normalizações simples
        if 'cellphone' in data:
            data['cellphone'] = re.sub(r'\D', '', data['cellphone'])[:20]
        if 'zip_code' in data:
            data['zip_code'] = re.sub(r'\D', '', data['zip_code'])[:10]
        if 'fiscal_number' in data and data['fiscal_number']:
            data['fiscal_number'] = re.sub(r'\D', '', data['fiscal_number'])[:20]
        return data


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = '__all__'
        read_only_fields = ['dtt_record', 'dtt_update']


class ProposalResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalResult
        fields = '__all__'
        read_only_fields = ['dtt_record']
