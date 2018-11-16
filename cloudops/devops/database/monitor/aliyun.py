# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/19
@  author  : qingyw
@  class: ALiYun
"""
import json
from aliyunsdkcore import client
from opscenter.models import Support
from aliyunsdkrds.request.v20140815 import DescribeDBInstancesRequest, DescribeRegionsRequest, \
    DescribeDBInstancePerformanceRequest


class ALiYun(object):

    def __init__(self, support_id, region_id):
        try:
            obj = Support.objects.get(id=support_id)
            self.accessKeyId = obj.access_key_id
            self.accessSecret = obj.access_key_secret
            if region_id:
                self.clt = client.AcsClient(self.accessKeyId, self.accessSecret, region_id)
            else:
                self.clt = client.AcsClient(self.accessKeyId, self.accessSecret, 'cn-hangzhou')
        except Support.DoesNotExist:
            exit(1)

    def get_region(self):
        """获取 RDS 实例的区域信息"""
        request = DescribeRegionsRequest.DescribeRegionsRequest()
        res = self.clt.do_action_with_exception(request)
        return json.loads(res.decode())

    def get_instance(self):
        """获取 RDS 实例的列表信息"""
        request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
        res = self.clt.do_action_with_exception(request)
        return json.loads(res.decode())

    def get_instance_monitordata(self, instance_id, keys, starttime, endtime):
        """获取 RDS 实例的监控数据"""
        request = DescribeDBInstancePerformanceRequest.DescribeDBInstancePerformanceRequest()
        request.add_query_param('DBInstanceId', instance_id)
        request.add_query_param('Key', keys)
        request.add_query_param('StartTime', starttime)
        request.add_query_param('EndTime', endtime)
        res = self.clt.do_action_with_exception(request)
        return json.loads(res.decode())
