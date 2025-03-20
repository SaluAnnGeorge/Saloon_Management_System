from django.contrib import admin
from .models import Appointment, Review
from utils.email_utils import send_appointment_status_update

# Register your models here.

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'service', 'appointment_date', 'appointment_time', 'status', 'total_amount')
    list_filter = ('status', 'appointment_date')
    search_fields = ('customer_name', 'service__name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-appointment_date', '-appointment_time')
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer', 'customer_name')
        }),
        ('Appointment Details', {
            'fields': ('service', 'appointment_date', 'appointment_time')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Payment', {
            'fields': ('total_amount', 'payment_status')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Save the model first
        super().save_model(request, obj, form, change)
        
        # If status was changed to approved or rejected, send email
        if change and 'status' in form.changed_data:
            try:
                send_appointment_status_update(obj)
                self.message_user(request, f"Status update email sent to {obj.customer_name}")
            except Exception as e:
                self.message_user(request, f"Failed to send status update email: {e}", level='ERROR')
    
    def has_add_permission(self, request):
        # Only allow adding appointments through the website
        return False
    
    # Custom actions
    actions = ['approve_appointments', 'reject_appointments']
    
    @admin.action(description='Approve selected appointments')
    def approve_appointments(self, request, queryset):
        for appointment in queryset:
            appointment.status = 'approved'
            appointment.save()
            try:
                send_appointment_status_update(appointment)
            except Exception as e:
                self.message_user(request, f'Error sending email for {appointment}: {e}', level='ERROR')
        
        updated = queryset.count()
        self.message_user(request, f'{updated} appointments were successfully approved.')
    
    @admin.action(description='Reject selected appointments')
    def reject_appointments(self, request, queryset):
        for appointment in queryset:
            appointment.status = 'rejected'
            appointment.save()
            try:
                send_appointment_status_update(appointment)
            except Exception as e:
                self.message_user(request, f'Error sending email for {appointment}: {e}', level='ERROR')
        
        updated = queryset.count()
        self.message_user(request, f'{updated} appointments were successfully rejected.')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'appointment', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'appointment__customer_name', 'comment']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'appointment', 'rating', 'comment')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
