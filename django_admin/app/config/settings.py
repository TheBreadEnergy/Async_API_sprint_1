import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from split_settings.tools import include

from .components import constants

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DEBUG", "False") == "True"


if DEBUG:
    load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = (
    os.environ.get("ALLOWED_HOSTS").split(",")
    if os.environ.get("ALLOWED_HOSTS")
    else ["127.0.0.1"]
)
INTERNAL_IPS = (
    os.environ.get("INTERNAL_HOSTS").split(",")
    if os.environ.get("INTERNAL_HOSTS")
    else ["127.0.0.1"]
)

include("components/apps.py")
include("components/database.py")
include("components/templates.py")
include("components/validators.py")
include("components/middlewares.py")
include("components/internationalization.py")
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

STATIC_URL = "/static/"
if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "staticfiles")]
STATIC_ROOT = BASE_DIR / "static"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
