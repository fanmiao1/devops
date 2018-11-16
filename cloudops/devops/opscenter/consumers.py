# -*- coding: utf-8 -*-
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from .models import SshOperationLogs, Certificate, Server
import paramiko
import select
import time
import socket
import sys

MAX_DATA_BUFFER = 1024*1024

class MyConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        stream = self.scope["url_route"]["kwargs"]
        if stream:
            try:
                sid = stream['sid']
                inoex = stream['inoex']
                cid = stream['cid']
            except Exception as _:
                await self.send(text_data='连接失败，请检查实例和凭证')
            else:
                cert_obj = Certificate.objects.get(id=int(cid))
                server_obj = Server.objects.get(id=int(sid))
                conn_ip = getattr(server_obj, inoex)

                await self.accept()
                self.hostname = conn_ip
                port = cert_obj.port
                username = cert_obj.username
                password = cert_obj.key
                self.ssh = paramiko.SSHClient()
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    self.ssh.connect(
                        hostname=self.hostname,
                        port=port,
                        username=username,
                        password=password,
                        timeout=15
                    )
                    self.data = self.ssh.invoke_shell(term='xterm')
                    a_control = 0
                    while a_control < 3:
                        result = self.data.recv(512).decode()
                        await self.send(result)
                        if not result:
                            break
                        a_control += 1
                except Exception as _:
                    await self.send(text_data='连接失败')
                    await self.close()

    async def receive(self, text_data=None, bytes_data=None,**kwargs):
        self.data.send(text_data)
        self.text_data = text_data
        # time.sleep(0.1)
        readlist, writelist, errlist = select.select([self.data], [], [])
        if self.data in readlist:
            ret = self.data.recv(MAX_DATA_BUFFER)
            await self.send(text_data=ret.decode())

    async def disconnect(self, message, **kwargs):
        try:
            await self.ssh.close()
            result = "Ssh close success!"
        except:
            result = "Ssh close Faild!"
        await self.close()
        # try:
        #     add_log = SshOperationLogs()
        #     add_log.user = self.scope["user"]
        #     add_log.host = self.hostname
        #     add_log.operation_record = self.text_data
        #     add_log.save()
        # except AttributeError as e:
        #     pass

