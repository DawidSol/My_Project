from django.contrib.gis import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import ShoppingList, Product, Location

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
        if not kwargs.get('instance'):
            last_shopping_list = ShoppingList.objects.filter(list_checked=False, user=user).last()
            if last_shopping_list:
                self.initial['shopping_list'] = last_shopping_list.pk


class MyCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=64)
    password = forms.CharField(max_length=64, widget=forms.PasswordInput)


class AddLocationForm(forms.ModelForm):
    latitude = forms.CharField(widget=forms.HiddenInput(), required=False)
    longitude = forms.CharField(widget=forms.HiddenInput(), required=False)
    city = forms.CharField(widget=forms.HiddenInput(), required=False)
    street = forms.CharField(widget=forms.HiddenInput(), required=False)
    point = forms.PointField(widget=forms.HiddenInput(), required=False)
    added_by = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = Location
        fields = ['name', 'point', 'city', 'street', 'added_by']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['added_by'].initial = user

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        if latitude and longitude:
            cleaned_data['point'] = f'POINT({latitude} {longitude})'
        else:
            self.add_error(None, forms.ValidationError("Uzupełnij wszystkie pola."))
        return cleaned_data


class ShoppingListLocationForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['shop']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['shop'].queryset = Location.objects.filter(added_by=user)
