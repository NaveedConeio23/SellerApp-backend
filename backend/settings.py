import os
import dj_database_url
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# BASIC SETTINGS
# -------------------------------------------------------------------

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# -------------------------------------------------------------------
# INSTALLED APPS
# -------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "corsheaders",

    "cloudinary",
    "cloudinary_storage",

    "sellers",
]

# -------------------------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------------------------

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

# -------------------------------------------------------------------
# TEMPLATES
# -------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# -------------------------------------------------------------------
# DATABASE
# -------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT'),
        'OPTIONS': {
            'sslmode': 'require'
        }
    }
}

# -------------------------------------------------------------------
# PASSWORD VALIDATION
# -------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = []

# -------------------------------------------------------------------
# INTERNATIONALIZATION
# -------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# STATIC & MEDIA CONFIG (IMPORTANT FOR AZURE)
# -------------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Media via Cloudinary (always used for Azure)
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

MEDIA_URL = "/media/"

# -------------------------------------------------------------------
# CLOUDINARY CONFIG
# -------------------------------------------------------------------

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}

# -------------------------------------------------------------------
# CORS SETTINGS
# -------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    os.getenv("FRONTEND_URL", ""),   # Azure frontend URL (optional)
]

CORS_ALLOW_CREDENTIALS = True

# -------------------------------------------------------------------
# REST FRAMEWORK + JWT
# -------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.getenv("SIMPLE_JWT_SECRET", SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# -------------------------------------------------------------------
# EMAIL SETTINGS (Works with Gmail / SMTP)
# -------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")


