
from django.shortcuts import render
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from datetime import date, datetime, timedelta
from decimal import Decimal
import calendar
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from inventory.models import Equipments
from customers.models import Customers
from booking.models import rental
@login_required
def reports_dashboard(request):
 
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    

    date_range = request.GET.get('range', '30')
    if date_range == '7':
        start_date = end_date - timedelta(days=7)
    elif date_range == 'month':
        start_date = end_date.replace(day=1)
    elif date_range == 'year':
        start_date = end_date.replace(month=1, day=1)

    total_revenue = calculate_total_revenue()
    
 
    current_month_revenue = calculate_monthly_revenue(end_date.year, end_date.month)
    last_month = end_date.replace(day=1) - timedelta(days=1)
    last_month_revenue = calculate_monthly_revenue(last_month.year, last_month.month)
    

    ytd_revenue = calculate_ytd_revenue(end_date.year)
    

    avg_rental_value = calculate_average_rental_value()


    

    equipment_analytics = get_equipment_analytics()
    
  
    avg_utilization = calculate_average_utilization()
    
   
    top_equipment = get_top_performing_equipment()
    

    detailed_equipment_reports = get_detailed_equipment_reports()

    

    customer_data = get_customer_analytics()
    
 
    top_customers = get_top_customers()
  
    repeat_customers = calculate_repeat_customer_percentage()


    
    rental_summary = get_rental_summary()

    context = {
      
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue,
        'last_month_revenue': last_month_revenue,
        'ytd_revenue': ytd_revenue,
        'avg_rental_value': avg_rental_value,
        
       
        'equipment_analytics': equipment_analytics,
        'avg_utilization': avg_utilization,
        'top_equipment': top_equipment,
        'detailed_equipment_reports': detailed_equipment_reports,
        

        'total_customers': customer_data['total'],
        'active_customers': customer_data['active'],
        'top_customers': top_customers,
        'repeat_customers': repeat_customers,
        

        'total_rentals': rental_summary['total'],
        'active_rentals': rental_summary['active'],
        'pending_rentals': rental_summary['pending'],
        'overdue_rentals': rental_summary['overdue'],
        'returned_rentals': rental_summary['returned'],
        'avg_rental_duration': rental_summary['avg_duration'],
        
        
  
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        'price': 20000,
    }
    
    return render(request, 'apps/reports/dashboard.html', context)

def calculate_total_revenue():
    
    total = Decimal('0.00')
    
   
    returned_rentals = rental.objects.filter(status='Returned')
    for r in returned_rentals:
        if r.revenue:
            total += r.revenue
    
    # Revenue from active/overdue rentals (projected)
    # active_rentals = rental.objects.filter(status__in=['Active', 'Overdue'])
    # for r in active_rentals:
    #     if r.total_amount_afterdue:
    #         total += r.total_amount_afterdue
            
    return total

def calculate_monthly_revenue(year, month):
    
    monthly_revenue = Decimal('0.00')
    

    month_start = date(year, month, 1)
    month_end = date(year, month, calendar.monthrange(year, month)[1])
    
    month_rentals = rental.objects.filter(
        Q(rental_date__lte=month_end) & 
        Q(due_date__gte=month_start)
    )
    
    for r in month_rentals:
        if r.status == 'Returned' and r.revenue:
            monthly_revenue += r.revenue
        # elif r.status in ['Active', 'Overdue']:
        #     monthly_revenue += r.total_amount or Decimal('0.00')
            
    return monthly_revenue

def calculate_ytd_revenue(year):

    ytd_revenue = Decimal('0.00')
    year_start = date(year, 1, 1)
    
    ytd_rentals = rental.objects.filter(rental_date__gte=year_start)
    
    for r in ytd_rentals:
        if r.status == 'Returned' and r.revenue:
            ytd_revenue += r.revenue
        # elif r.status in ['Active', 'Overdue'] and r.total_amount:
        #     ytd_revenue += r.total_amount
            
    return ytd_revenue

def calculate_average_rental_value():
 
    total_revenue = calculate_total_revenue()
    total_rentals = rental.objects.count()
    
    if total_rentals > 0:
        return total_revenue / total_rentals
    return Decimal('0.00')

def get_equipment_analytics():
   
    equipment_list = []
    
    for equipment in Equipments.objects.all():
       
        equipment_rentals = rental.objects.filter(equipment=equipment)
        
        rental_count = equipment_rentals.count()
        total_revenue = Decimal('0.00')
        
        for r in equipment_rentals:
            if r.status == 'Returned' and r.revenue:
                total_revenue += r.revenue
            elif r.status in ['Active', 'Overdue'] and r.total_amount:
                total_revenue += r.total_amount
        
        equipment_data = {
            'equipment_id': equipment.equipment_id,
            'name': equipment.name,
            'category': equipment.category,
            'utilization': equipment.utilization,
            'rental_count': rental_count,
            'total_revenue': total_revenue,
            'avg_duration': calculate_avg_duration_for_equipment(equipment),
        }
        
        equipment_list.append(equipment_data)
    
   
    return sorted(equipment_list, key=lambda x: x['utilization'], reverse=True)

