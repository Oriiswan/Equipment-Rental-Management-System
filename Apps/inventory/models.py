from django.db import models

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
  