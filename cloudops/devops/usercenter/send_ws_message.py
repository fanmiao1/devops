# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/9
@  author  : Xieyz
@  software: PyCharm
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class Send(object):

    def __init__(self, text):
        self.text = text
        self.channel_layer = get_channel_layer()

    def personal(self, channel_name):
        async_to_sync(self.channel_layer.send)(channel_name, {"type": "chat.message", "text":self.text})

    def group(self, group_name):
        async_to_sync(self.channel_layer.group_send)(group_name, {"type": "chat.message", "text": self.text})
