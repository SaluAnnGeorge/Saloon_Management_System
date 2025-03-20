from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from django.template import TemplateDoesNotExist
from datetime import datetime
import uuid
import json
from .models import Appointment, Review
from saloon.models import Service
from utils.email_utils import send_booking_confirmation, send_payment_confirmation, send_appointment_status_update

@login_required
def book_appointment(request):
    if request.method == 'POST':
        service_id = request.POST.get('service')
        customer_name = request.POST.get('customer_name')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        
        service = get_object_or_404(Service, id=service_id)
        
        # Convert string to datetime objects
        try:
            from datetime import datetime
            # Parse the date and time
            parsed_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            parsed_time = datetime.strptime(appointment_time, '%H:%M').time()

            # Check if the time slot is already booked
            if Appointment.objects.filter(appointment_date=parsed_date, appointment_time=parsed_time).exists():
                messages.error(request, 'This time slot is already booked! Please choose a different time.')
                return redirect('appointment:book_appointment')
            
            # Create appointment with pending status
            appointment = Appointment.objects.create(
                customer=request.user,
                customer_name=customer_name,
                service=service,
                appointment_date=parsed_date,
                appointment_time=parsed_time,
                status='pending',
                total_amount=service.cost
            )
            
            # Send booking confirmation email
            send_booking_confirmation(appointment)
            
            messages.success(request, 'Appointment booked successfully! Please wait for admin approval.')
            return redirect('appointment:my_appointments')
        except ValueError as e:
            messages.error(request, 'Invalid date or time format')
            return redirect('appointment:book_appointment')
    
    services = Service.objects.all()
    return render(request, 'saloon/appointment.html', {'services': services})

@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(customer=request.user).order_by('-appointment_date')
    return render(request, 'appointment/my_appointments.html', {'appointments': appointments})

@login_required
def check_status(request):
    appointment_id = request.GET.get('appointment_id')
    appointment = get_object_or_404(Appointment, id=appointment_id, customer=request.user)
    
    data = {
        'status': appointment.status,
        'payment_url': reverse('appointment:process_payment', args=[appointment.id]) if appointment.status == 'approved' else None
    }
    return JsonResponse(data)

@login_required
def confirmation_page(request, appointment_id):
    try:
        # Only get essential fields to speed up query
        appointment = get_object_or_404(
            Appointment.objects.select_related('service'),
            id=appointment_id,
            customer=request.user,
            status='confirmed'
        )
        return render(request, 'appointment/confirmation.html', {'appointment': appointment})
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found.')
        return redirect('appointment:my_appointments')
    except Exception as e:
        messages.error(request, 'Could not load confirmation page.')
        return redirect('appointment:my_appointments')

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        customer=request.user
    )
    
    if appointment.status in ['completed', 'cancelled']:
        messages.error(request, 'Cannot cancel a completed or already cancelled appointment.')
        return redirect('appointment:my_appointments')
    
    appointment.status = 'cancelled'
    appointment.save(update_fields=['status'])
    
    messages.success(request, 'Appointment cancelled successfully.')
    return redirect('appointment:my_appointments')

