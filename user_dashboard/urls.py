from django.contrib import admin
from django.urls import path,include
from user_dashboard import views
from django.contrib.auth import views as auth_view
app_name="user_dashboard"


urlpatterns = [
   path("",views.dashboard,name="dashboard"),
   path('profile/', views.profile, name='profile'),
   path("change-password/",auth_view.PasswordChangeView.as_view(template_name="user_dashboard/password-reset/change-password.html",success_url="/dashboard/password-changed/"),name="change_password"),
   path("password-changed/",views.password_changed,name="password_changed"),
   path('appointments/<str:appointment_id>/cancel/', views.cancel_booking, name='cancel_booking'),
   

]