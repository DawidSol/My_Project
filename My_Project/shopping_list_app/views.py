from django.views import View
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from shopping_list_app.forms import ProductForm
from shopping_list_app.models import ShoppingList, Product


def index(request):
    shopping_list = ShoppingList.objects.last()
    products = Product.objects.filter(shopping_list=shopping_list)
    return render(request, 'base.html', {'products': products})


def create_list(request):
    if request.method == 'GET':
        new_list = ShoppingList()
        new_list.add_date = datetime.now()
        new_list.save()
        return redirect('index')


class AddProductView(FormView):
    template_name = 'form.html'
    form_class = ProductForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        name = form.cleaned_data['name']
        quantity = form.cleaned_data['quantity']
        shopping_list = form.cleaned_data['shopping_list']
        Product.objects.create(name=name, quantity=quantity, shopping_list=shopping_list)
        return redirect('index')


class ListsView(ListView):
    model = ShoppingList
    template_name = 'lists.html'
    context_object_name = 'lists'


class ListDetailView(View):
    def get(self, request, shopping_list_id):
        shopping_list = ShoppingList.objects.get(pk=shopping_list_id)
        products = Product.objects.filter(shopping_list=shopping_list)
        return render(request, 'list_details.html',
                      {'shopping_list': shopping_list, 'products': products})


class DeleteProductView(View):
    pass
