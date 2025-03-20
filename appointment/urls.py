from django.urls import path
from . import views

app_name = 'appointment'

urlpatterns = [
    path('', views.index, name='index'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('confirmation/<int:appointment_id>/', views.confirmation_page, name='confirmation_page'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('manage/', views.manage_appointments, name='manage_appointments'),
    path('update-status/<int:appointment_id>/', views.update_appointment_status, name='update_appointment_status'),
    path('payment/<int:appointment_id>/', views.payment, name='payment'),
    path('process-payment/<int:appointment_id>/', views.process_payment, name='process_payment'),
    path('payment-success/<int:appointment_id>/', views.payment_success, name='payment_success'),
    path('add-review/<int:appointment_id>/', views.add_review, name='add_review'),
    path('edit-review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete_review'),
]
