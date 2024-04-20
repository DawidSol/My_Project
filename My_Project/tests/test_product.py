import pytest
from django.urls import reverse
from shopping_list_app.models import Product


@pytest.mark.django_db
def test_product_is_saved(client, test_user, shopping_list):
    initial_product_count = Product.objects.count()
    client.login(username='testuser', password='testpassword')
    response = client.post(reverse('add_product'), {
        'name': 'Test Product',
        'quantity': 2,
        'shopping_list': shopping_list.id,
    }, follow=True)
    assert response.status_code == 200
    assert Product.objects.count() == initial_product_count + 1
