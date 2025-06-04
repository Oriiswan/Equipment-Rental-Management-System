import requests

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