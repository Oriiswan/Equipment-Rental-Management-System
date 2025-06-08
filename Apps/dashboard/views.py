from django.shortcuts import render
from django.http import HttpResponse
from decimal import Decimal
from inventory.models import Equipments
import math
from booking.models import rental
from django.db.models import Sum
from django.db.models import F,Q

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