from django.urls import path
from . import views

urlpatterns = [
    path("auth/signup/", views.signup, name="signup"),
    path("auth/login/", views.login, name="login"),
    path("user/me/", views.user_me, name="user_me"),
    path("seller/update/<int:user_id>/", views.update_seller_profile, name="update_seller_profile"),
    path("auth/send-otp/", views.send_otp, name="send-otp"),
    path("auth/verify-otp/", views.verify_otp, name="verify-otp"),
    path("auth/forgot-password/", views.forgot_password, name="forgot-password"),
    path("auth/verify-reset-otp/", views.verify_reset_otp, name="verify-reset-otp"),
    path("auth/reset-password/", views.reset_password, name="reset-password"),
    path("auth/delete-user/<int:user_id>/", views.delete_user, name="delete_user"),
    path("seller/upload-doc/", views.upload_doc, name="upload_doc"),
    path("seller/status/<int:user_id>/", views.status_view, name="seller_status"),
    path("seller/update-status/", views.update_status, name="update_status"),
    path("admin/approve/<int:user_id>/", views.admin_approve, name="admin_approve"),
]
