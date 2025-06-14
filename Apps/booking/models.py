from django.db import models
from customers.models import Customers
from inventory.models import Equipments 
from datetime import date,datetime
from django.utils import timezone
from datetime import timedelta
from utils.zapier import notify_overdue_booking, notify_today_booking, notify_reserved_booking, notify_duedate_booking
from decimal import Decimal
class rental(models.Model):  
    calculated_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rental_id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(
        Customers, 
        on_delete=models.CASCADE,
        
        related_name='customer_rentals'
    )
    equipment = models.ForeignKey(
        Equipments,  
        on_delete=models.CASCADE,
        
        related_name='equipment_rentals'
    )
    is_pickup = models.BooleanField(default=False)
    rental_date = models.DateField(
        help_text="Date when the equipment rental starts"
    )
    due_date = models.DateField(
        help_text="Date when the equipment should be returned"
    )
    return_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Actual date when equipment was returned"
    )
    notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional notes about the rental"
    )
    rental_agreement = models.ImageField(
        upload_to='./static/images',
        blank=True,
        null=True,
        help_text="Upload rental agreement document"
    )
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    @property
    def days_ago(self):
        if not self.rental_date:
            return "Pending" 
        if self.rental_date > date.today():
            return "Pending"  
        return (date.today() - self.rental_date).days
    @property
    def days_left(self):
        return (self.due_date - date.today() ).days
    @property
    def total_amount(self):
        rental_duration = (self.due_date - self.rental_date).days
        return rental_duration * self.equipment.daily_rate
    
    @property
    def total_amount_afterdue(self):
        if date.today() < self.due_date:
            return self.total_amount
        extra_fee = (date.today() - self.due_date).days * self.equipment.daily_rate
        return self.total_amount + extra_fee
   
    @property
    def revenue(self):
        if self.return_date:
            if self.return_date < self.due_date:
                return self.total_amount or Decimal('0.00')

            extra_fee = (self.return_date - self.due_date).days * self.equipment.daily_rate
            total = (self.total_amount or Decimal('0.00')) + extra_fee
            return total
    @property
    def fullname(self):
        return self.customer.firstname +' '+self.customer.lastname
    @property
    def equipment_name(self):
        return self.equipment.name
    @property
    def created(self):
        """Returns time elapsed since creation as a timedelta"""
        return timezone.now() - self.created_at
    
    @property
    def updated(self):
        """Returns time elapsed since creation as a timedelta"""
        return timezone.now() - self.updated_at
    
    @property
    def created(self):
        """Returns time elapsed since creation as a timedelta"""
        return timezone.now() - self.created_at
    
    @property 
    def created_display(self):
        """
        Returns human-readable time since creation
        Format: "X days, Y hours ago" or "Just now"
        """
        delta = self.created
        
        if delta < timedelta(minutes=1):
            return "Just now"
        elif delta < timedelta(hours=1):
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif delta < timedelta(days=1):
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = delta.days
            hours = (delta.seconds // 3600)
            if hours > 0:
                return f"{days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''} ago"
            return f"{days} day{'s' if days != 1 else ''} ago"
    def recent_display(self):
        """
        Returns human-readable time since creation
        Format: "X days, Y hours ago" or "Just now"
        """
        delta = self.updated
        
        if delta < timedelta(minutes=1):
            return "Just now"
        elif delta < timedelta(hours=1):
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif delta < timedelta(days=1):
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = delta.days
            hours = (delta.seconds // 3600)
            if hours > 0:
                return f"{days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''} ago"
            return f"{days} day{'s' if days != 1 else ''} ago"
    def save(self, *args, **kwargs):
        self.calculated_amount = self.total_amount  # Uses your property
        super().save(*args, **kwargs)
    