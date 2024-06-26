import os
from geopy.distance import geodesic
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.paginator import Paginator
from django.views import View
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count
from django.db.models.functions import Lower
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, ListView, RedirectView
from dotenv import load_dotenv
from mailersend import emails
from .forms import ProductForm, MyCreationForm, LoginForm, AddLocationForm, ShoppingListLocationForm
from .models import ShoppingList, Product, Location


# Home page view, if user is authenticated show last shopping list, if not generate a new list
def index(request):
    products = None
    if request.user.is_authenticated:
        shopping_list = ShoppingList.objects.filter(list_checked=False, user=request.user).last()
        if shopping_list:
            products = Product.objects.filter(shopping_list=shopping_list)
    else:
        if 'shopping_list_id' not in request.session:
            shopping_list = ShoppingList.objects.create(add_date=datetime.now())
            request.session['shopping_list_id'] = shopping_list.id
        else:
            shopping_list_id = request.session.get('shopping_list_id')
            shopping_list = ShoppingList.objects.get(id=shopping_list_id)
            products = Product.objects.filter(shopping_list=shopping_list)
    return render(request, 'base.html', {'products': products,
                                         'shopping_list': shopping_list})


# Create new object ShoppingList
class CreateListView(LoginRequiredMixin, View):
    def get(self, request):
        title = 'Stwórz listę'
        question = 'Czy na pewno chcesz stworzyć nową listę?'
        return render(request, 'question_list.html', {'title': title, 'question': question})

    def post(self, request):
        answer = request.POST.get('answer')
        if answer == "True":
            ShoppingList.objects.create(add_date=datetime.now(), user=self.request.user)
        return redirect('index')


# Add product to shopping list
class AddProductView(FormView):
    template_name = 'form.html'
    form_class = ProductForm

    def form_valid(self, form):
        shopping_list = form.cleaned_data['shopping_list']
        product = form.save(commit=False)
        product.shopping_list = shopping_list
        product.save()
        self.request.session['shopping_list_id'] = shopping_list.id
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

    def get_success_url(self):
        if self.request.user.is_authenticated:
            shopping_list_id = self.request.session.get('shopping_list_id')
            return reverse_lazy('list_details', kwargs={'shopping_list_id': shopping_list_id})
        else:
            return reverse_lazy('index')


