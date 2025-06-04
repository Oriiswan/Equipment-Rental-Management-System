from django.db import models
import datetime
from datetime import date
# Create your models here.
class Customers(models.Model):
  customer_id = models.BigAutoField(primary_key=True, blank=False)
  firstname = models.CharField(max_length=55, blank=False)
  lastname = models.CharField(max_length=55, blank=False)
  address = models.CharField(max_length=55, blank=False)
  isactive = models.BooleanField(default=False)
  email = models.EmailField(max_length=55, blank=False)
  contact_number = models.CharField(max_length=55, blank=False)
  total_rent = models.IntegerField(default=0)
  valid_id = models.ImageField(upload_to='./static/images/', blank=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  recent_pickups = models.CharField(max_length=56, blank=True)
  last_rent = models.DateField(null=True, blank=True)
  

     