# mysite/asgi.py
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from channels.routing import get_default_application

application = get_default_application()
