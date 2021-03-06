# Generated by Django 4.0.4 on 2022-05-30 15:22

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_id', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=120)),
                ('desc', models.CharField(blank=True, max_length=500, null=True)),
                ('uri', models.CharField(blank=True, max_length=150, null=True)),
                ('external_link', models.CharField(blank=True, max_length=150, null=True)),
                ('owner', models.CharField(max_length=50)),
                ('date_mint', models.DateTimeField(blank=True, null=True)),
                ('media', models.CharField(blank=True, max_length=500, null=True)),
                ('media_origin', models.CharField(blank=True, max_length=500, null=True)),
                ('media_storage', models.FileField(blank=True, upload_to='media')),
                ('current_price', models.FloatField(default=0)),
                ('rarity', models.FloatField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chain_id', models.CharField(default='eth', max_length=50)),
                ('address', models.CharField(blank=True, max_length=50, null=True)),
                ('is_contract', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=120)),
                ('desc', models.CharField(blank=True, max_length=500, null=True)),
                ('media', models.CharField(blank=True, max_length=500, null=True)),
                ('media_storage', models.FileField(blank=True, upload_to='media')),
                ('is_approved', models.BooleanField(default=False)),
                ('token_schema', models.CharField(default='erc721', max_length=50)),
                ('token_symbol', models.CharField(blank=True, max_length=50, null=True)),
                ('total_supply', models.IntegerField(default=0)),
                ('init_price', models.FloatField(default=0)),
                ('payment_symbol', models.CharField(default='ETH', max_length=50)),
                ('date_mint', models.DateTimeField(blank=True, null=True)),
                ('trails', models.JSONField(blank=True, null=True)),
                ('links', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=50)),
                ('born', models.IntegerField(default=2022)),
                ('transaction', models.IntegerField(default=0)),
                ('joined_project', models.IntegerField(default=0)),
                ('mask', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wallets', to='app.asset')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('tx_hash', models.CharField(max_length=256)),
                ('tx_date', models.DateTimeField(blank=True, null=True)),
                ('value', models.FloatField(default=0)),
                ('address_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='from_txs', to='app.wallet')),
                ('address_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_txs', to='app.wallet')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='app.contract')),
            ],
        ),
        migrations.CreateModel(
            name='Trait',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind_format', models.CharField(blank=True, default='text', max_length=128, null=True)),
                ('field', models.CharField(max_length=128)),
                ('value', models.CharField(max_length=256)),
                ('rarity', models.FloatField(default=1)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='traits', to='app.contract')),
            ],
            options={
                'index_together': {('contract', 'field', 'value')},
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_range', models.CharField(default='d', max_length=50)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('floor_price', models.FloatField(default=0)),
                ('owners', models.IntegerField(default=0)),
                ('market_cap', models.FloatField(default=0)),
                ('volume', models.FloatField(default=0)),
                ('sales', models.IntegerField(default=0)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='app.contract')),
            ],
        ),
        migrations.AddField(
            model_name='asset',
            name='contract',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='app.contract'),
        ),
        migrations.AddField(
            model_name='asset',
            name='traits',
            field=models.ManyToManyField(blank=True, related_name='assets', to='app.trait'),
        ),
    ]
