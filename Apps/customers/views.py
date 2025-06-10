from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import Customers
from django.contrib import messages
from booking.models import rental
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import login, authenticate
@login_required
def customer_list(request):
    rentals = rental.objects.all()
    customers = Customers.objects.all()
    
    # Update customer data
    for customer in customers:
        for record in rentals:
            if customer == record.customer:
                customer.recent_pickups = record.equipment.name
                customer.last_rent = record.rental_date
                customer.save()
                
    for customer in customers:
        customer.total_rent = rentals.filter(Q(customer=customer) & (Q(status='Active') | Q(status='Overdue'))).count()
        customer.save()
    
    # Get search parameter
    search = request.POST.get('search') if request.method == 'POST' else request.GET.get('search', '')
    
    # Filter customers based on search
    if search:
        customers_filtered = customers.filter(
            Q(firstname__icontains=search) | 
            Q(lastname__icontains=search) | 
            Q(customer_id__icontains=search) |
            Q(email__icontains=search) |
            Q(contact_number__icontains=search)
        )
    else:
        customers_filtered = customers
    
    # Pagination
    items_per_page = 10  # You can adjust this number
    paginator = Paginator(customers_filtered, items_per_page)
    
    page = request.GET.get('page', 1)
    try:
        customers_page = paginator.page(page)
    except PageNotAnInteger:
        customers_page = paginator.page(1)
    except EmptyPage:
        customers_page = paginator.page(paginator.num_pages)
    
    # Calculate statistics
    overdue = Customers.objects.filter(total_rent=0)
    active = Customers.objects.filter(total_rent__gt=0)
    
    data = {
        'customers': customers_page,  
        'count': len(customers),
        'overdue': len(overdue),
        'active': len(active),
        'rentals': rental.objects.all(),
        'search': search,
        'paginator': paginator,
        'page_obj': customers_page,
    }
    
    return render(request, 'apps/customers/list.html', data)
@login_required
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
@login_required
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
@login_required
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
        customer.total_rent = rentals.filter(Q(customer=customer) & (Q(status='Active') | Q(status='Overdue'))).count()
        customer.save()
    
   
    search = request.POST.get('search') if request.method == 'POST' else request.GET.get('search', '')
    

    active_customers = customers.filter(total_rent__gt=0)
    

    if search:
        customers_filtered = active_customers.filter(
            Q(firstname__icontains=search) | 
            Q(lastname__icontains=search) | 
            Q(customer_id__icontains=search) |
            Q(email__icontains=search) |
            Q(contact_number__icontains=search)
        )
    else:
        customers_filtered = active_customers
    

    items_per_page = 10  
    paginator = Paginator(customers_filtered, items_per_page)
    
    page = request.GET.get('page', 1)
    try:
        customers_page = paginator.page(page)
    except PageNotAnInteger:
        customers_page = paginator.page(1)
    except EmptyPage:
        customers_page = paginator.page(paginator.num_pages)
    
 
    overdue = Customers.objects.filter(total_rent=0)
    active = Customers.objects.filter(total_rent__gt=0)
    
    data = {
        'customers': customers_page,  
        'count': len(customers),
        'overdue': len(overdue),
        'active': len(active),
        'rentals': rental.objects.all(),
        'search': search,
        'paginator': paginator,
        'page_obj': customers_page,
    }
    
    return render(request, 'apps/customers/active-list.html', data)

@login_required
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
        customer.total_rent = rentals.filter(Q(customer=customer) & (Q(status='Active') | Q(status='Overdue'))).count()
        customer.save()
    
 
    search = request.POST.get('search') if request.method == 'POST' else request.GET.get('search', '')
    
 
    overdue_customers = customers.filter(total_rent=0)
    

    if search:
        customers_filtered = overdue_customers.filter(
            Q(firstname__icontains=search) | 
            Q(lastname__icontains=search) | 
            Q(customer_id__icontains=search) |
            Q(email__icontains=search) |
            Q(contact_number__icontains=search)
        )
    else:
        customers_filtered = overdue_customers
    
    
    items_per_page = 10  
    paginator = Paginator(customers_filtered, items_per_page)
    
    page = request.GET.get('page', 1)
    try:
        customers_page = paginator.page(page)
    except PageNotAnInteger:
        customers_page = paginator.page(1)
    except EmptyPage:
        customers_page = paginator.page(paginator.num_pages)
    
    
    overdue = Customers.objects.filter(total_rent=0)
    active = Customers.objects.filter(total_rent__gt=0)
    
    data = {
        'customers': customers_page,  
        'count': len(customers),
        'overdue': len(overdue),
        'active': len(active),
        'rentals': rental.objects.all(),
        'search': search,
        'paginator': paginator,
        'page_obj': customers_page,
    }
    
    return render(request, 'apps/customers/overdue.html', data)
@login_required
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
  
  
