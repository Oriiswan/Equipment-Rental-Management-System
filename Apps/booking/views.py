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
#
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
@login_required
def booking_list(request):
    # Update statuses before displaying list
    update_rental_statuses()
    
    # Rest of your existing booking_list code remains the same
    records = rental.objects.all()
    today = date.today()
    
    # Get search parameter
    search = request.POST.get('search') if request.method == 'POST' else request.GET.get('search', '')
    
    # Filter rentals that are not returned
    active_rentals = records.exclude(status='returned')
    
    # Apply search filter if search term exists
    if search:
        rentals_filtered = active_rentals.filter(
            Q(customer__firstname__icontains=search) | 
            Q(customer__lastname__icontains=search) | 
            Q(rental_id__icontains=search) | 
            Q(equipment__name__icontains=search)
        )
    else:
        rentals_filtered = active_rentals
    
    # Rest of your existing code...
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
        'overdue_count': rental.objects.filter(status='overdue').count(),
        'returned_count': rental.objects.filter(status='returned').count(),
        'active_count': rental.objects.filter(status='active').count(),
        'pending_count': rental.objects.filter(status='pending').count(),
        'total': total,
        'search': search,
        'paginator': paginator,
        'page_obj': rentals_page,
    }
    
    return render(request, 'apps/booking/list.html', data)
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
    
    if request.method == 'POST':
        
        rental_date_str = request.POST.get('rental_date')
        due_date_str = request.POST.get('due_date')
        rental_date = datetime.strptime(rental_date_str, "%Y-%m-%d").date()
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        customer_id = request.POST.get('customer')
        equipment_id = request.POST.get('equipment')
        equipment = Equipments.objects.get(pk=equipment_id)
        if due_date <=  rental_date:
            messages.error(request,'Due date must be after rental date')
            return render(request, 'apps/booking/edit_booking.html', {
            'customers':Customers.objects.all(),
            'equipments': Equipments.objects.all(),
            'booking': booking,
            'rental_id': f'RNT-00{booking.rental_id}'
        })
        booking.customer = Customers.objects.get(customer_id=customer_id)
        booking.equipment = Equipments.objects.get(equipment_id=equipment_id)
        booking.rental_date = datetime.strptime(rental_date_str, "%Y-%m-%d").date()
        booking.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        
        booking.save()
        if rental_date <= date.today() and equipment.available_quantity > 0:
            equipment.available_quantity -= 1
            equipment.save()
        return redirect('booking_list')
    else:
        
        return render(request, 'apps/booking/edit_booking.html', {
            'customers':Customers.objects.all(),
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
            now = date.today()
            customer_id = request.POST.get('customer')
            equipment_id = request.POST.get('equipment')
            equipment = Equipments.objects.get(pk=equipment_id)
            rental_date = datetime.strptime(request.POST['rental_date'], '%Y-%m-%d').date()
            due_date = datetime.strptime(request.POST['due_date'], '%Y-%m-%d').date()

            # Validate dates
            if rental_date > due_date:
                messages.error(request, "Due date must be after rental date")
                return redirect('add_booking')

            if equipment.available_quantity == 0:
                messages.error(request, "Equipment is out of stock")
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

            # Determine status based on dates
            if now > due_date:
                status = 'Overdue'
            elif now >= rental_date:
                status = 'Active'
            else:
                status = 'Upcoming'

            # Create rental record
            new_rental = rental.objects.create(
                customer_id=customer_id,
                equipment_id=equipment_id,
                rental_date=rental_date,
                due_date=due_date,
                notes=request.POST.get('notes', ''),
                rental_agreement=request.FILES.get('rental_agreement'),
                status=status  # Use the status we determined here
            )
           
            # Adjust equipment quantity only if the rental is starting now or earlier
            if now >= rental_date:
                equipment.available_quantity -= 1
                equipment.save()

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

@login_required
def mark_as_returned(request, rental_id):

    rental_obj = get_object_or_404(rental, pk=rental_id)
    now = datetime.now()
    
    if request.method == 'POST':
        rental_obj.status = 'Returned'
        rental_obj.return_date = timezone.now().date()  
        rental_obj.save()
        
        equipment = rental_obj.equipment
        equipment.available_quantity += 1
        equipment.save()
        
        messages.success(request, f'Equipment {equipment.name} has been returned successfully!')
        
        return redirect('booking_list')
    
    
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
        'total': sum(item.revenue or Decimal('0.00') for item in rental.objects.all()),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
        'search': search,
        'paginator': paginator,
        'page_obj': rentals_page,
    }
    return render(request, 'apps/booking/return.html', context)
@login_required
def mark_as_returned_active_list(request, rental_id):
    
    rentals = rental.objects.all()
    
    rental_obj = get_object_or_404(rental, pk=rental_id)
    now = datetime.now()
    if request.method == 'POST':
        
        rental_obj.status = 'Returned'
        rental_obj.return_date = timezone.now().date()  
        rental_obj.updated_at = rental_obj.return_date
        rental_obj.save()
       
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
        'total': sum(item.revenue or Decimal('0.00') for item in rentals),

        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    }
    return render(request, 'apps/booking/return-active.html', context)
@login_required
def mark_as_returned_overdue_list(request, rental_id):
    rentals = rental.objects.all()
    

    rental_obj = get_object_or_404(rental, pk=rental_id)
    now = datetime.now()
    if request.method == 'POST':
      
        rental_obj.status = 'Returned'
        rental_obj.return_date = timezone.now().date()  
        rental_obj.updated_at = rental_obj.return_date
        rental_obj.save()
        
       
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
        'total': sum(item.revenue or Decimal('0.00') for item in rentals),
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
    

