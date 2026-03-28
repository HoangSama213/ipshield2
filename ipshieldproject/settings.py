from pathlib import Path
import mimetypes
import os
mimetypes.init()
mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("text/javascript", ".js", True)
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-0f1o%1de=udhg@xz6o$k=&d$t_16^!gr2!p7lcrg(q_p8527l0"

DEBUG = True
ALLOWED_HOSTS = ["ipshield.vn", "www.ipshield.vn",'127.0.0.1', 'localhost']


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
     "django.contrib.staticfiles",
    'django.contrib.humanize',
    "ipshieldapp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ipshieldproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "ipshieldapp.context_processors.global_sliders",
            ],
        },
    },
]

WSGI_APPLICATION = "ipshieldproject.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

TIME_ZONE = "Asia/Ho_Chi_Minh"

USE_I18N = True
USE_TZ = False

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

STATIC_ROOT = BASE_DIR / 'staticfiles'





# MEDIA FILES (UPLOAD)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'



DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
# ============================
# CSRF & SECURITY (FIX 403)
# ============================

CSRF_TRUSTED_ORIGINS = [
    "https://ipshield.vn",
    "https://www.ipshield.vn",
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_DOMAIN = ".ipshield.vn"
SESSION_COOKIE_DOMAIN = ".ipshield.vn"