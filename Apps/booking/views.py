from django.shortcuts import render,redirect
from django.http import HttpResponse
from inventory.models import Equipments
from customers.models import Customers
from .models import rental
from datetime import date,datetime
from django.db import connection
from django.contrib import messages
def booking_list(request):
    records = rental.objects.all()
    total = sum(item.total_amount for item in records)
    return render(request, 'apps/booking/list.html',{
      'rentals': rental.objects.all(),
      'equipments': Equipments.objects.all(),
      'customers': Customers.objects.all(),
      'overdue_count': rental.objects.filter(status='Overdue').count(),
      'returned_count': rental.objects.filter(status='Returned').count(),
      'active_count': rental.objects.filter(status='Active').count(),
      'total': total
    })
    
def active_list(request):
    records = rental.objects.all()
    total = sum(item.total_amount for item in records)
    return render(request, 'apps/booking/active.html',{
      'rentals': rental.objects.all(),
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
      'rentals': rental.objects.all(),
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
      'rentals': rental.objects.all(),
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