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
from app import serializers
from app.models import Wallet, Asset, Contract, Report, Transaction, Trait
from app.helpers import parsers
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
        if request.GET.get("related") and request.GET.get("contract__address"):
            related = Asset.objects.get(
                item_id=request.GET.get("related"),
                contract__address=request.GET.get("contract__address")
            )
            queryset = queryset.filter(rarity=related.rarity)
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
    pagination_class = Pagination
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
            parsers.parse_opensea(data, request.data.get("chain_id", "ethereum"))
    return Response(status=status.HTTP_201_CREATED)
