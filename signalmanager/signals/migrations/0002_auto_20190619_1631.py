# Generated by Django 2.0.1 on 2019-06-19 16:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('signals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('bot_id', models.TextField()),
                ('token', models.TextField()),
                ('username', models.TextField()),
                ('name', models.TextField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bots', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('channel_id', models.TextField(unique=True)),
                ('title', models.TextField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channels', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='MessageRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('message_id', models.TextField()),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messagerecords_channel', to='signals.Channel')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messagerecords_bot', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='Signal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('order_id', models.TextField()),
                ('order_symbol', models.TextField()),
                ('order_type', models.CharField(max_length=10)),
                ('order_stoploss', models.TextField()),
                ('order_price', models.TextField()),
                ('order_lot', models.TextField()),
                ('order_takeprofit', models.TextField()),
                ('order_status', models.CharField(choices=[('Cancled', 'Cancled'), ('Pending', 'Pending'), ('Closed', 'Closed'), ('Active', 'Active'), ('Deleted', 'Deleted')], default='', max_length=10)),
                ('message_id', models.TextField(default='0')),
                ('order_comment', models.CharField(blank=True, default='', max_length=100)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signals', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.AddField(
            model_name='messagerecord',
            name='signal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messagerecords_signal', to='signals.Signal'),
        ),
        migrations.AlterUniqueTogether(
            name='signal',
            unique_together={('order_id', 'owner')},
        ),
        migrations.AlterUniqueTogether(
            name='messagerecord',
            unique_together={('channel', 'signal')},
        ),
    ]
