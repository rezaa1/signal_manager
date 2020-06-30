# Generated by Django 2.2.6 on 2019-12-12 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0021_auto_20191212_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='status',
            field=models.IntegerField(choices=[(2, 'Canceled'), (0, 'Pending'), (5, 'Closed'), (1, 'Active'), (4, 'Deleted'), (6, 'Unknown')], default=6),
        ),
    ]
