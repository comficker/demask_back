import datetime

from django.db import models
from django.core.files.temp import NamedTemporaryFile
from django.utils import timezone
from urllib.parse import urlparse
import requests
from django.core.files import File


# Create your models here.
class Contract(models.Model):
    chain_id = models.CharField(max_length=50, default="eth")
    address = models.CharField(max_length=50, null=True, blank=True)
    is_contract = models.BooleanField(default=True)

    name = models.CharField(max_length=120)
    desc = models.CharField(max_length=500, null=True, blank=True)
    media = models.CharField(max_length=500, blank=True, null=True)
    media_storage = models.FileField(upload_to='media', blank=True)
    is_approved = models.BooleanField(default=False)

    token_schema = models.CharField(max_length=50, default="erc721")
    token_symbol = models.CharField(max_length=50, blank=True, null=True)
    total_supply = models.IntegerField(default=0)
    init_price = models.FloatField(default=0)
    payment_symbol = models.CharField(max_length=50, default="ETH")
    date_mint = models.DateTimeField(null=True, blank=True)

    trails = models.JSONField(null=True, blank=True)
    links = models.JSONField(null=True, blank=True)


class Trait(models.Model):
    contract = models.ForeignKey(Contract, related_name="traits", on_delete=models.CASCADE)
    kind_format = models.CharField(max_length=128, default="text", null=True, blank=True)
    field = models.CharField(max_length=128)
    value = models.CharField(max_length=256)
    rarity = models.FloatField(default=1)

    class Meta:
        index_together = (
            ('contract', 'field', 'value'),
        )

    def calculate(self):
        if self.rarity == 0:
            self.rarity = self.assets.count() / self.contract.assets.count()
            self.save()


class Asset(models.Model):
    contract = models.ForeignKey(Contract, related_name="assets", on_delete=models.CASCADE)
    item_id = models.CharField(max_length=100)

    name = models.CharField(max_length=120)
    desc = models.CharField(max_length=500, null=True, blank=True)
    uri = models.CharField(max_length=150, null=True, blank=True)
    external_link = models.CharField(max_length=150, null=True, blank=True)

    owner = models.CharField(max_length=50)
    date_mint = models.DateTimeField(null=True, blank=True)
    media = models.CharField(max_length=500, blank=True, null=True)
    media_origin = models.CharField(max_length=500, blank=True, null=True)
    media_storage = models.FileField(upload_to='media', blank=True)
    traits = models.ManyToManyField(Trait, blank=True, related_name="assets")

    current_price = models.FloatField(default=0)
    rarity = models.FloatField(default=1)

    def save_media(self, url):
        if url is None:
            return None
        name = urlparse(url).path.split('/')[-1]
        temp = NamedTemporaryFile(delete=True)
        try:
            req = requests.get(url=url, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True)
            disposition = req.headers.get("Content-Disposition")
            if disposition:
                test = disposition.split("=")
                if len(test) > 1:
                    name = test[1].replace("\"", "")
            temp.write(req.content)
            ext = name.split('.')[-1]
            if ext == '':
                ext = 'jpg'
                name = name + '.' + ext
            if ext.lower() in ['jpg', 'jpeg', 'png', 'mp4']:
                temp.flush()
                self.media_storage.save(name, File(temp))
            return None
        except Exception as e:
            print(e)
            return None


class Wallet(models.Model):
    address = models.CharField(max_length=50)
    born = models.IntegerField(default=2022)
    transaction = models.IntegerField(default=0)
    joined_project = models.IntegerField(default=0)
    mask = models.ForeignKey(Asset, related_name="wallets", on_delete=models.SET_NULL, null=True, blank=True)


class Report(models.Model):
    time_range = models.CharField(max_length=50, default='d')
    created = models.DateTimeField(default=timezone.now)

    contract = models.ForeignKey(Contract, related_name="reports", on_delete=models.CASCADE)
    floor_price = models.FloatField(default=0)
    owners = models.IntegerField(default=0)
    market_cap = models.FloatField(default=0)
    volume = models.FloatField(default=0)
    sales = models.IntegerField(default=0)


class Transaction(models.Model):
    asset = models.ForeignKey(Contract, related_name="transactions", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    tx_hash = models.CharField(max_length=256)
    tx_date = models.DateTimeField(null=True, blank=True)
    address_from = models.ForeignKey(Wallet, related_name="from_txs", null=True, blank=True, on_delete=models.CASCADE)
    address_to = models.ForeignKey(Wallet, related_name="to_txs", null=True, blank=True, on_delete=models.CASCADE)
    value = models.FloatField(default=0)
