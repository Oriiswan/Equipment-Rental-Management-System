# booking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.booking_list, name='booking_list'),
    path('add/', views.add_booking, name='add_booking'),
    path('pending/', views.pending_list, name='pending_list'),
    path('active/', views.active_list, name='active_list'),
    path('overdue/', views.overdue_list, name='overdue_list'),
]
