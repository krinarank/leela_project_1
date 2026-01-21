# menu/admin.py
from django.contrib import admin
from .models import Inquiry

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('inquiry_id', 'user', 'subject', 'inquiry_date', 'status')
    list_filter = ('status', 'inquiry_date')
    search_fields = ('subject', 'message')
