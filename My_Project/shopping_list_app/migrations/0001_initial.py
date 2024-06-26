# Generated by Django 5.0.4 on 2024-04-13 09:57

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('city', models.CharField(max_length=64)),
                ('street', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('list_checked', models.BooleanField(default=False)),
                ('add_date', models.DateTimeField()),
                ('checked_date', models.DateTimeField(blank=True, null=True)),
                ('shop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shopping_list_app.location')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('quantity', models.IntegerField(default=1)),
                ('shopping_list', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shopping_list_app.shoppinglist')),
            ],
        ),
    ]
