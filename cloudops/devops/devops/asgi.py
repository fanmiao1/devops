# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/31
@  author  : XieYZ
@  software: PyCharm
"""
import os
import django
from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devops.settings")
django.setup()
application = get_default_application()
