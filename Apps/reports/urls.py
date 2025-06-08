
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [

    path('', views.reports_dashboard, name='dashboard'),
    

    path('api/monthly-revenue/', views.get_monthly_revenue_data, name='monthly_revenue_api'),
    

    path('export/equipment/', views.export_equipment_report, name='export_equipment'),
    
    # Additional report views (you can add these later)
    # path('revenue/', views.revenue_report, name='revenue_report'),
    # path('equipment/', views.equipment_report, name='equipment_report'),
    # path('customers/', views.customer_report, name='customer_report'),
]

