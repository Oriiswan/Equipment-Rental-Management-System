# inventory/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.equipment_list, name='equipment_list'),
    path('add/', views.add_equipment, name='add_equipment'),
    path('available/', views.available_list, name='available_list'),
    path('rented/', views.rented_list, name='rented_list'),
    
]
