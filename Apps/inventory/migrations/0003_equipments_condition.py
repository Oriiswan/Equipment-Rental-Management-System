# Generated by Django 4.2 on 2025-06-14 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_equipments_utilizations'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipments',
            name='condition',
            field=models.CharField(default='good', max_length=55),
        ),
    ]
