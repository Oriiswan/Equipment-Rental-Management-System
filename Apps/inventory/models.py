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
  image = models.ImageField(upload_to='./static/images/')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def get_availability_details(self, start_date, end_date):
        """
        Returns detailed availability information for this equipment
        
        Args:
            start_date (date): Start date to check
            end_date (date): End date to check
            
        Returns:
            dict: {
                'is_available': bool,
                'unavailable_dates': list[date],
                'max_available': int
            }
        """
        from booking.models import rental
        
        # Filter rentals for THIS equipment (self)
        overlapping_rentals = rental.objects.filter(
            equipment=self,  # Use self instead of the parameter
            return_date__isnull=True
        ).exclude(
            status__in=['Returned', 'Cancelled']
        ).filter(
            Q(rental_date__lte=end_date) & Q(due_date__gte=start_date)
        )

        unavailable_dates = []
        current_date = start_date
        max_concurrent = 0

        while current_date <= end_date:
            concurrent = overlapping_rentals.filter(
                rental_date__lte=current_date,
                due_date__gte=current_date
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


