from rest_framework import serializers
from app.models import Wallet, Asset, Contract, Report, Transaction, Trait


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = "__all__"

    def to_representation(self, instance):
        self.fields['mask'] = AssetSerializer(read_only=True)
        return super(WalletSerializer, self).to_representation(instance)


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = "__all__"

    def to_representation(self, instance):
        self.fields['contract'] = ContractSerializer(read_only=True)
        self.fields['traits'] = TraitSerializer(read_only=True, many=True)
        return super(AssetSerializer, self).to_representation(instance)


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class TraitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trait
        fields = "__all__"
