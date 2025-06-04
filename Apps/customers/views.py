from django.shortcuts import render,redirect,get_object_or_404
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
      
      
  overdue = Customers.objects.filter(total_rent = 0)
  active = Customers.objects.filter(total_rent__gt=0)
  data = {
    'customers': customers,
    'count': len(customers),
    'overdue': len(overdue),
    'active': len(active),
    'rentals': rental.objects.all(),
    
    
    
  }
  return render(request, 'apps/customers/list.html', data)

def edit_customer(request,customer_id):
  try:
    customer_obj = get_object_or_404(Customers, pk=customer_id)
    if request.method == 'POST':
      firstname = request.POST.get('first_name')
      lastname = request.POST.get('last_name')
      email = request.POST.get('email')
      contact_number = request.POST.get('contact_number')
      address = request.POST.get('address')
      
      customer_obj.firstname = firstname
      customer_obj.lastname = lastname
      customer_obj.email = email
      customer_obj.contact_number = contact_number
      customer_obj.address = address
      customer_obj.save()
      messages.success(request,'Edit successfully')
      return redirect('customer_list')
    else:
      return render(request, 'apps/customers/edit-user.html',{
        'customer': customer_obj
      })
  except Exception as e:
    return HttpResponse(f'Error occurred during{e}')
  
def delete_customer(request, customer_id):
    customers = Customers.objects.all()
    rentals = rental.objects.all()
    customer_obj = get_object_or_404(Customers, pk=customer_id)
    if request.method == 'POST':
        customer= Customers.objects.filter(customer_id=customer_id)
        customer.delete()
        messages.success(request,'Delete Customer successfully')
        return redirect('customer_list')
   
 
    for customer in customers:
      for record in rentals:
        if customer == record.customer:
          customer.recent_pickups = record.equipment.name
          customer.last_rent = record.rental_date
          customer.save()
        
    for customer in customers:
        customer.total_rent = rentals.filter(Q(customer=customer) & (Q(status='Active') | Q(status ='Overdue'))).count()
        customer.save()
        
        
    overdue = Customers.objects.filter(total_rent = 0)
    active = Customers.objects.filter(total_rent__gt=0)
    data = {
      'customer': customer_obj,
      'customers': customers,
      'count': len(customers),
      'overdue': len(overdue),
      'active': len(active),
      'rentals': rental.objects.all(),
    }
    return render(request, 'apps/customers/delete_customer.html', data)
def active_customer(request):
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
      
      
  overdue = Customers.objects.filter(total_rent = 0)
  active = Customers.objects.filter(total_rent__gt=0)
  data = {
    'customers': customers,
    'count': len(customers),
    'overdue': len(overdue),
    'active': len(active),
    'rentals': rental.objects.all(),
    
    
    
  }
  return render(request, 'apps/customers/active-list.html', data)

def overdue_customer(request):
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
      
      
  overdue = Customers.objects.filter(total_rent = 0)
  active = Customers.objects.filter(total_rent__gt=0)
  data = {
    'customers': customers,
    'count': len(customers),
    'overdue': len(overdue),
    'active': len(active),
    'rentals': rental.objects.all(),
    
    
    
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
  
  
