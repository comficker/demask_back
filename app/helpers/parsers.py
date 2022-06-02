from app.models import Asset, Contract, Trait


def parse_opensea(data, chain_id="ethereum"):
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
        chain_id=chain_id,
        defaults={
            "name": data["asset_contract"]["name"],
            "desc": data["collection"]["description"][:260] if data["collection"]["description"] else None,
            "is_approved": True,
            "token_schema": data["asset_contract"]["schema_name"],
            "token_symbol": data["asset_contract"]["symbol"],
            "total_supply": int(data["asset_contract"]["total_supply"]),
            "media": data["asset_contract"]["image_url"],
            "links": links
        }
    )
    current_price = 0
    if data.get("last_sale") and data["last_sale"].get("total_price"):
        current_price = int(data["last_sale"]["total_price"]) / pow(10, 18)
    asset, is_created = Asset.objects.get_or_create(
        contract=contract,
        item_id=data["token_id"],
        defaults={
            "name": data["name"] if data["name"] else "{} #{}".format(
                data["asset_contract"]["name"],
                data["token_id"]
            ),
            "desc": data["description"][:260] if data["description"] else data["collection"]["description"],
            "uri": data["token_metadata"] if data["token_metadata"] and len(data["token_metadata"]) < 500 else None,
            "owner": data["owner"]["address"] if data["owner"] else None,
            "media_origin": data["image_original_url"],
            "media": data["image_url"],
            "external_link": data["external_link"],
            "current_price": current_price
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
                check = Trait.objects.create(
                    contract=contract,
                    field=trait["trait_type"],
                    value=trait["value"],
                    kind_format=trait["display_type"] or "text",
                    rarity=rarity
                )
            asset.traits.add(check)
