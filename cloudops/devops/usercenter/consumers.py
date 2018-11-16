# -*- coding: utf-8 -*-
"""
@  time    : 2018/7/5
@  author  : Xieyz
@  software: PyCharm
"""
import requests
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User, Group

class MyConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.add_group = None
        self.my_path = None
        await self.accept()
        print (self.scope)
        for i in self.scope['headers']:
            if i[0] == bytes('origin', encoding='utf-8'):
                self.my_path = str(i[1], encoding='utf-8')
        self.add_client_url = '{path}/usercenter/client/add/'.format(path=self.my_path)
        self.delete_client_url = '{path}/usercenter/client/delete/'.format(path=self.my_path)
        add_client_data = {'channel_name': self.channel_name, 'user':self.scope['user'].id}
        add_client = requests.post(url=self.add_client_url, data=add_client_data, cookies=self.scope['cookies'])
        self.client_id = add_client.json()['id']
        group_list_res = requests.post(url='{path}/usercenter/get_group_list_by_user/'.format(path=self.my_path),
                                        data={'id': self.scope['user'].id}, cookies=self.scope['cookies'])
        self.group_list = group_list_res.json()
        print(group_list_res)
        for group_id in self.group_list:
            await self.channel_layer.group_add("group-{group_id}".format(group_id=group_id), self.channel_name)
        await self.channel_layer.group_add("chat", self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            self.group_list = eval(text_data)['group']
            for i in self.group_list:
                await self.channel_layer.group_add(i, self.channel_name)
        except Exception as _:
            pass

    async def disconnect(self, close_code):
        if self.client_id:
            add_client = requests.delete(url=self.delete_client_url, data={'id': self.client_id},
                                         cookies=self.scope['cookies'])
        if self.group_list:
            for group_id in self.group_list:
                await self.channel_layer.group_discard("group-{group_id}".format(group_id=group_id), self.channel_name)
        await self.channel_layer.group_discard("chat", self.channel_name)
        if self.group_list:
            for i in self.group_list:
                await self.channel_layer.group_add(i, self.channel_name)
        await self.close()

    async def chat_message(self, event):
        await self.send(text_data=event["text"])
