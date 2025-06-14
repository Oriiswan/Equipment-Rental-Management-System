from django.db import models
import math

from django.db.models import Q
from datetime import date, datetime,timedelta
# Create your models here.
class Equipments(models.Model):
  equipment_id = models.BigAutoField(primary_key=True, blank=False)
  name = models.CharField(max_length=55, blank=False)
  category = models.CharField(max_length=55, blank=False)
  daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
  total_quantity = models.IntegerField(default=0)
  available_quantity = models.IntegerField(default=0)
  utilizations = models.IntegerField(default=0)
  image = models.ImageField(upload_to='./static/images/')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  condition = models.CharField(max_length=55, blank=False, default='good')
  def get_current_available_quantity(self):
        """Calculate real-time available quantity based on active rentals"""
        from booking.models import rental
        
        active_rentals = rental.objects.filter(
            equipment=self,
            status__in=['active', 'pickup', 'overdue'],
            return_date__isnull=True
        ).count()
        
        return max(0, self.total_quantity - active_rentals)
    
  def sync_available_quantity(self):
        """Sync the available_quantity field with calculated value"""
        calculated_qty = self.get_current_available_quantity()
        if self.available_quantity != calculated_qty:
            self.available_quantity = calculated_qty
            self.save(update_fields=['available_quantity'])
        return calculated_qty
  def get_availability_details(self, start_date, end_date):
    from booking.models import rental
    
    # Equipment is unavailable if:
    # rental_date <= check_date < due_date (due_date is exclusive)
    overlapping_rentals = rental.objects.filter(
        equipment=self,
        return_date__isnull=True
    ).exclude(
        status__in=['Returned', 'Cancelled']
    ).filter(
        Q(rental_date__lte=end_date) & Q(due_date__gt=start_date)  # Changed gte to gt
    )

    unavailable_dates = []
    current_date = start_date
    max_concurrent = 0

    while current_date <= end_date:
        concurrent = overlapping_rentals.filter(
            rental_date__lte=current_date,
            due_date__gt=current_date  # Changed gte to gt - due date is exclusive
        ).count()

        max_concurrent = max(max_concurrent, concurrent)

        if concurrent >= self.available_quantity:
            unavailable_dates.append(current_date)

        current_date += timedelta(days=1)

    return {
        'is_available': len(unavailable_dates) == 0,
        'unavailable_dates': unavailable_dates,
        'max_available': max(0, self.available_quantity - max_concurrent)
    }
  
  
  @property
  def utilization(self):
    return math.floor(((self.total_quantity - self.available_quantity) / self.total_quantity) * 100) 
  
  @property
  def availability(self):
    return math.floor((self.available_quantity / self.total_quantity) * 100)


