import pytest
from shopping_list_app.models import Product, ShoppingList


@pytest.mark.django_db
def test_index_authenticated_user(client, test_user, shopping_list):
    client.login(username='testuser', password='testpassword')
    shopping_list = ShoppingList.objects.filter(user=test_user, list_checked=False).last()
    Product.objects.create(name="product 1", shopping_list=shopping_list)
    Product.objects.create(name="product 2", shopping_list=shopping_list)
    response = client.get('/')
    assert shopping_list is not None
    products = Product.objects.filter(shopping_list=shopping_list)
    assert response.status_code == 200
    assert all(product.shopping_list == shopping_list for product in products)


@pytest.mark.django_db
def test_index_unauthenticated_user(client):
    assert ShoppingList.objects.count() == 0
    assert 'shopping_list_id' not in client.session
    response = client.get('/')
    assert response.status_code == 200
    if 'shopping_list_id' in client.session:
        shopping_list_id = client.session['shopping_list_id']
        assert ShoppingList.objects.filter(id=shopping_list_id).exists()
    else:
        assert ShoppingList.objects.count() == 1


@pytest.mark.django_db
def test_create_new_list(client):
    initial_shopping_list_count = ShoppingList.objects.count()
    client.login(username='testuser', password='testpassword')
    response = client.get('/create_list/')
    assert response.status_code == 302
    response = client.post('/', {
        'answer': True
    })
    assert response.status_code == 200
    assert ShoppingList.objects.count() == initial_shopping_list_count + 1
