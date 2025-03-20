from django.contrib import admin
from .models import Category, Service, Review, Contact, Payment

# Admin for Category
admin.site.register(Category)
admin.site.register(Service)

# Admin for Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'rating', 'comment', 'created_at')
    list_filter = ('rating', 'service', 'created_at')
    search_fields = ('user__username', 'user__email', 'service__name', 'comment')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 20

# Admin for Contact
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'replied', 'created_at')
    list_filter = ('replied', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    fields = ('name', 'email', 'subject', 'message', 'reply', 'replied', 'created_at')

    def save_model(self, request, obj, form, change):
        if obj.reply and not obj.replied:
            obj.replied = True
        super().save_model(request, obj, form, change)

admin.site.register(Contact, ContactAdmin)

# Admin for Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service', 'amount', 'payment_method', 'payment_status', 'payment_date')
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    search_fields = ('user__username', 'user__email', 'service__name', 'transaction_id')
    readonly_fields = ('payment_date', 'last_updated')
    date_hierarchy = 'payment_date'
    ordering = ('-payment_date',)
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'service', 'amount')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'payment_status', 'transaction_id')
        }),
        ('Additional Information', {
            'fields': ('notes', 'payment_date', 'last_updated'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.transaction_id and obj.payment_status == 'completed':
            # Generate a simple transaction ID if not provided
            import uuid
            obj.transaction_id = str(uuid.uuid4())[:8].upper()
        super().save_model(request, obj, form, change)



