from django.core.management.base import BaseCommand
from app.models import Contract, Asset, Trait
from web3 import Web3
import json
import requests


class Command(BaseCommand):

    def handle(self, *args, **options):
        url = "https://api.opensea.io/api/v2/beta/assets"
        req = requests.get(url, params={
            "chain_identifier": "ethereum",
            "asset_contract_address": "0x018befb7d1f3e84948466ef15cc46baf9ba5295f"
            # "owner_address": "0xff992e92099035ce63f459a5967e4a8c0d95dd71"
        })
        for item in req.json()["results"]:
            contract, _ = Contract.objects.get_or_create(
                address=item["asset_contract"]["address"],
                defaults={
                    "name": item["asset_contract"]["name"],
                    "chain_id": item["asset_contract"]["chain_identifier"],
                    "token_schema": item["asset_contract"]["contract_standard"],
                    "media": item["collection"]["image_url"],
                    "desc": item["metadata"]["description"]
                }
            )
            asset, _ = Asset.objects.get_or_create(
                contract=contract,
                item_id=item["token_id"],
                defaults={
                    "media": item["metadata"]["image_url"],
                    "desc": item["metadata"]["description"],
                    "uri": item["metadata"]["metadata_url"]
                }
            )
            for trait in item["metadata"]["traits"]:
                trait_instance = Trait.objects.get_or_create(
                    contract=contract,
                    field=trait["trait_type"],
                    value=trait["value"]
                )
