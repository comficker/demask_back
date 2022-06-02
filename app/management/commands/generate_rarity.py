from django.core.management.base import BaseCommand
from app.models import Contract, Asset, Trait
from django.db.models import Sum


class Command(BaseCommand):

    def handle(self, *args, **options):
        contracts = Contract.objects.filter(address__in=[
            "0x75335297cb5029c2a9acb2b47507f18ffd48e96c",
            "0x986aea67c7d6a15036e18678065eb663fc5be883"
        ])
        for contract in contracts:
            total = contract.assets.count()
            traits = contract.traits.all()
            for trait in traits:
                if trait.rarity == 1:
                    trait.rarity = trait.assets.count() / total
                    trait.save()
                    print(trait.id)
            if len(traits) > 0:
                assets = contract.assets.all()
                for asset in assets:
                    if asset.rarity == 1:
                        asset.rarity = asset.traits.aggregate(Sum('rarity'))['rarity__sum'] / asset.traits.count()
                        asset.save()
                        print(asset.id)
