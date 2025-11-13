from django.contrib import admin
from .models import SellerProfile, Document

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ("factory_name", "user", "status")
    search_fields = ("factory_name", "user__username")

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("seller", "doc_type", "uploaded_at")
    readonly_fields = ("uploaded_at",)
