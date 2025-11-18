from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from cloudinary_storage.storage import MediaCloudinaryStorage

# 💡 Added "new" as the default status for newly registered sellers
VERIFICATION_CHOICES = [
    ("new", "New"),           
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]


class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    factory_name = models.CharField(max_length=255)
    gstin = models.CharField(max_length=64, blank=True, null=True)
    iec = models.CharField(max_length=64, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True, null=True)
    geo_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geo_long = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=32, choices=VERIFICATION_CHOICES, default="new")  
    admin_comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.factory_name} ({self.user.username})"

def seller_doc_path(instance, filename):
    label = instance.doc_type.lower().replace(" ", "_")
    return f"seller_docs/{instance.seller.id}/{label}_{filename}"


class Document(models.Model):
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=128)
    file = models.FileField(upload_to=seller_doc_path, storage=MediaCloudinaryStorage())
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.factory_name} - {self.doc_type}"


class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)  # OTP valid for 10 minutes
        super().save(*args, **kwargs)

    def is_valid(self, otp_input):
        return self.otp == otp_input and timezone.now() <= self.expires_at

    def __str__(self):
        return f"{self.email} - {self.otp}"


class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self, otp_input):
        return self.otp == otp_input and timezone.now() <= self.expires_at

    def __str__(self):
        return f"{self.email} - {self.otp}"
