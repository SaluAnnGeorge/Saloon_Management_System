
from django.shortcuts import render,redirect

from django.contrib import messages
from django.db import models
from django.db.models import Count
from django.http import JsonResponse
from userauths.models import Profile
from appointment.models import Appointment

from django.db import models
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from appointment.models import Appointment
from userauths.models import Profile
from userauths.forms import UserUpateForm,ProfileUpdateForm
@login_required
def dashboard(request):
    # Get the logged-in staff or admin user
    user = request.user

    # Count of total appointments
    total_appointments = Appointment.objects.all().count()

    # Count of confirmed appointments (status = "confirmed")
    confirmed_appointments = Appointment.objects.filter(status="confirmed").count()

    # Count of rejected appointments (status = "rejected")
    rejected_appointments = Appointment.objects.filter(status="rejected").count()

    # Count of appointments per service
    services_data = Appointment.objects.values('service__name').annotate(service_count=Count('service')).order_by('-service_count')

    context = {
        'total_appointments': total_appointments,
        'confirmed_appointments': confirmed_appointments,
        'rejected_appointments': rejected_appointments,
        'services_data': services_data,  # New data to visualize the number of services
        'user': user
    }
    return render(request, 'user_dashboard/dashboard.html', context)

@login_required
def profile(request):
    profile= Profile.objects.get(user=request.user)

    if request.method == "POST":
        u_form = UserUpateForm(request.POST,instance=request.user)
        p_form = ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()

            messages.success(request,"Profile updated successfully")
            return redirect("user_dashboard:profile")
    
    else:
        u_form = UserUpateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)


    context={
        "Profile":profile,
        "u_form":u_form,
        "p_form":p_form,
    }
    return render(request,"user_dashboard/profile.html",context)

@login_required
def password_changed(request):
    return render(request,"user_dashboard/password_changed.html")


from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from appointment.models import Appointment
@login_required
def cancel_booking(request, appointment_id):
    # Retrieve the appointment object for the logged-in user
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        customer=request.user,  # Ensure the customer matches the logged-in user
        payment_status="completed",  # Make sure the payment status is completed
    )

    # Check if the appointment is already cancelled
    if appointment.status == 'cancelled':
        messages.error(request, "This appointment has already been cancelled.")
        return redirect("appointment:my_appointments")

    if request.method == "POST":
        # Mark the appointment as cancelled
        appointment.status = 'cancelled'  # Update the status to 'cancelled'
        appointment.save()

        # Prepare the context for the cancellation email
        context = {
            'customer_name': appointment.customer.get_full_name(),
            'service_name': appointment.service.name,
            'appointment_date': appointment.appointment_date,
            'appointment_time': appointment.appointment_time,
        }

        # Define the subject and the message body for the cancellation email
        subject = "Salon Appointment Cancelled"
        html_message = render_to_string("user_dashboard/appointment_cancelled_email.html", context)

        # Send the cancellation email to the user
        send_mail(
            subject,
            "Your salon appointment has been successfully cancelled.",
            "saluanngeorge@gmail.com",  # Your salon's email (sender's email)
            [appointment.customer.email],  # Recipient's email (user's email)
            fail_silently=False,
            html_message=html_message
        )

        # Show a success message to the user
        messages.success(
            request,
            "Your appointment has been cancelled successfully. We hope to see you again soon!"
        )

        # Redirect to the appointments list page
        return redirect("appointment:my_appointments")

    return render(request, "user_dashboard/cancel_appointment_confirmation.html", {"appointment": appointment})
