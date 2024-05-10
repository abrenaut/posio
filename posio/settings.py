import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# Application definition

INSTALLED_APPS = [
    "daphne",
    "channels",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "game",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "posio.urls"

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

WSGI_APPLICATION = "posio.wsgi.application"
ASGI_APPLICATION = "posio.asgi.application"

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, 6379)],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.spatialite",
        "NAME": "db/posio.db",
        "USER": "geo",
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

if "SPATIALITE_LIBRARY_PATH" in os.environ:
    SPATIALITE_LIBRARY_PATH = os.environ["SPATIALITE_LIBRARY_PATH"]

if "GDAL_LIBRARY_PATH" in os.environ:
    GDAL_LIBRARY_PATH = os.environ["GDAL_LIBRARY_PATH"]

if "GEOS_LIBRARY_PATH" in os.environ:
    GEOS_LIBRARY_PATH = os.environ["GEOS_LIBRARY_PATH"]


DEBUG = True

ALLOWED_HOSTS = []

SECRET_KEY = "django-insecure-7=($1kgke##+h&14!f)x)@(fdfry!f!$onr4k62kbn&=d52phs"

STATIC_ROOT = os.path.join(BASE_DIR, "static")

# https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
if os.environ.get("ENV") == "production":
    DEBUG = False

    # Persist database connections for 60 seconds
    CONN_MAX_AGE = 60

    # Avoid transmitting the session cookie over HTTP accidentally
    SESSION_COOKIE_SECURE = True

    # Avoid transmitting the CSRF cookie over HTTP accidentally
    CSRF_COOKIE_SECURE = True

    SECRET_KEY = os.environ["SECRET_KEY"]
    ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(",")

    STATIC_ROOT = os.environ["STATIC_ROOT"]
    STATIC_URL = os.environ["STATIC_URL"]

    MEDIA_ROOT = os.environ["MEDIA_ROOT"]
    MEDIA_URL = os.environ["MEDIA_URL"]

    CSRF_TRUSTED_ORIGINS = os.environ["CSRF_TRUSTED_ORIGINS"].split(",")
