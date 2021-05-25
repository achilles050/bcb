# Generated by Django 3.0.5 on 2021-05-24 19:34

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0032_auto_20210525_0225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='refund_datetime',
            field=models.DateTimeField(verbose_name=datetime.datetime(2021, 5, 25, 2, 34, 4, 87, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='booking',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 25, 2, 34, 4, 87, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='payment',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 25, 2, 34, 4, 1088, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='refund',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 25, 2, 34, 4, 1088, tzinfo=utc)),
        ),
    ]
