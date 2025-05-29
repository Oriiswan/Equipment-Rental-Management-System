from django.shortcuts import render
from django.http import HttpResponse
def equipment_list(request):
  return render(request, 'apps/equipment/list.html')