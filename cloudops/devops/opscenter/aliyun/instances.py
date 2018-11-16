# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/1
@  author  : Xieyz
@  software: PyCharm
"""
import json
from opscenter.models import Support
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest, DescribeInstanceStatusRequest, \
    DescribeInstanceAutoRenewAttributeRequest


class Instances(object):

    def __init__(self, support_id, page_size=100, page_number=1):
        try:
            obj = Support.objects.get(id=support_id)
            self.accessKeyId = obj.access_key_id
            self.accessSecret = obj.access_key_secret
        except Support.DoesNotExist:
            exit(1)
        self.PageSize = page_size
        self.PageNumber = page_number

    def api_client(self, region_id):
        clt = client.AcsClient(self.accessKeyId, self.accessSecret, region_id)
        return clt

    def response(self, request, region_id, page_number=1, instance_id=None):
        """设置参数并请求"""
        request.set_accept_format('json')

        request.add_query_param('RegionId', region_id)
        if instance_id:
            request.add_query_param('InstanceId', instance_id)
        if self.PageSize:
            request.add_query_param('PageSize', 100)
        if self.PageNumber:
            request.add_query_param('PageNumber', page_number)
        # 发起请求
        response = self.api_client(region_id).do_action_with_exception(request)
        return json.loads(response.decode())

    def get_instances_detail(self, region_id):
        """获取一台或多台实例的详细信息"""
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        res = self.response(request, region_id)
        count = res['TotalCount']
        offset = 100
        page_number = 1
        while count - offset > 0:
            page_number += 1
            res_offest = self.response(request, region_id, page_number)
            offset += 100
            res['Instances']['Instance'] += res_offest['Instances']['Instance']
        return res

    def get_full_instances_status(self, region_id):
        """获取当前用户所有实例的状态信息"""
        request = DescribeInstanceStatusRequest.DescribeInstanceStatusRequest()
        res = self.response(request, region_id)
        return res

    def get_instance_auto_renew(self, region_id, instance_id=None):
        """查询实例自动续费状态"""
        request = DescribeInstanceAutoRenewAttributeRequest.DescribeInstanceAutoRenewAttributeRequest()
        res = self.response(request, region_id, instance_id)
        return res
