from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import ShoppingList, Product

User = get_user_model()


def validate_quantity(value):
    if value < 1:
        raise forms.ValidationError('Ilość produktu nie może być mniejsza niż 1')


class ProductForm(forms.ModelForm):
    quantity = forms.IntegerField(validators=[validate_quantity])

    class Meta:
        model = Product
        fields = ['name', 'quantity', 'shopping_list']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if not user:
            self.fields['shopping_list'].widget = forms.HiddenInput()
            self.fields['shopping_list'].queryset = ShoppingList.objects.filter(list_checked=False, user=None)
        else:
            self.fields['shopping_list'].queryset = ShoppingList.objects.filter(list_checked=False, user=user)


class MyCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=64)
    password = forms.CharField(max_length=64, widget=forms.PasswordInput)