@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        customer=request.user
    )
    
    if request.method == 'POST':
        new_date = request.POST.get('appointment_date')
        new_time = request.POST.get('appointment_time')
        
        if not all([new_date, new_time]):
            return JsonResponse({
                'success': False,
                'message': 'Please select both date and time'
            })
        
        try:
            appointment.appointment_date = datetime.strptime(new_date, '%Y-%m-%d').date()
            appointment.appointment_time = datetime.strptime(new_time, '%H:%M').time()
            appointment.save(update_fields=['appointment_date', 'appointment_time'])
            
            return JsonResponse({
                'success': True,
                'message': 'Appointment rescheduled successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    context = {
        'appointment': appointment,
        'page_title': 'Reschedule Appointment'
    }
    return render(request, 'appointment/reschedule.html', context)

@login_required
def add_review(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        customer=request.user,
        status='completed'
    )
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not rating:
            messages.error(request, 'Please provide a rating')
            return redirect('appointment:add_review', appointment_id=appointment_id)
        
        Review.objects.create(
            appointment=appointment,
            user=request.user,
            rating=rating,
            comment=comment
        )
        
        messages.success(request, 'Review added successfully')
        return redirect('appointment:my_appointments')
    
    context = {
        'appointment': appointment,
        'page_title': 'Add Review'
    }
    return render(request, 'appointment/add_review.html', context)

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(
        Review,
        id=review_id,
        user=request.user
    )
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not rating:
            messages.error(request, 'Please provide a rating')
            return redirect('appointment:edit_review', review_id=review_id)
        
        review.rating = rating
        review.comment = comment
        review.save(update_fields=['rating', 'comment'])
        
        messages.success(request, 'Review updated successfully')
        return redirect('appointment:my_appointments')
    
    context = {
        'review': review,
        'page_title': 'Edit Review'
    }
    return render(request, 'appointment/edit_review.html', context)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(
        Review,
        id=review_id,
        user=request.user
    )
    
    review.delete()
    messages.success(request, 'Review deleted successfully')
    return redirect('appointment:my_appointments')

@login_required
def index(request):
    return redirect('appointment:my_appointments')

@login_required
def manage_appointments(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('saloon:index')
    
    appointments = Appointment.objects.all().order_by('-appointment_date')
    return render(request, 'appointment/manage_appointments.html', {'appointments': appointments})

@login_required
def update_appointment_status(request, appointment_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    status = request.POST.get('status')
    
    if status not in ['approved', 'rejected']:
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    try:
        # Update appointment status
        appointment.status = status
        appointment.save()
        
        # Send status update email
        send_appointment_status_update(appointment)
        
        return JsonResponse({
            'success': True,
            'message': f'Appointment status updated to {status}',
            'status': status
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to update appointment status: {str(e)}'
        }, status=500)

@login_required
def payment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        customer=request.user
    )
    
    # If payment is already completed, show the success page
    if appointment.payment_status == 'completed':
        return redirect('appointment:payment_success', appointment_id=appointment.id)
        
    context = {
        'appointment': appointment,
        'amount': appointment.total_amount,
    }
    
    return render(request, 'appointment/payment.html', context)

@login_required
def payment_success(request, appointment_id):
    # Get appointment with proper filtering
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        customer=request.user
    )
    
    # Only show success page for completed payments
    if appointment.payment_status != 'completed':
        messages.error(request, 'Payment is not completed for this appointment.')
        return redirect('appointment:payment', appointment_id=appointment_id)
    
    context = {
        'appointment': appointment,
        'page_title': 'Payment Successful'
    }
    
    return render(request, 'appointment/payment_success.html', context)

@login_required
def process_payment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        customer=request.user,
        status='approved',
        payment_status='pending'
    )
    
    if request.method == 'POST':
        try:
            # For demo purposes, we'll just mark the payment as successful
            transaction_id = f"DEMO-{uuid.uuid4().hex[:8].upper()}"
            
            # Update appointment
            appointment.status = 'confirmed'
            appointment.payment_status = 'completed'
            appointment.payment_method = request.POST.get('payment_method', 'card')
            appointment.transaction_id = transaction_id
            appointment.payment_date = timezone.now()
            appointment.save()
            
            # Send payment confirmation email
            send_payment_confirmation_email(appointment)
            
            messages.success(request, 'Payment successful! Your appointment has been confirmed.')
            
            # Redirect to success page with appointment details
            return redirect('appointment:payment_success', appointment_id=appointment.id)
            
        except Exception as e:
            messages.error(request, 'Payment failed. Please try again.')
            return redirect('appointment:payment', appointment_id=appointment_id)
    
    return redirect('appointment:payment', appointment_id=appointment_id)

def send_booking_confirmation_email(appointment):
    subject = 'Appointment Confirmation - Velvet Touch Beauty Salon'
    html_message = render_to_string('appointment/email/booking_confirmation.html', {
        'appointment': appointment,
        'customer_name': appointment.customer.get_full_name(),
        'service_name': appointment.service.name,
        'appointment_date': appointment.appointment_date,
        'appointment_time': appointment.appointment_time,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [appointment.customer.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_payment_confirmation_email(appointment):
    subject = 'Payment Confirmation - Velvet Touch Beauty Salon'
    context = {
        'customer_name': appointment.customer.get_full_name(),
        'service_name': appointment.service.name,
        'appointment_date': appointment.appointment_date,
        'appointment_time': appointment.appointment_time,
        'amount': appointment.total_amount,
        'transaction_id': appointment.transaction_id,
        'payment_date': appointment.payment_date,
        'payment_method': appointment.payment_method,
        'salon_name': 'Velvet Touch Beauty Salon',
        'salon_address': '123 Main Street, City, State - 12345',
        'salon_phone': '(123) 456-7890',
        'salon_email': 'contact@velvettouch.com'
    }
    
    html_message = render_to_string('appointment/email/payment_confirmation.html', context)
    plain_message = strip_tags(html_message)
    
    try:
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

def send_booking_confirmation(appointment):
    subject = 'Appointment Confirmation - Velvet Touch Beauty Salon'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [appointment.customer.email]
    
    # Build the salon URL
    salon_url = f'http://127.0.0.1:8000/appointment/my-appointments/'
    
    # Prepare context for email template
    context = {
        'appointment': appointment,
        'salon_url': salon_url
    }
    
    # Render HTML email template
    html_message = render_to_string('emails/booking_confirmation.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        # Send email
        send_mail(
            subject,
            plain_message,
            from_email,
            to_email,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send booking confirmation email: {e}")
        return False

def send_appointment_status_update(appointment):
    subject = 'Appointment Status Update - Velvet Touch Beauty Salon'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [appointment.customer.email]
    
    # Prepare context for email template
    context = {
        'appointment': appointment,
    }
    
    # Render HTML email template
    html_message = render_to_string('emails/appointment_status_update.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        # Send email
        send_mail(
            subject,
            plain_message,
            from_email,
            to_email,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send appointment status update email: {e}")
        return False
