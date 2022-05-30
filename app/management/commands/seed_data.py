from django.core.management.base import BaseCommand
from app.models import Contract


class Command(BaseCommand):

    def handle(self, *args, **options):
        categories = [
            {"id": "most-expensive-nft", "name": "Most expensive NFT", "chain_id": "global"},
            {"id": "solana-nft", "name": "Solana NFT", "chain_id": "solana"},
            {"id": "ethereum-nft", "name": "Ethereum NFT", "chain_id": "ethereum"},
            {"id": "polygon-nft", "name": "Polygon NFT", "chain_id": "polygon"},
            {"id": "bsc-nft", "name": "BSC NFT", "chain_id": "binance-smart-chain"},
            {"id": "near-nft", "name": "Near NFT", "chain_id": "near"},
        ]
        for item in categories:
            Contract.objects.get_or_create(
                chain_id=item["chain_id"],
                address=item["id"],
                defaults={
                    "name": item["name"],
                    "is_contract": False
                }
            )
