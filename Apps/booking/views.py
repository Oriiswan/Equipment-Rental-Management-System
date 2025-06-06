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

def booking_list(request):
    records = rental.objects.all()
    today = date.today()
    
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/list.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
    
def booking_list_newest(request):
    records = rental.objects.all().order_by('-rental_date')
    today = date.today()
    
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
    
def booking_list_oldest(request):
    records = rental.objects.all().order_by('rental_date')
    today = date.today()
    
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
    
def booking_list_today(request):
    
    today = date.today()
    records = rental.objects.filter(rental_date=today)
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
def active_list(request):
    records = rental.objects.all()
    
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/active.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'active_list': rental.objects.filter(status='Active'),
      'total': total
    })
def active_list_newest(request):
    records = rental.objects.all().order_by('-rental_date')
    
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/newest/active.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'active_list': rental.objects.filter(status='Active'),
      'total': total
    })
def active_list_oldest(request):
    records = rental.objects.all().order_by('rental_date')
    
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/oldest/active.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'active_list': rental.objects.filter(status='Active'),
      'total': total
    })

def active_list_today(request):
    records = rental.objects.filter(rental_date = date.today())
    
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/today/active.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'active_list': rental.objects.filter(status='Active'),
      'total': total
    })
def pending_list(request):
    records = rental.objects.all()
    
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/pending.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'pending_list': rental.objects.filter(status='Pending'),
      'total': total
      
    })
def pending_list_newest(request):
    records = rental.objects.all().order_by('-rental_date')
    
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/newest/pending.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'pending_list': rental.objects.filter(status='Pending'),
      'total': total
      
    })
def pending_list_oldest(request):
    records = rental.objects.all().order_by('rental_date')
    
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/oldest/pending.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'pending_list': rental.objects.filter(status='Pending'),
      'total': total
      
    })
def pending_list_today(request):
    records = rental.objects.filter(rental_date=date.today())
    
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/today/pending.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'pending_list': rental.objects.filter(status='Pending'),
      'total': total
      
    })
def overdue_list(request):
    records = rental.objects.all()
    
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/overdue.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'overdue_list': rental.objects.filter(status='Overdue'),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total,
    })
def overdue_list_newest(request):
    records = rental.objects.all().order_by('-rental_date')
    
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/newest/overdue.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'overdue_list': rental.objects.filter(status='Overdue'),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total,
    })

def overdue_list_oldest(request):
    records = rental.objects.all().order_by('rental_date')
    
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/oldest/overdue.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'overdue_list': rental.objects.filter(status='Overdue'),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total,
    })

def overdue_list_today(request):
    records = rental.objects.filter(rental_date=date.today())
    
    total = sum(item.revenue or Decimal('0.00') for item in records)
    return render(request, 'apps/booking/today/overdue.html',{
      'rentals': records,
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'overdue_list': rental.objects.filter(status='Overdue'),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total,
    })



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

            if rental_date > due_date:
                messages.error(request, "Due date must be after rental date")
                return redirect('add_booking')

            if equipment.available_quantity == 0:
                messages.error(request, "Equipment is out of stock")
                return redirect('add_booking')

            availability_info = equipment.get_availability_details(rental_date, due_date,equipment)
            if not availability_info['is_available']:
                messages.error(
                    request,
                    f"Not available for all dates. Unavailable: {availability_info['unavailable_dates']}"
                )
                return redirect('add_booking')

            if availability_info['max_available'] < 1:
                messages.error(
                    request,
                    "No available units for the selected period."
                )
                return redirect('add_booking')



            # Create rental record
            rental.objects.create(
                customer_id=customer_id,
                equipment_id=equipment_id,
                rental_date=rental_date,
                due_date=due_date,
                notes=request.POST.get('notes', ''),
                rental_agreement=request.FILES.get('rental_agreement'),
                status=determine_status(rental_date, due_date)
            )

            # Adjust equipment quantity only if the rental is starting now or earlier
            if now >= rental_date:
                equipment.available_quantity -= 1
                equipment.save()

            # Show updated list with success message
            records = rental.objects.all()
            total = sum(item.revenue or Decimal('0.00') for item in records)

            messages.success(request, "Booking created successfully!")
            return render(request, 'apps/booking/list.html', {
                'rentals': records,
                'equipments': Equipments.objects.all(),
                'customers': Customers.objects.all(),
                'overdue_count': rental.objects.filter(status='Overdue').count(),
                'returned_count': rental.objects.filter(status='Returned').count(),
                'active_count': rental.objects.filter(status='Active').count(),
                'total': total
            })

        except KeyError as e:
            messages.error(request, f"Missing required field: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error creating booking: {str(e)}")

    # GET request or failed POST
    equipments = Equipments.objects.all()
    customers = Customers.objects.all()
    return render(request, 'apps/booking/create.html', {
        'equipments': equipments,
        'customers': customers
    })

def determine_status(rental_date, due_date):
    today = date.today()
    if today >= rental_date and today <= due_date:
        return 'Active'
    elif today > due_date:
        return 'Overdue'
    return 'Pending'

def mark_as_returned(request, rental_id):
    # Get the specific rental object
    rentals = rental.objects.all()
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
    return render(request, 'apps/booking/return.html', context)


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

def return_list(request):
    rentals = rental.objects.all()
    
    return render(request, 'apps/booking/return_list.html', {
        'rentals': rentals,
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': sum(item.revenue or Decimal('0.00') for item in rentals),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    })
    
def return_list_today(request):
    rentals = rental.objects.filter(rental_date = date.today())
    
    return render(request, 'apps/booking/today/returned.html', {
        'rentals': rentals,
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': sum(item.revenue or Decimal('0.00') for item in rentals),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    })
    

def return_list_newest(request):
    rentals = rental.objects.all().order_by('-rental_date')

    
    return render(request, 'apps/booking/newest/returned.html', {
        'rentals': rentals,
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': sum(item.revenue or Decimal('0.00') for item in rentals),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    })
    

def return_list_oldest(request):
    rentals = rental.objects.all().order_by('rental_date')
    
    return render(request, 'apps/booking/oldest/returned.html', {
        'rentals':rentals,
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': sum(item.revenue or Decimal('0.00') for item in rentals),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    })
    
