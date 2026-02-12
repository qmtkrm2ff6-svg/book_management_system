import os
from pathlib import Path
from dotenv import load_dotenv

# 1. 自动读取项目根目录下的 .env 文件
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-8!gr1+(#x=&q8nq=00trg+w*@!xz9d0t!ni8icb5j^zz(hp!y6'

DEBUG = True

ALLOWED_HOSTS = []

# 2. 注册 Swagger 和 REST Framework 插件
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',  # Django REST framework
    'django_filters',  # 确保这个也在，用于搜索功能
    'drf_yasg',        # Swagger 文档插件
    'books',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# 3. 数据库配置：从 .env 文件中读取变量
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', '123456'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans'  # 改为中文界面
TIME_ZONE = 'Asia/Shanghai' # 改为北京时间
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 4. REST Framework 全局配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'books.authenticator.FlexibleJWTAuthentication',
    ),
    # 开启全局登录限制：所有接口默认都必须带 Token 才能访问
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
}

# 5. JWT 详细配置
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # 令牌 60 分钟后过期，需要重新登录或刷新
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# settings.py

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization', # 依然保持这个请求头名字
            'in': 'header',
            'description': '直接粘贴你的 Access Token 即可（无需输入 Bearer 前缀）'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}


LOGIN_URL = '/login/'  # 我们接下来要创建的登录地址
LOGIN_REDIRECT_URL = '/'  # 登录成功后跳回书籍列表
LOGOUT_REDIRECT_URL = '/'