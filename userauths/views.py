from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
from urllib.parse import uses_query
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.conf import settings
from saloon_prj.settings import DEFAULT_FROM_EMAIL

from userauths.models import User,Profile
from userauths.forms import UserRegisterForm
def RegisterView(request):
    if request.user.is_authenticated:
        messages.warning(request,f"You are already logged in.")
    
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        full_name=form.cleaned_data.get("full_name")
        phone=form.cleaned_data.get("phone")
        email=form.cleaned_data.get("email")
        password=form.cleaned_data.get("password1")
        user = authenticate(email=email,password=password)
        login(request,user)
        messages.success(request,f"{full_name} your account has been created successfully")

        profile=Profile.objects.get(user=request.user)

        profile.full_name=full_name
        profile.phone=phone
        profile.save()
        messages.success(request, f"{full_name}, your account has been created successfully!")
        return redirect("saloon:index")
        
    context={
        "form":form
    }
    return render(request,"userauths/sign-up.html",context)

def loginViewTemp(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect("saloon:index") 
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            user_auth = authenticate(request, email=email, password=password)

            if user_auth is not None:
                login(request, user_auth)
                messages.success(request, "You are logged in")
                
                # Correct next URL handling
                next_url = request.GET.get("next", "saloon:index") 
                return redirect(next_url)
            else:
                messages.error(request, "Username or Password does not exist")
                return redirect("userauths:sign-in")
        except User.DoesNotExist:
            messages.error(request, "Username does not exist")
            return redirect("userauths:sign-in")

    return render(request, "userauths/sign-in.html")


def logoutView(request):
    logout(request)
    messages.success(request,"You are logged out")
    return redirect("saloon:index") 

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.mail import EmailMessage
def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse('userauths:reset-password', kwargs={'uidb64': uid, 'token': token})
            )
            # Render the email content as HTML
            subject = "Password Reset Request"
            message = render_to_string('userauths/reset_email.html', {'reset_url': reset_url})
            email_message = EmailMessage(subject, message, DEFAULT_FROM_EMAIL, [email])
            email_message.content_subtype = "html"  # Specify the email content type as HTML
            email_message.send()
            
            messages.success(request, "Password reset link has been sent to your email.")
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return redirect("userauths:forgot-password")
    
    return render(request, "userauths/forgot_password.html")


def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect("userauths:sign-in")
            else:
                messages.error(request, "Passwords do not match.")
        return render(request, "userauths/reset_password.html")
    else:
        messages.error(request, "The reset link is invalid or has expired.")
        return redirect("userauths:forgot-password")