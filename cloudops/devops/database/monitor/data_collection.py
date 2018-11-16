# -*- coding: utf-8 -*-
"""
@  time    : 2018/6/20
@  author  : qingyw
@  func: collect_rds_instance, collect_rds_monitordata
"""
from .aliyun import ALiYun
from opscenter.models import Support
from database.models import RDSInstance, Instance, History, Item, Category
from django.utils import timezone
from django.db.models import Max
from dateutil.parser import parse
import ipaddress
from database.monitor.mysql_status import MySQLStatus
from database.aes_pycryto import Prpcrypt
from pandas import DataFrame
prpCryptor = Prpcrypt()


def collect_ali_instance(cloud_platform):
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
                        rds_instance.create_time = parse(row['CreateTime'].replace('T', ' ').replace('Z', ''))
                        rds_instance.expire_time = parse(row['ExpireTime'].replace('T', ' ').replace('Z', ''))
                        rds_instance.instance_status = row['DBInstanceStatus']
                        rds_instance.save()
        return True
    else:
        return False


def collect_ali_mysql():
    try:
        supports = Support.objects.filter(name__icontains='阿里云').values_list('id', flat=True)
        keys = 'MySQL_COMDML,MySQL_MemCpuUsage,MySQL_DetailedSpaceUsage,MySQL_NetworkTraffic,MySQL_QPSTPS,MySQL_IOPS,MySQL_Sessions,MySQL_RowDML'
        starttime = (timezone.now() - timezone.timedelta(minutes=5)).isoformat(timespec='minutes').replace("+00:00",
                                                                                                           "Z")
        endtime = (timezone.now()).isoformat(timespec='minutes').replace("+00:00", "Z")
        if supports:
            for support_id in supports:
                region_id = RDSInstance.objects.filter(support_id=support_id).values_list('region_id', flat=True)
                if region_id:
                    for reg_id in list(set(region_id)):
                        client = ALiYun(support_id, reg_id)
                        instance_id = RDSInstance.objects.filter(region_id=reg_id).values_list('instance_id', flat=True)
                        for ins_id in list(set(instance_id)):
                            instance_monitor = client.get_instance_monitordata(ins_id, keys, starttime, endtime)
                            if instance_monitor:
                                for item in instance_monitor['PerformanceKeys']['PerformanceKey']:
                                    if item['Values']['PerformanceValue']:
                                        item_list = item['ValueFormat'].split('&')
                                        item_value = item['Values']['PerformanceValue'][0]['Value'].split('&')
                                        clock = parse(item['Values']['PerformanceValue'][0]['Date'])
                                        for item_name in item_list:
                                            item_id = Item.objects.only('id').get(
                                                db_key=item_name).id if Item.objects.only('id').filter(
                                                db_key=item_name) else 0
                                            value = item_value[item_list.index(item_name)]
                                            if item_id:
                                                History.objects.get_or_create(instance_id=ins_id, item_id=item_id, value=value, delta_value=value, clock=clock)
        return True
    except Exception as e:
        print(str(e))
        return False


def collect_local_mysql(id):
    try:
        instance = Instance.objects.get(id=id)
        monitor = MySQLStatus(
            host=instance.server_ip,
            user=instance.instance_username,
            password=prpCryptor.decrypt(instance.instance_password),
            port=instance.instance_port
        )
        item = Item.objects.filter(key_type=1)
        clock = timezone.now().replace(microsecond=0)
        for row in item:
            a_value = monitor.exec(row.db_key)
            if row.delta:
                max_id = History.objects.filter(item_id=row.id, instance_id=instance.instance_name).aggregate(Max('id'))['id__max']
                if max_id:
                    b_value = History.objects.get(id=max_id)
                    delta_value = round((a_value - b_value.value) / (clock - b_value.clock).seconds, 2)
                else:
                    delta_value = 0
                History.objects.create(item_id=row.id, instance_id=instance.instance_name, value=a_value,
                                       delta_value=delta_value, clock=clock)
            else:
                History.objects.create(item_id=row.id, instance_id=instance.instance_name, value=a_value,
                                       delta_value=a_value, clock=clock)
        return True
    except Exception as e:
        print(str(e))
        return False


def get_data(item_id, physical_instance, ali_rds, start_time, end_time):
        item_data = {}
        for row in physical_instance:
            val = History.objects.filter(item_id=item_id, clock__gte=start_time, clock__lte=end_time,
                                         instance_id=row['instance_name']).values('clock', 'delta_value')
            item_data[row['instance_name']] = DataFrame(list(val)).values.tolist()
        for row in ali_rds:
            val = History.objects.filter(item_id=item_id, clock__gte=start_time, clock__lte=end_time,
                                         instance_id=row['instance_id']).values('clock', 'delta_value')
            item_data[row['instance_description']] = DataFrame(list(val)).values.tolist()
        return item_data
