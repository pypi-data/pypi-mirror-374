_G='default'
_F='BACKEND'
_E='localhost'
_D='IS_CYPRESS'
_C='NAME'
_B=True
_A=False
from pathlib import Path
import os,socket
from itertools import product
from spartaqube_app.secrets import sparta_61772791e6
secrets_dict=sparta_61772791e6()
from mimetypes import add_type
add_type('application/javascript','.js',_B)
BASE_DIR=Path(__file__).resolve().parent.parent
LOGIN_URL='/login'
SECRET_KEY=secrets_dict['DJANGO_SECRET_KEY']
IS_CYPRESS=int(os.environ.get(_D,'0'))==1
IS_VITE=_A
IS_DEV=_A
IS_DEV_VIEW_ENABLED=_A
IS_LLM=_A
if IS_CYPRESS:IS_VITE=_A;IS_DEV=_A;IS_DEV_VIEW_ENABLED=_A;IS_LLM=_A;os.environ[_D]='0'
DEBUG=_A
DEFAULT_TIMEOUT=60
PROJECT_NAME='SpartaQube'
IS_GUEST_CODE_REQUIRED=_A
WEBSOCKET_PREFIX='ws'
HOST_WS_PREFIX=WEBSOCKET_PREFIX+'://'
CAPTCHA_SITEKEY=secrets_dict['CAPTCHA_SITEKEY']
CAPTCHA_SECRET=secrets_dict['CAPTCHA_SECRET_KEY']
SPARTAQUBE_WEBSITE='https://www.spartaqube.com'
FORBIDDEN_EMAIL='forbidden@spartaqube.com'
CONTACT_US_EMAIL=secrets_dict['CONTACT_US_EMAIL']
ADMIN_EMAIL_TICKET='contact@mysite.com'
ADMIN_DEFAULT_USER='admin'
ADMIN_DEFAULT_EMAIL='admin@spartaqube.com'
ADMIN_DEFAULT_PWD='admin'
URL_TERMS='www.spartaqube.com/terms'
URL_WEBSITE='www.spartaqube.com'
COMPANY_NAME='Spartacus Lab'
COMPANY_SLOGAN='A plug and play solution to visualize your data and build web components'
MAX_TICKETS=5
B_TOOLBAR=_A
DAPHNE_PREFIX=''
DATA_UPLOAD_MAX_MEMORY_SIZE=524288000
EPYC_HOST=''
SERVER_CF='https://registration-key-worker.spartaqube.workers.dev'
def sparta_620a7bfce8():A=socket.gethostname();B=socket.gethostbyname(A);return B
allowed_domains=['https://*.127.0.0.1','http://*.127.0.0.1','http://localhost',f"http://{EPYC_HOST}",'http://*','https://*','*']
ALLOWED_HOSTS=['django',_E,'localhost:*','localhost:81',EPYC_HOST,f"{EPYC_HOST}*",'*']+allowed_domains
CSRF_TRUSTED_ORIGINS=['http://localhost:*','http://localhost:81/*',f"http://{EPYC_HOST}/*",f"http://{EPYC_HOST}:3000*"]+allowed_domains
ports=range(1,65536)
protocols=['http','https']
hostnames=[_E,sparta_620a7bfce8()]
CSRF_TRUSTED_ORIGINS=[f"{A}://{B}"for A in protocols for B in hostnames]
CSRF_TRUSTED_ORIGINS+=[f"{A}://{B}:*"for A in protocols for B in hostnames]
CSRF_COOKIE_NAME='csrftoken'
CORS_ALLOW_CREDENTIALS=_B
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','corsheaders','channels','project']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware','whitenoise.middleware.WhiteNoiseMiddleware']
ROOT_URLCONF='spartaqube_app.urls'
TEMPLATES=[{_F:'django.template.backends.django.DjangoTemplates','DIRS':[os.path.join(BASE_DIR,'templates'),os.path.join(BASE_DIR,'project/templates')],'APP_DIRS':_B,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='spartaqube_app.wsgi.application'
ASGI_APPLICATION='spartaqube_app.routing.application'
X_FRAME_OPTIONS='ALLOWALL'
from spartaqube_app.db_path import sparta_65175fef66
LOCAL_DB_PATH=sparta_65175fef66()
DATABASES={_G:{'ENGINE':'django.db.backends.sqlite3',_C:LOCAL_DB_PATH}}
CACHES={_G:{_F:'django.core.cache.backends.locmem.LocMemCache','LOCATION':'spartaqube-cache'}}
AUTH_PASSWORD_VALIDATORS=[{_C:'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{_C:'django.contrib.auth.password_validation.MinimumLengthValidator'},{_C:'django.contrib.auth.password_validation.CommonPasswordValidator'},{_C:'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='en-us'
TIME_ZONE='UTC'
USE_I18N=_B
USE_TZ=_B
STATIC_URL='/static/'
STATIC_ROOT=os.path.join(BASE_DIR,'staticfiles')
STATICFILES_DIRS=os.path.join(BASE_DIR,'static'),os.path.join(BASE_DIR,'static/dist/')
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'