# Show all shopping lists of the user
class ListsView(LoginRequiredMixin, ListView):
    model = ShoppingList
    template_name = 'lists.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lists = ShoppingList.objects.filter(user=self.request.user).order_by('-add_date')
        paginator = Paginator(lists, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


# Show details of specific shopping list
class ListDetailView(LoginRequiredMixin, View):
    def get(self, request, shopping_list_id):
        shopping_list = ShoppingList.objects.get(pk=shopping_list_id)
        products = Product.objects.filter(shopping_list=shopping_list)
        return render(request, 'list_details.html',
                      {'shopping_list': shopping_list, 'products': products})


# Remove products from shopping list
class DeleteProductView(View):
    def post(self, request):
        selected_products = request.POST.getlist('selected_products')
        if selected_products:
            Product.objects.filter(id__in=selected_products).delete()
        return redirect('index')


# Create new user
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


# Log in
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


# Log out
class LogoutView(RedirectView):
    url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


# Create new shop location
class AddLocationView(LoginRequiredMixin, FormView):
    template_name = 'location.html'
    form_class = AddLocationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


# Get current location and close the shopping list
class LeaveLocationView(LoginRequiredMixin, View):

    def post(self, request):
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        shopping_list_id = request.POST.get('shopping_list_id')
        shopping_list = ShoppingList.objects.get(id=shopping_list_id)
        products = Product.objects.filter(shopping_list=shopping_list)
        if latitude and longitude:
            latitude = float(latitude)
            longitude = float(longitude)
            my_current_location = Location.objects.create(name='current_location',
                                                          point='POINT({} {})'.format(latitude, longitude))
            shop_location = shopping_list.shop
            if shop_location:
                if geodesic(shop_location.point, my_current_location.point) > 0.1:
                    return redirect('close_list', shopping_list_id=shopping_list_id)
                else:
                    info = 'Nie opuszczono okolic sklepu!'
            else:
                info = 'Lista nie jest przypisana do żadnego sklepu!'
        else:
            info = 'Brak danych lokalizacyjnych'
        return render(request, 'list_details.html', {'info': info,
                                                     'shopping_list': shopping_list, 'products': products})


# Check if all products from list were bought if so close list, if not go to more options
class CloseListView(LoginRequiredMixin, View):
    def get(self, request, shopping_list_id):
        title = 'Zamknij listę'
        question = 'Czy wszystkie produkty z listy zostały kupione??'
        return render(request, 'question_list.html', {'title': title, 'question': question})

    def post(self, request, shopping_list_id):
        answer = request.POST.get('answer')
        shopping_list = ShoppingList.objects.get(id=shopping_list_id)
        if answer == "True":
            shopping_list.list_checked = True
            shopping_list.checked_date = datetime.now()
            shopping_list.save()
            info = 'Lista pomyślnie zamknięta!'
            products = Product.objects.filter(shopping_list=shopping_list)
            return render(request, 'list_details.html', {'shopping_list': shopping_list,
                                                         'products': products, 'info': info})
        else:
            return redirect('change_list', shopping_list_id=shopping_list_id)


# Delete products that were not bought or add them to a new list
class ChangeListView(LoginRequiredMixin, View):
    def get(self, request, shopping_list_id):
        shopping_list = ShoppingList.objects.get(id=shopping_list_id)
        products = Product.objects.filter(shopping_list=shopping_list)
        return render(request, 'change_lists.html', {'shopping_list': shopping_list,
                                                     'products': products})

    def post(self, request, shopping_list_id):
        option = request.POST.get('option')
        selected_products = request.POST.getlist('selected_products')
        if option == 'delete':
            Product.objects.filter(id__in=selected_products).delete()
            info = 'Lista pomyślnie zamknięta!'
        elif len(selected_products) == 0:
            info = 'Nie wybrano żadnych produktów, lista została zrealizowana w całości'
        else:
            new_shopping_list = ShoppingList.objects.create(add_date=datetime.now(), user=request.user)
            for product in selected_products:
                changed_product = Product.objects.get(id=product)
                changed_product.shopping_list = new_shopping_list
                changed_product.save()
            info = 'Produkty przeniesiono do nowej listy'
        shopping_list = ShoppingList.objects.get(id=shopping_list_id)
        shopping_list.list_checked = True
        shopping_list.checked_date = datetime.now()
        shopping_list.save()
        return render(request, 'base.html', {'info': info})


# Add shop location to a shopping list
class AddLocationToListView(LoginRequiredMixin, FormView):
    template_name = 'form.html'
    form_class = ShoppingListLocationForm

    def form_valid(self, form):
        shop = form.cleaned_data['shop']
        shopping_list = form.instance
        shopping_list.shop = shop
        shopping_list.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['instance'] = ShoppingList.objects.get(id=self.kwargs['shopping_list_id'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Choose Shop'
        context['button'] = 'Wybierz'
        return context

    def get_success_url(self):
        shopping_list_id = self.kwargs.get('shopping_list_id')
        return reverse_lazy('list_details', kwargs={'shopping_list_id': shopping_list_id})


# Send an e-mail with most popular products for the shop location
class SendReminderView(LoginRequiredMixin, View):
    def get(self, request, shopping_list_id):
        user = request.user
        shopping_list = ShoppingList.objects.get(id=shopping_list_id)
        products = Product.objects.filter(shopping_list=shopping_list)
        shop_location = shopping_list.shop
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')
        if latitude and longitude:
            latitude = float(latitude)
            longitude = float(longitude)
            my_current_location = Location.objects.create(name='current_location',
                                                          point='POINT({} {})'.format(latitude, longitude))
            if geodesic(shop_location.point, my_current_location.point) < 0.2:
                done_lists = ShoppingList.objects.filter(list_checked=True, user=request.user, shop=shop_location)
                if len(done_lists) > 1:
                    product_count = (Product.objects.annotate(lower_name=Lower('name')).values('lower_name')
                                     .annotate(count=Count('shopping_list')).order_by('-count')[:5])
                    filtered_product_count = [item for item in product_count if item['lower_name']
                                              not in [product.name.lower() for product in products]]
                    if len(filtered_product_count) > 0:
                        message = f'Witaj {user.username}!\n\n'
                        message += f'Znajdujesz się w pobliżu {shop_location}!\n'
                        message += 'Oto kilka najczęściej kupowanych przez Ciebie produktów w tym sklepie, '
                        message += 'których obecnie nie ma na Twojej liście:\n'
                        for product in filtered_product_count:
                            message += f'\t{product["lower_name"]}\n'
                        try:
                            load_dotenv()
                            api_key = os.getenv('MAILERSEND_API_KEY')
                            mailer = emails.NewEmail(api_key)
                            mail_body = {}
                            mail_from = {"name": "noreply", "email": settings.DEFAULT_FROM_EMAIL}
                            recipient = [{"name": user.username, "email": user.email}]
                            mailer.set_mail_from(mail_from, mail_body)
                            mailer.set_mail_to(recipient, mail_body)
                            mailer.set_subject("Przypomnienie", mail_body)
                            mailer.set_plaintext_content(message, mail_body)
                            response = mailer.send(mail_body)
                            if response == '202\n':
                                messages.success(request, 'Wiadomość e-mail została wysłana pomyślnie!')
                                return redirect('list_details', shopping_list_id=shopping_list_id)
                            else:
                                messages.error(request, 'Wystąpił problem podczas wysyłania wiadomości e-mail.')
                                return redirect('index')
                        except Exception as e:
                            messages.error(request, f'An error occurred: {e}')
                            return redirect('index')
                messages.info(request, 'Nie ma żadnych przypomnień!')
                return redirect('list_details', shopping_list_id=shopping_list_id)
            messages.info(request, 'W pobliżu nie ma żadnego z Twoich sklepów!')
            my_current_location.delete()
            return redirect('list_details', shopping_list_id=shopping_list_id)
        else:
            messages.info(request, 'Brak danych lokalizacyjnych')
            return redirect('list_details', shopping_list_id=shopping_list_id)
