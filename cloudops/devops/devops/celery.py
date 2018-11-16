#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   time    : 2018/4/4 10:36
#   author  : Mosasaur Wu
#   software: PyCharm
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devops.settings')
app = Celery('aukeyops')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
