from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Customers
from django.contrib import messages
from booking.models import rental
def customer_list(request):
  rentals = rental.objects.all()
  customers = Customers.objects.all()
  
  
  for customer in customers:
      customer.total_rent = rentals.filter(customer_id=customer.customer_id).count()
      customer.save()
      if rentals.filter(customer_id=customer.customer_id).exists():
        customer.isactive = True
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
        messages.error(request, 'This product is already exists')
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
  
  
