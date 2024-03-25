from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from Shopping_list_app.forms import ProductForm


def index(request):
    return render(request, 'base.html')


class AddProductView(FormView):
    template_name = 'form.html'
    form_class = ProductForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        product = form.save(commit=False)
        product.save()
        return super().form_valid(form)
