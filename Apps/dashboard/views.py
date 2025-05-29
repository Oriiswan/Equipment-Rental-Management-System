from django.shortcuts import render
from django.http import HttpResponse
def info(request):
  return render(request, 'apps/dashboard/index.html')