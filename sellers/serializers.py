from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SellerProfile, Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ("id", "doc_type", "file", "uploaded_at")

class SellerProfileSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    class Meta:
        model = SellerProfile
        fields = ("id", "factory_name", "mobile", "gstin", "iec", "address", "geo_lat", "geo_long", "status", "admin_comment", "documents")

class UserSerializer(serializers.ModelSerializer):
    seller_profile = SellerProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "seller_profile")
