# inventory/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.equipment_list, name='equipment_list'),
    path('add/', views.add_equipment, name='add_equipment'),
    path('available/', views.available_list, name='available_list'),
    path('repair/<int:equipment_id>/', views.repair_equipment, name='repair_equipment'),
    path('rented/', views.rented_list, name='rented_list'),
    path('maintenance/', views.equipment_maintenance_list, name='maintenance_list'),
    path('edit/<int:equipment_id>', views.edit_equipment, name='edit_equipment'),
    path('delete/<int:equipment_id>', views.delete_equipment, name='delete_equipment'),
    path('delete/available/<int:equipment_id>', views.delete_avail_equipment, name='delete_avail_equipment'),
    
]
