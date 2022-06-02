import cloudscraper
import json
import requests
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
    res = requests.post('https://touch.demask.io/import-opensea', json={
        "dataset": body.get("assets", []),
        "pwd": "DKMVKL"
    })
    print(res.status_code)
    # for data in body.get("assets", []):
    #     parsers.parse_opensea(data)
    if body.get("next"):
        crawl(address, body.get("next"))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('address', type=str)

    def handle(self, *args, **options):
        crawl(options['address'], "")
