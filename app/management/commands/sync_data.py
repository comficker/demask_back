import os
import json
import requests
from django.core.management.base import BaseCommand
from app.models import Contract, Asset, Trait

excludes = ["0x160c404b2b49cbc3240055ceaee026df1e8497a0"]


def check_number(text):
    return text.isnumeric()


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def sync_range(start, end):
    root = "/Users/hoanganhlam/WebstormProjects/crawl-nft/data_opensea/eth"
    contracts = os.listdir(root)
    contracts.sort()
    for d in contracts:
        if d in excludes or d == ".DS_Store":
            continue
        item_ids = os.listdir("{}/{}".format(root, d))
        filtered = list(filter(lambda x: x.isnumeric() and start < int(x) < end, item_ids))
        filtered = list(map(lambda x: int(x), filtered))
        for chunk in chunks(filtered, 50):
            dataset = []
            for item in chunk:
                if item < start or item > end:
                    continue
                file = open("{}/{}/{}/data.json".format(root, d, item))
                data = json.load(file)
                dataset.append(data)
            res = requests.post('https://touch.demask.io/import-opensea', json={
                "dataset": dataset,
                "pwd": "DKMVKL"
            })
            print(res.status_code)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('start', type=int)
        parser.add_argument('end', type=int)

    def handle(self, *args, **options):
        sync_range(options['start'], options['end'])
