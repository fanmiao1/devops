# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/6
@  author  : Xieyz
@  software: PyCharm
"""
from django.urls import path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .consumers import MyConsumer as publicConsumer

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("chart/ws_public/", publicConsumer),
            path('ws_public/connect', publicConsumer.connect),
            path('ws_public/receive', publicConsumer.receive),
            path('ws_public/disconnect', publicConsumer.disconnect),
        ])
    ),
})