def calculate_average_utilization():
   
    equipment = Equipments.objects.all()
    if equipment.exists():
        total_utilization = sum(eq.utilization for eq in equipment)
        return round(total_utilization / equipment.count(), 1)
    return 0

def get_top_performing_equipment():

    equipment_revenue = []
    
    for equipment in Equipments.objects.all():
        equipment_rentals = rental.objects.filter(equipment=equipment)
        total_revenue = Decimal('0.00')
        rental_count = equipment_rentals.count()
        
        for r in equipment_rentals:
            if r.status == 'Returned' and r.revenue:
                total_revenue += r.revenue
            elif r.status in ['Active', 'Overdue'] and r.total_amount:
                total_revenue += r.total_amount
        
        if total_revenue > 0:
            equipment_revenue.append({
                'name': equipment.name,
                'category': equipment.category,
                'total_revenue': total_revenue,
                'rental_count': rental_count,
                'revenue_percentage': 0 
            })
    
  
    equipment_revenue.sort(key=lambda x: x['total_revenue'], reverse=True)
    
    if equipment_revenue:
        max_revenue = equipment_revenue[0]['total_revenue']
        for item in equipment_revenue:
            item['revenue_percentage'] = round((item['total_revenue'] / max_revenue) * 100, 1)
    
    return equipment_revenue[:10]  # Top 10

def get_detailed_equipment_reports():
 
    return get_equipment_analytics()  

def get_customer_analytics():

    total_customers = Customers.objects.count()
    
  
    active_customers = Customers.objects.filter(
        customer_rentals__status__in=['Active', 'Pending', 'Overdue']
    ).distinct().count()
    
    return {
        'total': total_customers,
        'active': active_customers,
    }

def get_top_customers():
  
    customer_revenue = []
    
    for customer in Customers.objects.all():
        customer_rentals = rental.objects.filter(customer=customer)
        total_revenue = Decimal('0.00')
        
        for r in customer_rentals:
            if r.status == 'Returned' and r.revenue:
                total_revenue += r.revenue
            elif r.status in ['Active', 'Overdue'] and r.total_amount:
                total_revenue += r.total_amount
        
        if total_revenue > 0:
            customer_revenue.append({
                'customer_id': customer.customer_id,
                'firstname': customer.firstname,
                'lastname': customer.lastname,
                'total_rent': customer.total_rent,
                'total_revenue': total_revenue,
            })
    
    # Sort by revenue descending
    return sorted(customer_revenue, key=lambda x: x['total_revenue'], reverse=True)[:10]

def calculate_repeat_customer_percentage():
 
    total_customers = Customers.objects.count()
    if total_customers == 0:
        return 0
    
    repeat_customers = Customers.objects.annotate(
        rental_count=Count('customer_rentals')
    ).filter(rental_count__gt=1).count()
    
    return round((repeat_customers / total_customers) * 100, 1)

def get_rental_summary():
 
    all_rentals = rental.objects.all()
    
    total = all_rentals.count()
    active = all_rentals.filter(status='Active').count()
    pending = all_rentals.filter(status='Pending').count()
    overdue = all_rentals.filter(status='Overdue').count()
    returned = all_rentals.filter(status='Returned').count()
    
    # Calculate average rental duration
    completed_rentals = all_rentals.filter(status='Returned', return_date__isnull=False)
    avg_duration = 0
    
    if completed_rentals.exists():
        total_days = sum(
            (r.return_date - r.rental_date).days 
            for r in completed_rentals 
            if r.return_date and r.rental_date
        )
        avg_duration = round(total_days / completed_rentals.count(), 1)
    
    return {
        'total': total,
        'active': active,
        'pending': pending,
        'overdue': overdue,
        'returned': returned,
        'avg_duration': avg_duration,
    }

def calculate_avg_duration_for_equipment(equipment):

    equipment_rentals = rental.objects.filter(
        equipment=equipment,
        status='Returned',
        return_date__isnull=False
    )
    
    if equipment_rentals.exists():
        total_days = sum(
            (r.return_date - r.rental_date).days 
            for r in equipment_rentals
        )
        return round(total_days / equipment_rentals.count(), 1)
    
    return 0



def get_monthly_revenue_data(request):
    import json
    from django.http import JsonResponse
    
    current_year = date.today().year
    monthly_data = []
    
    for month in range(1, 13):
        revenue = calculate_monthly_revenue(current_year, month)
        monthly_data.append({
            'month': calendar.month_abbr[month],
            'revenue': float(revenue)
        })
    
    return JsonResponse({'data': monthly_data})

def export_equipment_report(request):
 
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="equipment_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Equipment ID', 'Name', 'Category', 'Total Rentals', 
        'Revenue', 'Utilization %', 'Avg Duration (days)'
    ])
    
    for equipment in get_detailed_equipment_reports():
        writer.writerow([
            equipment['equipment_id'],
            equipment['name'],
            equipment['category'],
            equipment['rental_count'],
            equipment['total_revenue'],
            equipment['utilization'],
            equipment['avg_duration'],
        ])
    
    return response