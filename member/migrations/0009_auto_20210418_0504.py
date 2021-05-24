# Generated by Django 3.0.5 on 2021-04-17 22:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0008_auto_20210414_2338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmember',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='member.Group'),
        ),
        migrations.AlterField(
            model_name='groupmember',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='member.Member'),
        ),
    ]
