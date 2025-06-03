# booking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.booking_list, name='booking_list'),
    path('add/', views.add_booking, name='add_booking'),
    path('pending/', views.pending_list, name='pending_list'),
    path('active/', views.active_list, name='active_list'),
    path('overdue/', views.overdue_list, name='overdue_list'),
    path('mark_as_returned/<int:rental_id>', views.mark_as_returned, name='return_booking'),
    path('mark_as_returned_pending/<int:rental_id>', views.mark_as_returned_pending_list, name='return_booking'),
    path('mark_as_returned_active/<int:rental_id>', views.mark_as_returned_active_list, name='return_booking'),
    path('mark_as_returned_overdue/<int:rental_id>', views.mark_as_returned_overdue_list, name='return_booking'),
    
    path('return_list/', views.return_list, name='return_list'),
]
