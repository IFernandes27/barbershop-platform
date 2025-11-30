# barbershop/settings.py
from pathlib import Path
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dev-secret-key'  # substitui em produção
DEBUG = True
ALLOWED_HOSTS: list[str] = []

# ---------------------------
# APPS
# ---------------------------
INSTALLED_APPS = [
    # Django base
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps do projeto
    'bookings',
    'accounts',

    "widget_tweaks",
]

# ---------------------------
# MIDDLEWARE
# ---------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',      # suporte a i18n
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'barbershop.urls'

# ---------------------------
# TEMPLATES
# ---------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Ex: templates/index.html
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'barbershop.wsgi.application'

# ---------------------------
# BASE DE DADOS (SQLite)
# ---------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------------------------
# PASSWORD VALIDATORS
# ---------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------
# INTERNACIONALIZAÇÃO
# ---------------------------
LANGUAGE_CODE = 'pt'  # idioma padrão

LANGUAGES = [
    ('pt', _('Português')),
    ('en', _('English')),
]

USE_I18N = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'Europe/Lisbon'
USE_TZ = True

# ---------------------------
# FICHEIROS ESTÁTICOS E MEDIA
# ---------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']      # durante desenvolvimento
STATIC_ROOT = BASE_DIR / 'staticfiles'        # para collectstatic (produção)

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---------------------------
# AUTENTICAÇÃO E LOGIN
# ---------------------------
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'bookings:index'
LOGOUT_REDIRECT_URL = 'bookings:index'

# ---------------------------
# OUTRAS CONFIGURAÇÕES
# ---------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
