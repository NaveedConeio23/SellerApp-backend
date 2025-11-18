import random
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SellerProfile, Document, EmailOTP, PasswordResetOTP
from .serializers import SellerProfileSerializer, DocumentSerializer
from .utils.email_service import send_acs_email


# ======================================================================
# Helper Functions
# ======================================================================

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_otp(email, otp, subject="OTP Verification", name="User", template="email/otp_email.html"):
    html_content = render_to_string(template, {"otp": otp, "subject": subject, "name": name})
    plain_text = f"Your OTP is {otp}."

    send_acs_email(
        to_email=email,
        subject=subject,
        html_content=html_content,
        plain_text=plain_text
    )


# ======================================================================
# SIGNUP
# ======================================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    email = request.data.get("email")
    phone = request.data.get("mobile")
    password = request.data.get("password")
    owner_name = request.data.get("owner_name", "")
    factory_name = request.data.get("factory_name", "Unnamed Factory")

    if not email or not phone or not password:
        return Response({"detail": "Email, mobile, and password are required"}, status=400)

    if User.objects.filter(username=email).exists():
        return Response({"detail": "User already exists"}, status=400)

    user = User.objects.create_user(
        username=email, email=email, password=password, first_name=owner_name, is_active=False
    )

    profile = SellerProfile.objects.create(
        user=user,
        factory_name=factory_name,
        mobile=phone,
        gstin=request.data.get("gstin", ""),
        iec=request.data.get("iec", ""),
        address=request.data.get("address", "")
    )

    otp = generate_otp()
    EmailOTP.objects.create(email=email, otp=otp, expires_at=timezone.now() + timedelta(minutes=10))
    send_email_otp(email, otp, name=owner_name)

    return Response({"userId": profile.id, "detail": "OTP sent to email"}, status=201)


# ======================================================================
# LOGIN
# ======================================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"detail": "Email and password required"}, status=400)

    user = authenticate(username=email, password=password)
    if not user:
        return Response({"detail": "Invalid credentials"}, status=401)

    try:
        profile = user.seller_profile
    except SellerProfile.DoesNotExist:
        return Response({"detail": "User profile not found"}, status=404)

    tokens = get_tokens_for_user(user)

    return Response({
        "userId": profile.id,
        "status": profile.status,
        "tokens": tokens
    })


# ======================================================================
# USER PROFILE UPDATE
# ======================================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_seller_profile(request, user_id):
    try:
        profile = SellerProfile.objects.get(id=user_id, user=request.user)
    except SellerProfile.DoesNotExist:
        return Response({"detail": "Profile not found"}, status=404)

    serializer = SellerProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# ======================================================================
# USER ME
# ======================================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_me(request):
    user = request.user
    try:
        profile = user.seller_profile
        profile_data = SellerProfileSerializer(profile).data
    except SellerProfile.DoesNotExist:
        profile_data = None

    return Response({
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "profile": profile_data
    })


# ======================================================================
# SEND OTP
# ======================================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp(request):
    email = request.data.get("email")
    if not email:
        return Response({"detail": "Email is required"}, status=400)

    otp_code = generate_otp()
    EmailOTP.objects.update_or_create(
        email=email,
        defaults={"otp": otp_code, "expires_at": timezone.now() + timedelta(minutes=10)},
    )

    send_email_otp(email, otp_code)
    return Response({"detail": "OTP sent to email"})


# ======================================================================
# VERIFY OTP
# ======================================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    email = request.data.get("email")
    otp_input = request.data.get("otp")

    if not email or not otp_input:
        return Response({"detail": "Email and OTP are required"}, status=400)

    try:
        otp_obj = EmailOTP.objects.filter(email=email).latest("created_at")
    except EmailOTP.DoesNotExist:
        return Response({"detail": "No OTP found for this email"}, status=404)

    if otp_obj.is_valid(otp_input):
        try:
            user = User.objects.get(username=email)
            user.is_active = True
            user.save()
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)

        tokens = get_tokens_for_user(user)
        return Response({"detail": "OTP verified", "tokens": tokens})

    return Response({"detail": "Invalid or expired OTP"}, status=400)


