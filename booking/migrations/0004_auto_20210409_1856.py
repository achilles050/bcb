# Generated by Django 3.0.5 on 2021-04-09 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_auto_20210409_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allcourtinfo',
            name='qrcode',
            field=models.ImageField(null=True, upload_to='pic'),
        ),
    ]
