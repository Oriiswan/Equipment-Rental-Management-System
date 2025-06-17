from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from inventory.models import Equipments
from customers.models import Customers
from .models import rental
from datetime import date,datetime
from django.db import connection
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from utils.zapier import notify_overdue_booking, notify_today_booking, notify_reserved_booking, notify_duedate_booking
from datetime import date
from django.utils import timezone

def update_rental_statuses():
    """Update all rental statuses based on current date"""
    today = timezone.now().date()  # Using timezone-aware date
    rentals_to_update = rental.objects.exclude(status__in=['Returned', 'Cancelled'])
    updated_count = 0
    
    for rental_obj in rentals_to_update:
        old_status = rental_obj.status
        new_status = old_status
        
        # Assuming rental_date is already a DateField (should be in your model)
        rental_date = rental_obj.rental_date
        
        # Determine new status based on dates
        if rental_obj.return_date:
            new_status = 'Returned'
        elif today > rental_obj.due_date:
            new_status = 'Overdue'
        elif today < rental_date:
            new_status = 'Pending'
        elif today == rental_date and not rental_obj.is_pickup:
            new_status = 'Pickup'
        elif today >= rental_date and rental_obj.is_pickup and today <= rental_obj.due_date:
            new_status = 'Active'
        elif today > rental_date and not rental_obj.is_pickup:
          
            new_status = 'Cancelled'
        
        
            
   
        if old_status.lower() != new_status.lower():
            rental_obj.status = new_status
            rental_obj.save(update_fields=['status'])
            updated_count += 1
    
    return updated_count
@login_required
@login_required
def booking_list(request):

    update_rental_statuses()
    

    records = rental.objects.all()
    today = date.today()
    

    search = request.POST.get('search') if request.method == 'POST' else request.GET.get('search', '')
   
    active_rentals = records.exclude(status='Returned')
    

    if search:
        rentals_filtered = active_rentals.filter(
            Q(customer__firstname__icontains=search) | 
            Q(customer__lastname__icontains=search) | 
            Q(rental_id__icontains=search) | 
            Q(equipment__name__icontains=search)
        )
    else:
        rentals_filtered = active_rentals
    

    items_per_page = 10  
    paginator = Paginator(rentals_filtered, items_per_page)
    
    page = request.GET.get('page', 1)
    try:
        rentals_page = paginator.page(page)
    except PageNotAnInteger:
        rentals_page = paginator.page(1)
    except EmptyPage:
        rentals_page = paginator.page(paginator.num_pages)

    total = sum(item.revenue or Decimal('0.00') for item in records if item.revenue)
    
    data = {
        'rentals': rentals_page,  
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'pending_count': rental.objects.filter(status='Pending').count(),
        'total': total,
        'search': search,
        'paginator': paginator,
        'page_obj': rentals_page,
    }
    
    return render(request, 'apps/booking/list.html', data)

@login_required
def pickup_confirmation(request, rental_id):
    record = get_object_or_404(rental, pk=rental_id)
    
    if request.method == 'POST':
        # Mark as picked up
        record.status = 'Active'
        record.is_pickup = True
        equipment = record.equipment
        equipment.available_quantity -= 1
        equipment.save()
        record.save()
        
        # If this is the first time being picked up, reduce available quantity
        if record.status == 'Pickup':
            equipment = record.equipment
            equipment.available_quantity = max(0, equipment.available_quantity - 1)
            equipment.save(update_fields=['available_quantity'])
        
        messages.success(request, f'Rental #{rental_id} has been confirmed as picked up!')
        return redirect('booking_list')
    
    # Context for GET request
    data = {
        'booking': record,
        'rentals': rental.objects.exclude(status='Returned'),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'pending_count': rental.objects.filter(status='Pending').count(),
        'total': sum(item.revenue or Decimal('0.00') for item in rental.objects.all() if item.revenue),
    }
    
    return render(request, 'apps/booking/pickup_confirmation.html', data)

# Add this utility function to sync all equipment quantities
def sync_all_equipment_quantities():
    """Sync available_quantity for all equipment based on active rentals"""
    for equipment in Equipments.objects.all():
        equipment.sync_available_quantity()
    print("All equipment quantities synced successfully!")
