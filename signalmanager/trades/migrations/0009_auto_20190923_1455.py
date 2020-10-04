# Generated by Django 2.0.1 on 2019-09-23 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0008_auto_20190923_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='status',
            field=models.IntegerField(choices=[(2, 'Cancled'), (0, 'Pending'), (5, 'Closed'), (1, 'Active'), (4, 'Deleted'), (6, 'Unknown')], default=6),
        ),
    ]
