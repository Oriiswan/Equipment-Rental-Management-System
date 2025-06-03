from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Equipments
from django.contrib import messages
import math
from booking.models import rental
from django.db.models import Q
def equipment_list(request):
  equipments =Equipments.objects.all()
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
    'available': avail,
    'rented': total - avail,
    'available_percent': math.floor(((avail / total) * 100)),
    'rented_percent' : math.floor(((total - avail) / total) * 100 ) ,
    
    
  }
  return render(request, 'apps/equipment/list.html', data)

def add_equipment(request):
  try:
    if request.method == 'POST':
      name = request.POST.get('name')
      category = request.POST.get('category')
      rate = request.POST.get('rate')
      total_quantity = request.POST.get('quantity')
      available_quantity = request.POST.get('available-quantity')
      image = request.FILES.get('image')
      
      exists = Equipments.objects.filter(name=name).exists()
      if exists:
        messages.error(request, 'This product is already exists')
        return render(request, 'apps/equipment/Add-equipment.html')
      elif total_quantity < available_quantity:
        messages.error(request, 'This product is already exists')
        return render(request, 'apps/equipment/Add-equipment.html')
      else:
        Equipments.objects.create(
          name=name,
          category=category,
          daily_rate=rate,
          total_quantity=total_quantity,
          available_quantity=available_quantity,
          image=image
          )
        return redirect('/equipments/list')
    else:
      return render(request, 'apps/equipment/Add-equipment.html')
  except Exception as e:
    return HttpResponse(f'Error occurred during {e}')
  
def available_list(request):
  equipments =Equipments.objects.all()
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
    'available': avail,
    'rented': total - avail,
    'available_percent': math.floor((avail / total) * 100),
    'rented_percent' : math.floor(((total - avail) / total) * 100 ),
    
    
  }
  return render(request, 'apps/equipment/available-list.html', data)

def rented_list(request):
  equipments =Equipments.objects.all()
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
    'available': avail,
    'rented': total - avail,
    'available_percent': math.floor((avail / total) * 100),
    'rented_percent' : math.floor(((total - avail) / total) * 100 ),
    
    
  }
  return render(request, 'apps/equipment/rented.html', data)