from django.shortcuts import render
from django.http import HttpResponse
def booking(request):
  return render(request, 'apps/booking/list.html')
# Create your views here.