def booking_list_newest(request):
    records = rental.objects.all().order_by('-rental_date')
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/newest/all.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/newest/all.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def booking_list_oldest(request):
    records = rental.objects.all().order_by('rental_date')
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/oldest/all.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/oldest/all.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def booking_list_today(request):
    
    today = date.today()
    records = rental.objects.filter(rental_date=today)
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/today/all.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/today/all.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def edit_booking(request, rental_id):
    booking = rental.objects.get(rental_id=rental_id)
    old_equipment = booking.equipment
    old_status = booking.status
    
    if request.method == 'POST':
        rental_date_str = request.POST.get('rental_date')
        due_date_str = request.POST.get('due_date')
        rental_date = datetime.strptime(rental_date_str, "%Y-%m-%d").date()
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        customer_id = request.POST.get('customer')
        equipment_id = request.POST.get('equipment')
        new_equipment = Equipments.objects.get(pk=equipment_id)
        
        if due_date <= rental_date:
            messages.error(request, 'Due date must be after rental date')
            return render(request, 'apps/booking/edit_booking.html', {
                'customers': Customers.objects.all(),
                'equipments': Equipments.objects.all(),
                'booking': booking,
                'rental_id': f'RNT-00{booking.rental_id}'
            })
        
        # If equipment changed and booking is active/pickup/overdue, check availability
        if old_equipment != new_equipment and old_status in ['Active', 'Pickup', 'Overdue']:
            new_equipment.sync_available_quantity()
            if new_equipment.available_quantity <= 0:
                messages.error(request, 'Selected equipment is not available')
                return render(request, 'apps/booking/edit_booking.html', {
                    'customers': Customers.objects.all(),
                    'equipments': Equipments.objects.all(),
                    'booking': booking,
                    'rental_id': f'RNT-00{booking.rental_id}'
                })
            
            # Return quantity to old equipment
            old_equipment.available_quantity += 1
            old_equipment.save(update_fields=['available_quantity'])
            
            # Take quantity from new equipment
            new_equipment.available_quantity -= 1
            new_equipment.save(update_fields=['available_quantity'])
        
        # Update booking
        booking.customer = Customers.objects.get(customer_id=customer_id)
        booking.equipment = new_equipment
        booking.rental_date = rental_date
        booking.due_date = due_date
        
        booking.save()
        
        messages.success(request, 'Booking updated successfully!')
        return redirect('booking_list')
    else:
        return render(request, 'apps/booking/edit_booking.html', {
            'customers': Customers.objects.all(),
            'equipments': Equipments.objects.all(),
            'booking': booking,
            'rental_id': f'RNT-00{booking.rental_id}'
        })
@login_required
def active_list(request):
    records = rental.objects.all()
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/active.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/active.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def active_list_newest(request):
    records = rental.objects.all().order_by('-rental_date')
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/newest/active.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking//newest/active.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def active_list_oldest(request):
    records = rental.objects.all().order_by('rental_date')
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/oldest/active.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking//oldest/active.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def active_list_today(request):
    records = rental.objects.filter(rental_date = date.today())
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/today/active.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking//today/active.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def pending_list(request):
    records = rental.objects.all()
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/pending.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/pending.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def pending_list_newest(request):
    records = rental.objects.all().order_by('-rental_date')
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/newest/pending.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/newest/pending.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def pending_list_oldest(request):
    records = rental.objects.all().order_by('rental_date')
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/oldest/pending.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/oldest/pending.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def pending_list_today(request):
    records = rental.objects.filter(rental_date=date.today())
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/today/pending.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/today/pending.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def overdue_list(request):
    records = rental.objects.all()
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/overdue.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/overdue.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def overdue_list_newest(request):
    records = rental.objects.all().order_by('-rental_date')
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/newest/overdue.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/newest/overdue.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def overdue_list_oldest(request):
    records = rental.objects.all().order_by('rental_date')
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/oldest/overdue.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/oldest/overdue.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def overdue_list_today(request):
    records = rental.objects.filter(rental_date=date.today())
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/today/overdue.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/today/overdue.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })


