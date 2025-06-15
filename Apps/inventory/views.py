from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Equipments
from django.contrib import messages
import math
from booking.models import rental
from django.db.models import Q,F
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def equipment_list(request):
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Base queryset
    equipments = Equipments.objects.all()
    
    # Apply search filter
    if search_query:
        equipments = equipments.filter(
            Q(name__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(equipment_id__icontains=search_query)
        )
    
    # Calculate stats for all equipment (not filtered)
    all_equipments = Equipments.objects.all()
    equipments_count = all_equipments.count()
    categories = all_equipments.values_list('category').distinct()
    unique = sorted(set(categories))
    
    total = 0
    avail = 0
    for equipment in all_equipments:
        total += equipment.total_quantity
        avail += equipment.available_quantity 
    
    # Calculate maintenance count for the dashboard
    maintenance_count = all_equipments.filter(condition__iexact='Poor').count()
    
    # Pagination
    paginator = Paginator(equipments, 12)  # Show 12 equipment per page
    page = request.GET.get('page')
    
    try:
        equipments = paginator.page(page)  # Changed variable name to match template
    except PageNotAnInteger:
        equipments = paginator.page(1)
    except EmptyPage:
        equipments = paginator.page(paginator.num_pages)
    
    data = {
        'count': equipments_count,
        'available': avail,
        'equipments': equipments,  # This now contains paginated results
        'category': len(unique),
        'rented': total - avail,
        'available_percent': math.floor(((avail / total) * 100)) if total > 0 else 0,
        'rented_percent': math.floor(((total - avail) / total) * 100) if total > 0 else 0,
        'maintenance_count': maintenance_count,
        'search_query': search_query,  # Pass search query to template
        'total_results': equipments.paginator.count,  # Total filtered results
    }
    
    return render(request, 'apps/equipment/list.html', data)

@login_required
def repair_equipment(request, equipment_id):
  # If not POST, redirect back to maintenance page
    # Get all equipment for stats
    all_equipments = Equipments.objects.all()
    equipments_count = all_equipments.count()
    categories = all_equipments.values_list('category').distinct()
    unique = sorted(set(categories))
    
    
    # Calculate totals
    total = 0
    avail = 0
    for equipment in all_equipments:
        total += equipment.total_quantity
        avail += equipment.available_quantity 
    
    # Get equipment by condition (only poor and excellent)
    poor_equipments = all_equipments.filter(condition__iexact='Poor')
    excellent_equipments = all_equipments.filter(condition__iexact='excellent')
    
    # Add latest return notes for poor equipment
    for equipment in poor_equipments:
        try:
            from booking.models import rental
            latest_rental = rental.objects.filter(
                equipment=equipment,
                condition_on_return__iexact='Poor',
                return_notes__isnull=False
            ).exclude(return_notes='').order_by('-return_date').first()
            
            equipment.latest_return_notes = latest_rental.return_notes if latest_rental else None
        except:
            equipment.latest_return_notes = None
    
    # Calculate condition counts
    maintenance_count = poor_equipments.count()
    excellent_count = excellent_equipments.count()
    
    equipment = get_object_or_404(Equipments, equipment_id=equipment_id)
    
    if request.method == 'POST':
        equipment.condition = 'excellent'
        equipment.save()
    
        
        messages.success(
            request, 
            f'Equipment "{equipment.name}" has been successfully repaired and marked as excellent condition!'
        )
        data = {
        'count': equipments_count,
        'available': avail,
        'category': len(unique),
        'rented': total - avail,
        'available_percent': math.floor(((avail / total) * 100)) if total > 0 else 0,
        'rented_percent': math.floor(((total - avail) / total) * 100) if total > 0 else 0,
        
        # Maintenance specific data
        'poor_equipments': poor_equipments,
        'maintenance_count': maintenance_count,
        'excellent_count': excellent_count,
    }
    
        return render(request, 'apps/equipment/maintenance.html', data)
    
    
    data = {
        'count': equipments_count,
        'available': avail,
        'category': len(unique),
        'rented': total - avail,
        'available_percent': math.floor(((avail / total) * 100)) if total > 0 else 0,
        'rented_percent': math.floor(((total - avail) / total) * 100) if total > 0 else 0,
        
        # Maintenance specific data
        'poor_equipments': poor_equipments,
        'maintenance_count': maintenance_count,
        'excellent_count': excellent_count,
    }
    
    return render(request, 'apps/equipment/maintenance_repaired.html', data)

@login_required
def equipment_maintenance_list(request):
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Get all equipment for stats
    all_equipments = Equipments.objects.all()
    equipments_count = all_equipments.count()
    categories = all_equipments.values_list('category').distinct()
    unique = sorted(set(categories))
    
    # Calculate totals
    total = 0
    avail = 0
    for equipment in all_equipments:
        total += equipment.total_quantity
        avail += equipment.available_quantity 
    
    # Get equipment by condition (only poor)
    poor_equipments = all_equipments.filter(condition__iexact='Poor')
    
    # Apply search filter
    if search_query:
        poor_equipments = poor_equipments.filter(
            Q(name__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(equipment_id__icontains=search_query)
        )
    
    # Add latest return notes for poor equipment
    for equipment in poor_equipments:
        try:
            from booking.models import rental
            latest_rental = rental.objects.filter(
                equipment=equipment,
                condition_on_return__iexact='Poor',
                return_notes__isnull=False
            ).exclude(return_notes='').order_by('-return_date').first()
            
            equipment.latest_return_notes = latest_rental.return_notes if latest_rental else None
        except:
            equipment.latest_return_notes = None
    
    # Calculate condition counts
    maintenance_count = all_equipments.filter(condition__iexact='Poor').count()
    excellent_count = sum(r.total_quantity for r in all_equipments) - maintenance_count
    
    # Pagination
    paginator = Paginator(poor_equipments, 12)
    page = request.GET.get('page')
    
    try:
        poor_equipments = paginator.page(page)  # Changed variable name to match template
    except PageNotAnInteger:
        poor_equipments = paginator.page(1)
    except EmptyPage:
        poor_equipments = paginator.page(paginator.num_pages)
    
    data = {
        'count': equipments_count,
        'available': excellent_count - (total - avail),
        'category': len(unique),
        'rented': total - avail,
        'available_percent': math.floor(((avail / total) * 100)) if total > 0 else 0,
        'rented_percent': math.floor(((total - avail) / total) * 100) if total > 0 else 0,
        
        # Maintenance specific data
        'poor_equipments': poor_equipments,  # This now contains paginated results
        'maintenance_count': maintenance_count,
        'excellent_count': excellent_count,
        'search_query': search_query,
        'total_results': poor_equipments.paginator.count,
    }
    
    return render(request, 'apps/equipment/maintenance.html', data)


@login_required
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
      elif total_quantity < available_quantity  or total_quantity > available_quantity:
        messages.error(request, 'The quantity must be both equal')
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

@login_required
def available_list(request):
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Base queryset - only available equipment
    equipments = Equipments.objects.filter(available_quantity__gt=0)
    
    # Apply search filter
    if search_query:
        equipments = equipments.filter(
            Q(name__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(equipment_id__icontains=search_query)
        )
    
    # Calculate stats for all equipment
    all_equipments = Equipments.objects.all()
    equipments_count = all_equipments.count()
    categories = all_equipments.values_list('category').distinct()
    unique = sorted(set(categories))
    total = 0
    avail = 0
    
    for equipment in all_equipments:
        total += equipment.total_quantity
        avail += equipment.available_quantity 
    
    # Calculate maintenance count
    maintenance_count = all_equipments.filter(condition__iexact='poor').count()
    
    # Pagination
    paginator = Paginator(equipments, 12)
    page = request.GET.get('page')
    
    try:
        equipments = paginator.page(page)  # Changed variable name to match template
    except PageNotAnInteger:
        equipments = paginator.page(1)
    except EmptyPage:
        equipments = paginator.page(paginator.num_pages)
    
    data = {
        'count': equipments_count,
        'equipments': equipments,  # This now contains paginated results
        'category': len(unique),
        'available': avail,
        'rented': total - avail,
        'available_percent': math.floor((avail / total) * 100) if total > 0 else 0,
        'rented_percent': math.floor(((total - avail) / total) * 100) if total > 0 else 0,
        'maintenance_count': maintenance_count,
        'search_query': search_query,
        'total_results': equipments.paginator.count,
    }
    return render(request, 'apps/equipment/available-list.html', data)

@login_required
def rented_list(request):
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Base queryset - only rented equipment (where available < total)
    equipments = Equipments.objects.filter(available_quantity__lt=F('total_quantity'))
    
    # Apply search filter
    if search_query:
        equipments = equipments.filter(
            Q(name__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(equipment_id__icontains=search_query)
        )
    
    # Calculate stats for all equipment
    all_equipments = Equipments.objects.all()
    equipments_count = all_equipments.count()
    categories = all_equipments.values_list('category').distinct()
    unique = sorted(set(categories))
    total = 0
    avail = 0
    
    for equipment in all_equipments:
        total += equipment.total_quantity
        avail += equipment.available_quantity 
    
    # Calculate maintenance count
    maintenance_count = all_equipments.filter(condition__iexact='poor').count()
    
    # Pagination
    paginator = Paginator(equipments, 12)
    page = request.GET.get('page')
    
    try:
        equipments = paginator.page(page)  # Changed variable name to match template
    except PageNotAnInteger:
        equipments = paginator.page(1)
    except EmptyPage:
        equipments = paginator.page(paginator.num_pages)
    
    data = {
        'count': equipments_count,
        'equipments': equipments,  # This now contains paginated results
        'category': len(unique),
        'available': avail,
        'rented': total - avail,
        'available_percent': math.floor((avail / total) * 100) if total > 0 else 0,
        'rented_percent': math.floor(((total - avail) / total) * 100) if total > 0 else 0,
        'maintenance_count': maintenance_count,
        'search_query': search_query,
        'total_results': equipments.paginator.count,
    }
    return render(request, 'apps/equipment/rented.html', data)

@login_required
def edit_equipment(request, equipment_id):
  equipment = Equipments.objects.get(pk=equipment_id)
  name = request.POST.get('name')
  category = request.POST.get('category')
  rate = request.POST.get('rate')
  quantity = request.POST.get('quantity')
  image = request.FILES.get('image')
  
    
  if request.method == 'POST':
    
    equipment.name = name
    equipment.category = category
    equipment.daily_rate = rate
    if int(quantity) > equipment.total_quantity:
      equipment.available_quantity = equipment.available_quantity + (int(quantity) - equipment.total_quantity)
    elif int(quantity) < equipment.total_quantity:
      equipment.available_quantity = equipment.available_quantity -  (equipment.total_quantity - int(quantity))
    equipment.total_quantity = int(quantity)
    if image:
      equipment.image = image
    equipment.save()
    return redirect('equipment_list')
  return render (request, 'apps/equipment/edit.html', {
    'name': equipment.name,
    'category': equipment.category,
    'daily_rate': equipment.daily_rate,
    'quantity': equipment.total_quantity,
    'available_quantity': equipment.available_quantity,
  })
@login_required
def delete_equipment(request,equipment_id):
    equipments =Equipments.objects.all()
    equipments_count = Equipments.objects.count()
    categories = Equipments.objects.values_list('category').distinct()
    unique = sorted(set(categories))
    total = 0
    avail = 0
    
    if request.method == 'POST':
      equip  = Equipments.objects.get(pk = equipment_id)
      equip.delete()
   
      return redirect('equipment_list')
    for equipment in equipments:
      total += equipment.total_quantity
      avail += equipment.available_quantity 
    data = {
      'count': equipments_count,
      'equipment': Equipments.objects.get(pk = equipment_id),
      'equipments': equipments, 
      'category': len(unique),
      'available': avail,
      'rented': total - avail,
      'available_percent': math.floor(((avail / total) * 100)),
      'rented_percent' : math.floor(((total - avail) / total) * 100 ) ,
      
      
    }
    return render(request, 'apps/equipment/delete.html', data)
@login_required
def delete_avail_equipment(request,equipment_id):
    equipments =Equipments.objects.all()
    equipments_count = Equipments.objects.count()
    categories = Equipments.objects.values_list('category').distinct()
    unique = sorted(set(categories))
    total = 0
    avail = 0
    
    if request.method == 'POST':
      equip  = Equipments.objects.get(pk = equipment_id)
      equip.delete()
      
      return redirect('available_list')
    for equipment in equipments:
      total += equipment.total_quantity
      avail += equipment.available_quantity 
    data = {
      'count': equipments_count,
      'equipment': Equipments.objects.get(pk = equipment_id),
      'equipments': equipments, 
      'category': len(unique),
      'available': avail,
      'rented': total - avail,
      'available_percent': math.floor(((avail / total) * 100)),
      'rented_percent' : math.floor(((total - avail) / total) * 100 ) ,
      
      
    }
    return render(request, 'apps/equipment/delete-available.html', data)