# backend/settings.py

import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECRET_KEY = '8tn-zzsg(kowyzm0)1xp#1cy2^1au#imt@eb@m)_n#1ei(^yay'
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', default='None')

# DEBUG = True
DEBUG = True

# ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', default='web localhost 127.0.0.1 [::1]]').split(" ")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',
    'corsheaders',
    'users.apps.UsersConfig',
    'foodgram.apps.FoodgramConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

WSGI_APPLICATION = 'backend.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': os.getenv('POSTGRES_DB', default='postgres_db_1'),
        'USER': os.getenv('POSTGRES_USER', default='postgres_user_1'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='qawsed123456'),
        'HOST': os.getenv('DB_HOST', default='db'),
        'PORT': os.getenv('DB_PORT', default='5432')
    }
}

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

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'staticfiles')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'foodgram:index'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')
DEFAULT_FROM_EMAIL = 'noreply@api.ru'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS': 'api.pagination.FoodgramPagination',
    'PAGE_SIZE': 6,
}

DJOSER = {
    'LOGIN_FIELD': 'email',
    'LOGOUT_ON_PASSWORD_CHANGE': True,
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
        # 'user_list': ['rest_framework.permissions.IsAuthenticated'],
        # 'user_create': ['rest_framework.permissions.AllowAny'],
        # 'token_create': ['rest_framework.permissions.AllowAny'],
        # 'token_destroy': ['rest_framework.permissions.IsAuthenticated'],
        # 'activation': ['rest_framework.permissions.AllowAny'],
        # 'password_reset': ['rest_framework.permissions.AllowAny'],
        # 'password_reset_confirm': ['rest_framework.permissions.AllowAny'],
        # 'set_password': ['rest_framework.permissions.CurrentUserOrAdmin'],
        # 'username_reset': ['rest_framework.permissions.AllowAny'],
        # 'username_reset_confirm': ['rest_framework.permissions.AllowAny'],
        # 'set_username': ['rest_framework.permissions.CurrentUserOrAdmin'],
        # 'user_delete': ['rest_framework.permissions.IsAdminUser'],
    },
    'SERIALIZERS': {
        'user': 'api.serializers.UserSerializer',
        'user_create': 'api.serializers.UserCreateSerializer',
        'current_user': 'api.serializers.UserSerializer',
        # 'user': 'api.serializers.UserSerializer',
        # 'user_create': 'api.serializers.UserSerializer',
        # 'user_list': 'api.serializers.UserSerializer',
        # 'user_create': 'api.serializers.UserSerializer',
        # 'user': 'djoser.serializers.UserSerializer',
    },
}

AUTH_USER_MODEL = 'users.User'

RESERVED_USERNAME: str = r'me'

ACCEPT_REGEX: bool = False
REJECT_REGEX: bool = True

USERNAME_REGEXES: list = [
    (fr'(^{RESERVED_USERNAME})$', REJECT_REGEX,),
    (r'(^[\w.@+-]+)$', ACCEPT_REGEX,),
]

COLORS_HEX_REGEX: tuple = (r'^#(?:[0-9a-fA-F]{6})$', ACCEPT_REGEX,)

CORS_ALLOW_ALL_ORIGINS = True  # Старое наименование CORS_ORIGIN_ALLOW_ALL
CORS_URLS_REGEX = r'^/api/.*$', r'^/admin/.*$'
# CORS_ALLOWED_ORIGINS = []  # Старое наименование  CORS_ORIGIN_WHITELIST
