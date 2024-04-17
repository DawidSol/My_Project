import os
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.conf import settings
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
    info = 'Lista zakupów:'
    return render(request, 'base.html', {'products': products,
                                         'shopping_list': shopping_list,
                                         'info': info})


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


class AddLocationView(LoginRequiredMixin, FormView):
    template_name = 'location.html'
    form_class = AddLocationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class LeaveLocationView(LoginRequiredMixin, View):

    def post(self, request):
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        if latitude and longitude:
            latitude = float(latitude)
            longitude = float(longitude)
            my_current_location = Location.objects.create(name='current_location',
                                                          point='POINT({} {})'.format(latitude, longitude))
            shopping_list_id = request.POST.get('shopping_list_id')
            shopping_list = ShoppingList.objects.get(id=shopping_list_id)
            try:
                shop_location = shopping_list.shop
                if shop_location.point.distance(my_current_location.point) > 0.05:
                    return redirect('close_list', shopping_list_id=shopping_list_id)
                else:
                    info = 'Nie opuszczono okolic sklepu!'
            except Location.DoesNotExist:
                info = 'Lista nie jest przypisana do żadnego sklepu!'
                return render(request, 'base.html', {'info': info})
        else:
            info = 'Brak danych lokalizacyjnych'
        return render(request, 'base.html', {'info': info})


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
            return render(request, 'base.html', {'info': info})
        else:
            return redirect('change_list', shopping_list_id=shopping_list_id)


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


class AddLocationToListView(LoginRequiredMixin, FormView):
    template_name = 'form.html'
    form_class = ShoppingListLocationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        shop = form.cleaned_data['shop']
        shopping_list = form.instance
        shopping_list.shop = shop
        shopping_list.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = ShoppingList.objects.get(id=self.kwargs['shopping_list_id'])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Choose Shop'
        context['button'] = 'Wybierz'
        return context


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
            if shop_location.point.distance(my_current_location.point) < 50:
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
                            if int(response) == 202:
                                messages.success(request, 'Wiadomość e-mail została wysłana pomyślnie!')
                                return HttpResponseRedirect(reverse_lazy('index'))
                            else:
                                messages.error(request, 'Wystąpił problem podczas wysyłania wiadomości e-mail.')
                                return HttpResponseRedirect(reverse_lazy('index'))
                        except Exception as e:
                            messages.error(request, f'An error occurred: {e}')
                            return HttpResponseRedirect(reverse_lazy('index'))
                messages.info(request, 'Nie ma żadnych przypomnień!')
                return HttpResponseRedirect(reverse_lazy('index'))
            messages.info(request, 'W pobliżu nie ma żadnego z Twoich sklepów!')
            my_current_location.delete()
            return HttpResponseRedirect(reverse_lazy('index'))
        else:
            messages.info(request, 'Brak danych lokalizacyjnych')
            return HttpResponseRedirect(reverse_lazy('index'))
