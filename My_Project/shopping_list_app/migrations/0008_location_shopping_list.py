# Generated by Django 5.0.4 on 2024-04-05 18:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_list_app', '0007_rename_location_location_point'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='shopping_list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shopping_list_app.shoppinglist'),
        ),
    ]
