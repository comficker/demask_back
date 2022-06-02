from django.core.management.base import BaseCommand
from app.models import Contract, Asset, Trait
from django.db.models import Sum


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('addresses', type=str)

    def handle(self, *args, **options):
        contracts = Contract.objects.filter(address__in=options["addresses"].split("|"))
        for contract in contracts:
            total = contract.assets.count()
            traits = contract.traits.all()
            for trait in traits:
                if total > 0:
                    trait.rarity = trait.assets.count() / total
                    trait.save()
                    print("trait: {}".format(trait.id))
            if len(traits) > 0:
                assets = contract.assets.all()
                for asset in assets:
                    asset.rarity = asset.traits.aggregate(Sum('rarity'))['rarity__sum'] / asset.traits.count()
                    asset.save()
                    print("asset: {}".format(asset.id))
