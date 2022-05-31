import json
import base64
from rest_framework import viewsets
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from app.models import Wallet, Asset, Contract, Report, Transaction, Trait
from app import serializers
from eth_account.messages import defunct_hash_message
from web3 import Web3
from collections import OrderedDict


class Pagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('most_rarity', self.most_rarity if hasattr(self, 'most_rarity') else None),
            ('most_expensive', self.most_expensive if hasattr(self, 'most_expensive') else None),
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class WalletViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    models = Wallet
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.WalletSerializer
    lookup_field = "address"

    def retrieve(self, request, *args, **kwargs):
        instance, _ = Wallet.objects.get_or_create(address=kwargs["address"])
        mask = Asset.objects.filter(owner=kwargs["address"]).first()
        if instance.mask is None and mask:
            instance.mask = mask
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class AssetViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    models = Asset
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.AssetSerializer
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['owner', 'contract__address', 'contract__chain_id', 'item_id']
    ordering_fields = ['id', 'item_id', 'rarity', 'current_price']
    lookup_field = "item_id"

    def retrieve(self, request, *args, **kwargs):
        queryset = Asset.objects.filter(contract__address=request.GET.get("contract__address"))
        if kwargs["item_id"] == "most-rarity":
            instance = queryset.order_by('rarity').first()
        elif kwargs["item_id"] == "most-expensive":
            instance = queryset.order_by('-current_price').first()
        else:
            instance = queryset.filter(item_id=kwargs["item_id"]).first()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.GET.get("ordering") is None and request.GET.get("item_id") is None:
            setattr(
                self.paginator, 'most_rarity',
                serializers.AssetSerializer(queryset.order_by('rarity').first()).data)
            setattr(
                self.paginator, 'most_expensive',
                serializers.AssetSerializer(queryset.order_by('-current_price').first()).data
            )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ContractViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    models = Contract
    queryset = models.objects.order_by('-id').distinct()
    serializer_class = serializers.ContractSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assets__owner']
    lookup_field = "address"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(is_contract=True))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ReportViewSet(viewsets.ViewSet, generics.ListAPIView):
    models = Report
    queryset = models.objects.order_by('-created')
    serializer_class = serializers.ReportSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contract__address']


class TransactionViewSet(viewsets.ViewSet, generics.ListAPIView):
    models = Transaction
    queryset = models.objects.order_by('-tx_date')
    serializer_class = serializers.TransactionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = []


@api_view(['POST'])
def update_mask(request):
    w3 = Web3(Web3.HTTPProvider(request.data.get("rpc")))
    sign_mess = request.data.get("message")
    signature = request.data.get("signature")
    message_hash = defunct_hash_message(text=sign_mess)
    address = w3.eth.account.recoverHash(message_hash, signature=signature)
    decoded = base64.b64decode(sign_mess)
    m_json = json.loads(decoded)
    if address == request.wallet.address and m_json.get("id"):
        wallet, _ = Wallet.objects.get_or_create(address=address)
        asset = Asset.objects.get(pk=m_json.get("id"))
        wallet.mask = asset
        return Response({}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def import_opensea(request):
    if request.data.get("pwd") == "DKMVKL":
        for data in request.data["dataset"]:
            links = {
                "external_url": data["collection"]["external_url"],
                "discord": data["collection"]["discord_url"],
                "medium_username": data["collection"]["discord_url"],
                "telegram_url": data["collection"]["telegram_url"],
                "twitter_username": data["collection"]["twitter_username"],
                "instagram_username": data["collection"]["instagram_username"],
                "is_nsfw": data["collection"]["is_nsfw"]
            }
            contract, _ = Contract.objects.get_or_create(
                address=data["asset_contract"]["address"],
                chain_id="eth",
                defaults={
                    "name": data["asset_contract"]["name"],
                    "desc": data["asset_contract"]["description"],
                    "is_approved": True,
                    "token_schema": data["asset_contract"]["schema_name"],
                    "token_symbol": data["asset_contract"]["symbol"],
                    "total_supply": int(data["asset_contract"]["total_supply"]),
                    "media": data["asset_contract"]["image_url"],
                    "links": links
                }
            )
            asset, is_created = Asset.objects.get_or_create(
                contract=contract,
                item_id=data["token_id"],
                defaults={
                    "name": data["name"] if data["name"] else "{} #{}".format(data["asset_contract"]["name"],
                                                                              data["token_id"]),
                    "desc": data["description"] if data["description"] else data["asset_contract"]["description"],
                    "uri": data["token_metadata"],
                    "owner": data["owner"]["address"] if data["owner"] else None,
                    "media_origin": data["image_original_url"],
                    "media": data["image_url"],
                    "external_link": data["external_link"]
                }
            )
            if is_created:
                for trait in data["traits"]:
                    rarity = 0
                    if int(data["asset_contract"]["total_supply"]) > 0:
                        rarity = trait["trait_count"] / int(data["asset_contract"]["total_supply"])
                    check = Trait.objects.filter(
                        contract=contract,
                        field=trait["trait_type"],
                        value=trait["value"],
                    ).first()
                    if check is None:
                        check = Trait.objects.get_or_create(
                            contract=contract,
                            field=trait["trait_type"],
                            value=trait["value"],
                            kind_format=trait["display_type"] or "text",
                            rarity=rarity
                        )
                    asset.traits.add(check)
    return Response(status=status.HTTP_201_CREATED)