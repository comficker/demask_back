from django.core.management.base import BaseCommand
from app.models import Contract, Asset, Trait
from django.db.models import Sum


class Command(BaseCommand):

    def handle(self, *args, **options):
        traits = Trait.objects.all()
        for trait in traits:
            trait.calculate()

        assets = Asset.objects.all()
        for asset in assets:
            if asset.traits.count():
                asset.rarity = asset.traits.aggregate(Sum('rarity'))['rarity__sum'] / asset.traits.count()
                print(asset.rarity)
                asset.save()
