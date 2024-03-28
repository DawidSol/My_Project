from django import forms
from .models import ShoppingList


def validate_quantity(value):
    if value < 1:
        raise forms.ValidationError('Ilość produktu nie może być mniejsza niż 1')


class ProductForm(forms.Form):
    name = forms.CharField(max_length=64)
    quantity = forms.IntegerField(validators=[validate_quantity])
    shopping_list = forms.ModelChoiceField(queryset=ShoppingList.objects.filter(list_checked=False),
                                           widget=forms.RadioSelect)
