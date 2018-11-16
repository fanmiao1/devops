# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/4
@  author  : Xieyz
@  software: PyCharm
"""
from opscenter.models import Support
from .sdk import UcloudApiClient

base_url = "https://api.ucloud.cn"


class Instances(object):

    def __init__(self, support_id, page_size=None, instance_id=None):
        try:
            obj = Support.objects.get(id=support_id)
            self.accessKeyId = obj.access_key_id
            self.accessSecret = obj.access_key_secret
        except Support.DoesNotExist:
            exit(1)
        self.instance_id = instance_id
        self.PageSize = page_size

    def api_client(self):
        alt = UcloudApiClient(base_url, self.accessKeyId, self.accessSecret)
        return alt

    def response(self, action, region_id, Offset=0):
        parameters = {
            "Action": action,
            "Region": region_id,
            "Limit": 100,
            "Offset": Offset
        }
        response = self.api_client().get("/", parameters)
        return response

    def get_instances_detail(self, region_id):
        action = "DescribeUHostInstance"
        res = self.response(action, region_id).json()
        count = res['TotalCount']
        offset = 100
        while count - offset > 0:
            res_offest = self.response(action, region_id, offset).json()
            offset += 100
            res['UHostSet'] += res_offest['UHostSet']
        res = str(res)
        return res
