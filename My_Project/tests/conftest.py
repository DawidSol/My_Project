from datetime import datetime
import pytest
from django.contrib.gis.geos import Point
from django.test import Client
from shopping_list_app.models import ShoppingList, Location, Product
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def test_user():
    return User.objects.create_user(
        username='testuser',
        password='testpassword',
        email='testemail@example.com',
    )


@pytest.fixture
def shopping_list(location, test_user):
    return ShoppingList.objects.create(
        list_checked=False,
        add_date=datetime.now(),
        checked_date=None,
        shop=location,
        user=test_user
    )


@pytest.fixture
def location(test_user):
    point = Point(50.12345, 20.54321)
    return Location.objects.create(
        name="Test Location",
        city="Test City",
        street="Test Street",
        point=point,
        added_by=test_user
    )


@pytest.fixture
def product(shopping_list):
    return Product.objects.create(
        name="Test Product",
        quantity=2,
        shopping_list=shopping_list.id,
    )
