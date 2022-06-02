import cloudscraper
import json
from django.core.management.base import BaseCommand
from app.helpers import parsers


def crawl(address, page):
    url = "https://api.opensea.io/api/v1/assets?format=json&order_by=pk&asset_contract_address={}&cursor={}".format(
        address, page
    )
    print(url)
    scraper = cloudscraper.create_scraper()
    res = scraper.get(url).text
    body = json.loads(res)
    for data in body.get("assets", []):
        parsers.parse_opensea(data)
    if body.get("next"):
        crawl(address, body.get("next"))


class Command(BaseCommand):

    def handle(self, *args, **options):
        crawl("0x75335297cb5029c2a9acb2b47507f18ffd48e96c", "")
