from django.db import models
from customers.models import Customers
from inventory.models import Equipments  # You'll need to create this model

class rental(models.Model):  # Changed to PascalCase (Django convention)
    rental_id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(
        Customers, 
        on_delete=models.CASCADE,
        
        related_name='customer_rentals'
    )
    equipment = models.ForeignKey(
        Equipments,  # Changed to point to Equipment model
        on_delete=models.CASCADE,
        
        related_name='equipment_rentals'
    )
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

   