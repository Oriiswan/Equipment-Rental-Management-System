from django.shortcuts import render
from django.http import HttpResponse
from inventory.models import Equipments
import math
from booking.models import rental
def info(request):
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
    'available': avail,
    'rented': total - avail,
    'available_percent': math.floor((avail / total) * 100),
    'rented_percent' : math.floor(((total - avail) / total) * 100 ),
    'overdue_count': rental.objects.filter(status='Overdue').count(),
    'returned_count': rental.objects.filter(status='Returned').count(),
    'active_count': rental.objects.filter(status='Active').count(),
    'pending_count': rental.objects.filter(status='Pending').count(),
    
    
  }
  return render(request, 'apps/dashboard/index.html', data)