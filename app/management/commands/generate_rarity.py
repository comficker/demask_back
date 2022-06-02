from django.core.management.base import BaseCommand
from app.models import Contract, Asset, Trait
from django.db.models import Sum


class Command(BaseCommand):

    def handle(self, *args, **options):
        contracts = Contract.objects.all()
        for contract in contracts:
            total = contract.assets.count()
            traits = contract.traits.all()
            for trait in traits:
                if trait.rarity == 0:
                    trait.rarity = trait.assets.count() / total
                    trait.save()
                    print(trait.id)
            if len(traits) > 0:
                assets = contract.assets.all()
                for asset in assets:
                    if asset.rarity == 0:
                        asset.rarity = asset.traits.aggregate(Sum('rarity'))['rarity__sum'] / asset.traits.count()
                        asset.save()
                        print(asset.id)
