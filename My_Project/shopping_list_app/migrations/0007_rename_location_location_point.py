# Generated by Django 5.0.4 on 2024-04-04 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_list_app', '0006_location'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='location',
            new_name='point',
        ),
    ]