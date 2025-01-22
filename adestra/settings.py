
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-p#r@xi=7h4s0$oxhc-i7p59*e13j692upj!s+mr!%wpoy)(^!x'

DEBUG = True

ALLOWED_HOSTS = ["*"]

AUTH_USER_MODEL = 'account.CustomUser'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', 
    'account.backends.EmailBackend', 
]

CORS_ORIGIN_ALLOW_ALL = True  # or specify specific origins


INSTALLED_APPS = [
    'jazzmin',
    # 'rangefilter',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'account',
    'ckeditor'
]

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': 'auto',
    },
}



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'adestra.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'account.context_processors.user_balance_processor', 
                'account.context_processors.setting_processor', 
                'account.context_processors.notices_processor',
                'account.context_processors.admin_chart_processor',
            ],
            'libraries':{
            'custom_filters': 'core.templatetags.custom_filters',
            
            }
        },
    },
]

WSGI_APPLICATION = 'adestra.wsgi.application'



# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cparobust',
        'USER': 'user1',
        'PASSWORD': 'password1',
        # 'NAME': 'shambhdn_cparobust',
        # 'USER': 'shambhdn_cparobust',
        # 'PASSWORD': 'Cparobust@2024',
        'HOST': 'localhost', 
        'PORT': '3306',     
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}






JAZZMIN_SETTINGS = {
    "site_title": "Cparobust",

    "site_header": "Cparobust",

    "site_brand": "Cparobust",

    # "site_logo": "books/img/logo.png",

    # "login_logo": None,

    # "login_logo_dark": None,

    # "site_logo_classes": "img-circle",

    # "site_icon": None,

    "welcome_sign": "Welcome to the cparobust",

    "copyright": "Cparobust",

    "hide_recent_acitons" : True,

    "dashboard_links" : [
        {"name": "Manage Users", "url": '/admin/auth/user/', 'icon': 'fas fa-user'},
    ],


}










# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'cparobust.com'  # Outgoing server
EMAIL_PORT = 465              # SMTP Port for SSL
EMAIL_USE_SSL = True          # Use SSL
EMAIL_HOST_USER = 'noreply@cparobust.com'
EMAIL_HOST_PASSWORD = '1qazZAQ!@#1'  # Replace this with the actual password for the email account
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
