# booking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.booking_list, name='booking_list'),
    path('list/today', views.booking_list_today),
    path('list/newest', views.booking_list_newest ),
    path('list/oldest', views.booking_list_oldest),
    path('add/', views.add_booking, name='add_booking'),
    path('pending/', views.pending_list, name='pending_list'),
    path('pending/today', views.pending_list_today),
    path('pending/newest', views.pending_list_newest),
    path('pending/oldest', views.pending_list_oldest),
    path('active/', views.active_list, name='active_list'),
    path('active/today', views.active_list_today),
    path('active/newest', views.active_list_newest),
    path('active/oldest', views.active_list_oldest),
    path('overdue/', views.overdue_list, name='overdue_list'),
    path('overdue/today', views.overdue_list_today),
    path('overdue/newest', views.overdue_list_newest),
    path('overdue/oldest', views.overdue_list_oldest),
    path('mark_as_returned/<int:rental_id>', views.mark_as_returned, name='return_booking'),
    path('delete/<int:rental_id>', views.delete_booking, name='delete_booking'),
   
    path('delete_pending_list/<int:rental_id>', views.delete_pending_list, name='delete_pending_list'),
    path('delete_returned/<int:rental_id>', views.delete_returned_list, name='delete_return_list'),
    
    path('mark_as_returned_active/<int:rental_id>', views.mark_as_returned_active_list, name='return_booking'),
    path('mark_as_returned_overdue/<int:rental_id>', views.mark_as_returned_overdue_list, name='return_booking'),
    path('edit/<int:rental_id>', views.edit_booking, name='edit_booking'),
    
    path('return_list/', views.return_list, name='return_list'),
    path('return_list/today', views.return_list_today),
    path('return_list/newest', views.return_list_newest),
    path('return_list/oldest', views.return_list_oldest),
]
