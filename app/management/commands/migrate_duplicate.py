from django.core.management.base import BaseCommand
from app.models import Contract


class Command(BaseCommand):

    def handle(self, *args, **options):
        contracts = Contract.objects.filter(chain_id="eth")
        for contract in contracts:
            to_contract = Contract.objects.filter(address=contract.address, chain_id="ethereum").first()
            if to_contract:
                for item in contract.traits.all():
                    item.contract = to_contract
                    item.save()
                for item in contract.assets.all():
                    item.contract = to_contract
                    item.save()
