# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/5
@  author  : Xieyz
@  software: PyCharm
"""
from opscenter.models import Support
import boto3


class Instances(object):
    def __init__(self, support_id, instance_id=None):
        try:
            obj = Support.objects.get(id=support_id)
            self.accessKeyId = obj.access_key_id
            self.accessSecret = obj.access_key_secret
        except Support.DoesNotExist:
            exit(1)
        self.session = boto3.Session(aws_access_key_id=self.accessKeyId, aws_secret_access_key=self.accessSecret)
        self.instance_id = instance_id

    def client(self, region_id, service_name='ec2'):
        self.region_id = region_id
        ApiClient = self.session.client(service_name=service_name, region_name=region_id)
        return ApiClient

    def get_instances_detail(self, region_id):
        response = self.client(region_id).describe_instances()['Reservations']
        return response
