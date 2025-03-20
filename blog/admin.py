from django.contrib import admin
from .models import Blog

# Register your models here.

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_date', 'published_date')
    list_filter = ('created_date', 'published_date', 'author')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_date'
    ordering = ('-created_date',)
