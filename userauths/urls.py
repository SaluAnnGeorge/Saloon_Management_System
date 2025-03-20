from django.contrib import admin
from django.urls import path,include
from userauths import views

app_name = 'userauths'

urlpatterns = [
    #path('admin/', admin.site.urls),
    path("sign-up/",views.RegisterView,name="sign-up"),
    path("sign-in/",views.loginViewTemp,name="sign-in"),
    path("sign-out/",views.logoutView,name="sign-out"),
    path('forgot-password/', views.forgot_password_view, name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset-password'),

]