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
def booking_list(request):
    records = rental.objects.all()
    today = date.today()
    
    total = sum(item.total_amount for item in records)
    return render(request, 'apps/booking/list.html',{
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
        customer_id = request.POST.get('customer')
        equipment_id = request.POST.get('equipment')
        
        booking.customer = Customers.objects.get(customer_id=customer_id)
        booking.equipment = Equipments.objects.get(equipment_id=equipment_id)
        booking.rental_date = datetime.strptime(rental_date_str, "%Y-%m-%d").date()
        booking.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        booking.save()
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
    
    total = sum(item.total_amount for item in records)
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
def pending_list(request):
    records = rental.objects.all()
    
    total = sum(item.total_amount for item in records)
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
def overdue_list(request):
    records = rental.objects.all()
    
    total = sum(item.total_amount for item in records)
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

def add_booking(request):
    if request.method == 'POST':
        try:
            # Get form data
            customer_id = request.POST.get('customer')  # Required field
            equipment_id = request.POST.get('equipment')  # Required field
            rental_date = datetime.strptime(request.POST['rental_date'], '%Y-%m-%d').date()
            due_date = datetime.strptime(request.POST['due_date'], '%Y-%m-%d').date()
            
            # Validate dates
            if rental_date > due_date:
                messages.error(request, "Due date must be after rental date")
                return redirect('add_booking')
            
            # Create rental
            rental.objects.create(
                customer_id=customer_id,
                equipment_id=equipment_id,
                rental_date=rental_date,
                due_date=due_date,
                notes=request.POST.get('notes', ''),
                rental_agreement=request.FILES.get('rental_agreement'),
                status=determine_status(rental_date, due_date)
            )
            records = rental.objects.all()
            total = sum(item.total_amount for item in records)
            # Update customer
            
            
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
    rental_obj = get_object_or_404(rental, pk=rental_id)
    now = datetime.now()
    if request.method == 'POST':
        # Update status to Returned
        rental_obj.status = 'Returned'
        rental_obj.return_date = timezone.now().date()  # Add if you track return dates
        rental_obj.updated_at = rental_obj.return_date
        rental_obj.save()
        
        # Update equipment availability if needed
        equipment = rental_obj.equipment
        equipment.available_quantity += 1
        equipment.save()
        
        messages.success(request, f'Equipment {equipment.name} has been returned successfully!')
        
        return redirect('booking_list')
    
    # For GET requests
    context = {
        'booking': rental_obj,
        'rentals': rental.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': rental.objects.aggregate(total=Sum('calculated_amount'))['total'] or 0,
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    }
    return render(request, 'apps/booking/return.html', context)

def mark_as_returned_pending_list(request, rental_id):
    rentals = rental.objects.all()
    # Get the specific rental object
    rental_obj = get_object_or_404(rental, pk=rental_id)
    now = datetime.now()
    if request.method == 'POST':
        # Update status to Returned
        rental_obj.status = 'Returned'
        rental_obj.return_date = timezone.now().date()  # Add if you track return dates
        rental_obj.updated_at = rental_obj.return_date
        rental_obj.save()
        
        # Update equipment availability if needed
        equipment = rental_obj.equipment
        equipment.available_quantity += 1
        equipment.save()
        
        messages.success(request, f'Equipment {equipment.name} has been returned successfully!')
        
        return redirect('booking_list')
    
    # For GET requests
    context = {
        'booking': rental_obj,
        'rentals': rental.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total':sum(item.total_amount for item in rentals),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    }
    return render(request, 'apps/booking/return-pending.html', context)
def mark_as_returned_active_list(request, rental_id):
    # Get the specific rental object
    rentals = rental.objects.all()
    
    rental_obj = get_object_or_404(rental, pk=rental_id)
    now = datetime.now()
    if request.method == 'POST':
        # Update status to Returned
        rental_obj.status = 'Returned'
        rental_obj.return_date = timezone.now().date()  # Add if you track return dates
        rental_obj.updated_at = rental_obj.return_date
        rental_obj.save()
        
        # Update equipment availability if needed
        equipment = rental_obj.equipment
        equipment.available_quantity += 1
        equipment.save()
        
        messages.success(request, f'Equipment {equipment.name} has been returned successfully!')
        
        return redirect('booking_list')
    
    # For GET requests
    context = {
        'booking': rental_obj,
        'rentals': rental.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total':sum(item.total_amount for item in rentals),

        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    }
    return render(request, 'apps/booking/return-active.html', context)
def mark_as_returned_overdue_list(request, rental_id):
    rentals = rental.objects.all()
    
    # Get the specific rental object
    rental_obj = get_object_or_404(rental, pk=rental_id)
    now = datetime.now()
    if request.method == 'POST':
        # Update status to Returned
        rental_obj.status = 'Returned'
        rental_obj.return_date = timezone.now().date()  # Add if you track return dates
        rental_obj.updated_at = rental_obj.return_date
        rental_obj.save()
        
        # Update equipment availability if needed
        equipment = rental_obj.equipment
        equipment.available_quantity += 1
        equipment.save()
        
        messages.success(request, f'Equipment {equipment.name} has been returned successfully!')
        
        return redirect('booking_list')
    
    # For GET requests
    context = {
        'booking': rental_obj,
        'rentals': rental.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total':sum(item.total_amount for item in rentals),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    }
    return render(request, 'apps/booking/return-overdue.html', context)

def return_list(request):
    rentals = rental.objects.all()
    return render(request, 'apps/booking/return_list.html', {
        'rentals': rental.objects.all(),
        'overdue_count': rental.objects.filter(status='Overdue').count(),
        'returned_count': rental.objects.filter(status='Returned').count(),
        'active_count': rental.objects.filter(status='Active').count(),
        'total': sum(item.total_amount for item in rentals),
        'equipments': Equipments.objects.all(),
        'customers': Customers.objects.all(),
    })