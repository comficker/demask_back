from django.core.management.base import BaseCommand
from app.models import Contract, Asset
from web3 import Web3
import json
import requests

CHAIN_MAPPING = {
    "eth": "https://main-light.eth.linkpool.io/",
    "polygon": "https://polygon-rpc.com/",
    "bsc": "https://bsc-dataseed.binance.org/"
}

with open('app/abi.json') as json_file:
    ABI_721 = json.load(json_file)


class Command(BaseCommand):

    def handle(self, *args, **options):
        base_contract = {
            "address": "0x352bb674cd16ad62eeb2266809c9c2a395166c56",
            "chain_id": "eth",
            "uri": "https://ipfs.io/ipfs/QmVqZbJ6rfUwmcRETENWrs5bDU1PVWQpQZPDMM8zxmWZ9n/{item_id}",
            "name": "THE DRONES",
            "media": "https://ipfs.io/ipfs/QmejjoJ1viVGS8k8wUQWsDCu1aJkfD1rM9eC6WgmjbEyzy/{item_id}.mp4",
            "desc": "The Drones is the first collection of NFT's by the artist KATSU. The collection consists of 1,513 generative videos. The project allows holders to work together in the creation of a large web3 NFT drone painting known as the Meta Canvas."
        }

        w3 = Web3(Web3.HTTPProvider("https://main-light.eth.linkpool.io"))
        ct_instance = w3.eth.contract(
            address=Web3.toChecksumAddress("0x352bb674cd16ad62eeb2266809c9c2a395166c56"),
            abi=ABI_721
        )
        contract, _ = Contract.objects.get_or_create(
            address=base_contract["address"],
            chain_id=base_contract["chain_id"],
            defaults={
                "name": base_contract["name"],
                "desc": base_contract["desc"]
            }
        )
        total_supply = ct_instance.functions.totalSupply().call()
        for i in range(0, total_supply):
            uri = base_contract["uri"].format(item_id=i)
            name = "{name} #{item_id}".format(item_id=i, name=base_contract["name"])
            media = base_contract["media"].format(item_id=i)
            asset, created = Asset.objects.get_or_create(
                contract=contract,
                item_id=i,
                defaults={
                    "uri": uri,
                    "name": name,
                    "media": media
                }
            )
            if created:
                asset.save_media(media)
        # contracts = Contract.objects.all()
        # for contract in contracts:
        #     w3 = Web3(Web3.HTTPProvider(CHAIN_MAPPING[contract.chain_id]))
        #     ct_instance = w3.eth.contract(
        #         address=Web3.toChecksumAddress(contract.address),
        #         abi=ABI_721
        #     )
        #     print(ct_instance.functions.symbol().call())
        #     print(ct_instance.functions.totalSupply().call())
