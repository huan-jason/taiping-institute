from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def get_secret(name: str) -> str:

    with open(f"{BASE_DIR}/secrets/{name}.txt") as f:
        return f.readline().strip()


ADMINS = [
    'huan.jason@gmail.com',
]

ALLOWED_HOSTS = ['*']

ASGI_APPLICATION = "project.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}

CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = [
    "https://*.agojin.com",
    "https://*.527664826.xyz",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': get_secret("postgres_password"),
        'HOST': 'db',
    },
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 10_000_000_000

DEBUG = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEFAULT_FROM_EMAIL = 'Agojin Admin<agojin917@gmail.com>'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'agojin917@gmail.com'
EMAIL_HOST_PASSWORD = get_secret("email_host_password")
EMAIL_USE_TLS = True
EMAIL_PORT = 587

INSTALLED_APPS = [
    'taiping',
    'project',
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

SECRET_KEY = get_secret("django_secret_key")

SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 3600

SESSION_COOKIE_SECURE = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

TIME_ZONE = 'Asia/Singapore'

USE_L10N = True

USE_THOUSAND_SEPARATOR = True

X_FRAME_OPTIONS = "SAMEORIGIN"
