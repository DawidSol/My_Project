from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import ShoppingList


def validate_quantity(value):
    if value < 1:
        raise forms.ValidationError('Ilość produktu nie może być mniejsza niż 1')


class ProductForm(forms.Form):
    name = forms.CharField(max_length=64)
    quantity = forms.IntegerField(validators=[validate_quantity])
    shopping_list = forms.ModelChoiceField(queryset=ShoppingList.objects.filter(list_checked=False),
                                           widget=forms.RadioSelect)


class MyCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=64)
    password = forms.CharField(max_length=64, widget=forms.PasswordInput)
