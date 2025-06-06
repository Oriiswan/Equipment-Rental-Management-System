# customers/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.customer_list, name='customer_list'),
    path('add/', views.add_customer, name='add_customer'),
    path('edit/<int:customer_id>', views.edit_customer, name='edit_customer'),
    path('active/', views.active_customer, name='active_customer'),
    path('overdue/', views.overdue_customer, name='overdue_customer'),
    path('delete_customer/<int:customer_id>', views.delete_customer, name='delete_customer'),
]
