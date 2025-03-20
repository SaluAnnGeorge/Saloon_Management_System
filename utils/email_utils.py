from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_booking_confirmation(appointment):
    """Send booking confirmation email"""
    subject = f'Appointment Confirmation - {appointment.service.name}'
    
    # Build the salon URL
    salon_url = f'http://127.0.0.1:8000/appointment/my-appointments/'
    
    # Prepare context for email template
    context = {
        'appointment': appointment,
        'salon_url': salon_url,
        'salon_name': 'Velvet Touch Beauty Salon',
        'salon_address': '123 Main Street, City, State - 12345',
        'salon_phone': '(123) 456-7890',
        'salon_email': 'contact@velvettouch.com'
    }
    
    try:
        # Render HTML email template
        html_message = render_to_string('emails/booking_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.customer.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send booking confirmation email: {e}")
        return False

def send_payment_confirmation(appointment):
    """Send payment confirmation email"""
    subject = 'Payment Confirmation - Velvet Touch Beauty Salon'
    
    try:
        # Get the payment record
        from saloon.models import Payment
        payment = Payment.objects.filter(
            service=appointment.service,
            user=appointment.customer,
            payment_status='completed'
        ).latest('payment_date')
    except Payment.DoesNotExist:
        print("Payment record not found")
        return False
    
    # Build the receipt URL
    receipt_url = f'http://127.0.0.1:8000/appointment/receipt/{appointment.id}/'
    
    # Prepare context for email template
    context = {
        'customer_name': appointment.customer.get_full_name(),
        'service_name': appointment.service.name,
        'appointment_date': appointment.appointment_date,
        'appointment_time': appointment.appointment_time,
        'payment': payment,
        'receipt_url': receipt_url,
        'salon_name': 'Velvet Touch Beauty Salon',
        'salon_address': '123 Main Street, City, State - 12345',
        'salon_phone': '(123) 456-7890',
        'salon_email': 'contact@velvettouch.com'
    }
    
    # Render HTML email template
    html_message = render_to_string('appointment/email/payment_confirmation.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        # Send email
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.customer.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send payment confirmation email: {e}")
        return False

def send_appointment_status_update(appointment):
    """Send appointment status update email"""
    subject = f'Appointment Status Update - {appointment.service.name}'
    
    # Build the salon URL
    salon_url = f'http://127.0.0.1:8000/appointment/my-appointments/'
    
    context = {
        'appointment': appointment,
        'customer_name': appointment.customer_name,
        'service_name': appointment.service.name,
        'appointment_date': appointment.appointment_date,
        'appointment_time': appointment.appointment_time,
        'status': appointment.status,
        'salon_url': salon_url,
        'salon_name': 'Velvet Touch Beauty Salon',
        'salon_address': '123 Main Street, City, State - 12345',
        'salon_phone': '(123) 456-7890',
        'salon_email': 'contact@velvettouch.com'
    }
    
    try:
        # Render HTML email template
        html_message = render_to_string('emails/appointment_status_update.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.customer.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"Successfully sent status update email for appointment {appointment.id}")
        return True
    except Exception as e:
        print(f"Failed to send status update email: {e}")
        raise  # Re-raise the exception to handle it in the calling function
