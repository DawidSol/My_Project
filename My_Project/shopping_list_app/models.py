from django.contrib.gis.db import models
from django.contrib.auth.models import User


class Location(models.Model):
    name = models.CharField(max_length=64)
    point = models.PointField()
    city = models.CharField(max_length=64)
    street = models.CharField(max_length=64)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.name}({self.street})'


class ShoppingList(models.Model):
    list_checked = models.BooleanField(default=False)
    add_date = models.DateTimeField()
    checked_date = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    shop = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.add_date.date())


class Product(models.Model):
    name = models.CharField(max_length=64)
    quantity = models.IntegerField(default=1)
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name