# ======================================================================
# FORGOT PASSWORD
# ======================================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get("email")

    if not email:
        return Response({"detail": "Email is required"}, status=400)

    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)

    otp = generate_otp()
    PasswordResetOTP.objects.update_or_create(
        email=email,
        defaults={"otp": otp, "expires_at": timezone.now() + timedelta(minutes=10)},
    )

    send_email_otp(
        email,
        otp,
        subject="Password Reset OTP",
        name=user.first_name or email,
        template="email/password_reset_email.html"
    )

    return Response({"detail": "OTP sent to email"})


# ======================================================================
# VERIFY RESET OTP
# ======================================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def verify_reset_otp(request):
    email = request.data.get("email")
    otp_input = request.data.get("otp")

    if not email or not otp_input:
        return Response({"detail": "Email and OTP are required"}, status=400)

    try:
        otp_obj = PasswordResetOTP.objects.get(email=email)
    except PasswordResetOTP.DoesNotExist:
        return Response({"detail": "No OTP found"}, status=404)

    if otp_obj.is_valid(otp_input):
        return Response({"detail": "OTP verified"})

    return Response({"detail": "Invalid or expired OTP"}, status=400)


# ======================================================================
# RESET PASSWORD
# ======================================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data.get("email")
    otp_input = request.data.get("otp")
    new_password = request.data.get("password")

    if not email or not otp_input or not new_password:
        return Response({"detail": "Email, OTP, and password are required"}, status=400)

    try:
        otp_obj = PasswordResetOTP.objects.get(email=email)
    except PasswordResetOTP.DoesNotExist:
        return Response({"detail": "No OTP found"}, status=404)

    if not otp_obj.is_valid(otp_input):
        return Response({"detail": "Invalid or expired OTP"}, status=400)

    try:
        user = User.objects.get(username=email)
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password reset successful"})
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)


# ======================================================================
# UPLOAD DOCUMENT
# ======================================================================

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def upload_doc(request):
    try:
        profile = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        return Response({"detail": "Seller profile not found"}, status=404)

    if profile.status.lower() in ["rejected", "new"]:
        profile.status = "pending"
        profile.admin_comment = ""
        profile.save()

    uploaded_docs = []
    for key, file in request.FILES.items():
        doc = Document.objects.create(seller=profile, doc_type=key, file=file)
        uploaded_docs.append(DocumentSerializer(doc).data)

    return Response({
        "message": "Documents uploaded successfully",
        "status": profile.status,
        "documents": uploaded_docs
    })


# ======================================================================
# STATUS VIEW FOR FRONTEND
# ======================================================================

@api_view(["GET"])
@permission_classes([AllowAny])
def status_view(request, user_id):
    try:
        profile = SellerProfile.objects.get(user__id=user_id)
    except SellerProfile.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    data = SellerProfileSerializer(profile).data

    return Response({
        "status": profile.status,
        "admin_comment": profile.admin_comment,
        "profile": data
    })


# ======================================================================
# UPDATE STATUS
# ======================================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_status(request):
    try:
        profile = request.user.seller_profile
        new_status = request.data.get("status", "pending")
        profile.status = new_status
        profile.save()

        return Response({"message": f"Status updated to {profile.status}"})
    except SellerProfile.DoesNotExist:
        return Response({"detail": "Seller profile not found"}, status=404)


# ======================================================================
# DELETE USER
# ======================================================================

@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)

    user.delete()
    return Response({"message": f"User {user_id} deleted successfully"})


# ======================================================================
# ADMIN APPROVE / REJECT SELLER
# ======================================================================

@api_view(["POST"])
@permission_classes([IsAdminUser])
def admin_approve(request, user_id):
    try:
        profile = SellerProfile.objects.get(user__id=user_id)
    except SellerProfile.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    status_val = request.data.get("status", "approved")
    comment = request.data.get("admin_comment", "")

    profile.status = status_val
    profile.admin_comment = comment
    profile.save()

    return Response({
        "message": "Updated",
        "status": profile.status,
        "admin_comment": profile.admin_comment
    })
