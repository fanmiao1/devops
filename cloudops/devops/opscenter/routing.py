from django.urls import path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .consumers import MyConsumer
from usercenter.consumers import MyConsumer as publicConsumer

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("websocket/chart/push/sid=<path:sid>/inoex=<path:inoex>/cid=<path:cid>/", MyConsumer),
            path('websocket.connect/', MyConsumer.connect),
            path('websocket.receive', MyConsumer.receive),
            path('websocket.disconnect', MyConsumer.disconnect),
            path("websocket/chart/ws_public/", publicConsumer),
            path('ws_public/connect', publicConsumer.connect),
            path('ws_public/receive', publicConsumer.receive),
            path('ws_public/disconnect', publicConsumer.disconnect),
        ])
    ),
})
