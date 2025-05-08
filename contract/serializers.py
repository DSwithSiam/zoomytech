from rest_framework import serializers
from .models import *



class ContractProposalSerializers(serializers.ModelSerializer):
    class Meta:
        model = ContractProposal
        fields = '__all__'



