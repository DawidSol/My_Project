"""
URL configuration for My_Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from shopping_list_app.views import (index,
                                     CreateListView,
                                     AddProductView,
                                     ListsView,
                                     ListDetailView,
                                     DeleteProductView,
                                     CreateUserView,
                                     LoginView,
                                     LogoutView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('create_list/', CreateListView.as_view(), name='create_list'),
    path('add_product/', AddProductView.as_view(), name='add_product'),
    path('lists/', ListsView.as_view(), name='lists'),
    path('lists/<shopping_list_id>/', ListDetailView.as_view(), name='list_details'),
    path('delete_product/', DeleteProductView.as_view(), name='delete_product'),
    path('create_user/', CreateUserView.as_view(), name='create_user'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout')
]
