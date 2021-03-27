# mysite/asgi.py
from channels.routing import get_default_application
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()


application = get_default_application()
