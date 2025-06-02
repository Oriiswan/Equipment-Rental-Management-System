from django.shortcuts import render
from django.http import HttpResponse
from inventory.models import Equipments
import math
from booking.models import rental
from django.db.models import Sum
def info(request):
  last_four = rental.objects.order_by('-created_at', '-updated_at')[:5]
  records = rental.objects.all()
  totals = sum(item.total_amount for item in records)
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
    'total': totals,
    'recent_activities': last_four,
    
  }
  return render(request, 'apps/dashboard/index.html', data)