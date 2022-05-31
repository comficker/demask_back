import os
import json
from django.core.management.base import BaseCommand
from app.models import Contract, Asset, Trait

excludes = ["0x160c404b2b49cbc3240055ceaee026df1e8497a0"]


def check_number(text):
    return text.isnumeric()


def sync_range(start, end):
    root = "/Users/hoanganhlam/WebstormProjects/crawl-nft/data_opensea/eth"
    contracts = os.listdir(root)
    contracts.sort()
    for d in contracts:
        if d in excludes or d == ".DS_Store":
            continue
        item_ids = os.listdir("{}/{}".format(root, d))
        filtered = list(filter(check_number, item_ids))
        filtered = list(map(lambda x: int(x), filtered))
        for f in filtered:
            if f < start or f > end:
                continue
            file = open("{}/{}/{}/data.json".format(root, d, f))
            data = json.load(file)
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
                    trait_instance, _ = Trait.objects.get_or_create(
                        contract=contract,
                        field=trait["trait_type"],
                        value=trait["value"],
                        defaults={
                            "kind_format": trait["display_type"] or "text",
                            "rarity": rarity
                        }
                    )
                    asset.traits.add(trait_instance)
            print(f)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('start', type=int)
        parser.add_argument('end', type=int)

    def handle(self, *args, **options):
        sync_range(options['start'], options['end'])
