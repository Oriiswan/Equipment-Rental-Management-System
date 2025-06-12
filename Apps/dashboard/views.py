from django.shortcuts import render
from django.http import HttpResponse
from decimal import Decimal
from inventory.models import Equipments
import math
from booking.models import rental
from django.db.models import Sum
from django.db.models import F,Q
from django.contrib.auth.decorators import login_required
from datetime import date
from django.contrib.auth import login, authenticate
@login_required
def info(request):
    # Update rental statuses first
    update_rental_statuses()
    
    # Now proceed with your existing dashboard logic
    last_four = rental.objects.order_by('-updated_at')[:10]
    most = Equipments.objects.filter(~Q(available_quantity=F('total_quantity')))
    
    records = rental.objects.all()
    totals = sum(item.revenue or Decimal('0.00') for item in records if item.revenue)
    
    equipments = Equipments.objects.all()
    equipments_count = Equipments.objects.count()
    categories = Equipments.objects.values_list('category').distinct()
    unique = sorted(set(categories))
    total = 0
    avail = 0
    
    for equipment in equipments:
        total += equipment.total_quantity
        avail += equipment.available_quantity 
    
    data = {
        'count': equipments_count,
        'equipments': equipments, 
        'category': len(unique),
        'categories': categories,
        'available': avail,
        'rented': total - avail,
        'available_percent': math.floor((avail / total) * 100) if total > 0 else 0,
        'rented_percent': math.floor(((total - avail) / total) * 100) if total > 0 else 0,
        'overdue_count': rental.objects.filter(status='overdue').count(),
        'returned_count': rental.objects.filter(status='returned').count(),
        'active_count': rental.objects.filter(status='active').count(),
        'pending_count': rental.objects.filter(status='pending').count(),
        'total': totals,
        'recent_activities': last_four,
        'recent_actcount': last_four.count(),
        'most_popular_equipment': most.order_by('available_quantity')[:4]
    }
    
    return render(request, 'apps/dashboard/index.html', data)
def update_rental_statuses():
    """Update all rental statuses based on current date"""
    today = date.today()
    rentals_to_update = rental.objects.exclude(status='returned').exclude(status='cancelled')
    updated_count = 0
    
    for rental_obj in rentals_to_update:
        old_status = rental_obj.status
        new_status = old_status
        
        # Determine new status based on dates
        if rental_obj.return_date:
            new_status = 'returned'
        elif today < rental_obj.rental_date:
            new_status = 'pending'
        elif rental_obj.rental_date <= today <= rental_obj.due_date:
            new_status = 'active'
        elif today > rental_obj.due_date:
            new_status = 'overdue'
        
        # Update if status changed
        if old_status != new_status:
            rental_obj.status = new_status
            rental_obj.save(update_fields=['status'])
            updated_count += 1
    
    return updated_count
@login_required
def info(request):
  last_four = rental.objects.order_by('-updated_at')
  most = Equipments.objects.filter(~Q(available_quantity=F('total_quantity')))
  
  records = rental.objects.all()
  totals = sum(item.revenue or Decimal('0.00') for item in records)
  equipments =Equipments.objects.all()
  equipments_count = Equipments.objects.count()
  categories = Equipments.objects.values_list('category').distinct()
  unique = sorted(set(categories))
  total = 0
  avail = 0
  rentals = rental.objects.all()
  for equipment in equipments:
    total += equipment.total_quantity
    avail += equipment.available_quantity 
  data = {
    'count': equipments_count,
    'equipments': equipments, 
    'category': len(unique),
    'categories': categories,
    'available': avail,
    'rented': total - avail,
    'available_percent': math.floor((avail / total) * 100),
    'rented_percent' : math.floor(((total - avail) / total) * 100 ),
    'overdue_count': rental.objects.filter(status='Overdue').count(),
    'returned_count': rental.objects.filter(status='Returned').count(),
    'active_count': rental.objects.filter(status='Active').count(),
    'pending_count': rental.objects.filter(status='Pending').count(),
    'total': totals,
    'recent_activities': last_four,
    'recent_actcount': last_four.count(),
    'most_popular_equipment': most.order_by('available_quantity')[:4]
    
  }
  return render(request, 'apps/dashboard/index.html', data)