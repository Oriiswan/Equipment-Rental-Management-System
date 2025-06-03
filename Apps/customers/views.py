from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Customers
from django.contrib import messages
from booking.models import rental
from django.db.models import Q
def customer_list(request):
  rentals = rental.objects.all()
  customers = Customers.objects.all()
  
  for customer in customers:
    for record in rentals:
      if customer == record.customer:
        customer.recent_pickups = record.equipment.name
        customer.last_rent = record.rental_date
        customer.save()
        
  for customer in customers:
      customer.total_rent = rentals.filter(Q(customer=customer) & (Q(status='Active') | Q(status ='Overdue'))).count()
      customer.save()
      
      
  overdue = Customers.objects.filter(isactive = False)
  active = Customers.objects.filter(isactive = True)
  data = {
    'customers': customers,
    'count': len(customers),
    'overdue': len(overdue),
    'active': len(active),
    'rentals': rental.objects.all(),
    
    
    
  }
  return render(request, 'apps/customers/list.html', data)


def active_customer(request):
  customers = Customers.objects.all()
  overdue = Customers.objects.filter(isactive = False)
  active = Customers.objects.filter(isactive = True)
  data = {
    'customers': customers,
    'count': len(customers),
    'overdue': len(overdue),
    'active': len(active)
  }
  return render(request, 'apps/customers/active-list.html', data)

def overdue_customer(request):
  customers = Customers.objects.all()
  overdue = Customers.objects.filter(isactive = False)
  active = Customers.objects.filter(isactive = True)
  data = {
    'customers': customers,
    'count': len(customers),
    'overdue': len(overdue),
    'active': len(active)
  }
  return render(request, 'apps/customers/overdue.html', data)

def add_customer(request):
  try:
    if request.method == 'POST':
      customers = Customers.objects.all()
      first_name = request.POST.get('first_name')
      last_name = request.POST.get('last_name')
      email = request.POST.get('email')
      phone = request.POST.get('contact_number')
      address = request.POST.get('address')
      image = request.FILES.get('valid_id')
      
      exists = Customers.objects.filter(firstname = first_name, lastname = last_name).exists()
      if exists:
        messages.error(request, 'This Customer is already exists')
        return render(request, 'apps/customers/Add-users.html')
      else:
        Customers.objects.create(
          firstname=first_name,
          lastname=last_name,
          email=email,
          address = address,
          contact_number=phone,
          valid_id=image
          )
        data = {
          'customers': customers
        }
        return redirect('/customers/list')
    else:
      return render(request, 'apps/customers/add-users.html')
  except Exception as e:
    return HttpResponse(f'Error occurred during {e}')
  
  
