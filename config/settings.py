from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BRAND_IMAGES_ROOT = BASE_DIR / "brand-images"

SECRET_KEY = "django-insecure-impress-seating-dev-key"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "catalog.apps.CatalogConfig",
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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "catalog.context_processors.site_info",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_NAME = "Impress Signature Seating"
SITE_TAGLINE = "Luxury seating for every celebration"
SITE_PHONE = "+91 90872 10003"
SITE_PHONE_TEL = "+919087210003"
SITE_WHATSAPP = "919087210003"
SITE_EMAIL = "hello@impressseating.com"
SITE_ADDRESS_LINES = [
    "No. 86/1B1A Toll Plaza, Sea City Main Road,",
    "East Coast Rd, near Aruna Farm Lane, near Uthandi,",
    "Kannathur Reddy Kuppam, Chennai – 603112.",
]
SITE_MAP_EMBED = (
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3888.195587118873"
    "!2d80.24812969999999!3d12.959332999999997!2m3!1f0!2f0!3f0!3m2!1i1024!2i768"
    "!4f13.1!3m3!1m2!1s0x3a525d112e919141%3A0x4fe2e097091736a2!2sImpress%20Decors"
    "!5e0!3m2!1sen!2sin!4v1781339507632!5m2!1sen!2sin"
)