@login_required
def delete_booking(request,rental_id):
    rentals = rental.objects.all()
    rental_obj = get_object_or_404(rental, pk=rental_id)
    if request.method == 'POST':
        record = rental.objects.filter(rental_id=rental_id)
        record.delete()
        return redirect('booking_list')
    context = {
        'booking': rental_obj,
        'rentals': rental.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': sum(item.revenue or Decimal('0.00') for item in rentals),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    }
    return render(request, 'apps/booking/delete_booking.html', context)
@login_required
def delete_pending_list(request,rental_id):
    rentals = rental.objects.all()
    rental_obj = get_object_or_404(rental, pk=rental_id)
    if request.method == 'POST':
        record = rental.objects.filter(rental_id=rental_id)
        record.delete()
        return redirect('pending_list')
    context = {
        'booking': rental_obj,
        'rentals': rental.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': sum(item.revenue or Decimal('0.00') for item in rentals),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    }
    return render(request, 'apps/booking/delete_pending.html', context)
@login_required
def delete_returned_list(request,rental_id):
    rentals = rental.objects.all()
    rental_obj = get_object_or_404(rental, pk=rental_id)
    if request.method == 'POST':
        record = rental.objects.filter(rental_id=rental_id)
        record.delete()
        return redirect('return_list')
    context = {
        'booking': rental_obj,
        'rentals': rental.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': sum(item.revenue or Decimal('0.00') for item in rentals),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    }
    return render(request, 'apps/booking/delete_returned.html', context)

@login_required
def add_booking(request):
    if request.method == 'POST':
        try:
            # Get form data
            now = timezone.now().date()
            customer_id = request.POST.get('customer')
            equipment_id = request.POST.get('equipment')
            equipment = Equipments.objects.get(pk=equipment_id)
            rental_date = datetime.strptime(request.POST['rental_date'], '%Y-%m-%d').date()
            due_date = datetime.strptime(request.POST['due_date'], '%Y-%m-%d').date()

            # Validate dates
            if rental_date > due_date:
                messages.error(request, "Due date must be after rental date")
                return redirect('add_booking')

           

            # Now call with only the required parameters (equipment is self)
            availability_info = equipment.get_availability_details(rental_date, due_date)
            
            if not availability_info['is_available']:
                unavailable_dates_str = ', '.join([d.strftime('%Y-%m-%d') for d in availability_info['unavailable_dates']])
                messages.error(
                    request,
                    f"Not available for all dates. Unavailable dates: {unavailable_dates_str}"
                )
                return redirect('add_booking')

            if availability_info['max_available'] < 1:
                messages.error(
                    request,
                    "No available units for the selected period."
                )
                return redirect('add_booking')
            pickup = False
            # Determine status based on dates
            if now > due_date:
                status = 'Overdue'
                
            elif now > rental_date:
                status = 'Active'
                pickup = True
            elif now == rental_date:
                status = 'Pickup'
            else:
                status = 'Pending'

            # Create rental record
            new_rental = rental.objects.create(
                is_pickup = pickup,
                customer_id=customer_id,
                equipment_id=equipment_id,
                rental_date=rental_date,
                due_date=due_date,
                notes=request.POST.get('notes', ''),
                rental_agreement=request.FILES.get('rental_agreement'),
                status=status  # Use the status we determined here
            )
            
            if status == 'Overdue':
                notify_overdue_booking(new_rental)
            elif status == 'Active':
                equipment.available_quantity -= 1
                equipment.save()
            elif status == 'Pickup':
                notify_today_booking(new_rental)
            else:  
                notify_reserved_booking(new_rental)

            

            messages.success(request, "Booking created successfully!")
            return redirect('booking_list')

        except Equipments.DoesNotExist:
            messages.error(request, "Selected equipment does not exist")
        except ValueError as e:
            messages.error(request, f"Invalid date format: {str(e)}")
        except KeyError as e:
            messages.error(request, f"Missing required field: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error creating booking: {str(e)}")
            import traceback
            print(f"Full error trace: {traceback.format_exc()}")

    # GET request or failed POST
    equipments = Equipments.objects.all()
    customers = Customers.objects.all()
    return render(request, 'apps/booking/create.html', {
        'equipments': equipments,
        'customers': customers
    })

@login_required
def determine_status(rental_date, due_date):
   
    today = date.today()
    
    if rental_date > today:
        return 'Pending'
    elif rental_date <= today <= due_date:
        return 'Active'
    elif today > due_date:
        return 'Overdue'
    else:
        return 'Pending'

# Updated Django View

@login_required
def mark_as_returned(request, rental_id):
    rental_obj = get_object_or_404(rental, pk=rental_id)
    
    if request.method == 'POST':
        # Get condition data from form
        condition_rating = request.POST.get('condition')
        
        # Validate that condition is selected
        if not condition_rating:
            messages.error(request, 'Please select the equipment condition before confirming the return.')
            return render(request, 'apps/booking/return.html', {
                'booking': rental_obj,
                'form_errors': True
            })
        
        # Update rental record
        rental_obj.status = 'Returned'
        rental_obj.return_date = timezone.now().date()
        rental_obj.save()
        
        # Return equipment to available quantity
        equipment = rental_obj.equipment
        equipment.available_quantity += 1
        
        # Update equipment condition if needed
        condition_hierarchy = {'Excellent': 4, 'Good': 3, 'fair': 2, 'Poor': 1}
        current_condition_score = condition_hierarchy.get(equipment.condition.lower(), 4)
        return_condition_score = condition_hierarchy.get(condition_rating, 4)
        
        if return_condition_score < current_condition_score:
            equipment.condition = condition_rating.title()
        
        equipment.save()
        
        messages.success(request, f'Equipment {equipment.name} has been returned successfully with condition: {condition_rating.title()}!')
        return redirect('booking_list')
    
    # GET request - show return form
    search = request.GET.get('search', '')
    rentals = rental.objects.exclude(status='Returned')
    
    if search:
        rentals_filtered = rentals.filter(
            Q(customer__firstname__icontains=search) | 
            Q(customer__lastname__icontains=search) | 
            Q(rental_id__icontains=search) | 
            Q(equipment__name__icontains=search)
        )
    else:
        rentals_filtered = rentals
    
    items_per_page = 10
    paginator = Paginator(rentals_filtered, items_per_page)
    
    page = request.GET.get('page', 1)
    try:
        rentals_page = paginator.page(page)
    except PageNotAnInteger:
        rentals_page = paginator.page(1)
    except EmptyPage:
        rentals_page = paginator.page(paginator.num_pages)

    context = {
        'booking': rental_obj,
        'rentals': rentals_page, 
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': sum(item.revenue or Decimal('0.00') for item in rental.objects.all() if item.revenue),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'search': search,
        'paginator': paginator,
        'page_obj': rentals_page,
    }
    return render(request, 'apps/booking/return.html', context)

@login_required
def mark_as_returned_active_list(request, rental_id):
    rental_obj = get_object_or_404(rental, pk=rental_id)
    
    if request.method == 'POST':
        rental_obj.status = 'Returned'
        rental_obj.return_date = timezone.now().date()  
        rental_obj.updated_at = timezone.now()
        rental_obj.save()
        
        # Return equipment to available quantity
        equipment = rental_obj.equipment
        equipment.available_quantity += 1
        equipment.save()
        
        messages.success(request, f'Equipment {equipment.name} has been returned successfully!')
        return redirect('active_list')

    context = {
        'booking': rental_obj,
        'rentals': rental.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': sum(item.revenue or Decimal('0.00') for item in rental.objects.all() if item.revenue),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    }
    return render(request, 'apps/booking/return-active.html', context)

@login_required
def mark_as_returned_overdue_list(request, rental_id):
    rental_obj = get_object_or_404(rental, pk=rental_id)
    
    if request.method == 'POST':
        rental_obj.status = 'Returned'
        rental_obj.return_date = timezone.now().date()  
        rental_obj.updated_at = timezone.now()
        rental_obj.save()
        
        # Return equipment to available quantity
        equipment = rental_obj.equipment
        equipment.available_quantity += 1
        equipment.save()
        
        messages.success(request, f'Equipment {equipment.name} has been returned successfully!')
        return redirect('overdue_list')

    context = {
        'booking': rental_obj,
        'rentals': rental.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': sum(item.revenue or Decimal('0.00') for item in rental.objects.all() if item.revenue),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    }
    return render(request, 'apps/booking/return-overdue.html', context)
@login_required
def return_list(request):
    records = rental.objects.all()
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in records)
        return render(request, 'apps/booking/return_list.html',{
        'rentals': records.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/return_list.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def return_list_today(request):
    rentals = rental.objects.filter(return_date = date.today())
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in rentals)
        return render(request, 'apps/booking/today/returned.html',{
        'rentals': rentals.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in rentals)
    return render(request, 'apps/booking/today/returned.html',{
      'rentals': rentals,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
    
    
@login_required
def return_list_newest(request):
    rentals = rental.objects.all().order_by('-rental_date')

    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in rentals)
        return render(request, 'apps/booking/newest/returned.html',{
        'rentals': rentals.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in rentals)
    return render(request, 'apps/booking/newest/returned.html',{
      'rentals': rentals,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
@login_required
def return_list_oldest(request):
    rentals = rental.objects.all().order_by('rental_date')
    
    if request.method == 'POST':
        search = request.POST.get('search')
        total = sum(item.revenue or Decimal('0.00') for item in rentals)
        return render(request, 'apps/booking/oldest/returned.html',{
        'rentals': rentals.filter(Q(customer__firstname__icontains=search) | Q(customer__lastname__icontains=search) | Q(rental_id__icontains=search) | Q(equipment__name__contains=search)),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': total
        })
    total = sum(item.revenue or Decimal('0.00') for item in rentals)
    return render(request, 'apps/booking/oldest/returned.html',{
      'rentals': rentals,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
    

