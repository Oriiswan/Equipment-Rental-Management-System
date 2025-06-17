import requests
from datetime import date, datetime
def notify_overdue_booking(booking):
   if booking.status == "Overdue":
     webhook_url = 'https://hooks.zapier.com/hooks/catch/23224648/2ve3wim/'
     data ={
       'customer_email': booking.customer.email,
       'customer_name': f'{booking.customer.firstname} {booking.customer.lastname}',
       'equipment': booking.equipment.name,
       'due_date': str(booking.due_date),
       'booking_id': booking.rental_id
     } 
     requests.post(webhook_url, json=data)
     
def notify_pickup_booking(booking):
   if booking.status == "Pickup":
     webhook_url = 'https://hooks.zapier.com/hooks/catch/23224648/uo3uid6/'
     data ={
       'customer_email': booking.customer.email,
       'customer_name': f'{booking.customer.firstname} {booking.customer.lastname}',
       'equipment': booking.equipment.name,
       'due_date': str(booking.due_date),
       'rental_date': str(booking.rental_date),
       'booking_id': booking.rental_id
     } 
     requests.post(webhook_url, json=data)
def notify_reserved_booking(booking):
   if booking.status == "Pending":
     webhook_url = 'https://hooks.zapier.com/hooks/catch/23224648/uyuy7el/'
     data ={
       'customer_email': booking.customer.email,
       'customer_name': f'{booking.customer.firstname} {booking.customer.lastname}',
       'equipment': booking.equipment.name,
       'due_date': str(booking.due_date),
       'booking_id': booking.rental_id,
  
      'email_subject': 'Equipment Reservation Confirmed',
     } 
     requests.post(webhook_url, json=data)
def notify_today_booking(booking):
   if booking.status == "Active":
     webhook_url = 'https://hooks.zapier.com/hooks/catch/23224648/uyu34ou/'
     data ={
       'customer_email': booking.customer.email,
       'customer_name': f'{booking.customer.firstname} {booking.customer.lastname}',
       'equipment': booking.equipment.name,
       'due_date': str(booking.due_date),
       'booking_id': booking.rental_id,
       'email_subject': 'Your Equipment Rental Starts Today',
     } 
     requests.post(webhook_url, json=data)
def notify_duedate_booking(booking):
   if booking.due_date == date.today():
     webhook_url = 'https://hooks.zapier.com/hooks/catch/23224648/2ve3wim/'
     data ={
       'customer_email': booking.customer.email,
       'customer_name': f'{booking.customer.firstname} {booking.customer.lastname}',
       'equipment': booking.equipment.name,
       'due_date': str(booking.due_date),
       'booking_id': booking.rental_id,
       'email_subject': ' Equipment Due Back Today',
     } 
     requests.post(webhook_url, json=data)