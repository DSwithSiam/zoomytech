from rest_framework import serializers
from .models import *



class ContractProposalSerializers(serializers.ModelSerializer):
    class Meta:
        model = ContractProposal
        fields = '__all__'


class ContractDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model = ContractDetails
        fields = '__all__'
