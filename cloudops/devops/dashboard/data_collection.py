# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/20
@  author  : qingyw
@  func: collect_rds_instance, collect_rds_monitordata
"""
from dashboard.aliyun import ALiYun
from opscenter.models import Support
from dashboard.models import RDSInstance
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect


def collect_rds_instance(cloud_platform):
    supports = Support.objects.filter(name__icontains=cloud_platform).values_list('id', flat=True)
    if supports:
        for support_id in supports:
            region_id = []
            client = ALiYun(support_id, region_id=None)
            regions = client.get_region()
            for row in regions['Regions']['RDSRegion']:
                region_id.append(row['RegionId'])
            for id in list(set(region_id)):
                client = ALiYun(support_id, id)
                instances = client.get_instance()
                if instances['TotalRecordCount']:
                    for row in instances['Items']['DBInstance']:
                        if RDSInstance.objects.filter(instance_id=row['DBInstanceId']):
                            rds_instance = RDSInstance.objects.get(instance_id=row['DBInstanceId'])
                        else:
                            rds_instance = RDSInstance()
                        rds_instance.support_id = support_id
                        rds_instance.instance_id = row['DBInstanceId']
                        rds_instance.instance_type = row['DBInstanceType']
                        rds_instance.instance_class = row['DBInstanceClass']
                        rds_instance.engine = row['Engine']
                        rds_instance.engine_version = row['EngineVersion']
                        rds_instance.region_id = row['RegionId']
                        rds_instance.instance_description = row['DBInstanceDescription']
                        rds_instance.create_time = row['CreateTime']
                        rds_instance.expire_time = row['ExpireTime']
                        rds_instance.instance_status = row['DBInstanceStatus']
                        rds_instance.save()
        return True
    else:
        return False


def collect_rds_monitordata(cloud_platform):
    supports = Support.objects.filter(name__icontains=cloud_platform).values_list('id', flat=True)
    monitordata = []
    keys = 'MySQL_QPSTPS,MySQL_IOPS,MySQL_MemCpuUsage'
    starttime = (timezone.now() - timezone.timedelta(hours=4)).isoformat(timespec='minutes').replace("+00:00", "Z")
    endtime = (timezone.now()).isoformat(timespec='minutes').replace("+00:00", "Z")
    if supports:
        for support_id in supports:
            region_id = RDSInstance.objects.only('region_id').values_list('region_id', flat=True)
        for id in list(set(region_id)):
            client = ALiYun(support_id, region_id)
            instance_id = RDSInstance.objects.only('region_id').filter(region_id=region_id).values_list('region_id', flat=True)
            for id in instance_id:
                instance_monitor = client.get_instance_monitordata(id, keys, starttime, endtime)
                if instance_monitor:
                    monitordata.append(instance_monitor)
    return JsonResponse({'result': monitordata})
