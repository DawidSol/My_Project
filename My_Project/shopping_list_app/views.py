from django.contrib.auth import authenticate, login, logout
from django.views import View
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, ListView, RedirectView
from shopping_list_app.forms import ProductForm, MyCreationForm, LoginForm
from shopping_list_app.models import ShoppingList, Product


def index(request):
    if request.user.is_authenticated:
        shopping_list = ShoppingList.objects.filter(list_checked=False, user=request.user).last()
        products = Product.objects.filter(shopping_list=shopping_list)
    else:
        if 'shopping_list_id' not in request.session:
            shopping_list = ShoppingList.objects.create(add_date=datetime.now())
            request.session['shopping_list_id'] = shopping_list.id
        else:
            shopping_list_id = request.session.get('shopping_list_id')
            shopping_list = ShoppingList.objects.get(id=shopping_list_id)
        products = Product.objects.filter(shopping_list=shopping_list)
    return render(request, 'base.html', {'products': products})


class CreateListView(LoginRequiredMixin, View):
    def get(self, request):
        ShoppingList.objects.create(add_date=datetime.now(), user=self.request.user)
        return redirect('index')


class AddProductView(FormView):
    template_name = 'form.html'
    form_class = ProductForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        shopping_list = form.cleaned_data['shopping_list']
        product = form.save(commit=False)
        product.shopping_list = shopping_list
        product.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs['user'] = self.request.user
        else:
            shopping_list_id = self.request.session.get('shopping_list_id')
            kwargs['initial'] = {'shopping_list': shopping_list_id}
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Product'
        context['button'] = 'Dodaj'
        return context


class ListsView(LoginRequiredMixin, ListView):
    model = ShoppingList
    template_name = 'lists.html'
    context_object_name = 'lists'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class ListDetailView(LoginRequiredMixin, View):
    def get(self, request, shopping_list_id):
        shopping_list = ShoppingList.objects.get(pk=shopping_list_id)
        products = Product.objects.filter(shopping_list=shopping_list)
        return render(request, 'list_details.html',
                      {'shopping_list': shopping_list, 'products': products})


class DeleteProductView(View):
    def post(self, request):
        selected_products = request.POST.getlist('selected_products')
        if selected_products:
            Product.objects.filter(id__in=selected_products).delete()
        next_url = request.POST.get('next', '/')
        return redirect(next_url)


class CreateUserView(FormView):
    template_name = 'form.html'
    form_class = MyCreationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registration'
        context['button'] = 'Stwórz'
        return context


class LoginView(FormView):
    template_name = 'form.html'
    form_class = LoginForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Login lub hasło nieprawidłowe')
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return self.form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Log In'
        context['button'] = 'Zaloguj'
        return context


class LogoutView(RedirectView):
    url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)
