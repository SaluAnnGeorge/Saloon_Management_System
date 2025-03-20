from django.contrib import admin
from django.urls import path, include
from . import views
from .views import generate_appointment_charts

app_name = "saloon"

urlpatterns = [
    path("", views.index, name="index"),
    path('about/', views.about, name='about'),
    path('contact/',views.contact,name="contact"),
    path('gallery/', views.gallery, name='gallery'),
    path('404/', views.error, name='404'),
    path('service/', views.service, name='service'),
    path('price/', views.price, name='price'),
    path('team/', views.team, name='team'),
    path('testimonial/', views.testimonial, name='testimonial'),
    path('testimonial/add-review/', views.add_review, name='add_review'),
    path('appointment/', views.appointment, name='appointment'),
    path('category/<int:category_id>/', views.service, name='service_by_category'),
    
    # Service detail and review URLs
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    path('service/<int:service_id>/review/', views.add_service_review, name='add_service_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('my-enquiries/', views.my_enquiries, name='my_enquiries'),
    path('search/', views.search_services, name='search_services'),
    path('customer-report/', views.customer_report, name='customer_report'),
    path('recommend/', views.personalized_recommendation, name='service_recommendation'),
    # path('chat/', views.chat, name='chat'),
    path('Voice_search/', views.search_service, name='search_service'),
    path('appointment-charts/',generate_appointment_charts, name='appointment_charts'),
]


